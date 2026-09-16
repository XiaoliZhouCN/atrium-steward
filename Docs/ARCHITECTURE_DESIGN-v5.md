# AtriumSteward 架构设计文档（v5）

> **项目**：AtriumSteward\
> **版本**：v5.0（Resident Host / Managed Tools / C++ First）\
> **修订日期**：2026-09-12\
> **状态**：重构基线草案，作为 v5 迁移依据

***

## 0. 与 v4 的关系

- `ARCHITECTURE_DESIGN-v4.md` 作为 **Python Launcher 阶段归档文档** 保留，不再覆盖更新。
- 本文档定义新的 v5 架构方向：`AtriumSteward` 从“桌面启动器”升级为“常驻主控 + 工具编排器 + 状态中枢”。
- v5 不采用一次性全量重写，而是采用 **先收束 Python 边界，再引入 C++ 宿主** 的渐进迁移方案。

## 1. 项目定义

### 1.1 一句话定义

> **AtriumSteward** 是 `Manager` 工作区中的常驻桌面主控器，负责统一管理工具进程、工作区状态、轻量入口面板与跨工具协同；重型能力和旗舰工具逐步迁移到 C++，轻量工具与脚本能力继续保留在 Python。

### 1.2 v5 当前阶段目标

1. 明确 `Steward` 的职责边界，避免其继续膨胀为“什么都做”的单体程序。
2. 将当前 Python 版 `AtriumSteward` 收束为可迁移、可拆分、可验证的过渡基线。
3. 为未来新增 `AtriumCppTools/` 做出清晰的目录和契约预留。
4. 将 Mermaid 可视化笔记工具纳入长期旗舰工具规划，但不把其具体实现塞入 `Steward` 本体。
5. 建立“宿主进程 - 独立工具 - 内容仓库”三者分离的长期结构。

### 1.3 v5 非目标

当前阶段暂不追求：

- 一次性把所有 Python 代码改写成 C++
- 把所有工具都嵌入 `Steward` 主窗口内部
- 立即实现完整的人生管理平台、项目进度系统、日程系统、知识图谱系统
- 过早引入重型插件市场、脚本沙箱、动态模块装卸框架

## 2. 核心架构决策

### 2.1 Steward 不再只是 Launcher

v4 中 `Steward` 以 Launcher 为第一优先级，这个方向在早期是正确的；但 v5 起，`Steward` 的定位升级为：

- 常驻进程
- 工具生命周期管理器
- 工作区上下文中枢
- 轻量入口面板

也就是说，`Steward` 不再是“唤起进程后就撒手”的启动器，而是 **负责挂载、观察和协调工具** 的宿主。

### 2.2 Steward 也不是全能业务中心

`Steward` 负责“管理”，不负责“承包所有业务实现”。

它可以知道：

- 哪些工具存在
- 哪些工具在运行
- 当前用户在哪个项目、哪套笔记、哪个任务上下文中工作

但它不应该直接承担：

- Mermaid 笔记编辑器实现
- PDF 解析与渲染引擎
- 图布局算法
- 专用工具的复杂领域状态

### 2.3 C++ First，但不是 Python 清零

v5 采用 **C++ First** 原则：

- 常驻宿主、重型工具、长期维护的桌面基础设施优先使用 C++
- 原型、轻量工具、脚本胶水、AI 辅助模块继续保留 Python

保留 Python 的原因不是妥协，而是为了维持：

- 快速迭代速度
- 文本处理与脚本化优势
- 外部服务整合速度
- 低成本试验新想法的能力

### 2.4 工具以“独立受管进程”为主

v5 默认工具运行形态为：

- 独立进程
- 由 `Steward` 启动、挂载、跟踪状态
- 通过明确协议交换状态、上下文与命令

不再默认把工具作为 `Steward` 的内部窗口类直接 import 进来。

### 2.5 笔记应用与笔记内容必须分离

对未来的 Mermaid 可视化笔记工具，必须区分：

- **应用代码**：如 `AtriumCanvasNote`
- **内容仓库**：如 `AtriumNote`

应用负责：

- 编辑
- 渲染
- 布局
- 媒体承载

内容仓库负责：

- Markdown 文件
- 附件
- PDF 索引结果
- 用户笔记资产

### 2.6 面板必须保持轻量

`Steward` 的热键面板可以存在，而且应该存在；但它只能是：

- Command Palette
- 状态入口
- 快速切换界面
- 当前工作区摘要

不能演变为重型业务编辑器。

## 3. 分层架构

### 3.1 总览

```text
┌────────────────────────────────────────────────────────────┐
│                    User Interaction Layer                  │
│  - 热键呼出                                                 │
│  - 托盘菜单                                                 │
│  - 状态面板 / 命令面板                                      │
└────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────┐
│                    Steward UI Layer                        │
│  - 轻量面板                                                 │
│  - 工具状态列表                                             │
│  - 当前上下文摘要                                           │
└────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────┐
│                   Steward Core Layer                       │
│  - process_manager                                         │
│  - tool_registry                                           │
│  - session_manager                                         │
│  - workspace_context                                       │
│  - event_bus                                               │
└────────────────────────────────────────────────────────────┘
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
┌──────────────────────────────┐  ┌──────────────────────────┐
│      Python Tool Layer       │  │     C++ Tool Layer       │
│  - colorpicker               │  │  - canvas note           │
│  - scripts / glue            │  │  - pdf parsing           │
│  - lightweight utilities     │  │  - layout engines        │
└──────────────────────────────┘  └──────────────────────────┘
             │                           │
             └─────────────┬─────────────┘
                           ▼
┌────────────────────────────────────────────────────────────┐
│                    Content / Asset Layer                   │
│  - AtriumNote markdown                                     │
│  - attachments / media                                     │
│  - cached indexes / derived data                           │
└────────────────────────────────────────────────────────────┘
```

### 3.2 各层职责

#### Steward UI Layer

负责：

- 显示热键面板、托盘、状态入口
- 展示工具运行状态
- 呈现当前上下文
- 发出启动、切换、附着、关闭等操作意图

不负责：

- 子进程管理细节
- 图布局算法
- PDF 解析
- 工具内部业务状态

#### Steward Core Layer

负责：

- 工具注册表
- 进程启动与退出
- 工具健康状态维护
- 当前会话与工作区上下文
- 工具之间的轻量协调

不负责：

- 直接渲染复杂业务界面
- 实现专用工具业务逻辑

#### Python Tool Layer

负责：

- 轻量工具
- 原型验证
- 文本处理脚本
- AI 辅助与自动化胶水

不负责：

- 常驻宿主基础设施
- 高负载长期运行的核心应用

#### C++ Tool Layer

负责：

- 重型可视化工具
- PDF 解析与缓存
- 复杂布局引擎
- 大型项目扫描与索引
- 高性能、长期运行的桌面工具

## 4. 推荐工作区结构

```text
Manager/
├── AtriumSteward/          # C++ 常驻主控器
├── AtriumCppTools/         # C++ 重型工具集合
│   └── AtriumCanvasNote/   # Mermaid 可视化笔记工具
├── AtriumPyTools/          # Python 轻量工具与脚本
├── AtriumNote/             # Markdown / 附件 / 个人内容仓库
├── AtriumContracts/        # 跨工具 schema / 协议 / 示例
├── launchers/              # .bat / powershell / 快捷启动
└── docs/                   # 工作区级总文档
```

### 4.1 信息组织原则

1. **宿主与工具分离**：`AtriumSteward/` 不实现工具业务本体。
2. **代码与内容分离**：`AtriumCanvasNote/` 与 `AtriumNote/` 不混放。
3. **按负载分语言**：高负载与基础设施用 C++，轻量与试验用 Python。
4. **契约先行**：工具接入 `Steward` 时必须先定义协议，而不是先写直连调用。

## 5. AtriumSteward（C++ 目标结构）

```text
AtriumSteward/
├── CMakeLists.txt
├── apps/
│   └── steward-desktop/
├── include/
│   └── steward/
│       ├── core/
│       ├── services/
│       ├── ui/
│       └── contracts/
├── src/
│   ├── core/
│   │   ├── process_manager/
│   │   ├── tool_registry/
│   │   ├── session_manager/
│   │   ├── workspace_context/
│   │   └── event_bus/
│   ├── services/
│   │   ├── config/
│   │   ├── logging/
│   │   ├── ipc/
│   │   └── discovery/
│   ├── ui/
│   │   ├── tray/
│   │   ├── hotkey_panel/
│   │   ├── widgets/
│   │   └── viewmodels/
│   └── integrations/
│       ├── python_tools/
│       └── cpp_tools/
├── resources/
├── tests/
└── Docs/
```

### 5.1 Steward 模块职责

- `core/`：进程编排、运行时状态、工具挂载、会话控制
- `services/`：配置、日志、IPC、工具发现、环境适配
- `ui/`：轻量面板、托盘、热键入口、状态展示
- `integrations/`：与 Python / C++ 工具的协议适配层

### 5.2 Steward 架构红线

| 编号 | 规则 | 说明 |
| :- | :-- | :-- |
| V5-S1 | `ui/` 不得直接管理工具进程 | 通过 `core/` 统一编排 |
| V5-S2 | `Steward` 不得直接实现重型工具业务 | 避免宿主膨胀 |
| V5-S3 | 热键面板只做入口与状态 | 不承载复杂编辑 |
| V5-S4 | 工具接入必须经过注册表与协议 | 禁止隐式源码直连 |
| V5-S5 | 宿主必须支持独立工具进程挂载 | 与长期方向一致 |

## 6. AtriumPyTools 重构要求

`AtriumPyTools` 在 v5 中继续保留，但定位必须收束为 **轻量工具层与脚本层**。

### 6.1 保留方向

- 小工具 CLI
- 文本处理脚本
- 原型算法
- AI 辅助脚本
- 自动化 glue code

### 6.2 不再承载的方向

- `Steward` 的主控逻辑
- 长驻基础设施
- 大型可视化编辑器
- 复杂多媒体承载与长期状态管理

### 6.3 推荐结构

```text
AtriumPyTools/
├── pyproject.toml
├── tools/
│   ├── colorpicker/
│   └── ...
├── scripts/
├── shared/
├── tests/
└── docs/
```

### 6.4 Python 侧必须执行的重构

1. 将当前 `AtriumSteward` 中依赖 Python 工具源码直连的部分逐步改为稳定接口调用。
2. `colorpicker` 继续保留在 `AtriumPyTools/tools/`，但对外暴露稳定 CLI 或稳定 API。
3. 新 Python 工具不得默认依赖 `Steward` Qt 窗口对象。
4. 文本处理、Markdown 预处理、AI 摘要等适合脚本化的能力优先留在 Python。

## 7. 当前 Python 版 AtriumSteward 的过渡期重构

在 C++ 宿主完成前，现有 Python 版 `AtriumSteward` 必须先做一次 **边界收束重构**，避免把不合理结构直接搬到 C++。

### 7.1 当前问题

- `main.py` 同时承担单实例、热键、托盘、窗口管理、工具创建等职责
- `Steward` 仍直接 import 本地工具实现
- `web/flask_app.py` 是旧探索遗留，与主方向不一致
- `pyproject.toml` 为空，工程元信息不完整
- 当前目录更像原型，不像长期可迁移骨架

### 7.2 Python 过渡期目标结构

```text
AtriumSteward/
├── main.py
├── pyproject.toml
├── requirements.txt
├── steward_app/
│   ├── app.py
│   ├── runtime/
│   │   ├── single_instance.py
│   │   ├── window_manager.py
│   │   └── tool_runner.py
│   ├── core/
│   │   ├── config_loader.py
│   │   ├── tool_registry.py
│   │   └── workspace_context.py
│   ├── ui/
│   │   ├── launcher_window.py
│   │   ├── tray_controller.py
│   │   └── hotkey_panel.py
│   └── integrations/
│       ├── pytools/
│       └── local_web/
├── web/
│   └── assets/
├── tests/
└── Docs/
```

### 7.3 Python 过渡期重构动作

1. 从 `main.py` 中拆出：
   - 单实例逻辑
   - 窗口生命周期管理
   - 工具运行器
   - 托盘与热键入口
2. 将当前 `qt/` 中的窗口实现迁移到 `steward_app/ui/`。
3. 将 `core/` 明确为纯逻辑目录，不允许依赖 Qt。
4. 清理或归档 `web/flask_app.py`，保留纯本地离线画布资源。
5. 补齐 `pyproject.toml`，把 Python 版 `AtriumSteward` 定义为过渡期应用，而不是长期主架构终点。
6. 补充最小测试：
   - `tool_registry`
   - `config_loader`
   - 单实例行为
   - 工具状态切换

## 8. AtriumCppTools 与旗舰工具规划

### 8.1 推荐结构

```text
AtriumCppTools/
├── CMakeLists.txt
├── common/
├── tools/
│   └── AtriumCanvasNote/
│       ├── CMakeLists.txt
│       ├── include/
│       ├── src/
│       │   ├── document/
│       │   ├── graph/
│       │   ├── media/
│       │   ├── pdf/
│       │   ├── render/
│       │   └── ui/
│       ├── resources/
│       ├── tests/
│       ├── benchmarks/
│       └── Docs/
└── third_party/
```

### 8.2 AtriumCanvasNote 职责

- 以 Markdown 为主存储格式
- 以 Mermaid 为图结构描述语言之一
- 在内部维护更强的节点、子图、媒体、布局语义
- 提供个性化画布展示，而不是受限于 Mermaid 默认渲染
- 支持图片、视频、未来的 PDF 笔记接入

### 8.3 与 AtriumNote 的关系

`AtriumCanvasNote` 读写 `AtriumNote/` 内容，但不与其源码混放。

## 9. 契约与数据组织

建议新增 `AtriumContracts/`，集中放置：

- JSON Schema
- YAML 配置模板
- 工具注册表示例
- 工具状态上报协议
- `Steward` 与工具的启动参数约定

### 9.1 推荐契约边界

- `tool.manifest.json`：工具标识、入口、能力声明
- `session.context.json`：当前项目、当前笔记库、当前用户上下文
- `tool.status.json`：运行状态、最近错误、健康检查结果

## 10. 分阶段重构计划

### 阶段 0：冻结 v4，建立归档基线

目标：

- 明确 v4 为归档版本
- 停止继续往 v4 架构里叠加新业务

动作：

- 保留 `ARCHITECTURE_DESIGN-v4.md`
- 新需求统一以 v5 文档为准
- 对当前 Python 代码仅做必要修复，不再扩写结构性新能力

阶段产出：

- v4 归档完成
- v5 文档成为唯一新增设计依据

### 阶段 1：Python 版 Steward 收束重构

目标：

- 把当前 Python 主控整理成“可迁移宿主”

动作：

- 拆分 `main.py`
- 清理旧 `Flask` 探索路径
- 规范 `pyproject.toml`
- 建立 `runtime/core/ui/integrations` 四层
- 为工具接入建立统一运行器，而不是散落 import

阶段产出：

- Python 版 `Steward` 拥有清晰边界
- 后续 C++ 迁移有稳定映射目标

### 阶段 2：定义宿主与工具契约

目标：

- 在迁语言前先固定接入规则

动作：

- 设计工具清单格式
- 设计工具启动参数
- 设计上下文同步格式
- 设计状态上报与健康检查协议
- 明确 `AtriumNote` 作为内容仓库的边界

阶段产出：

- `AtriumContracts/` 初版
- Python 工具与未来 C++ 工具都可按同一契约挂接

### 阶段 3：建立 C++ 版 Steward 壳层

目标：

- 先搭出 C++ 宿主骨架，不急着迁完整业务

动作：

- 创建 `AtriumSteward` CMake 工程
- 实现最小入口、托盘、热键面板
- 实现工具注册表读取
- 实现独立工具进程拉起与状态跟踪

阶段产出：

- C++ 版 `Steward` 可启动、可展示、可挂载工具

### 阶段 4：迁移主控能力到 C++

目标：

- 把宿主基础设施从 Python 挪到 C++

动作：

- 迁移单实例
- 迁移进程管理
- 迁移工具状态管理
- 迁移工作区上下文维护
- 保留 Python 工具通过适配层接入

阶段产出：

- Python 不再负责宿主核心
- C++ 成为真正主控

### 阶段 5：建设 AtriumCanvasNote

目标：

- 将 Mermaid 可视化笔记工具作为旗舰工具落地

动作：

- 定义 Markdown + Mermaid + 扩展元数据模型
- 实现节点、子图、媒体容器语义
- 实现基础画布与自定义布局
- 预留 PDF 接入点
- 接入 `Steward` 的工具挂载协议

阶段产出：

- 独立运行的 `AtriumCanvasNote`
- 受 `Steward` 管理但不内嵌于 `Steward`

### 阶段 6：扩展为工作区中枢

目标：

- 在宿主稳定后再逐步承接更多跨工具能力

动作：

- 增加项目上下文切换
- 增加轻量任务入口
- 增加最近活动与状态汇总
- 评估是否纳入日程、进度、留痕聚合

阶段产出：

- `Steward` 成为工作区中枢，而不是仅仅 Launcher

## 11. 迁移优先级建议

优先迁移到 C++ 的内容：

1. `Steward` 常驻宿主
2. 工具进程管理
3. 热键面板与托盘入口
4. Mermaid 可视化笔记工具
5. PDF 解析、布局、缓存、渲染等重型能力

继续保留在 Python 的内容：

1. `colorpicker`
2. 文本处理脚本
3. AI 辅助流程
4. Markdown 预处理与批量整理
5. 新工具的快速原型

## 12. v5 成功标准

满足以下条件后，可认为 v5 架构方向成立：

1. `Steward` 已具备独立宿主能力，而不是仅能打开窗口
2. `Steward` 面板仍保持轻量，没有承包重型业务界面
3. Python 工具与 C++ 工具都可通过统一契约接入
4. `AtriumCanvasNote` 作为独立工具挂接成功
5. `AtriumNote` 作为内容仓库保持独立，不与应用代码混杂

***

## 13. 总结

v5 的核心不是“把 Python 改成 C++”这么简单，而是重设整个 `Manager` 工作区的长期结构：

- `AtriumSteward` 是宿主与中枢
- `AtriumCppTools` 是重型工具层
- `AtriumPyTools` 是轻量工具与脚本层
- `AtriumNote` 是内容资产层

这条路线允许当前 Python 基线继续工作，也为未来的 C++ 主导体系预留了清晰、渐进、可验证的迁移路径。
