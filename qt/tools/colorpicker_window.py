# ChestSteward/qt/tools/colorpicker_window.py
"""取色器工具窗口。"""
from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QGroupBox, QGridLayout 
from PySide6.QtCore import Qt, QTimer
from ..tool_window import ToolWindow
from colorpicker import sample_at_cursor

class ColorPickerWindow(ToolWindow):
    """屏幕取色器工具窗口（真实取色逻辑）"""

    def __init__(self, parent=None):
        super().__init__("取色器", parent)
        
        self.timer = QTimer(self)
        self.timer_interval = 100

        self.init_ui()

    # ============ UI 构建区域（视觉分离） ============
    def _setup_ui(self):
        """只负责创建控件和布局，不涉及业务逻辑"""
        super()._setup_ui()

        self.setFixedSize(400, 420)
        self.set_stay_on_top(True)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        
        # 标题
        self.title_label = QLabel("🎨 屏幕取色器")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: 600;")
        main_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 色块
        self.swatch = QLabel()
        self.swatch.setFixedSize(240, 140)
        self.swatch.setStyleSheet("background-color: #6c5ce7; border-radius: 10px; border: 2px solid #444;")
        main_layout.addWidget(self.swatch, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.value_group = QGroupBox("颜色值")
        self._setup_value_grid()
        main_layout.addWidget(self.value_group)
        
        self._setup_buttons(main_layout)
        
        self.hint_label = QLabel("💡 将鼠标移动到任意位置...")
        self.hint_label.setStyleSheet("color: #888; font-size: 12px;")
        self.hint_label.setWordWrap(True)
        main_layout.addWidget(self.hint_label)
        
        self.setLayout(main_layout)

    def _setup_value_grid(self):
        """提取数值区域的 Grid 布局创建"""
        grid = QGridLayout(self.value_group)
        grid.setHorizontalSpacing(20)
        
        self.label_r = QLabel("R: 0.0000")
        self.label_g = QLabel("G: 0.0000")
        self.label_b = QLabel("B: 0.0000")
        self.label_hex = QLabel("HEX: #000000")
        self.label_coord = QLabel("坐标: (0, 0)")
        
        mono_font = "monospace"
        for lbl in [self.label_r, self.label_g, self.label_b, self.label_hex, self.label_coord]:
            lbl.setStyleSheet(f"font-family: {mono_font}; font-size: 13px;")
        
        grid.addWidget(self.label_r, 0, 0)
        grid.addWidget(self.label_g, 0, 1)
        grid.addWidget(self.label_b, 1, 0)
        grid.addWidget(self.label_hex, 1, 1)
        grid.addWidget(self.label_coord, 2, 0, 1, 2)

    def _setup_buttons(self, parent_layout):
        """提取按钮区域的创建"""
        btn_layout = QHBoxLayout()
        
        self.pick_btn = QPushButton("📸 单次取色")
        self.pick_btn.setFixedWidth(120)
        btn_layout.addWidget(self.pick_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.auto_btn = QPushButton("▶ 自动取色")
        self.auto_btn.setFixedWidth(120)
        self.auto_btn.setCheckable(True)
        btn_layout.addWidget(self.auto_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        parent_layout.addLayout(btn_layout)

    # ============ 信号连接区域（逻辑分离） ============
    def _setup_signals(self):
        """只负责信号的绑定"""
        self.pick_btn.clicked.connect(self.pick_once)
        self.auto_btn.clicked.connect(self.toggle_auto_pick)
        self.timer.timeout.connect(self.update_color)

    # ============ 默认状态设置 ============
    def _setup_defaults(self):
        """只负责初始化显示状态"""
        self.update_color()

    def pick_once(self):
        """单次取色，并给出反馈"""
        self.update_color()
        self.hint_label.setText("✅ 已取色 (单次)")

    def toggle_auto_pick(self, checked: bool):
        """切换自动取色"""
        if checked:
            self.timer.start(self.timer_interval)
            self.auto_btn.setText("⏹ 停止")
            self.hint_label.setText("🔄 自动取色已开启 (100ms)")
        else:
            self.timer.stop()
            self.auto_btn.setText("▶ 自动取色")
            self.hint_label.setText("⏸ 自动取色已暂停")

    def update_color(self):
        """获取当前鼠标位置的颜色并更新 UI"""
        try:
            color = sample_at_cursor()
            x_int = int(round(color["x"]))
            y_int = int(round(color["y"]))
            r = float(color["r"])
            g = float(color["g"])
            b = float(color["b"])

            r_byte = self._to_byte(r)
            g_byte = self._to_byte(g)
            b_byte = self._to_byte(b)
            hex_color = f"#{r_byte:02x}{g_byte:02x}{b_byte:02x}"
            self.swatch.setStyleSheet(
                f"background-color: {hex_color}; border-radius: 10px; border: 2px solid #444;"
            )

            self.label_r.setText(f"R: {r:.4f}")
            self.label_g.setText(f"G: {g:.4f}")
            self.label_b.setText(f"B: {b:.4f}")
            self.label_hex.setText(f"HEX: {hex_color.upper()}")
            self.label_coord.setText(f"坐标: ({x_int}, {y_int})")

            if r > 1.0 or g > 1.0 or b > 1.0:
                self.hint_label.setText("💡 HDR 颜色值 (>1.0) 已捕获，显示已裁切为 0-1 范围。")
        except Exception as e:
            self.hint_label.setText(f"❌ 取色失败: {str(e)}")

    @staticmethod
    def _to_byte(value: float) -> int:
        """将浮点颜色值裁切到 0-255 的显示范围。"""
        return int(max(0.0, min(value, 1.0)) * 255)

    def closeEvent(self, event):
        """窗口关闭时停止定时器，再交给基类发信号"""
        self.timer.stop()
        super().closeEvent(event)
