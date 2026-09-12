"""主程序入口。"""

import sys
from importlib import import_module
from pathlib import Path

ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

import keyboard
from PySide6.QtCore import QMetaObject, Qt
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import QApplication, QMenu, QStyle, QSystemTrayIcon

from core.tool_registry import get_enabled_tools, get_tool_spec
from qt.launcher_window import LauncherWindow

APP_SERVER_NAME = "ChestSteward.SingletonServer"


class SingleInstanceGuard:
    """使用本地命名 socket 保证仅启动一个实例。"""

    def __init__(self, server_name: str):
        self.server_name = server_name
        self.server: QLocalServer | None = None
        self.activate_callback = None

    def start_or_notify_existing(self) -> bool:
        """尝试成为主实例；若失败则通知已存在实例并返回 False。"""
        if self._notify_existing_instance():
            return False

        # 清理异常退出后残留的本地服务名。
        QLocalServer.removeServer(self.server_name)

        self.server = QLocalServer()
        self.server.newConnection.connect(self._process_pending_connections)
        if not self.server.listen(self.server_name):
            print("[SingleInstance] Failed to listen on local server.")
            return False

        return True

    def set_activate_callback(self, activate_callback) -> None:
        """设置主实例收到激活消息后的处理函数。"""
        self.activate_callback = activate_callback

    def cleanup(self) -> None:
        """关闭本地监听并清理服务名。"""
        if self.server is not None:
            self.server.close()
            self.server.deleteLater()
            self.server = None
        QLocalServer.removeServer(self.server_name)

    def _notify_existing_instance(self) -> bool:
        """如果已存在实例，则发送激活消息。"""
        socket = QLocalSocket()
        socket.connectToServer(self.server_name)
        if not socket.waitForConnected(150):
            socket.abort()
            return False

        socket.write(b"activate")
        socket.flush()
        socket.waitForBytesWritten(150)
        socket.disconnectFromServer()
        return True

    def _process_pending_connections(self) -> None:
        """处理其他实例发来的激活请求。"""
        if self.server is None:
            return

        while self.server.hasPendingConnections():
            socket = self.server.nextPendingConnection()
            if socket is None:
                continue

            socket.waitForReadyRead(150)
            _ = bytes(socket.readAll())
            socket.disconnectFromServer()
            socket.deleteLater()
            if self.activate_callback is not None:
                self.activate_callback()


class ChestStewardApp:
    """协调 Launcher、工具窗口和系统托盘。"""

    def __init__(self):
        self.tool_windows: dict[str, object] = {}
        self.tool_specs = get_enabled_tools()
        self.tray_icon: QSystemTrayIcon | None = None

        self.launcher = LauncherWindow(self.tool_specs)
        self.launcher.tool_triggered.connect(self.open_tool)
        self.launcher.hide_to_tray.connect(self.launcher.hide_with_animation)
        self.launcher.quit_app.connect(QApplication.quit)

        self._register_hotkey()
        self._setup_tray_icon()
        self.launcher.show_with_animation()

    def _register_hotkey(self):
        """注册全局热键。失败时仅记录，不阻塞主流程。"""
        try:
            keyboard.add_hotkey("ctrl+shift+space", self.toggle_launcher)
            print("[Hotkey] Ctrl+Shift+Space registered")
        except Exception as exc:
            print(f"[Hotkey] Failed to register: {exc}")

    def toggle_launcher(self):
        """将显示切换排队到 Qt 主线程执行。"""
        QMetaObject.invokeMethod(
            self.launcher,
            "toggle_visibility",
            Qt.ConnectionType.QueuedConnection,
        )

    def activate_main_window(self):
        """唤起已存在实例的主入口窗口。"""
        if self.launcher.isVisible():
            self.launcher.raise_()
            self.launcher.activateWindow()
            self.launcher.setFocus()
            return

        self.launcher.show_with_animation()

    def open_tool(self, tool_name: str):
        """创建或激活工具窗口。"""
        if tool_name in self.tool_windows:
            window = self.tool_windows[tool_name]
            window.raise_()
            window.activateWindow()
            self.launcher.hide_with_animation()
            return

        tool_spec = get_tool_spec(tool_name)
        if tool_spec is None or not tool_spec.enabled:
            print(f"[Tool] Unknown tool: {tool_name}")
            return

        module = import_module(tool_spec.module_path)
        window_class = getattr(module, tool_spec.class_name)
        window = window_class()
        window.closed.connect(
            lambda tool_id=tool_name: self._handle_tool_closed(tool_id)
        )

        self.tool_windows[tool_name] = window
        window.show()
        self.launcher.hide_with_animation()

    def _handle_tool_closed(self, tool_name: str):
        """工具窗口关闭后返回主 Launcher。"""
        self.tool_windows.pop(tool_name, None)

        if not any(window.isVisible() for window in self.tool_windows.values()):
            self.launcher.show_with_animation()

    def _setup_tray_icon(self):
        """初始化系统托盘图标。"""
        if self.tray_icon is not None:
            return

        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("[Tray] System tray not supported.")
            return

        self.tray_icon = QSystemTrayIcon(self.launcher)
        icon = QApplication.style().standardIcon(QStyle.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("ChestSteward")
        self.tray_icon.activated.connect(self._on_tray_activated)

        menu = QMenu()
        show_action = menu.addAction("显示 / 隐藏")
        show_action.triggered.connect(self.toggle_launcher)
        menu.addSeparator()
        quit_action = menu.addAction("退出")
        quit_action.triggered.connect(QApplication.quit)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_launcher()


def main():
    """创建应用并进入事件循环。"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("ChestSteward")

    single_instance = SingleInstanceGuard(APP_SERVER_NAME)
    if not single_instance.start_or_notify_existing():
        print("[SingleInstance] Existing instance activated.")
        return 0

    style_path = ROOT_DIR / "qt" / "resources" / "style.qss"
    if style_path.exists():
        with open(style_path, "r", encoding="utf-8") as file:
            app.setStyleSheet(file.read())

    steward = ChestStewardApp()
    single_instance.set_activate_callback(steward.activate_main_window)

    exit_code = app.exec()
    single_instance.cleanup()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
