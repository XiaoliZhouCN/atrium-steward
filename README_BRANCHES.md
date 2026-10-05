# 工作区分支总览

> 数据采集日期：2026-09-19。分支状态变化快，使用前建议用 `git branch -a` 复核。
> 工作区级规范见 [`Docs/WORKSPACE_SPECIFICATION.md`](Docs/WORKSPACE_SPECIFICATION.md)。

## Manager 下仓库

| 仓库 | 当前 HEAD | 本地分支 |
| :-- | :-- | :-- |
| `AtriumSteward` | `develop` | `main` / `develop` / `dev/basic` |
| `AtriumNote` | `develop` | `main` / `develop` / `dev/basic` |
| `AtriumPyTools` | `develop` | `main` / `develop` / `dev/basic` / `dev/basic-colorpicker` |
| `AtriumCppTools` | `dev/basic` | `main` / `develop` / `dev/basic` / `tools` / `tool/loomery` |

`Manager/launchers` 与 `Manager/.venv` 不纳入版本控制。

## AtriumSteward

- `develop`（HEAD，最新）：44 文件，2026-09-16
- `dev/basic`：43 文件，2026-09-12
- `main`：43 文件，2026-09-12（经 PR #3 合入 `develop`）

> `main` **并非**空分支，已包含完整代码与文档；`develop` 领先一个文档提交。

## AtriumNote

- `develop`（HEAD）：22 文件，2026-09-12（PR #1 合入 `dev/basic`）
- `dev/basic`：22 文件，2026-09-12
- `main`：22 文件，2026-09-12（PR #2 合入 `develop`）

## AtriumPyTools

- `develop`（HEAD）：39 文件，2026-09-16
- `dev/basic-colorpicker`：38 文件，2026-09-12（取色工具分支）
- `dev/basic`：38 文件，2026-09-12（PR #1 合入 `dev/basic-colorpicker`）
- `main`：38 文件，2026-09-12（PR #3 合入 `develop`）

> 该仓库尚未采用 `tool/<name>` 命名，取色器分支仍是旧式 `dev/basic-colorpicker`（见待决项）。

## AtriumCppTools

分支模型最完整，**框架与工具严格隔离**（详细纪律见该仓库 `README.md` §1.2）：

| 分支 | 角色 | 文件数 | 状态 |
| :-- | :-- | :-- | :-- |
| `main` | 最终汇总，只做合入 | 1 | 仅 Initial commit |
| `develop` | 框架开发：`common/`、构建系统、契约基线 | 21 | 2026-09-19 |
| `dev/basic` | 框架开发分支，合入 `develop` | 11 | 当前 HEAD；框架 v2.0 定案但尚未合入 `develop` |
| `tools` | 工具汇总分支 | 21 | 与 `develop` 同源 |
| `tool/loomery` | 首个工具 `Loomery` 开发分支 | 12 | 已建最小 Qt 窗口起点，未开工 |

派生链：`develop` → `tools` → `tool/<tool>`。工具分支不得修改框架文件。

> 工具分支前缀必须是 `tool/` 而非 `tools/`：git 无法同时存在 `refs/heads/tools` 与 `refs/heads/tools/<x>`。

## 未纳入本总览

`Projects/` 下 7 个项目、`Storage/`、`DeepseekHarness/` 不属 `Manager` 工作区范围，各自独立管理。

## 远端仓库对应关系

| 目录 | 远端 |
| :-- | :-- |
| `Manager/AtriumSteward` | `git@github-shirley:XiaoliZhouCN/atrium-steward.git` |
| `Manager/AtriumNote` | `git@github-shirley:XiaoliZhouCN/atrium-note.git` |
| `Manager/AtriumPyTools` | `git@github-shirley:XiaoliZhouCN/atrium-pytools.git` |
| `Manager/AtriumCppTools` | `git@github-shirley:XiaoliZhouCN/atrium-cpptools.git` |
| `Projects/ChromaCMS` | `git@github-shirley:XiaoliZhouCN/chroma-cms.git` |
| `Projects/NexusRenderer` | `git@github-shirley:XiaoliZhouCN/nexus-renderer.git` |

`AtriumCppTools` 与 `AtriumSteward` 之外的 `Atrium*` 仓库已完成从 `Chest*` 的改名迁移。
