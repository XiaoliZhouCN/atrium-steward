# ChestSteward/qt/tools/mermaid_window.py
"""Mermaid 占位窗口。"""
from PySide6.QtWidgets import QVBoxLayout, QLabel, QTextEdit
from PySide6.QtCore import Qt
from ..tool_window import ToolWindow

class MermaidWindow(ToolWindow):
    """Mermaid 编辑器占位窗口。"""
    
    def __init__(self, parent=None):
        super().__init__("Mermaid", parent)
        self.init_ui()
        
    def _setup_ui(self):
        super()._setup_ui()
        self.resize(760, 520)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        title = QLabel("📝 Mermaid 占位窗口")
        title.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(title)

        description = QLabel("当前阶段仅保留占位，不接入 WebView / Flask / Mermaid 渲染链路。")
        description.setWordWrap(True)
        description.setStyleSheet("color: #a0a0a0;")
        layout.addWidget(description)

        self.editor = QTextEdit()
        self.editor.setReadOnly(True)
        self.editor.setPlainText("graph TD\n    A[开始] --> B[结束]")
        layout.addWidget(self.editor)
        
        preview_hint = QLabel("预览区域暂未启用。关闭窗口后将返回主 Launcher。")
        preview_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_hint.setStyleSheet(
            "background-color: #1e1e1e; color: #aaa; padding: 24px; border-radius: 8px;"
        )
        layout.addWidget(preview_hint)
