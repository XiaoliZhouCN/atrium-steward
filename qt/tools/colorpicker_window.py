# qt/tools/colorpicker_window.py
from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt
from ..tool_window import ToolWindow

class ColorPickerWindow(ToolWindow):
    """取色器工具窗口（当前为占位，后续接入真实取色逻辑）"""
    
    def __init__(self, parent=None):
        super().__init__("取色器", parent)
        self.setFixedSize(360, 280)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # 标题
        title = QLabel("🎨 屏幕取色器")
        title.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(title, alignment=Qt.AlignCenter)
        
        # 色块占位
        swatch = QLabel()
        swatch.setFixedSize(200, 120)
        swatch.setStyleSheet("background-color: #6c5ce7; border-radius: 10px;")
        layout.addWidget(swatch, alignment=Qt.AlignCenter)
        
        # 数值占位
        labels = QLabel("R: 0.8000    G: 0.4000    B: 0.2000")
        labels.setStyleSheet("font-family: monospace; font-size: 14px;")
        layout.addWidget(labels, alignment=Qt.AlignCenter)
        
        # 按钮
        btn_layout = QHBoxLayout()
        pick_btn = QPushButton("📸 单次取色")
        pick_btn.setFixedWidth(120)
        pick_btn.clicked.connect(lambda: labels.setText("📸 已取色（模拟）"))
        btn_layout.addWidget(pick_btn, alignment=Qt.AlignCenter)
        
        auto_btn = QPushButton("▶ 自动取色")
        auto_btn.setFixedWidth(120)
        auto_btn.setCheckable(True)
        auto_btn.clicked.connect(lambda checked: auto_btn.setText("⏹ 停止" if checked else "▶ 自动取色"))
        btn_layout.addWidget(auto_btn, alignment=Qt.AlignCenter)
        
        layout.addLayout(btn_layout)
        
        # 提示
        hint = QLabel("💡 后续接入真实取色逻辑")
        hint.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(hint, alignment=Qt.AlignCenter)