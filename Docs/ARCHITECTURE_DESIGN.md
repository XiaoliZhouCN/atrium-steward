# AtriumSteward 架构设计

> **项目**：AtriumSteward
> **定位**：常驻宿主 / 受管工具 / C++ First
> **修订日期**：2026-09-19
> **状态**：重构基线；本文档描述**目标架构**，当前实现进度见仓库 `README.md`

---

## 1. 项目定义

### 1.1 一句话定义

> **AtriumSteward** 是 `Manager` 工作区中的常驻桌面主控器，负责统一管理工具进程、工作区状态、轻量入口面板与跨工具协同；重型能力和旗舰工具逐步迁移到 C++，轻量工具与脚本能力继续保留在 Python。

### 1.2 当前阶段目标

1. 明确 `Steward` 的职责边界，避免其继续膨胀为"什么都做"的单体程序。
2. 将现有 Python 版收束为可迁移、可拆分、可验证的过渡基线。
3. 为 `AtriumCppTools/` 做出清晰的目录与契约预留。
4. 把 Mermaid 可视化笔记工具（`Loomery`）纳入长期旗舰工具规划，但不把其实现塞入 `Steward` 本体。
5. 建立"宿主进程 - 独立工具 - 内容仓库"三者分离的长期结构。

### 1.3 非目标

暂不追求：一次性把所有 Python 改写成 C++；把所有工具嵌入 `Steward` 主窗口；立即实现完整的人生管理平台、进度系统、日程系统、知识图谱；过早引入插件市场、脚本沙箱、动态模块装卸框架。

---

## 2. 核心架构决策

### 2.1 Steward 不再只是 Launcher

早期以 Launcher 为第一优先级是正确的；现在 `Steward` 的定位升级为：

- 常驻进程
- 工具生命周期管理器
- 工作区上下文中枢
- 轻量入口面板

`Steward` 不再是"唤起进程后就撒手"的启动器，而是负责**挂载、观察、协调工具**的宿主。

### 2.2 Steward 也不是全能业务中心

`Steward` 负责"管理"，不负责"承包所有业务实现"。它可以知道哪些工具存在、哪些在运行、当前用户在哪个上下文工作；但它**不承担**笔记编辑器、PDF 解析渲染、图布局算法等专用工具的领域实现。

### 2.3 C++ First，但不是 Python 清零

- 常驻宿主、重型工具、长期维护的桌面基础设施优先使用 C++。
- 原型、轻量工具、脚本胶水、AI 辅助模块继续保留 Python。

保留 Python 是为了维持快速迭代、文本处理与脚本化优势、外部服务整合速度、低成本试验新想法的能力。

### 2.4 工具以"独立受管进程"为主

工具默认形态为：独立进程 + 由 `Steward` 启动/挂载/跟踪状态 + 通过明确协议交换上下文与命令。不再默认把工具作为 `Steward` 的内部窗口类直接 import 进来。

### 2.5 笔记应用与笔记内容必须分离

- **应用代码**：如 `AtriumCppTools/tools/Loomery`
- **内容仓库**：`AtriumNote`

应用负责编辑、渲染、布局、媒体承载；内容仓库负责 Markdown 文件、附件、索引结果与笔记资产。

### 2.6 面板必须保持轻量

热键面板可以存在而且应该存在，但只能是 Command Palette、状态入口、快速切换、工作区摘要，不能演变为重型业务编辑器。

---

## 3. 分层架构

```text
┌────────────────────────────────────────────────────────────┐
│                 User Interaction Layer                     │
│  热键呼出 / 托盘菜单 / 状态面板                             │
└────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────┐
│                   Steward UI Layer                         │
│  轻量面板 / 工具状态列表 / 当前上下文摘要                     │
└────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────┐
│                  Steward Core Layer                        │
│  process_manager / tool_registry / session_manager          │
│  workspace_context / event_bus                              │
└────────────────────────────────────────────────────────────┘
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│    Python Tool Layer     │  │      C++ Tool Layer      │
│  colorpicker / scripts   │  │  Loomery / pdf / layout  │
└──────────────────────────┘  └──────────────────────────┘
            │                           │
            └─────────────┬─────────────┘
                          ▼
┌────────────────────────────────────────────────────────────┐
│                  Content / Asset Layer                     │
│  AtriumNote markdown / attachments / cached indexes         │
└────────────────────────────────────────────────────────────┘
```

### 3.1 各层职责与非职责

| 层 | 负责 | 不负责 |
| :-- | :-- | :-- |
| UI | 显示面板与状态、呈现上下文、发出操作意图 | 子进程管理细节、图布局、PDF 解析、工具内部业务状态 |
| Core | 工具注册表、进程启停、健康状态、会话与上下文、工具间轻量协调 | 直接渲染复杂业务界面、实现专用工具业务逻辑 |
| Python Tool | 轻量工具、原型验证、文本处理脚本、AI 辅助与自动化胶水 | 常驻宿主基础设施、高负载长期运行的核心应用 |
| C++ Tool | 重型可视化、PDF 解析与缓存、复杂布局引擎、大型项目扫描索引、高性能长期运行工具 | — |
| Content | Markdown、附件、派生索引 | 应用代码 |

### 3.2 架构红线

| 编号 | 规则 | 说明 |
| :-- | :-- | :-- |
| V5-S1 | `ui/` 不得直接管理工具进程 | 通过 `core/` 统一编排 |
| V5-S2 | `Steward` 不得直接实现重型工具业务 | 避免宿主膨胀 |
| V5-S3 | 热键面板只做入口与状态 | 不承载复杂编辑 |
| V5-S4 | 工具接入必须经过注册表与协议 | 禁止隐式源码直连 |
| V5-S5 | 宿主必须支持独立工具进程挂载 | 与长期方向一致 |

---

## 4. 目标工作区结构

```text
Manager/
├── AtriumSteward/          # 常驻主控器
├── AtriumCppTools/         # C++ 重型工具集合
│   └── tools/Loomery/      # 可视化笔记工具（详见该仓库 README）
├── AtriumPyTools/          # Python 轻量工具与脚本
├── AtriumNote/             # Markdown / 附件 / 内容资产
├── launchers/              # 启动脚本
└── .venv/                  # 共享虚拟环境
```

**信息组织原则**：宿主与工具分离；代码与内容分离；按负载分语言；契约先行（工具接入前先定义协议，而不是先写直连调用）。

> `AtriumContracts/` 为规划中的跨工具 schema / 协议仓库，尚未创建，当前契约权威来源为 `AtriumCppTools/README.md`（待决项 W2）。

---

## 5. AtriumSteward 目标结构（C++）

```text
AtriumSteward/
├── CMakeLists.txt
├── apps/steward-desktop/
├── include/steward/{core,services,ui,contracts}/
├── src/
│   ├── core/            # process_manager / tool_registry / session_manager
│   │                    # workspace_context / event_bus
│   ├── services/        # config / logging / ipc / discovery
│   ├── ui/              # tray / hotkey_panel / widgets / viewmodels
│   └── integrations/    # python_tools / cpp_tools
├── resources/
├── tests/
└── Docs/
```

| 目录 | 职责 |
| :-- | :-- |
| `core/` | 进程编排、运行时状态、工具挂载、会话控制 |
| `services/` | 配置、日志、IPC、工具发现、环境适配 |
| `ui/` | 轻量面板、托盘、热键入口、状态展示 |
| `integrations/` | 与 Python / C++ 工具的协议适配层 |

---

## 6. Python 过渡期结构

在 C++ 宿主完成前，现有 Python 版必须先做一次**边界收束重构**，避免把不合理结构直接搬到 C++。

### 6.1 目标结构

```text
AtriumSteward/
├── main.py
├── pyproject.toml
├── requirements.txt
├── steward_app/
│   ├── app.py
│   ├── runtime/          # single_instance / window_manager / tool_runner
│   ├── core/             # config_loader / tool_registry / workspace_context
│   ├── ui/               # launcher_window / tray_controller / hotkey_panel
│   └── integrations/     # pytools / local_web
├── web/assets/
├── tests/
└── Docs/
```

### 6.2 重构动作

1. 从 `main.py` 中拆出单实例逻辑、窗口生命周期管理、工具运行器、托盘与热键入口。
2. 将当前 `qt/` 中的窗口实现迁移到 `steward_app/ui/`。
3. 将 `core/` 明确为纯逻辑目录，不允许依赖 Qt。
4. 清理旧 Flask 探索代码（`web/flask_app.py` 含公网 CDN 引用，违反离线原则），只保留纯本地离线画布资源。
5. 补齐 `pyproject.toml`，把 Python 版定义为过渡期应用，而非长期主架构终点。
6. 补充最小测试：`tool_registry`、`config_loader`、单实例行为、工具状态切换。

> 当前实现与上述目标结构的差距，逐项记录在仓库 `README.md` 的"当前实现状态"一节。

---

## 7. 契约与数据组织

规划 `AtriumContracts/`，集中放置 JSON Schema、YAML 配置模板、工具注册表示例、工具状态上报协议、启动参数约定。

推荐契约边界：

- `tool.manifest.json`：工具标识、入口、能力声明
- `session.context.json`：当前项目、当前笔记库、当前用户上下文
- `tool.status.json`：运行状态、最近错误、健康检查结果

**当前权威来源**：`AtriumCppTools/README.md` 定义了完整生命周期契约（manifest 字段、命名管道帧格式、命令与上报类型、退出码、版本管理）。宿主侧实现必须与该契约对齐，字段冻结前不得单边先行。

---

## 8. 分阶段重构计划

| 阶段 | 目标 | 关键动作 | 阶段产出 |
| :-- | :-- | :-- | :-- |
| 0 冻结 v4 | 建立归档基线 | v4 架构与规范全文交给 git；停止向旧结构叠加新业务 | 新需求统一以本文档为准 |
| 1 Python 收束 | 把 Python 主控整理成"可迁移宿主" | 拆分 `main.py`、清理 Flask 路径、规范 `pyproject.toml`、建立 `runtime/core/ui/integrations` 四层、建立统一工具运行器 | Python 版边界清晰，C++ 迁移有稳定映射目标 |
| 2 定义契约 | 迁语言前先固定接入规则 | 设计工具清单格式、启动参数、上下文同步格式、状态上报与健康检查协议、明确 `AtriumNote` 边界 | `AtriumContracts/` 初版；Python 与未来 C++ 工具按同一契约挂接 |
| 3 C++ 宿主壳层 | 先搭骨架，不急着迁完整业务 | 创建 CMake 工程；实现最小入口、托盘、热键面板；实现注册表读取、独立工具进程拉起与状态跟踪 | C++ 版可启动、可展示、可挂载工具 |
| 4 主控迁移 | 宿主基础设施从 Python 挪到 C++ | 迁移单实例、进程管理、工具状态管理、工作区上下文；Python 工具通过适配层接入 | Python 不再负责宿主核心 |
| 5 旗舰工具 | 落地 `Loomery` | 定义 Markdown + Mermaid + 扩展元数据模型；实现节点/子图/媒体语义；基础画布与自定义布局；预留 PDF 接入点；接入工具挂载协议 | 独立运行、受宿主管理的 `Loomery` |
| 6 工作区中枢 | 宿主稳定后承接跨工具能力 | 项目上下文切换、轻量任务入口、最近活动与状态汇总；评估日程/进度/留痕聚合 | `Steward` 成为工作区中枢 |

**当前进度**：阶段 0 完成；阶段 1 进行中。

---

## 9. 迁移优先级

**优先迁 C++**：`Steward` 常驻宿主、工具进程管理、热键面板与托盘入口、`Loomery`、PDF 解析与布局渲染等重型能力。

**继续留在 Python**：`colorpicker`、文本处理脚本、AI 辅助流程、Markdown 预处理与批量整理、新工具的快速原型。

---

## 10. 成功标准

1. `Steward` 具备独立宿主能力，而不是仅能打开窗口。
2. 面板保持轻量，没有承包重型业务界面。
3. Python 工具与 C++ 工具都可通过统一契约接入。
4. `Loomery` 作为独立工具挂接成功。
5. `AtriumNote` 作为内容仓库保持独立，不与应用代码混杂。

---

## 11. 总结

核心不是"把 Python 改成 C++"，而是重设整个工作区的长期结构：

- `AtriumSteward` 是宿主与中枢
- `AtriumCppTools` 是重型工具层
- `AtriumPyTools` 是轻量工具与脚本层
- `AtriumNote` 是内容资产层

这条路线允许当前 Python 基线继续工作，也为未来 C++ 主导体系预留了清晰、渐进、可验证的迁移路径。
