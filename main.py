# main.py
import sys
import threading
from pathlib import Path

ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
import keyboard  # 全局热键库

from qt.launcher_window import LauncherWindow
from qt.tools.colorpicker_window import ColorPickerWindow
from qt.tools.mermaid_window import MermaidWindow
from qt.bridge import Bridge

def start_flask():
    """后台启动 Flask（后续供 Mermaid 预览使用）"""
    try:
        from web.flask_app import app
        print("[Flask] Starting on http://127.0.0.1:8080")
        app.run(host='127.0.0.1', port=8080, debug=False, use_reloader=False)
    except Exception as e:
        print(f"[Flask] Error: {e}")

class ChestStewardApp:
    def __init__(self):
        # 桥梁（后续扩展）
        self.bridge = Bridge()
        
        # 主面板
        self.launcher = LauncherWindow()
        self.launcher.tool_triggered.connect(self.open_tool)
        
        # 工具窗口注册表
        self.tool_windows = {}
        
        # 注册全局热键：Ctrl+Shift+Space（可自行修改）
        try:
            keyboard.add_hotkey('ctrl+shift+space', self.toggle_launcher)
            print("[Hotkey] Ctrl+Shift+Space registered")
        except Exception as e:
            print(f"[Hotkey] Failed to register: {e}")
        
        # ⭐ 新增：启动后默认显示主面板
        self.launcher.show_with_animation()
    
    def toggle_launcher(self):
        """切换主面板显示状态"""
        if self.launcher.isVisible():
            self.launcher.hide_with_animation()
        else:
            self.launcher.show_with_animation()
    
    def open_tool(self, tool_name: str):
        """创建或激活工具窗口"""
        # 如果窗口已存在，激活它
        if tool_name in self.tool_windows:
            window = self.tool_windows[tool_name]
            window.raise_()
            window.activateWindow()
            self.launcher.hide_with_animation()
            return
        
        # 创建新窗口
        if tool_name == "colorpicker":
            window = ColorPickerWindow()
        elif tool_name == "mermaid":
            window = MermaidWindow()
        else:
            print(f"[Tool] Unknown tool: {tool_name}")
            return
        
        # 注册关闭事件
        window.closed.connect(lambda: self.tool_windows.pop(tool_name, None))
        window.show()
        self.tool_windows[tool_name] = window
        
        # 隐藏主面板
        self.launcher.hide_with_animation()

def main():
    # 1. 后台启动 Flask（暂时不影响主流程）
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    # 2. 启动 Qt 应用
    app = QApplication(sys.argv)
    
    # 设置全局样式（暗色风格）
    app.setStyleSheet("""
        QWidget {
            background-color: #1a1a1e;
            color: #e0e0e0;
        }
        QPushButton {
            background-color: #2a2a30;
            border: 1px solid #3a3a40;
            border-radius: 6px;
            padding: 8px 16px;
        }
        QPushButton:hover {
            background-color: #3a3a45;
        }
        QLineEdit {
            background-color: #2a2a30;
            border: 1px solid #3a3a40;
            border-radius: 6px;
            padding: 6px 10px;
            color: #e0e0e0;
        }
        QTextEdit {
            background-color: #1a1a1e;
            border: 1px solid #3a3a40;
            border-radius: 6px;
            color: #e0e0e0;
        }
    """)
    
    steward = ChestStewardApp()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()