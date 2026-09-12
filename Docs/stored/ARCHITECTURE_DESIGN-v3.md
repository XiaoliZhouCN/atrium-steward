

# ChestSteward 架构设计文档

> **项目**：ChestSteward  
> **版本**：v2.0（Launcher 架构版）  
> **修订日期**：2026-09-04  
> **架构师**：System Architect

---

## 1. 项目概述

### 1.1 一句话定义

> **ChestSteward** —— 个人数字工作区的总控大脑，采用 **"Qt 原生主面板（Launcher）+ 独立工具窗口"** 架构，负责聚合展示项目进度、调度 Python 工具链、提供原生系统交互能力（全局热键、屏幕取色、色彩管理）。

### 1.2 核心目标

1. **轻量启动**：通过 `Ctrl+Shift+Space` 唤起 Spotlight 风格主面板，快速访问所有工具。
2. **工具隔离**：每个工具运行在独立窗口中，互不干扰，可自由拖拽、缩放、关闭。
3. **原生性能**：高频交互（取色、数值刷新）由 Qt 原生控件直接处理，延迟 < 5ms。
4. **复杂图表按需加载**：Mermaid 流程图、色度图等复杂可视化由 WebView 按需加载，不占用主界面资源。
5. **工具链集成**：通过 `pip install -e ../ChestPyTools` 直接调用纯 Python 工具函数。

---

## 2. 技术选型与选型博弈

| 架构维度 | 最终技术选型 | 核心理由 |
| :--- | :--- | :--- |
| **桌面框架** | PySide6（Qt 6） | 成熟稳定、原生系统 API 丰富、轻量窗口管理 |
| **主面板形态** | Qt 原生 `QWidget`（Frameless + 半透明） | Spotlight 风格，原生动画，极低资源占用 |
| **工具窗口** | 独立 `QWidget` / `QDialog` | 每个工具独立运行，互不阻塞 |
| **Web 引擎** | QWebEngineView | 仅用于 Mermaid/色度图等复杂图表 |
| **Web 服务** | Flask（轻量） | 为 WebView 提供图表数据，无状态，易扩展 |
| **通信桥梁** | Qt WebChannel | Python ↔ JavaScript 双向通信（仅 WebView 工具需要） |
| **全局热键** | `keyboard` 库 | 跨平台，简单可靠 |
| **工具调用** | 直接 import（`pip install -e ../ChestPyTools`） | 进程内调用，零序列化开销 |
| **配置文件** | YAML | 人类可读，Python 原生支持 |

### 2.1 架构演进路径

| 阶段 | 架构 | 说明 |
| :--- | :--- | :--- |
| **v1.0（已弃用）** | 全 Web（Flask + NiceGUI + Qt WebView） | 取色延迟高，系统能力受限 |
| **v1.5（过渡）** | Qt 主窗口 + WebView 全屏 | 中间态，仍依赖 Web 做 UI |
| **v2.0（当前）** | **Qt Launcher + 独立工具窗口** | 原生优先，Web 按需加载 ✅ |

---

## 3. 系统架构

### 3.1 整体分层架构

```text
┌─────────────────────────────────────────────────────────────────────┐
│                        用户交互层（User Interaction）                │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  全局热键：Ctrl+Shift+Space → 唤起/隐藏主面板               │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   主面板层（Launcher Layer）                         │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  LauncherWindow（Qt 原生）                                  │    │
│  │  - 无边框、置顶、半透明背景                                 │    │
│  │  - 淡入淡出动画                                             │    │
│  │  - 工具网格（按钮列表）                                     │    │
│  │  - 搜索框（预留）                                           │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                    tool_triggered 信号
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     工具窗口层（Tool Windows）                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  ToolWindow（基类，统一关闭事件）                           │    │
│  │  ┌─────────────────────────────────────────────────────┐   │    │
│  │  │  纯 Qt 原生工具（取色器）                            │   │    │
│  │  │  - 实时色块、RGB 数值                               │   │    │
│  │  │  - 自动/单次取色                                    │   │    │
│  │  │  - 快捷键复制                                       │   │    │
│  │  └─────────────────────────────────────────────────────┘   │    │
│  │  ┌─────────────────────────────────────────────────────┐   │    │
│  │  │  Qt + WebView 混合工具（Mermaid 编辑器）            │   │    │
│  │  │  - 左侧：Qt 原生编辑器（QTextEdit）                 │   │    │
│  │  │  - 右侧：QWebEngineView 加载 Mermaid.js 预览        │   │    │
│  │  └─────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    工具实现层（Tool Implementation）                 │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  ChestPyTools（pip install -e 引入）                       │    │
│  │  ├─ colorpicker.core.pick_screen_color() → 返回纯数据      │    │
│  │  └─ ...                                                   │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    数据服务层（Data Service）                        │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Flask（后台线程）                                         │    │
│  │  └─ /mermaid → Mermaid 预览页面                           │    │
│  │  └─ /chromaticity → 色度图页面（预留）                    │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 数据流

**示例：用户点击"取色器" → 点击"单次取色"**

```text
1. 用户按 Ctrl+Shift+Space → Launcher 显示
2. 用户点击"取色器"按钮 → Launcher 发射 tool_triggered("colorpicker") 信号
3. main.py 中 open_tool() 创建 ColorPickerWindow 实例
4. ColorPickerWindow 显示（独立窗口）
5. 用户点击"单次取色"按钮 → 触发 on_pick_once()
6. on_pick_once() 调用 from ChestPyTools.tools.colorpicker import pick_screen_color
7. pick_screen_color() 返回 ScreenColorResult（纯数据类）
8. Qt 原生控件直接更新：swatch.setStyleSheet(...) + labels.setText(...)
9. 整个过程无 Web 参与，延迟 < 5ms
```

---

## 4. 关键模块设计

### 4.1 LauncherWindow（主面板）

```python
# qt/launcher_window.py
class LauncherWindow(QWidget):
    tool_triggered = Signal(str)  # 工具名称 → 唤起对应窗口
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(560, 340)
        # 半透明背景 + 圆角
        # 工具网格布局
        # 淡入淡出动画
```

### 4.2 ToolWindow（工具窗口基类）

```python
# qt/tool_window.py
class ToolWindow(QWidget):
    closed = Signal()  # 窗口关闭时通知主面板
    
    def __init__(self, tool_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"ChestSteward — {tool_name}")
        self.setAttribute(Qt.WA_DeleteOnClose)
    
    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)
```

### 4.3 ColorPickerWindow（取色器工具）

```python
# qt/tools/colorpicker_window.py
class ColorPickerWindow(ToolWindow):
    def __init__(self, parent=None):
        super().__init__("取色器", parent)
        # 布局：色块 + R/G/B/HEX 标签 + 控制按钮
        # 定时器：自动取色刷新
    
    def update_color(self):
        from ChestPyTools.tools.colorpicker import pick_screen_color
        result = pick_screen_color()
        # 直接更新 Qt 原生控件（无 Web 参与）
        self.swatch.setStyleSheet(...)
        self.label_r.setText(...)
```

### 4.4 MermaidWindow（混合工具）

```python
# qt/tools/mermaid_window.py
class MermaidWindow(ToolWindow):
    def __init__(self, parent=None):
        super().__init__("Mermaid 编辑器", parent)
        # 左侧：QTextEdit（原生编辑器）
        # 右侧：QWebEngineView（加载 Flask /mermaid 页面）
        # WebChannel：推送代码给前端 Mermaid.js
```

---

## 5. 目录结构与模块职责

| 目录/文件 | 职责 | 依赖 |
| :--- | :--- | :--- |
| `main.py` | 应用入口，注册热键，管理主面板和工具窗口 | `qt/`, `web/` |
| `qt/launcher_window.py` | 主面板（Spotlight 风格） | `PySide6` |
| `qt/tool_window.py` | 工具窗口基类 | `PySide6` |
| `qt/tools/colorpicker_window.py` | 取色器工具（纯 Qt 原生） | `PySide6`, `ChestPyTools` |
| `qt/tools/mermaid_window.py` | Mermaid 编辑器（Qt + WebView） | `PySide6`, `PySide6-Addons`, `web/` |
| `qt/bridge.py` | WebChannel 桥梁（仅供 WebView 工具使用） | `PySide6`, `PySide6-Addons` |
| `web/flask_app.py` | Flask 服务，提供 Mermaid/色度图页面 | `Flask` |
| `web/templates/mermaid.html` | Mermaid 预览模板 | `Flask` |
| `core/` | 业务逻辑（扫描 YAML、日程聚合） | `PyYAML` |

---

## 6. 架构约束 / 红线规则

| 编号 | 规则 | 违反后果 |
| :--- | :--- | :--- |
| S1 | `core/` 不得 import `PySide6` 或 `Q*` | 代码评审不通过 |
| S2 | **高频交互（取色、数值刷新）必须使用 Qt 原生控件，禁止走 WebView** | 性能不合格 |
| S3 | `qt/tools/` 中每个工具窗口必须继承 `ToolWindow` | 无法正确通知主面板 |
| S4 | `qt/bridge.py` 仅供 WebView 工具使用，纯 Qt 工具不得依赖它 | 引入不必要的复杂度 |
| S5 | `ChestPyTools` 中的工具函数必须是纯函数（无状态、无 UI） | 工具无法被独立测试 |
| S6 | 所有异步操作（取色、爬虫）必须通过定时器或信号槽，避免阻塞 UI | UI 卡顿 |

---

## 7. 色彩管理相关功能预留

### 7.1 屏幕取色器交互设计

- **触发方式**：在取色器窗口中点击"自动取色"或"单次取色"。
- **体验**：自动取色模式下，每 80ms 刷新一次，色块和数值实时更新。
- **悬浮放大镜**（预留）：Qt 原生窗口（`Qt.FramelessWindowHint` + `Qt.WindowStaysOnTopHint`）跟随鼠标，显示 10x 放大像素。

### 7.2 与 `ChestPyTools` 的接口约定

```python
# 色彩工具的核心接口（未来扩展）
def pick_screen_color(sampling_size: int = 50) -> ScreenColorResult:
    """捕获当前鼠标位置的屏幕颜色，返回结构化数据。"""
    pass

def get_display_icc_profile(monitor_index: int = 0) -> ICCProfile:
    """获取指定显示器的 ICC 配置文件。"""
    pass

def convert_color_space(color: tuple, src: str, dst: str) -> tuple:
    """在不同色彩空间间转换（RGB ↔ XYZ ↔ CIELAB 等）。"""
    pass
```

---

## 8. 构建与部署

### 8.1 开发环境启动

```bash
cd ./Manager/manager/ChestSteward
pip install -e ../ChestPyTools  # 将工具库安装为可编辑包
python main.py                   # 启动 Qt 应用
```

### 8.2 打包为独立应用

```bash
pyinstaller --name ChestSteward --windowed --add-data "web/templates:templates" main.py
```

---

## 9. 版本计划

| 版本 | 核心功能 |
| :--- | :--- |
| v0.1 | Launcher 主面板显示 + 热键唤起 |
| v0.2 | 工具窗口基类 + 取色器占位窗口 |
| v0.3 | 取色器接入 ChestPyTools 真实取色逻辑 |
| v0.4 | Mermaid 编辑器（Qt + WebView） |
| v0.5 | 色度图工具（WebView + ECharts） |
| v1.0 | 完整工具链 + 打包发布 |