# ChestSteward/qt/tool_window.py
"""
tool_window 基类， tools/ 目录下的所有窗口继承自该类
（当前保留，后续扩展）
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget

class ToolWindow(QWidget):
    """所有工具窗口的基类，统一管理关闭事件"""
    closed = Signal()  # 窗口关闭时通知主面板
    
    def __init__(self, tool_name: str, parent=None):
        super().__init__(parent)
        self.tool_name = tool_name
        self.setWindowTitle(f"ChestSteward — {tool_name}")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setMinimumSize(400, 300)
    
    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)