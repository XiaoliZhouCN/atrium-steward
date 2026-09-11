# ChestSteward/qt/tool_window.py
"""工具窗口基类。"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget

class ToolWindow(QWidget):
    """所有工具窗口的基类，统一管理关闭事件"""
    closed = Signal()  # 窗口关闭时通知主面板
    
    def __init__(self, tool_name: str, parent=None):
        super().__init__(parent)
        self.tool_name = tool_name
        self._stay_on_top = False
    
    def init_ui(self):
        """子类完成自身属性初始化后调用此方法，触发 UI 构建三部曲"""
        self._setup_ui()
        self._setup_signals()
        self._setup_defaults()

    # ========== UI 构建规范（子类必须覆写） ==========
    def _setup_ui(self):
        """子类必须覆写此方法以构建 UI 控件和布局"""
        self.setWindowTitle(f"ChestSteward — {self.tool_name}")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setMinimumSize(400, 300)

    def _setup_signals(self):
        """信号与槽连接。子类可按需覆写，非必须。"""
        pass

    def _setup_defaults(self):
        """初始状态设置（如默认显示内容）。子类可按需覆写。"""
        pass

    # ========== 通用功能 ==========
    def set_stay_on_top(self, enabled: bool):
        """设置窗口是否置顶显示（在所有窗口之上）。"""
        if enabled == self._stay_on_top:
            return

        self._stay_on_top = enabled
        flags = self.windowFlags()
        if enabled:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)

        self.hide()
        self.show()

    def is_stay_on_top(self) -> bool:
        """返回当前是否置顶。"""
        return bool(self.windowFlags() & Qt.WindowType.WindowStaysOnTopHint)

    # ========== 事件处理 ==========
    def closeEvent(self, event):
        """关闭时发出信号，由主程序决定后续导航。"""
        self.closed.emit()
        super().closeEvent(event)
