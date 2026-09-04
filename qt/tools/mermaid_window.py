# qt/tools/mermaid_window.py
from PySide6.QtWidgets import QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt
from ..tool_window import ToolWindow

class MermaidWindow(ToolWindow):
    """Mermaid 编辑器工具窗口（当前为占位，后续接入 WebView 预览）"""
    
    def __init__(self, parent=None):
        super().__init__("Mermaid 编辑器", parent)
        self.setGeometry(200, 200, 800, 600)
        
        layout = QVBoxLayout(self)
        
        # 提示
        title = QLabel("📝 Mermaid 流程图编辑器")
        title.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(title)
        
        # 编辑器占位
        self.editor = QTextEdit()
        self.editor.setPlainText("graph TD\n    A[开始] --> B[结束]")
        layout.addWidget(self.editor)
        
        # 按钮
        btn_layout = QHBoxLayout()
        render_btn = QPushButton("🔄 刷新预览")
        render_btn.clicked.connect(self.render_preview)
        btn_layout.addWidget(render_btn)
        
        export_btn = QPushButton("💾 导出 SVG")
        export_btn.clicked.connect(lambda: print("导出功能待实现"))
        btn_layout.addWidget(export_btn)
        layout.addLayout(btn_layout)
        
        # 预览占位
        preview_hint = QLabel("📊 预览区域（后续接入 WebView + Mermaid.js）")
        preview_hint.setStyleSheet("background-color: #1e1e1e; color: #aaa; padding: 40px; border-radius: 8px;")
        preview_hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(preview_hint)
    
    def render_preview(self):
        print(f"Mermaid 代码:\n{self.editor.toPlainText()}")