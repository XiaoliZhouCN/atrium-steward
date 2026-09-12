# ChestSteward 架构设计文档

> **项目**：ChestSteward  
> **版本**：v1.0  
> **修订日期**：2026-09-03  
> **架构师**：System Architect

---

## 1. 项目概述

### 1.1 一句话定义

> **ChestSteward** —— 个人数字工作区的总控大脑，一个 **Qt 桌面应用外壳 + 内嵌 Web 仪表盘** 的混合架构系统，负责聚合展示所有项目进度、调度 Python 工具链、提供原生系统交互能力（全局热键、屏幕取色、色彩管理）。

### 1.2 核心目标

1. **信息聚合**：读取 `config.yaml` 扫描所有 `manager/` 和 `projects/` 下的状态文件，统一展示。
2. **工具调度**：通过 Qt WebChannel 调用 `ChestPyTools` 中的纯函数，将结果推送给 Web 前端展示。
3. **原生交互**：利用 Qt 提供全局热键、屏幕取色、系统色彩 API 调用等 Web 无法实现的能力。
4. **美观易用**：WebView 中运行 NiceGUI，提供现代化 UI 组件和图表。

---

## 2. 技术选型与选型博弈

| 架构维度 | 最终技术选型 | 核心理由 |
| :--- | :--- | :--- |
| **桌面框架** | PySide6（Qt 6） | 成熟稳定、原生系统 API 丰富、QWebEngineView 完美支持 Chromium 内核 |
| **Web 引擎** | QWebEngineView | 官方支持，与 Qt WebChannel 无缝集成 |
| **Web 服务** | Flask + NiceGUI | 零前端代码构建 UI，兼顾开发效率与美观 |
| **通信桥梁** | Qt WebChannel | Python ↔ JavaScript 双向通信，官方支持，低延迟 |
| **工具调用** | 直接 import（`pip install -e ../ChestPyTools`） | 进程内调用，零序列化开销，调试方便 |
| **系统交互** | `pynput` + `keyboard` + `win32gui`（Windows） | Qt 热键 API + Python 库双保险 |
| **配置文件** | YAML | 人类可读，Python 原生支持 |
| **部署** | PyInstaller 打包为独立 `.exe` | 分发给导师/面试官无需安装环境 |

### 2.1 为什么不用纯 Web 或纯 Qt？

| 方案 | 优点 | 缺点 | 结论 |
| :--- | :--- | :--- | :--- |
| 纯 Web 浏览器 | 跨平台、UI 丰富 | 无法获取屏幕色值、无法监听全局热键 | ❌ 否决 |
| 纯 Qt Widgets | 原生性能、完全控制 | UI 开发效率低、图表/动画实现繁琐 | ❌ 否决 |
| **Qt + WebView（本方案）** | 兼具原生能力与 Web 开发效率 | 体积较大（~100MB），可接受 | ✅ **采用** |

---

## 3. 系统架构

### 3.1 整体分层架构

```text
┌─────────────────────────────────────────────────────────────────┐
│                    表现层（Presentation Layer）                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Qt 原生控件（悬浮窗、托盘图标、全局热键）               │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  QWebEngineView（加载 Flask + NiceGUI）                 │    │
│  │  └─ 仪表盘页面、项目详情、图表、色彩对比工具              │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    通信层（Communication Layer）                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Qt WebChannel（双向 JSON 序列化通信）                   │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    业务逻辑层（Business Logic Layer）            │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  core/                                                  │    │
│  │  ├─ repo_scanner.py  (扫描项目状态)                     │    │
│  │  ├─ config_loader.py (加载 YAML)                       │    │
│  │  └─ scheduler.py     (日程聚合)                         │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    工具层（Tool Layer）                         │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  ChestPyTools（通过 pip install -e 引入）               │    │
│  │  ├─ colorpicker/   → 返回 ScreenColorResult            │    │
│  │  ├─ crawler/       → 返回 list[dict]                   │    │
│  │  └─ ...                                                │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 数据流

**示例：用户点击“屏幕取色”按钮**

```text
1. 用户在 Web 页面点击“取色”按钮
   ↓
2. JavaScript 调用 Qt WebChannel 暴露的 bridge.pickColor()
   ↓
3. bridge.py 中调用 ChestPyTools.tools.colorpicker.core.pick_screen_color()
   ↓
4. PyTools 返回 ScreenColorResult（hex, rgb, xyz, cie_lab, pixel_preview_bgr）
   ↓
5. bridge.py 将结果通过 WebChannel 发送给 JavaScript
   ↓
6. JavaScript 更新页面上的色块、色度图、RGB 数值
   ↓
7. （可选）Qt 主窗口显示原生悬浮放大镜（QWidget 置顶）
```

---

## 4. 关键模块设计

### 4.1 MainWindow（主窗口）

```python
# qt/main_window.py
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChestSteward")
        
        # 创建 WebView
        self.web_view = QWebEngineView()
        self.web_view.load(QUrl("http://127.0.0.1:5000"))
        
        # 创建 WebChannel 桥梁
        self.bridge = Bridge()
        self.web_view.page().setWebChannel(self.channel)
        self.channel.registerObject("bridge", self.bridge)
        
        # 设置为中心控件
        self.setCentralWidget(self.web_view)
```

### 4.2 Bridge（通信桥梁）

```python
# qt/bridge.py
from PySide6.QtCore import QObject, Signal
from ChestPyTools.tools.colorpicker import pick_screen_color

class Bridge(QObject):
    color_picked = Signal(str)  # 发送 JSON 给 JS
    
    @Slot()
    def pick_color(self):
        result = pick_screen_color()
        self.color_picked.emit(json.dumps(result.__dict__))
    
    @Slot(str)
    def run_tool(self, tool_name: str, params: str):
        # 动态调用 PyTools 中的工具
        pass
```

### 4.3 前端调用示例（NiceGUI + JS）

```javascript
// 嵌入在 NiceGUI 页面中（通过 ui.html() 或 ui.javascript()）
new QWebChannel(qt.webChannelTransport, function(channel) {
    window.bridge = channel.objects.bridge;
    bridge.colorPicked.connect(function(jsonData) {
        const data = JSON.parse(jsonData);
        document.getElementById('color_hex').innerText = data.hex;
        document.getElementById('color_preview').style.backgroundColor = data.hex;
        // 更新 ECharts 色度图...
    });
});

function onPickColor() {
    bridge.pick_color();
}
```

---

## 5. 目录结构与模块职责

| 目录/文件 | 职责 | 依赖 |
| :--- | :--- | :--- |
| `main.py` | 应用入口，启动 Flask 和 Qt | `qt/`, `web/` |
| `qt/main_window.py` | 主窗口布局、QWebEngineView 管理 | `qt/bridge.py` |
| `qt/bridge.py` | Qt ↔ JS 通信桥梁 | `ChestPyTools` |
| `qt/widgets/` | 自定义 Qt 控件（如悬浮放大镜） | `PySide6` |
| `web/flask_app.py` | Flask 应用工厂 | `core/`, `web/nicegui_pages/` |
| `web/nicegui_pages/` | NiceGUI 页面定义 | `core/` |
| `core/repo_scanner.py` | 扫描 YAML 状态文件 | `PyYAML` |
| `core/config_loader.py` | 加载 `config.yaml` | `PyYAML` |

---

## 6. 架构约束 / 红线规则

| 编号 | 规则 | 违反后果 |
| :--- | :--- | :--- |
| S1 | `core/` 不得 import `PySide6` 或 `Q*` | 代码评审不通过 |
| S2 | `web/` 不得直接调用系统 API（取色、热键） | 必须通过 bridge 间接调用 |
| S3 | `qt/bridge.py` 是**唯一**允许 import `ChestPyTools` 和 `PySide6` 的地方 | 保持分层清晰 |
| S4 | `ChestPyTools` 中的工具函数必须是纯函数（无状态、无 UI） | 工具无法被独立测试 |
| S5 | 所有异步操作（取色、爬虫）必须通过信号槽或回调，避免阻塞 UI | UI 卡顿 |

---

## 7. 色彩管理相关功能预留

### 7.1 屏幕取色器交互设计

- **触发方式**：用户按下全局热键（如 `Ctrl+Shift+C`），或点击 Web 页面的取色按钮。
- **体验**：鼠标指针变为十字准星，移动时页面实时显示 RGB/XYZ/CIE Lab 值，点击锁定颜色。
- **悬浮放大镜**：Qt 原生窗口（`Qt.FramelessWindowHint` + `Qt.WindowStaysOnTopHint`）跟随鼠标，显示 10x 放大像素。

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
# 使用 PyInstaller
pyinstaller --name ChestSteward --windowed --add-data "web:templates" main.py
```

---

## 9. 版本计划

| 版本 | 核心功能 |
| :--- | :--- |
| v0.1 | Qt 窗口 + WebView 显示空白页，Flask 启动成功 |
| v0.2 | 加载 NiceGUI，显示“Hello World” |
| v0.3 | 读取 `config.yaml`，显示项目列表卡片 |
| v0.4 | Qt WebChannel 通信打通，点击按钮调用 PyTools 示例 |
| v0.5 | 屏幕取色工具集成（简易版） |
| v1.0 | 完整仪表盘 + 全局热键 + 色彩工具 + 打包发布 |


## 建构目录

```
ChestSteward/
├── main.py                          # 【启动心脏】程序唯一入口。负责启动 Flask 后台、创建 Qt 应用、挂载 WebView
├── config.yaml                      # 【宇宙索引】全局配置文件（定义 manager/、projects/、storage/ 路径）
├── README.md                        # 项目说明
├── requirements.txt                 # Python 依赖（PySide6, Flask, NiceGUI, PyYAML, pywin32 等）
├── pyproject.toml                   # （可选）如果想把 Steward 本身也作为包管理
│
├── core/                            # 【纯逻辑层】零 Qt、零 Web 依赖，纯 Python 函数
│   ├── __init__.py
│   ├── config_loader.py             # 解析 config.yaml
│   ├── repo_scanner.py              # 遍历 manager/ 和 projects/，读取 project_status.yaml
│   ├── scheduler.py                 # 日程聚合（未来对接 Google Calendar）
│   └── data_aggregator.py           # 汇总所有数据为统一的 Dict/DataFrame 结构
│
├── web/                             # 【Web 内容层】运行在 QWebEngineView 中的 Flask 应用
│   ├── __init__.py
│   ├── flask_app.py                 # Flask 应用工厂（创建 app 实例，注册路由）
│   ├── nicegui_pages/               # NiceGUI 构建的页面（自动转为 HTML/JS）
│   │   ├── __init__.py
│   │   ├── dashboard.py             # 总览面板（卡片布局，显示所有项目进度）
│   │   ├── project_detail.py        # 点击卡片后跳转的详情页（含时间线/指标）
│   │   └── color_tool.py            # 【色彩工具专用页】显示 RGB/XYZ/CIE 图表
│   ├── static/                      # （预留）原生 JS/CSS，未来覆盖 NiceGUI 默认样式
│   └── templates/                   # （预留）Jinja2 模板，当从 NiceGUI 迁移到纯 Flask 时使用
│
├── qt/                              # 【Qt 原生层】桌面特有的窗口、控件、系统交互
│   ├── __init__.py
│   ├── main_window.py               # 主窗口类（继承 QMainWindow），布局 QWebEngineView
│   ├── bridge.py                    # 【关键桥梁】继承 QObject，暴露给 JS 的接口（通过 Qt WebChannel）
│   ├── resources/                   # 资源文件
│   │   ├── icons/                   # 应用图标、状态图标
│   │   └── style.qss                # Qt 样式表（QSS），统一桌面控件风格
│   └── widgets/                     # 自定义 Qt 原生控件（桌面特有）
│       ├── __init__.py
│       ├── color_picker_overlay.py  # 【悬浮取色放大镜】无边框置顶窗口，跟随鼠标显示像素放大
│       └── system_tray.py           # 系统托盘图标（后台常驻）
│
├── scripts/                         # 【运维工具】辅助开发的 CLI 脚本
│   ├── sync_all.py                  # 手动拉取所有子仓库最新提交
│   └── generate_report.py           # 将 Dashboard 数据导出为 Markdown/PDF 周报
│
├── data/                            # 【本地缓存】程序运行时产生的临时文件（.gitignore）
│   └── cache_progress.json          # 扫描结果的缓存，减少重复 I/O
│
├── tests/                           # 【单元测试】镜像 core/ 的结构
│   ├── __init__.py
│   ├── test_config_loader.py
│   └── test_repo_scanner.py
│
└── Docs/                            # 【项目文档】
    ├── WORKSPACE_SPECIFICATION.md   # 全局工作区宪法（我们刚定稿的 v2.0）
    └── ARCHITECTURE_DESIGN.md       # ChestSteward 自身的详细架构设计（我们刚写的第二份文档）
```

---