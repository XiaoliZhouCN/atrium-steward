# qt/tools/colorpicker_window.py
from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QGroupBox, QGridLayout 
from PySide6.QtCore import Qt, QTimer
from ..tool_window import ToolWindow
import colorpicker

try:
    from colorpicker import ScreenCapturer, GeometryProvider
except ImportError:
    # 如果导入失败（比如未安装），给出友好提示
    print("警告：无法导入 ChestPyTools，取色功能不可用。")
    # 定义占位类
    class ScreenCapturer:
        def capture_pixel(self, x, y):
            return (0.5, 0.5, 0.5)
    class GeometryProvider:
        def mouse_location(self):
            return (0.0, 0.0)
class ColorPickerWindow(ToolWindow):
    """屏幕取色器工具窗口（真实取色逻辑）"""

    def __init__(self, parent=None):
        super().__init__("取色器", parent)
        self.setFixedSize(400, 420)

        # 创建平台适配层实例
        self.capturer = ScreenCapturer()
        self.geometry = GeometryProvider()

        # UI 布局
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # 标题
        title = QLabel("🎨 屏幕取色器")
        title.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(title, alignment=Qt.AlignCenter)

        # 色块显示
        self.swatch = QLabel()
        self.swatch.setFixedSize(240, 140)
        self.swatch.setStyleSheet("background-color: #6c5ce7; border-radius: 10px; border: 2px solid #444;")
        layout.addWidget(self.swatch, alignment=Qt.AlignCenter)

        # 数值显示区域（使用网格布局）
        value_group = QGroupBox("颜色值")
        grid = QGridLayout(value_group)
        grid.setHorizontalSpacing(20)

        self.label_r = QLabel("R: 0.0000")
        self.label_g = QLabel("G: 0.0000")
        self.label_b = QLabel("B: 0.0000")
        self.label_hex = QLabel("HEX: #000000")
        self.label_coord = QLabel("坐标: (0, 0)")

        # 设置等宽字体
        mono_font = "monospace"
        for lbl in [self.label_r, self.label_g, self.label_b, self.label_hex, self.label_coord]:
            lbl.setStyleSheet(f"font-family: {mono_font}; font-size: 13px;")

        grid.addWidget(self.label_r, 0, 0)
        grid.addWidget(self.label_g, 0, 1)
        grid.addWidget(self.label_b, 1, 0)
        grid.addWidget(self.label_hex, 1, 1)
        grid.addWidget(self.label_coord, 2, 0, 1, 2)

        layout.addWidget(value_group)

        # 按钮区域
        btn_layout = QHBoxLayout()

        self.pick_btn = QPushButton("📸 单次取色")
        self.pick_btn.setFixedWidth(120)
        self.pick_btn.clicked.connect(self.pick_once)
        btn_layout.addWidget(self.pick_btn, alignment=Qt.AlignCenter)

        self.auto_btn = QPushButton("▶ 自动取色")
        self.auto_btn.setFixedWidth(120)
        self.auto_btn.setCheckable(True)
        self.auto_btn.clicked.connect(self.toggle_auto_pick)
        btn_layout.addWidget(self.auto_btn, alignment=Qt.AlignCenter)

        layout.addLayout(btn_layout)

        # 状态提示
        self.hint_label = QLabel("💡 将鼠标移动到任意位置，点击「单次取色」或开启「自动取色」")
        self.hint_label.setStyleSheet("color: #888; font-size: 12px;")
        self.hint_label.setWordWrap(True)
        layout.addWidget(self.hint_label)

        # 定时器（用于自动取色）
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_color)
        self.timer_interval = 100  # 毫秒

        # 初始化取色一次（显示默认值）
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
            # 1. 获取鼠标坐标
            x, y = self.geometry.mouse_location()
            # 坐标可能是浮点数，取整
            x_int = int(round(x))
            y_int = int(round(y))

            # 2. 捕获像素颜色
            r, g, b = self.capturer.capture_pixel(x_int, y_int)

            # 3. 更新 UI
            # 色块
            r_byte = int(min(r, 1.0) * 255)  # 如果 >1.0（HDR），截断显示
            g_byte = int(min(g, 1.0) * 255)
            b_byte = int(min(b, 1.0) * 255)
            hex_color = f"#{r_byte:02x}{g_byte:02x}{b_byte:02x}"
            self.swatch.setStyleSheet(
                f"background-color: {hex_color}; border-radius: 10px; border: 2px solid #444;"
            )

            # 数值
            self.label_r.setText(f"R: {r:.4f}")
            self.label_g.setText(f"G: {g:.4f}")
            self.label_b.setText(f"B: {b:.4f}")
            self.label_hex.setText(f"HEX: {hex_color.upper()}")
            self.label_coord.setText(f"坐标: ({x_int}, {y_int})")

            # 如果颜色值 >1.0，在提示中显示 HDR 标志
            if r > 1.0 or g > 1.0 or b > 1.0:
                self.hint_label.setText("💡 HDR 颜色值 (>1.0) 已捕获，显示已裁切为 0-1 范围。")
            else:
                # 如果当前没有特殊提示，恢复默认
                if not self.auto_btn.isChecked():
                    # 单次取色后不覆盖提示
                    pass

        except Exception as e:
            # 捕获任何错误（如像素读取失败）
            self.hint_label.setText(f"❌ 取色失败: {str(e)}")
            # 不更新 UI 颜色

    def closeEvent(self, event):
        """窗口关闭时停止定时器"""
        self.timer.stop()
        super().closeEvent(event)