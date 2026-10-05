# AGENTS.md

本文件是 `AtriumSteward` 仓库级 Agent 规则入口。工作区级规范见 [`Docs/WORKSPACE_SPECIFICATION.md`](Docs/WORKSPACE_SPECIFICATION.md)，本文档只承载**协作边界与权限**，不重复条文；冲突时以工作区规范为准。

## 适用范围

- 适用于 `D:\Repositories\Manager\AtriumSteward\` 整个仓库。
- 子目录若存在自己的 `AGENTS.md`，优先级更高。

## 先读后改

改动任何目录前必须先读：

1. `Docs/WORKSPACE_SPECIFICATION.md`（工作区红线与文档规范）
2. `Docs/ARCHITECTURE_DESIGN.md` 的相关章节
3. 目标目录的局部 `AGENTS.md`（若存在）

## 角色与权限

- **架构师 Agent**：目录规划、接口骨架、架构文档；允许建分支、提交、推送；不允许开 PR。
- **模块开发 Agent**：具体功能实现；仅允许修改本地文件。
- **测试 + 文档管理 Agent**：测试补充、验证执行、文档同步；仅允许修改本地文件。

> 档位的完整定义、叠加与降级规则见 [`Docs/AGENT_ROLES.md`](Docs/AGENT_ROLES.md)（工作区级，是 [`Docs/WORKSPACE_SPECIFICATION.md`](Docs/WORKSPACE_SPECIFICATION.md) §6.1 的展开）。

## 本仓库特有的管家设计

本节说明**本项目专属**的常驻管家设计，仅适用于 `AtriumSteward/`，属对上层规范的**扩写**，不改变任何权限结论。

- **档位与管家是两层**：档位管权限（工作区级，见 [`Docs/AGENT_ROLES.md`](Docs/AGENT_ROLES.md) §1）；管家管人格与服务域（本仓库专属，见 [`Docs/AGENTS_ROLES.md`](Docs/AGENTS_ROLES.md)）。
- **一名管家可同时持多个档位**，按动作取最小档位执行；**管家名不得作为权限依据**。当前映射：

| 管家 | 常戴档位 | 服务域 |
| :-- | :-- | :-- |
| `steward.konstantine` | 建设档（+ 掌籍档、视务档） | 成长计划、契约与结构、工程秩序 |
| `steward.gui` | 视务档（+ 掌籍档） | 图形渲染实现、工具与呈现、性能数据 |
| `steward.chestnut` | 掌籍档（+ 建设档） | 手账、习惯、足迹、鉴赏、理财记录、inbox |

- **服务范围不限于项目开发**：生活域（成长计划、手账、足迹、鉴赏、理财）同样在服务范围内。其内容结构以 [`../AtriumNote/Docs/ARCHITECTURE_DESIGN.md`](../AtriumNote/Docs/ARCHITECTURE_DESIGN.md) 为唯一权威；[`../AtriumNote/AGENTS.md`](../AtriumNote/AGENTS.md) 的红线（目录边界须人工确认、禁用 frontmatter、时间轴单一化）对本仓库管家同样有效。

### 下游仓库的扩写规则（跨仓库）

`AtriumSteward/AGENTS.md` 与 `Docs/` 是各子仓库 `AGENTS.md` 的**权威基础**：

1. **可扩写**：只写子仓库自有边界、禁令与最小验证项；不得复制上级条文，只做链接引用。
2. **可收紧**：允许比上级更严格，需在条目内写明理由。
3. **覆盖须标注**：与上级不一致的条目必须标 `[MARK]`，写明覆盖哪一条、理由与影响范围（格式见 `Docs/AGENT_ROLES.md` §4）。
4. **禁止静默改写**：不一致且无 `[MARK]` 的条目视为违规，发现即回写为链接引用或补标。

## 禁止事项

- **禁止修改 `Docs/WORKSPACE_SPECIFICATION.md` 的跨仓库条文**：它是工作区唯一权威来源，变更影响全部仓库，属人工决策范围。
- 禁止在 `core/` 中引入 `PySide6`、`QWebEngineView` 或任何 UI 依赖。
- 禁止在 `qt/` 中写业务逻辑；界面层只做显示、窗口状态与信号连接。
- 禁止在多个文件重复硬编码工具入口；工具清单只能来自 `core/tool_registry.py`。
- 禁止让 Web 画布依赖公网资源（CDN、外部 API、在线脚本）；本工作区离线优先。
- 禁止把工具实现直接 `import` 进宿主以绕过注册表与协议。
- 禁止创建独立虚拟环境；唯一环境是 `Manager/.venv`。
- 禁止提交 `__pycache__`、IDE 配置与构建产物。
- 禁止在文件名中携带版本号来复制文档（历史版本交给 git）。

## 最小验证要求

任何改动提交前必须完成：

1. 入口可导入：`& "D:\Repositories\Manager\.venv\Scripts\python.exe" -c "import main"`（在仓库根执行）。
2. 若改动涉及界面，手动运行 `main.py` 确认 Launcher 可显示、可关闭、可打开工具。
3. 若改动涉及注册表，确认 Launcher 按钮数量与 `core/tool_registry.py` 一致。
4. 若改动涉及 `core/` 分层，确认无 Qt 依赖：`rg "PySide6|QWebEngine" core/` 无结果。

**禁止的"验证"**：只看语法能过就宣称完成；只测导入路径而从未实际运行窗口；改动后不检查是否有残留进程。

## 当前未决项（不得擅自决定）

- `Docs/WORKSPACE_SPECIFICATION.md` §8 的 W1–W5。
- `Docs/ARCHITECTURE_DESIGN.md` 的迁移阶段推进顺序。
- 与 `AtriumCppTools` 的协议字段命名冻结（当前契约权威在 `AtriumCppTools/README.md`）。
- `web/` 遗留代码的处置方式（删除 / 改造为离线画布）。

## 详细规则入口

- 工作区规范：`Docs/WORKSPACE_SPECIFICATION.md`
- 工作区角色与权限档位：`Docs/AGENT_ROLES.md`
- 本仓库管家设计（人格与职责分区）：`Docs/AGENTS_ROLES.md`
- 本仓库架构：`Docs/ARCHITECTURE_DESIGN.md`
- 仓库定位与状态：`README.md`
