> **主要变更**：
> 1.  Dashboard 技术栈从 Flask+NceGUI 正式变更为 **Qt（PySide6）+ QWebEngineView + Flask 混合架构**。
> 2.  引入 `storage/` 顶级目录作为数据湖，与 `manager/`、`projects/` 平级。
> 3.  明确 PyTools 仅返回数据，UI 渲染由 ChestSteward 全权负责的契约。
> 4.  新增 Qt 相关的目录规范与红线规则。

---

# Chest 工作区规范手册

> **版本**：v2.0（Qt 架构版）  
> **生效日期**：2026-09-03  
> **适用范围**：`./Manager/` 下所有仓库  
> **维护者**：ChestSteward（总控仓库）

---

## 1. 总体设计哲学

本工作区遵循以下核心原则，所有规范均由此派生：

1. **关注点分离（Separation of Concerns）**：管理工具（manager/）与业务产出（projects/）物理隔离。
2. **约定优于配置（Convention over Configuration）**：统一的目录结构和命名规范减少决策成本。
3. **零信任数据入口（Zero Trust Data Ingestion）**：核心数据（笔记、项目状态）只能通过脚本写入，杜绝手工脏数据。
4. **UI 与逻辑解耦**：PyTools 只返回纯数据（不包含任何 UI 代码），所有渲染由 ChestSteward 统一负责。
5. 每个工具/项目目录下必须包含 `Docs/ARCHITECTURE_DESIGN.md`。

---

## 2. 物理目录布局

所有仓库平级位于 `./Manager/` 下，按职能分为三组：

```text
./Manager/
├── manager/                          # 【管理中枢】代码与配置，极少变动
│   ├── ChestSteward/                 # 总控大脑（Qt + WebView 桌面应用）
│   ├── ChestPyTools/                 # Python 纯工具库（无 UI）
│   └── ChestNote/                    # 知识库（Markdown + 元数据）
│
├── projects/                         # 【业务前线】高频迭代，可随意增删改
│   ├── NexusRenderer/                # 渲染算法研究平台（C++）
│   ├── CMSSystem/                    # 内容管理系统（C++）
│   └── (未来新项目...)
│
└── storage/                          # 【数据湖】运行产物、共享资源（.gitignore 为主）
    ├── .gitignore                    # 默认忽略全部
    ├── data/                         # 静态参考数据（种子配置、字典库）
    ├── outputs/                      # 动态产出（爬虫 JSON、指标报告、日志）
    │   ├── logs/
    │   ├── crawler/
    │   └── reports/
    ├── cache/                        # 临时缓存（缩略图、中间产物）
    └── shared_assets/                # 跨项目共享资源（HDRI、通用纹理）
```

**红线规则**：
- `manager/` 下的仓库数量应保持稳定（原则上不超过 5 个）。
- `projects/` 下的仓库数量不限，但**严禁**创建与 `manager/` 同名的仓库。
- `storage/` 下默认全部 `.gitignore`，仅保留目录结构。

---

## 3. 各仓库职责与内部规范

### 3.1 ChestSteward（总控大脑）

**定位**：纯信息聚合与调度中心。采用 **Qt 桌面外壳 + 内嵌 WebView（Flask + NiceGUI）** 混合架构，兼顾原生系统能力与现代化 UI 开发效率。

**技术栈**：
- 桌面框架：**PySide6（Qt 6）**
- Web 引擎：**QWebEngineView**（Chromium 内核）
- Web 服务：**Flask + NiceGUI**
- 通信桥梁：**Qt WebChannel**（Python ↔ JavaScript 双向通信）
- 配置文件：YAML
- 语言：Python 3.11+

**目录结构**：

```text
ChestSteward/
├── README.md
├── requirements.txt                 # Python 依赖（含 PySide6、Flask、NiceGUI）
├── config.yaml                      # 【核心】全局仓库索引
├── main.py                          # 【启动入口】创建 Qt 应用并挂载 WebView
├── core/                            # 业务逻辑（与 UI 解耦，纯 Python）
│   ├── __init__.py
│   ├── repo_scanner.py              # 扫描所有仓库的 status 文件
│   ├── config_loader.py             # 加载 config.yaml
│   └── scheduler.py                 # 日程聚合
├── web/                             # Flask Web 应用（运行在 QWebEngineView 中）
│   ├── __init__.py
│   ├── flask_app.py                 # Flask 主入口
│   ├── nicegui_pages/               # NiceGUI 页面
│   │   ├── dashboard.py             # 总览面板
│   │   └── project_detail.py        # 项目详情页
│   └── templates/                   # 【预留】Jinja2 模板
├── qt/                              # Qt 桌面层（与 Web 通信）
│   ├── __init__.py
│   ├── main_window.py               # 主窗口（含 QWebEngineView 布局）
│   ├── bridge.py                    # Qt WebChannel 桥梁对象
│   ├── resources/                   # 图标、QSS 样式表
│   │   ├── icons/
│   │   └── style.qss
│   └── widgets/                     # 自定义 Qt 控件（如悬浮取色放大镜）
│       └── color_picker_overlay.py
├── scripts/                         # CLI 运维脚本
│   ├── sync_all.py
│   └── generate_report.py
├── data/                            # 本地缓存（.gitignore）
│   └── cache_progress.json
├── tests/
│   └── test_repo_scanner.py
└── Docs/
    └── WORKSPACE_SPECIFICATION.md   # 本文件
    └── ARCHITECTURE_DESIGN.md       # 详细架构设计（见第二份文档）
```

**红线规则**：
- `qt/` 层只负责绘制窗口和原生控件，**绝不**包含业务逻辑（业务逻辑在 `core/`）。
- `web/` 层只负责 HTML/JS 渲染，**绝不**直接调用系统 API（取色、热键等）。
- `core/` 层**绝不**依赖 `PySide6` 或 `QWebEngineView`，保持纯 Python 可测试。
- 跨仓库路径写入 `config.yaml`，严禁硬编码。

---

### 3.2 ChestPyTools（纯工具库）

**定位**：无状态、可复用的纯 Python 工具函数。**不包含任何 UI 代码**（无 Qt、无 HTML、无 NiceGUI）。

**技术栈**：
- 语言：Python 3.11+
- 包管理：`pyproject.toml`
- 入口规范：每个工具提供纯函数 `run()` 或 `core.py` 暴露 API

**目录结构**：

```text
ChestPyTools/
├── README.md
├── pyproject.toml
├── requirements.txt
├── tools/
│   ├── __init__.py
│   ├── colorpicker/                 # 【色彩工具】屏幕取色、色差计算
│   │   ├── __init__.py              # 暴露: from .core import pick_screen_color
│   │   ├── core.py                  # 核心算法（截屏、RGB→XYZ、ICC 解析）
│   │   └── cli.py                   # 命令行入口（可选）
│   ├── crawler/
│   │   ├── __init__.py
│   │   ├── core.py
│   │   └── cli.py
│   └── file_processor/
│       ├── __init__.py
│       ├── core.py
│       └── cli.py
├── shared/
│   ├── __init__.py
│   └── paths.py                     # 统一路径管理（指向 storage/）
├── tests/
│   └── ...
└── cli.py                           # 统一总入口
```

**关键约定**：
| 层级 | 职责 | 对外暴露 |
| :--- | :--- | :--- |
| `core.py` | 核心算法，纯函数，无副作用 | `__init__.py` 暴露 |
| `cli.py` | 命令行参数解析 | `__init__.py` **不暴露** |
| 其他模块 | 内部辅助实现 | 不暴露 |

**返回数据格式示例（色彩工具）**：

```python
# tools/colorpicker/core.py
from dataclasses import dataclass

@dataclass
class ScreenColorResult:
    hex: str
    rgb: tuple[int, int, int]
    xyz: tuple[float, float, float]
    cie_lab: tuple[float, float, float]
    pixel_preview_bgr: bytes   # 50x50 像素块，由 Steward 转为 QPixmap
```

**红线规则**：
- **严禁**在 `tools/` 中 `import PySide6`、`import PyQt5` 或任何 `Q*` 类。
- **严禁**返回任何 UI 控件（如 QWidget、QLabel）。
- 所有 I/O 路径必须通过 `shared/paths.py` 指向 `storage/`，禁止硬编码。


### 3.3 ChestNote（知识库）

**定位**：只读（或仅通过脚本写入）的知识晶体。核心是防脏数据和结构化检索。

**技术栈**：
- 主体格式：Markdown + YAML Frontmatter
- 门禁脚本：Python（ingest / validate）

**目录结构**：

```text
ChestNote/
├── README.md
├── .gitignore
├── .git/hooks/pre-commit            # 软链指向 scripts/validate.py
├── subjects/                        # 本科/研究生科目
│   ├── ComputerGraphics/
│   │   ├── 01_LinearAlgebra.md
│   │   └── 02_RenderingPipeline.md
│   └── DeepLearning/
│       └── 01_Backpropagation.md
├── professional/                    # 专业领域
│   ├── Cpp_Core_Guidelines.md
│   └── CleanArchitecture.md
├── templates/                       # 笔记模板
│   └── default.md
├── scripts/                         # 【门禁系统】
│   ├── ingest.py                    # 唯一新建入口
│   ├── validate.py                  # Pre-commit 钩子
│   └── export_json.py               # 导出索引给 Steward
└── vault/                           # 图片/附件
```

**笔记文件格式（强制）**：

```markdown
---
title: 渲染管线中的矩阵变换
tags: [计算机图形学, 线性代数]
created_at: 2026-09-03
status: 已理解
---

# 正文开始
这里随心所欲写 Markdown...
```

**红线规则**：
- 严禁手动创建 `.md` 文件，一律通过 `ingest.py` 生成（自动填充 `created_at` 和 UUID）。
- `validate.py` 强制检查 Frontmatter 是否包含 `title`、`tags`、`created_at`，否则拦截 `git commit`。
- 导出的 `index.json` 仅作为缓存，禁止手动修改，加入 `.gitignore`。

---

### 3.4 C++ 项目标准模板（适用于 `projects/` 下所有 C++ 工程）

**依据**：本规范以 `NexusRenderer` 的架构设计为蓝本提炼而成，所有 C++ 项目（包括 `CMSSystem`）均应参照执行。

**技术栈**：
- 语言：C++20（推荐）
- 构建系统：CMake + CMakePresets.json
- 文档：`README.md` + `Docs/ARCHITECTURE_DESIGN.md`

**目录结构（核心骨架，必选）**：

```text
ProjectName/
├── CMakeLists.txt                   # 根 CMake
├── CMakePresets.json                # 预设构建配置
├── README.md                        # 进展、架构快照、构建指南
├── Docs/
│   ├── ARCHITECTURE_DESIGN.md       # 详细架构设计（参考 Nexus 文档）
│   └── ...
├── Source/                          # 【三层隔离核心】
│   ├── App/                         # 应用层（依赖 UI 框架）
│   │   ├── Main.cpp
│   │   └── ...
│   ├── Runtime/                     # 核心逻辑层（零 UI 依赖）
│   │   ├── Core/                    # 引擎上下文/主循环
│   │   ├── Modules/                 # 业务模块
│   │   └── Public/                  # 对外纯虚接口
│   └── Shared/                      # 跨层共享（POD、工具类、数学库）
│       ├── Math/
│       ├── Utils/
│       └── Platform/
├── Tests/                           # 单元测试
│   └── Runtime/
│       └── CoreTests.cpp
├── Assets/                          # 运行时资源
│   └── Configs/
└── Scripts/                         # 构建辅助脚本
    └── build.sh / build.bat
```

**CMake Target 依赖链规范**：

```text
ProjectName_App (executable)
  -> ProjectName_Runtime (static lib)
     -> ProjectName_Shared (static lib)
```

**红线规则（直接采自 NexusRenderer）**：
1. **Runtime 绝对禁止 `#include` 任何 GUI 框架头文件**（如 Qt、WinUI）。
2. **依赖方向严格单向**：`App -> Runtime -> Shared`，禁止反向依赖。
3. **跨层通信只允许 POD 结构体**（如 `NNativeWindowHandle`）。

**扩展模块（按需裁剪）**：
以下目录仅在项目需要时添加，非必须：

```text
├── Source/Runtime/RHI/              # 图形硬件抽象层（渲染项目）
├── Source/Runtime/AI/               # AI 推理接入层
├── Shaders/                         # HLSL/MSL 着色器
├── Scenes/                          # 测试场景集
└── Baselines/                       # 对比基准注册表
```

---

### 3.5 项目状态文件规范（用于 Steward 扫描）

每个 `projects/` 下的仓库**必须**在根目录提供一个 `project_status.yaml`，供 ChestSteward 读取展示进度。

**格式约定**：

```yaml
# projects/NexusRenderer/project_status.yaml
name: NexusRenderer
description: 可观测、可实验的实时渲染算法研究平台
current_phase: P1                          # 当前里程碑
status: 进行中                             # 进行中 / 已完成 / 暂停
last_updated: 2026-09-03
build_status: 通过                          # 通过 / 失败 / 未构建
key_metrics:
  - name: 三角形渲染
    status: ✅ 已完成
  - name: VertexBuffer
    status: ✅ 已完成
  - name: DXC 编译链
    status: ⏳ 进行中
  - name: GPU 时间戳
    status: ⏳ 进行中
upcoming_milestone: P2 - Cornell Box 双算法对比
blockers: []
```

---

## 4. 跨仓库链接策略

**核心决策：绝对不使用 Git Submodule。**

### 4.1 路径约定
- `ChestSteward/config.yaml` 使用相对路径。
- 环境变量 `$CHEST_HOME` 可选设置。

### 4.2 ChestSteward → ChestPyTools 调用方式

```python
# ChestSteward/qt/bridge.py
from ChestPyTools.tools.colorpicker import pick_screen_color

def on_pick_color():
    result = pick_screen_color()  # 返回 ScreenColorResult
    # 通过 Qt WebChannel 推送给前端 JS
    self.web_channel.send_color(result)
```

### 4.3 存储路径统一管理（`shared/paths.py`）

```python
# ChestPyTools/shared/paths.py
from pathlib import Path

def get_storage_root() -> Path:
    return Path(__file__).parent.parent.parent.parent / "storage"

def get_output_dir(tool_name: str) -> Path:
    out_dir = get_storage_root() / "outputs" / tool_name
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir
```

---

## 5. Qt + WebView 混合架构说明

### 5.1 为什么选择这个方案？
- **原生能力**：Qt 提供全局热键、鼠标钩子、原生窗口置顶、系统色彩 API 调用。
- **UI 开发效率**：NiceGUI 在 WebView 中提供现代化 UI 组件（图表、动画、响应式布局）。
- **双向通信**：Qt WebChannel 实现 Python ↔ JavaScript 无缝数据交换。

### 5.2 启动流程

```text
main.py
  → 启动 Flask 服务器（后台线程）
  → 创建 QApplication
  → 创建 MainWindow（含 QWebEngineView）
  → QWebEngineView 加载 http://127.0.0.1:5000
  → 注册 Qt WebChannel 桥梁对象
  → app.exec_()
```

### 5.3 通信架构图

```text
┌──────────────────────────────────────────────────────────────┐
│  Qt 桌面层 (Python)                                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  main_window.py (QMainWindow)                       │    │
│  │  ├─ QWebEngineView (加载 Flask 页面)                │    │
│  │  └─ ColorPickerOverlay (悬浮取色放大镜, QWidget)    │    │
│  └─────────────────────────────────────────────────────┘    │
│                       │                                      │
│              Qt WebChannel (双向通信)                        │
│                       ▼                                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  bridge.py (QObject 桥梁)                           │    │
│  │  - pick_color() → 调用 ChestPyTools                 │    │
│  │  - send_result_to_js(result)                       │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│  Flask Web 层 (Python + NiceGUI)                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  nicegui_pages/dashboard.py                         │    │
│  │  - UI 组件（表格、图表、卡片）                       │    │
│  │  - 通过 JS 调用 bridge.pick_color()                │    │
│  │  - 接收 bridge 推送的数据并刷新显示                  │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

---

## 6. 配置分层治理

### 6.1 全局配置：`ChestSteward/config.yaml`

（同前，略）

### 6.2 本地配置

（同前，略）

---

## 7. 红线规则汇总

| 编号 | 规则 | 适用范围 |
| :--- | :--- | :--- |
| R1 | `manager/` 与 `projects/` 物理隔离 | 全局 |
| R2 | `projects/` 下禁止创建与 `manager/` 同名仓库 | 全局 |
| R3 | C++ 项目的 `Runtime/` 层禁止 `#include` 任何 GUI 框架头 | C++ 项目 |
| R4 | C++ 项目依赖方向强制 `App -> Runtime -> Shared` | C++ 项目 |
| R5 | ChestNote 的 `.md` 文件必须通过 `ingest.py` 创建 | ChestNote |
| R6 | ChestNote 所有笔记必须包含 `title`、`tags`、`created_at` | ChestNote |
| R7 | **ChestPyTools 中严禁 `import PySide6` 或任何 UI 框架** | ChestPyTools |
| R8 | **ChestPyTools 严禁返回 UI 控件，只能返回纯数据类** | ChestPyTools |
| R9 | `ChestSteward/qt/` 层只负责 UI，业务逻辑在 `core/` | ChestSteward |
| R10 | 所有跨仓库路径写入 `config.yaml`，严禁硬编码 | ChestSteward |

---

## 8. 附录：快速参考卡片

### 8.1 常用命令

| 操作                   | 命令                                                                                              |
| :------------------- | :---------------------------------------------------------------------------------------------- |
| 启动 Steward Dashboard | `cd ./Manager/manager/ChestSteward && python web/flask_app.py`                          |
| 新建笔记                 | `cd ./Manager/manager/ChestNote && python scripts/ingest.py --title "新笔记" --tags CG`    |
| 执行 PyTools 工具        | `cd ./Manager/manager/PyTools && python cli.py crawler run --url xxx`                   |
| 构建 C++ 项目            | `cd ./Manager/projects/NexusRenderer && cmake --preset default && cmake --build build/` |

### 8.2 关键文件路径速查

| 文件       | 路径                                                     |
| :------- | :----------------------------------------------------- |
| 全局配置     | `manager/ChestSteward/config.yaml`                     |
| 工作区规范    | `manager/ChestSteward/Docs/WORKSPACE_SPECIFICATION.md` |
| 笔记门禁脚本   | `manager/ChestNote/scripts/validate.py`                |
| C++ 项目状态 | `projects/*/project_status.yaml`                       |

***

