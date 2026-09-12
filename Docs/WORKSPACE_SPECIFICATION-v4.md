# WORKSPACE\_SPECIFICATION.md（v4）

> **主要变更**
>
> 1. **开发优先级明确**：ChestSteward 第一阶段优先交付 `Launcher`，而不是一次性铺开全部工具。
> 2. **离线优先**：Web 相关能力仅作为本地预览画布，默认不依赖公网、不引入在线资源。
> 3. **插件化方式收敛**：采用“轻量注册表”而不是重型动态插件系统，保证可人工维护。
> 4. **V1 边界收紧**：V1 强制支持单实例；系统托盘不进入 V1；全局热键暂列为 `pending`。
> 5. **工程风格调整**：代码以清晰、可维护、可手工接管为优先目标，避免过度包装。

***

# Manager 工作区规范手册

> **版本**：v4.0（Launcher First / Offline First）\
> **生效日期**：2026-09-04\
> **适用范围**：`./Repositories/` 下所有仓库\
> **维护者**：AtriumSteward（总控仓库）

***

## 1. 总体设计哲学

- 唯一虚拟环境:G:\Repositories\Manager\.venv
    所有仓库都在该虚拟环境中运行，不允许创建独立虚拟环境。

本工作区遵循以下原则：

1. **关注点分离**：`Manager/` 与 `Projects/` 物理隔离。
2. **约定优于配置**：统一目录结构和命名，减少额外决策。
3. **零信任数据入口**：核心数据由脚本写入，避免手工脏数据。
4. **UI 与逻辑解耦**：Qt 负责界面，PyTools 负责纯数据与算法。
5. **原生优先，Web 为辅**：高频交互走 Qt；复杂可视化才使用 Web 画布。
6. **离线优先**：工作区默认按离线可运行设计，不以联网能力为前提。
7. **简单优先**：优先选择结构清晰、人工可维护的方案，避免过度工程化。
8. 每个工具/项目目录下必须包含 `Docs/ARCHITECTURE_DESIGN.md`。
9. Agent 协作规则以 `AGENTS.md` 为主入口；复杂模块可在 `Docs/Agents/` 下拆分详细契约文档。
10. Agent 规则遵循“子目录优先”原则：子目录 `AGENTS.md` 可以在局部范围内覆盖上层规则。

### 1.1 Agent 协作模板规范

为兼容 Trae、Cursor、dsh 等不同 AI IDE，本工作区统一采用 **“`AGENTS.md` 为主、其他工具规则文件按需映射”** 的组织方式。

**最小模板要求**：

- 仓库根目录建议提供一份 `AGENTS.md`，说明仓库范围、角色分工、禁改目录和最基本验证要求。
- 复杂子目录可放置局部 `AGENTS.md`，只描述该目录的特殊限制，不重复整仓规则。
- 详细背景、架构契约、第三方适配说明统一放在 `Docs/Agents/*.md`，由局部 `AGENTS.md` 链接引用。
- 第一批规则文件以“最小可用”为目标，不要求一次覆盖所有目录；优先覆盖高风险目录、第三方适配层和核心架构边界。

**协作目标**：

- 期望 AI IDE 自动识别 `AGENTS.md`；若工具暂不支持，也应允许通过人工提醒或任务上下文显式注入规则。
- 规则文件首先服务于“限制边界、明确权限、给出验证入口”，而不是堆积完整实现细节。
- 设计变更一旦影响目录边界、模块职责或接口契约，必须同步更新 `Docs/` 与相关 `AGENTS.md`。

***

## 2. 物理目录布局

```text
D:/Repositories/
├── Manager/
│   ├── ChestSteward/
│   ├── ChestPyTools/
│   └── ChestNote/
├── Projects/
│   ├── NexusRenderer/
│   ├── ChromaCMS/
│   └── (future projects...)
├── Storage/
│   ├── .gitignore
│   ├── data/
│   ├── outputs/
│   ├── cache/
│   └── shared_assets/
└── DeepseekHarness/
```

**红线规则**：

- `Manager/` 下仓库数量保持稳定，原则上不超过 5 个。
- `Projects/` 下严禁创建与 `Manager/` 同名的仓库。
- `Storage/` 默认全部忽略，仅保留目录骨架。

***

## 3. 各仓库职责与规范

### 3.1 ChestSteward（总控大脑）

**定位**：个人数字工作区的桌面总控器。采用 **“Qt 原生 Launcher + 独立工具窗口 + 本地预览画布”** 架构。

**当前阶段目标**：

1. 先完成可用的 `Launcher`。
2. 通过轻量注册表管理工具入口。
3. 接入 `ChestPyTools` 已有能力，优先打通取色工具链。
4. 为 Mermaid / 色度图保留本地预览画布能力。

**技术栈**：

- **桌面框架**：PySide6（Qt 6）
- **预览画布**：QWebEngineView（仅用于复杂可视化）
- **前后端通信**：Qt WebChannel / 本地进程内桥接
- **配置文件**：YAML
- **语言**：Python 3.11+

**约束说明**：

- Web 画布是 **本地预览组件**，不是联网浏览器。
- 默认不依赖公网 CDN、外部 API 或在线脚本。
- 如无必要，**不引入 Flask**；若未来确需本地 HTTP，仅允许用于本机回环地址和离线资源服务。
  - \[mark] 可以引入，但目前不着重开发。
- V1 **必须支持单实例**。
- 全局热键暂列 `pending`，不是 V1 阻塞项。
- 系统托盘优先级最低，不进入 V1 必选项。

**建议目录结构**：

```text
ChestSteward/
├── README.md
├── requirements.txt
├── config.yaml
├── main.py
├── core/
│   ├── __init__.py
│   ├── config_loader.py
│   ├── repo_scanner.py
│   ├── tool_registry.py
│   └── models.py
├── qt/
│   ├── __init__.py
│   ├── launcher_window.py
│   ├── tool_window.py
│   ├── bridge.py
│   ├── resources/
│   │   ├── icons/
│   │   └── style.qss
│   └── tools/
│       ├── __init__.py
│       ├── colorpicker_window.py
│       ├── mermaid_window.py
│       └── chromaticity_window.py
├── web/
│   ├── __init__.py
│   └── assets/
│       ├── mermaid/
│       │   ├── index.html
│       │   └── mermaid.min.js
│       └── chromaticity/
│           └── index.html
├── tests/
│   ├── test_repo_scanner.py
│   └── test_tool_registry.py
└── Docs/
    ├── WORKSPACE_SPECIFICATION-v4.md
    └── ARCHITECTURE_DESIGN-v4.md
```

**红线规则**：

- `qt/` 只负责界面、窗口状态和信号连接。
- `core/` 只负责配置、扫描、聚合、注册表等纯逻辑。
- `core/` 严禁依赖 `PySide6`、`QWebEngineView`。
- `qt/tools/` 下所有工具窗口必须继承 `ToolWindow`。
- 工具入口必须统一注册到 `tool_registry.py`，禁止在多个文件重复硬编码。
- 轻量注册表可以显式声明窗口类与元数据，但**不要求**做复杂的动态发现系统。

***

### 3.2 ChestPyTools（纯工具库）

**定位**：无状态、无 UI、可复用的 Python 工具集合。

**关键约束**：

- 严禁引入 Qt 或其他 UI 框架。
- 只返回纯数据，不返回任何控件对象。
- I/O 路径统一走共享路径工具，不允许硬编码。

**与 ChestSteward 的协作方式**：

- ChestSteward 通过直接 import 调用工具能力。
- 例如取色工具优先复用 `colorpicker.sample_at()`、`colorpicker.sample_at_cursor()` 这类纯函数接口。

***

### 3.3 ChestNote（知识库）

保持 v3 规范不变，核心要求如下：

- Markdown 文件必须通过脚本入口创建。
- Frontmatter 必须包含 `title`、`tags`、`created_at`。
- 导出索引仅作缓存，禁止手工修改。

***

### 3.4 `projects/` 下项目规范

保持 v3 规范不变，继续执行：

- C++ 项目采用 `App -> Runtime -> Shared` 单向依赖。
- `Runtime/` 层禁止引入 GUI 框架。
- 项目根目录必须包含 `project_status.yaml` 供 ChestSteward 扫描。

***

## 4. 跨仓库链接策略

### 4.1 基本原则

- 不使用 Git Submodule。
- `ChestSteward/config.yaml` 使用相对路径。
- 允许使用环境变量作为补充，但不能成为唯一入口。

### 4.2 ChestSteward 调用 ChestPyTools

```python
from colorpicker import sample_at_cursor

def update_color(self) -> None:
    color = sample_at_cursor()
    # Qt 层负责把纯数据渲染成界面
```

### 4.3 工具注册表示意

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ToolSpec:
    id: str
    title: str
    window_class: str
    enabled: bool = True
    uses_webview: bool = False
```

**约定**：

- 注册表是唯一工具清单来源。
- Launcher 根据注册表渲染按钮。
- 主程序根据注册表创建窗口实例。
- 不采用隐式扫描目录自动注册，避免维护成本失控。

***

## 5. ChestSteward 的产品边界

### 5.1 V1 必做

1. Launcher 主面板可显示、可关闭、可打开工具。
2. 轻量注册表可驱动工具列表与窗口创建。
3. 单实例约束可生效。
4. 取色器可接入 ChestPyTools 的现有取色逻辑。
5. Web 画布具备离线本地加载能力。

### 5.2 V1 非阻塞项

- 全局热键
- 系统托盘
- 项目看板
- 色度图完整功能
- 在线服务能力

***

## 6. 红线规则汇总

| 编号  | 规则                                       | 适用范围         |
| :-- | :--------------------------------------- | :----------- |
| R1  | `manager/` 与 `projects/` 必须物理隔离          | 全局           |
| R2  | `projects/` 下禁止创建与 `manager/` 同名仓库       | 全局           |
| R3  | ChestPyTools 严禁引入 UI 框架                  | ChestPyTools |
| R4  | ChestPyTools 严禁返回 UI 控件                  | ChestPyTools |
| R5  | ChestSteward 的 `core/` 严禁依赖 Qt / WebView | ChestSteward |
| R6  | 高频交互必须优先使用 Qt 原生控件                       | ChestSteward |
| R7  | Web 画布必须支持离线运行，禁止依赖公网资源                  | ChestSteward |
| R8  | 工具入口必须通过注册表统一管理                          | ChestSteward |
| R9  | V1 必须支持单实例                               | ChestSteward |
| R10 | 代码组织必须保持可人工维护，禁止无必要的复杂封装                 | 全局           |

***

## 7. AI Agent 协作规范

### 7.1 角色划分

工作区默认采用以下最小角色模型：

1. **架构师 Agent**
   负责仓库或工作区层面的架构设计、目录规划、接口骨架、必要函数框架以及架构文档产出；不负责具体功能细节的完整实现。
2. **模块开发 Agent**
   负责某个模块的具体功能实现；各模块负责目录必须互不相交，并尽量覆盖目标仓库全部业务子目录。
3. **测试 + 文档管理 Agent**
   负责测试补充、验证执行、文档整理与同步维护。

### 7.2 权限边界

- **架构师 Agent**：允许创建分支、提交、推送；不允许开 PR。
- **其他 Agent**：仅允许修改本地文件；不允许创建分支、提交、推送或开 PR。
- 当前阶段目录边界默认均可修改；未来如有禁区，应优先写入对应目录的 `AGENTS.md`。

### 7.3 当前禁改与变更原则

- **第三方源码**：原则上禁止直接修改；若确需个性化调整，应将目标部分迁移到工程自有目录中维护，而不是直接改动第三方源目录。
- **生成文件**：原则上禁止手工修改；如需变更，应通过脚本、生成器或格式化流程重新产出。
- **外部同步目录**：禁止修改。
- **归档文档**：禁止修改。
- **设计文档**：设计变更必须同步更新 `Docs/`，且默认仅允许架构师 Agent 修改。

### 7.4 验证与未决项

- 当前工作区尚未形成统一的测试分层、性能约束与安全约束清单；这些内容允许由各仓库后续逐步补充。
- 在缺少统一验证规范前，局部 `AGENTS.md` 至少应给出“改动前后需要运行或人工核对的最小检查项”。
- 允许改动级别、精度/性能/安全规则、测试分层等内容当前记为 `pending`，后续按仓库成熟度逐步落地。

### 7.5 文件组织建议

```text
<repo>/
├── AGENTS.md                  # 仓库级总入口
└── Docs/
    └── Agents/
        ├── AGENTS.md          # 局部目录摘要规则
        └── <topic>.md         # 详细契约、模块说明、第三方适配边界
```

**组织约定**：

- 根级 `AGENTS.md` 负责仓库级边界、角色、权限和通用禁令。
- 子目录 `AGENTS.md` 只补充局部特殊规则，默认继承上层约束。
- `Docs/Agents/*.md` 用于承载模块清单、依赖边界、适配契约等较长说明。

## 8. 快速参考

### 8.1 当前开发优先级

1. Launcher
2. Tool Registry
3. 单实例
4. ColorPicker 接入
5. 离线 Web 画布

### 8.2 文档归档规则

- `Docs/` 下保留当前生效版本文档。
- 历史版本统一移入 `Docs/stored/`。
- 归档文件命名保留版本号，不覆盖旧文件。

