# ChestSteward/qt/launcher_window.py
"""
launcher_window 唤起主界面
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QPushButton, 
    QLineEdit, QLabel, QFrame
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QFont, QColor, QPalette

class LauncherWindow(QWidget):
    """主面板：轻量启动器，类似 Spotlight"""
    tool_triggered = Signal(str)  # 工具名称 → 唤起对应窗口
    closed = Signal()  # 主面板关闭时通知主窗口
    
    def __init__(self):
        super().__init__()
        # 窗口属性：置顶、无边框、半透明背景
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(560, 340)
        
        # 主容器（带圆角和半透明背景）
        container = QFrame(self)
        container.setGeometry(0, 0, 560, 340)
        container.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 30, 35, 0.92);
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.08);
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        # 标题
        title = QLabel("🎯 ChestSteward")
        title.setStyleSheet("color: #ffffff; font-size: 20px; font-weight: 600;")
        layout.addWidget(title)
        
        # 工具网格
        grid = QGridLayout()
        grid.setSpacing(10)
        
        # 定义工具列表：(显示名称, 内部标识)
        tools = [
            ("🎨 取色器", "colorpicker"),
            ("📝 Mermaid", "mermaid"),
            ("📁 项目看板", "dashboard"),
            ("⚙️ 设置", "settings"),
        ]
        
        for idx, (label, name) in enumerate(tools):
            btn = QPushButton(label)
            btn.setFixedHeight(52)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.06);
                    border: 1px solid rgba(255, 255, 255, 0.06);
                    border-radius: 8px;
                    color: #e0e0e0;
                    font-size: 14px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.12);
                    border-color: rgba(100, 150, 255, 0.3);
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 0.18);
                }
            """)
            btn.clicked.connect(lambda checked, n=name: self.tool_triggered.emit(n))
            grid.addWidget(btn, idx // 3, idx % 3)
        
        layout.addLayout(grid)
        
        # 底部提示
        hint = QLabel("shift + ctrl + space 唤起 / 隐藏  |  ESC 关闭")
        hint.setStyleSheet("color: rgba(255,255,255,0.35); font-size: 11px;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)
        
        # 动画
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def show_with_animation(self):
        """带淡入动画的显示"""
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.show()
        self.animation.start()
    
    def hide_with_animation(self):
        """带淡出动画的隐藏"""
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(self.hide)
        self.animation.start()
    
    def keyPressEvent(self, event):
        """ESC 键关闭主面板"""
        if event.key() == Qt.Key.Key_Escape:
            self.hide_with_animation()
            return
        super().keyPressEvent(event)