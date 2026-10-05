# AtriumSteward

`Manager` 工作区的**常驻主控器**：管理工具进程、维护工作区上下文、提供轻量入口面板。

本仓库同时是**工作区级文档的唯一权威来源**（见 §文档）。

## 当前状态

Python 过渡基线可运行，目标架构（C++ 宿主）尚未开工。

**已落地**

| 能力 | 位置 |
| :-- | :-- |
| Launcher 主面板（Spotlight 式，含淡入淡出与 ESC 关闭） | `qt/launcher_window.py` |
| 轻量工具注册表（唯一工具清单来源） | `core/tool_registry.py` |
| 工具窗口基类（统一关闭信号与置顶切换） | `qt/tool_window.py` |
| 取色器工具窗口（调用 `colorpicker` 纯函数） | `qt/tools/colorpicker_window.py` |
| 单实例约束（`QLocalServer` 命名 socket + 激活唤起） | `main.py` |
| 全局热键 `Ctrl+Shift+Space`、系统托盘 | `main.py` |

**占位 / 未完成**

| 项 | 现状 |
| :-- | :-- |
| `core/config_loader.py`、`core/repo_scanner.py` | 只有一行 docstring，无实现 |
| `config.yaml`、`pyproject.toml`、`launchers/*.bat` | 0 字节空文件 |
| `tests/` | 不存在 |
| `web/flask_app.py` | 旧探索代码，且引用公网 CDN，违反离线原则，待删除 |
| `web/templates/index.html` | 同上，待改造为纯离线画布 |
| `qt/bridge.py` | WebChannel 占位，未接线 |
| `qt/tools/mermaid_window.py` | 占位窗口 |

**待办**：按 `Docs/ARCHITECTURE_DESIGN.md` §6 拆分 `main.py`，建立 `steward_app/{runtime,core,ui,integrations}` 四层，清理 Flask 遗留，补最小测试。

## 目录结构

```text
AtriumSteward/
├── main.py                     # 入口：单实例、热键、托盘、窗口协调
├── requirements.txt
├── config.yaml                 # 空，待补
├── core/                       # 纯逻辑层（禁止依赖 Qt）
│   ├── tool_registry.py
│   ├── config_loader.py        # 空
│   └── repo_scanner.py         # 空
├── qt/                         # 界面层
│   ├── launcher_window.py
│   ├── tool_window.py
│   ├── bridge.py
│   ├── resources/style.qss
│   └── tools/{colorpicker,mermaid}_window.py
├── web/                        # 本地离线画布（待清理）
├── AGENTS.md                   # Agent 协作边界
└── Docs/
    ├── WORKSPACE_SPECIFICATION.md   # 工作区级规范（权威）
    └── ARCHITECTURE_DESIGN.md       # 本仓库架构设计
```

## 环境

**唯一共享虚拟环境**：`D:\Repositories\Manager\.venv`（Python 3.14.2）。

实测已安装：`PySide6`、`keyboard`、`pywin32`、`PyYAML`、`Flask`。
**缺**：`colorpicker`（需以可编辑方式安装，否则 `main.py` 的 `from colorpicker import ...` 会失败）。

```powershell
# 安装缺失的本地工具包
& "D:\Repositories\Manager\.venv\Scripts\python.exe" -m pip install -e "D:\Repositories\Manager\AtriumPyTools\tools\colorpicker"
```

> `colorpicker` 的顶层包名就是 `colorpicker`，因此必须安装 `AtriumPyTools/tools/colorpicker` 这个子包，而不是 `AtriumPyTools` 仓库根包。

## 运行

```powershell
& "D:\Repositories\Manager\.venv\Scripts\python.exe" "D:\Repositories\Manager\AtriumSteward\main.py"
```

## 红线

- `core/` 严禁依赖 `PySide6` / `QWebEngineView`（见架构文档 §3.2）。
- `qt/` 只负责界面、窗口状态与信号连接。
- 工具入口必须统一注册到 `core/tool_registry.py`，禁止多处硬编码。
- 工具接入必须经过注册表与协议，禁止隐式源码直连。
- Web 画布必须离线可运行，禁止依赖公网资源。

## 文档

| 文档 | 内容 |
| :-- | :-- |
| [`Docs/WORKSPACE_SPECIFICATION.md`](Docs/WORKSPACE_SPECIFICATION.md) | **工作区级规范**：目录红线、仓库职责、文档规范、角色权限、待决项 |
| [`Docs/AGENT_ROLES.md`](Docs/AGENT_ROLES.md) | **工作区级角色与权限**：建设 / 掌籍 / 视务三档位的定义、叠加与降级规则、管家映射、子仓库 `AGENTS.md` 的 `[MARK]` 扩写规则 |
| [`Docs/ARCHITECTURE_DESIGN.md`](Docs/ARCHITECTURE_DESIGN.md) | 本仓库架构：分层、契约、C++ 迁移计划 |
| [`README_BRANCHES.md`](README_BRANCHES.md) | 工作区分支总览 |
| [`AGENTS.md`](AGENTS.md) | Agent 协作边界与验证要求 |
| [`Docs/AGENTS_ROLES.md`](Docs/AGENTS_ROLES.md) | 本仓库管家设计：Konstantine（秩序与计划）/ Gui（图形与实现）/ Chestnut（日子与痕迹）的个性、职责分区与协作机制 |

历史版本（v1–v4 的规范与架构）已删除，需要时用 `git log --diff-filter=D --name-only` 与 `git show` 取回。
