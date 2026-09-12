# ChestSteward/qt/launcher_window.py
"""Launcher 主面板。"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QPushButton,
    QLabel, QFrame, QHBoxLayout
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, Slot

from core.tool_registry import ToolSpec

class LauncherWindow(QWidget):
    """主面板：轻量启动器，类似 Spotlight"""
    tool_triggered = Signal(str)  # 工具名称 → 唤起对应窗口
    quit_app = Signal()           # 关闭整个程序
    hide_to_tray = Signal()       # 隐藏到托盘（-按钮）
    closed = Signal()             # 主面板关闭时通知（保留）
    
    def __init__(self, tool_specs: tuple[ToolSpec, ...]):
        super().__init__()
        self.tool_specs = tool_specs

        # 基本窗口属性（与 UI 分离，但放在 __init__ 最简洁）
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(560, 340)

        self._setup_ui()
        self._setup_signals()
        self._setup_defaults()
   
    # ============ 信号连接区域 ============
    def _setup_signals(self):
        """连接所有信号与槽"""
        for btn in self.tool_buttons:
            tool_name = btn.property("tool_name")
            btn.clicked.connect(lambda checked, n=tool_name: self.tool_triggered.emit(n))

        self.min_btn.clicked.connect(self.hide_to_tray.emit)
        self.close_btn.clicked.connect(self.quit_app.emit)

    # ============ 默认状态设置 ============
    def _setup_defaults(self):
        """初始化动画和窗口透明度（与 UI 状态相关）"""
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.setWindowOpacity(1.0)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def _clear_animation_finished_connections(self):
        """清理动画结束信号，避免重复连接。"""
        try:
            self.animation.finished.disconnect()
        except (RuntimeError, TypeError):
            pass

    @Slot()
    def toggle_visibility(self):
        if self.isVisible():
            self.hide_with_animation()
        else:
            self.show_with_animation()

    @Slot()
    def show_with_animation(self):
        """带淡入动画的显示"""
        self._clear_animation_finished_connections()
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.show()
        self.raise_()
        self.activateWindow()
        self.setFocus()
        self.animation.start()
    
    @Slot()
    def hide_with_animation(self):
        """带淡出动画的隐藏"""
        self._clear_animation_finished_connections()
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(
            self._on_fade_out_finished,
            Qt.ConnectionType.SingleShotConnection,
        )
        self.animation.start()
    
    @Slot()
    def _on_fade_out_finished(self):
        """淡出结束后的专用处理：隐藏窗口"""
        self.hide()
        
    def keyPressEvent(self, event):
        """ESC 键关闭主面板"""
        if event.key() == Qt.Key.Key_Escape:
            self.hide_with_animation()
            return
        super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """窗口关闭时发射 closed 信号（兼容基类风格）"""
        self.closed.emit()
        super().closeEvent(event)

    # ============ UI 构建区域 ============
    def _setup_ui(self):
        """创建所有控件、布局和样式表（纯视觉）"""
        self.container = QFrame(self)
        self.container.setGeometry(0, 0, 560, 340)
        self.container.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 30, 35, 0.92);
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.08);
            }
        """)

        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        title_row = QHBoxLayout()
        title_row.setSpacing(0)

        self.title_label = QLabel("🎯 ChestSteward")
        self.title_label.setStyleSheet("color: #ffffff; font-size: 20px; font-weight: 600;")
        title_row.addWidget(self.title_label)
        title_row.addStretch()

        self.min_btn = QPushButton("—")
        self.min_btn.setFixedSize(28, 28)
        self.min_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: rgba(255,255,255,0.5);
                font-size: 18px;
                font-weight: 300;
            }
            QPushButton:hover {
                color: #ffffff;
                background-color: rgba(100, 150, 255, 0.2);
                border-radius: 14px;
            }
            QPushButton:pressed {
                background-color: rgba(100, 150, 255, 0.4);
            }
        """)
        title_row.addWidget(self.min_btn)

        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: rgba(255,255,255,0.5);
                font-size: 16px;
                font-weight: 300;
            }
            QPushButton:hover {
                color: #ffffff;
                background-color: rgba(255, 80, 80, 0.2);
                border-radius: 14px;
            }
            QPushButton:pressed {
                background-color: rgba(255, 80, 80, 0.4);
            }
        """)
        title_row.addWidget(self.close_btn)

        main_layout.addLayout(title_row)

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(10)

        self.tool_buttons = []
        for idx, tool_spec in enumerate(self.tool_specs):
            btn = QPushButton(tool_spec.title)
            btn.setFixedHeight(52)
            btn.setProperty("tool_name", tool_spec.tool_id)
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
            self.grid_layout.addWidget(btn, idx // 3, idx % 3)
            self.tool_buttons.append(btn)

        main_layout.addLayout(self.grid_layout)

        self.hint_label = QLabel("Ctrl + Shift + Space 唤起 / 隐藏  |  ESC 关闭")
        self.hint_label.setStyleSheet("color: rgba(255,255,255,0.35); font-size: 11px;")
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.hint_label)
