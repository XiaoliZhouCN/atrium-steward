这是基于我们所有讨论整理而成的完整仓库规范文档。你可以直接将以下内容保存为 `ChestSteward/Docs/WORKSPACE_SPECIFICATION.md`。

这份文档定义了从工作区布局到每个仓库内部规范的全部约定，是整个 Chest 生态的"宪法"。

---

# Chest 工作区规范手册

> **版本**：v1.0  
> **生效日期**：2026-09-03  
> **适用范围**：`./Manager/` 下所有仓库  
> **维护者**：ChestSteward（总控仓库）

---

## 1. 总体设计哲学

本工作区遵循以下三条核心原则，所有规范均由此派生：

1. **关注点分离（Separation of Concerns）**：管理工具（manager/）与业务产出（projects/）物理隔离。
2. **约定优于配置（Convention over Configuration）**：统一的目录结构和命名规范减少决策成本。
3. **零信任数据入口（Zero Trust Data Ingestion）**：核心数据（笔记、项目状态）只能通过脚本写入，杜绝手工脏数据。

---

## 2. 物理目录布局

所有仓库平级位于 `./Manager/` 下，按职能分为两组：

```text
./Manager/
├── manager/                          # 【管理中枢】极少变动，禁止随意增删
│   ├── ChestSteward/                 # 总控大脑（含 Dashboard UI）
│   ├── PyTools/                      # 纯 Python 工具库（无界面）
│   └── ChestNote/                    # 知识库（Markdown + 元数据）
│
└── projects/                         # 【业务前线】高频迭代，可随意增删改
    ├── NexusRenderer/                # 渲染算法研究平台（C++）
    ├── CMSSystem/                    # 内容管理系统（C++）
    └── (未来新项目...)
```

**红线规则**：
- `manager/` 下的仓库数量应保持稳定（原则上不超过 5 个）。
- `projects/` 下的仓库数量不限，但**严禁**创建与 `manager/` 同名的仓库（如 `projects/PyTools`），否则 Steward 扫描脚本将报错。

---

## 3. 各仓库职责与内部规范

### 3.1 ChestSteward（总控大脑）

**定位**：纯信息聚合与调度中心。不存放具体项目代码，只存配置、索引和 UI 逻辑。

**技术栈**：
- 语言：Python 3.11+
- 配置文件：YAML
- Dashboard 框架：Flask + NiceGUI（双模运行，详见第 5 节）

**目录结构**：

```text
ChestSteward/
├── README.md
├── requirements.txt                 # Python 依赖
├── config.yaml                      # 【核心】全局仓库索引
├── core/                            # 业务逻辑（与 UI 解耦，未来可复用）
│   ├── __init__.py
│   ├── repo_scanner.py              # 扫描所有仓库的 status 文件
│   ├── config_loader.py             # 加载 config.yaml
│   └── scheduler.py                 # 日程聚合（Google Calendar API 等）
├── web/                             # Web 层（UI 展示）
│   ├── __init__.py
│   ├── flask_app.py                 # Flask 主入口
│   ├── nicegui_pages/               # NiceGUI 快速构建的页面
│   │   ├── dashboard.py             # 总览面板
│   │   └── project_detail.py        # 项目详情页
│   └── templates/                   # 【预留】未来 Flask + Jinja2 模板
│       └── (目前为空)
├── scripts/                         # CLI 运维脚本
│   ├── sync_all.py                  # 拉取所有仓库最新进度
│   └── generate_report.py           # 导出周报 Markdown
├── data/                            # 本地缓存（.gitignore）
│   └── cache_progress.json
├── tests/                           # 单元测试
│   └── test_repo_scanner.py
└── Docs/                            # 文档（本文件存放于此）
    └── WORKSPACE_SPECIFICATION.md
```

**红线规则**：
- `web/` 层严禁直接 import `core/` 以外的模块，保持 UI 轻量。
- 所有跨仓库路径写入 `config.yaml`，严禁硬编码绝对路径。

---

### 3.2 PyTools（纯工具库）

**定位**：无状态、可复用的纯 Python 工具函数与 CLI 脚本。**不包含 Dashboard 或任何 GUI 界面**。

**技术栈**：
- 语言：Python 3.11+
- 包管理：`pyproject.toml`（Hatchling / Setuptools）
- 入口规范：每个工具必须提供统一的 `run()` 或 CLI 接口

**目录结构**：

```text
PyTools/
├── README.md
├── pyproject.toml                   # 包配置，定义 console_scripts
├── requirements.txt                 # 全局依赖
├── tools/                           # 【核心工具集】
│   ├── __init__.py
│   ├── file_processor/              # 工具 A
│   │   ├── __init__.py
│   │   ├── cli.py                   # argparse 入口
│   │   └── core.py                  # 核心逻辑（无 side-effect）
│   ├── crawler/                     # 工具 B
│   │   ├── __init__.py
│   │   ├── cli.py
│   │   └── core.py
│   └── math_utils/                  # 工具 C
│       ├── __init__.py
│       └── core.py                  # 纯函数，无 CLI
├── shared/                          # 工具间共享代码（极其克制）
│   ├── __init__.py
│   └── network.py
├── tests/                           # 镜像 tools/ 的测试结构
│   ├── test_file_processor.py
│   └── test_crawler.py
└── cli.py                           # 【统一总入口】
```

**单个工具的内部规范**：
1. 每个工具目录必须有 `__init__.py`，暴露顶层 API。
2. 如有 CLI，必须实现 `def setup_parser(subparsers)` 和 `def main(args)`，以便 `cli.py` 动态注册。
3. 每个工具必须包含文档字符串，说明输入输出，便于 Steward 自动发现。

---

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

所有仓库独立 Git 管理，互不嵌套。跨仓库调用通过以下方式实现：

### 4.1 路径约定

- 所有仓库平级位于 `./Manager/manager/` 或 `./Manager/projects/`。
- `ChestSteward/config.yaml` 中使用**相对路径**（如 `../PyTools`）定位兄弟仓库。
- 环境变量 `$CHEST_HOME` 可选设置为 `~/Developer/Chest`，便于脚本动态定位。

### 4.2 PyTools 的导入方式（推荐）

在 `ChestSteward` 的虚拟环境中执行：

```bash
pip install -e ../manager/PyTools
```

随后即可在 Steward 中 `from PyTools.tools.crawler import fetch` 导入。

### 4.3 C++ 项目间的引用

如项目 A 需要引用项目 B 的共享库，在 `CMakeLists.txt` 中使用 `add_subdirectory` 或 `find_package`，前提是两个仓库已在本地相邻位置克隆。

---

## 5. Dashboard 技术选型：Flask + NiceGUI 双模架构

**策略**：以 Flask 作为主服务器，NiceGUI 作为快速原型层挂载其上，未来可平滑迁移到纯 Flask + HTMX。

### 5.1 技术栈

- **Flask**：主服务器，提供 API 路由和未来页面入口。
- **NiceGUI**：当前阶段的 UI 渲染引擎，零前端代码构建美观界面。
- **HTMX + TailwindCSS**：（预留）未来纯前端迁移目标。

### 5.2 启动入口示意

```python
# ChestSteward/web/flask_app.py
from flask import Flask
from nicegui import ui

app = Flask(__name__)

# Flask 原生 API 路由（为未来高定制化预留）
@app.route('/api/status')
def get_status():
    return {"progress": 85}

# NiceGUI 页面（当前主力）
@ui.page('/')
def main_dashboard():
    ui.label('Welcome to ChestSteward')
    # ... 调用 core/ 逻辑渲染组件

# 绑定启动
ui.run_with(app, port=8080, show=True)
```

### 5.3 迁移路径

- **第一阶段（当前）**：100% NiceGUI 渲染，快速出成果。
- **第二阶段（中期）**：部分页面用 Flask + Jinja2/HTMX 重写，与 NiceGUI 共存。
- **第三阶段（远期）**：若完全脱离 NiceGUI，只需删除 `ui.run_with`，将 `@ui.page` 改写为 `@app.route`，`core/` 逻辑完全复用。

---

## 6. 配置分层治理

### 6.1 全局配置：`ChestSteward/config.yaml`

唯一全局索引，定义所有仓库的位置和属性。

```yaml
workspace_root: ~/Developer/Chest

repositories:
  manager:
    - name: ChestSteward
      path: ../ChestSteward
      lang: python
      entry: web/flask_app.py
    - name: PyTools
      path: ../PyTools
      lang: python
      entry: cli.py
    - name: ChestNote
      path: ../ChestNote
      lang: markdown
      local_config: .noterc

  projects:
    - name: NexusRenderer
      path: ../projects/NexusRenderer
      lang: cpp
      status_file: project_status.yaml
    - name: CMSSystem
      path: ../projects/CMSSystem
      lang: cpp
      status_file: project_status.yaml
```

### 6.2 本地配置（每个仓库的"宪法"）

| 仓库 | 配置文件 | 职责 |
| :--- | :--- | :--- |
| ChestNote | `.noterc` | 标签白名单、允许的子目录、导出路径 |
| PyTools | `pyproject.toml` | 依赖列表、`console_scripts` 入口点 |
| C++ 项目 | `project_status.yaml` | 当前阶段、构建状态、里程碑 |
| C++ 项目（可选） | `.nexus_config` | 三方库版本、编译开关 |

---

## 7. 红线规则汇总

以下规则适用于整个工作区，违反即视为架构腐化：

| 编号 | 规则 | 适用范围 |
| :--- | :--- | :--- |
| R1 | `manager/` 与 `projects/` 物理隔离，禁止交叉存放 | 全局 |
| R2 | `projects/` 下禁止创建与 `manager/` 同名的仓库 | 全局 |
| R3 | C++ 项目的 `Runtime/` 层禁止 `#include` 任何 GUI 框架头 | C++ 项目 |
| R4 | C++ 项目依赖方向强制 `App -> Runtime -> Shared` | C++ 项目 |
| R5 | ChestNote 的 `.md` 文件必须通过 `ingest.py` 创建，禁止手动新建 | ChestNote |
| R6 | ChestNote 所有笔记必须包含 `title`、`tags`、`created_at` Frontmatter | ChestNote |
| R7 | `ChestSteward/web/` 层不得直接依赖 `core/` 以外的模块 | ChestSteward |
| R8 | 所有跨仓库路径写入 `config.yaml`，严禁硬编码绝对路径 | ChestSteward |

---

## 8. 附录：快速参考卡片

### 8.1 常用命令

| 操作 | 命令 |
| :--- | :--- |
| 启动 Steward Dashboard | `cd ./Manager/manager/ChestSteward && python web/flask_app.py` |
| 新建笔记 | `cd ./Manager/manager/ChestNote && python scripts/ingest.py --title "新笔记" --tags CG` |
| 执行 PyTools 工具 | `cd ./Manager/manager/PyTools && python cli.py crawler run --url xxx` |
| 构建 C++ 项目 | `cd ./Manager/projects/NexusRenderer && cmake --preset default && cmake --build build/` |

### 8.2 关键文件路径速查

| 文件 | 路径 |
| :--- | :--- |
| 全局配置 | `manager/ChestSteward/config.yaml` |
| 工作区规范 | `manager/ChestSteward/Docs/WORKSPACE_SPECIFICATION.md` |
| 笔记门禁脚本 | `manager/ChestNote/scripts/validate.py` |
| C++ 项目状态 | `projects/*/project_status.yaml` |

---

**文档结束。本规范自签署之日起生效，所有新仓库创建必须遵循上述约定。**