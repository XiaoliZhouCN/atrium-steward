# ChestSteward 架构设计文档（v4）

> **项目**：ChestSteward  
> **版本**：v4.0（Launcher First / Offline First）  
> **修订日期**：2026-09-04  
> **状态**：已确认的开发基线

---

## 1. 项目定义

### 1.1 一句话定义

> **ChestSteward** 是个人数字工作区的桌面启动器与工具总控器，采用 **Qt 原生 Launcher + 轻量工具注册表 + 独立工具窗口 + 离线本地预览画布** 架构。

### 1.2 当前阶段目标

1. 优先交付一个稳定、清晰、可维护的 `Launcher`。
2. 通过轻量注册表统一管理工具清单和窗口创建。
3. 打通与 `ChestPyTools` 的直接调用链，优先接入取色工具。
4. 为复杂图表保留离线本地 Web 画布能力，但不把 Web 当主界面。
5. 保持结构简洁，方便人工维护与后续增量开发。

### 1.3 非目标

当前阶段暂不追求：

- 系统托盘完整集成
- 联网浏览器能力
- 复杂插件市场式架构
- 过度抽象的多层包装

---

## 2. 核心架构决策

### 2.1 Launcher First

第一优先级不是某个单独工具，而是先完成统一入口：

- 显示工具列表
- 打开工具窗口
- 管理已打开窗口
- 为未来新增工具提供稳定接入点

这个决策的原因很直接：Launcher 是整个工作区的入口，后续工具都依附它生长。

### 2.2 Offline First

ChestSteward 的 Web 能力必须默认离线可运行：

- 不依赖公网 CDN
- 不依赖在线 API
- 不要求外网连接
- 预览资源随应用一同分发

Web 相关模块的职责是 **本地预览画布**，不是通用浏览器。

### 2.3 轻量注册表，而不是重型动态插件系统

本项目采用 **显式注册表**：

- 工具信息集中定义
- Launcher 从注册表读取按钮和元数据
- 主程序根据注册表创建窗口
- 新工具通过补一条注册项接入

不采用以下方案：

- 运行时扫描目录自动发现
- 隐式 import 链
- 复杂插件生命周期容器

原因：这类机制虽然“看起来高级”，但对个人长期维护不友好。

### 2.4 单实例进入 V1

V1 必须保证单实例运行，避免：

- 多个 Launcher 同时存在
- 重复注册资源
- 窗口状态混乱

### 2.5 全局热键暂挂起

全局热键有价值，但当前不作为 V1 阻塞项。  
若后续接入，必须作为可选能力，而不是让主链路依赖它。

---

## 3. 分层架构

### 3.1 总览

```text
┌────────────────────────────────────────────────────────────┐
│                     User Interaction                       │
│  - 手动启动应用                                            │
│  - 点击 Launcher 中的工具按钮                              │
└────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────┐
│                     Qt Launcher Layer                      │
│  - LauncherWindow                                          │
│  - ToolWindow 基类                                         │
│  - 独立工具窗口                                             │
└────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────┐
│                        Core Layer                          │
│  - config_loader                                           │
│  - tool_registry                                           │
│  - repo_scanner                                            │
│  - models                                                  │
└────────────────────────────────────────────────────────────┘
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
┌──────────────────────────────┐  ┌──────────────────────────┐
│      ChestPyTools Layer      │  │   Local Web Canvas Layer │
│  - colorpicker               │  │  - local html/js assets  │
│  - other pure tools          │  │  - QWebEngineView        │
└──────────────────────────────┘  └──────────────────────────┘
```

### 3.2 各层职责

#### Qt 层

负责：

- 窗口渲染
- 用户交互
- 信号槽连接
- 把纯数据渲染成可见界面

不负责：

- 仓库扫描逻辑
- 工具注册数据定义
- 色彩采样算法

#### Core 层

负责：

- 读取配置
- 管理工具注册表
- 提供仓库扫描与聚合结果
- 定义界面可消费的数据模型

不负责：

- 任何 Qt 控件
- 任何 WebView 控件
- 任何桌面系统 API

#### ChestPyTools 层

负责：

- 取色等纯工具能力
- 可测试的业务算法

不负责：

- 界面
- 窗口
- 交互流程

#### Local Web Canvas 层

负责：

- Mermaid / 色度图等复杂可视化预览
- 本地 HTML / JS 资源渲染

不负责：

- 系统调用
- 主界面导航
- 高频实时数据刷新

---

## 4. 建议目录结构

```text
ChestSteward/
├── main.py
├── config.yaml
├── requirements.txt
├── core/
│   ├── __init__.py
│   ├── config_loader.py
│   ├── models.py
│   ├── repo_scanner.py
│   └── tool_registry.py
├── qt/
│   ├── __init__.py
│   ├── launcher_window.py
│   ├── tool_window.py
│   ├── bridge.py
│   ├── resources/
│   └── tools/
│       ├── __init__.py
│       ├── colorpicker_window.py
│       ├── mermaid_window.py
│       └── chromaticity_window.py
├── web/
│   ├── __init__.py
│   └── assets/
│       ├── mermaid/
│       └── chromaticity/
├── tests/
└── Docs/
```

**说明**：

- `web/` 是本地预览资源目录，不代表联网服务层。
- 若未来必须引入本地 HTTP，只能作为可替换适配层，不能反过来成为主结构核心。

---

## 5. 工具注册表设计

### 5.1 设计目标

注册表是整个 Launcher 架构的枢纽，必须做到：

1. 唯一数据源
2. 明确可读
3. 易于手工维护
4. 不依赖隐式发现

### 5.2 推荐数据模型

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ToolSpec:
    id: str
    title: str
    description: str
    window_factory: str
    enabled: bool = True
    uses_webview: bool = False
```

### 5.3 推荐组织方式

```python
TOOL_REGISTRY = {
    "colorpicker": ToolSpec(
        id="colorpicker",
        title="取色器",
        description="屏幕像素采样工具",
        window_factory="qt.tools.colorpicker_window:ColorPickerWindow",
    ),
    "mermaid": ToolSpec(
        id="mermaid",
        title="Mermaid",
        description="本地流程图预览工具",
        window_factory="qt.tools.mermaid_window:MermaidWindow",
        uses_webview=True,
    ),
}
```

### 5.4 注册表规则

- Launcher 按注册表生成按钮，不自行维护另一份工具列表。
- `main.py` 或应用协调器按 `window_factory` 创建窗口实例。
- 对未启用工具可以显示为禁用，也可以不显示，但策略必须统一。
- 未注册工具不得从 UI 入口直接打开。

---

## 6. 关键模块说明

### 6.1 `main.py`

职责：

- 创建 Qt 应用
- 处理单实例约束
- 初始化注册表
- 创建 Launcher
- 统一管理工具窗口实例

不应承载：

- 大量工具实现细节
- 仓库扫描细节
- Web 业务逻辑

### 6.2 `core/tool_registry.py`

职责：

- 定义 `ToolSpec`
- 提供注册表访问接口
- 校验工具 ID 唯一性

### 6.3 `qt/launcher_window.py`

职责：

- 渲染启动器界面
- 显示工具按钮
- 发出“打开工具”信号

不负责：

- 决定某工具如何实例化
- 承担业务状态存储

### 6.4 `qt/tool_window.py`

职责：

- 统一工具窗口基类行为
- 统一关闭通知
- 统一公共样式与生命周期钩子

### 6.5 `qt/tools/colorpicker_window.py`

职责：

- 调用 `ChestPyTools` 的取色能力
- 渲染色块、坐标、RGB 数值
- 管理自动取色定时器

**推荐调用接口**：

```python
from colorpicker import sample_at_cursor, sample_at
```

### 6.6 `qt/tools/mermaid_window.py`

职责：

- 左侧提供原生文本编辑区
- 右侧提供本地 Web 预览区
- 通过桥接把 Mermaid 文本传给本地画布

### 6.7 `qt/bridge.py`

职责：

- 仅服务于 Web 预览工具
- 处理 Python 与本地页面脚本之间的数据交换

约束：

- 纯 Qt 工具不得依赖该桥接层

---

## 7. 数据流设计

### 7.1 打开工具

```text
1. 用户启动 ChestSteward
2. main.py 完成单实例检查
3. main.py 加载 TOOL_REGISTRY
4. LauncherWindow 根据注册表生成按钮
5. 用户点击某工具按钮
6. Launcher 发出 open_tool(tool_id) 信号
7. 应用协调器根据注册表创建或激活对应窗口
```

### 7.2 取色器数据流

```text
1. 用户打开 ColorPickerWindow
2. 点击“单次取色”或开启“自动取色”
3. Qt 层调用 colorpicker.sample_at_cursor()
4. ChestPyTools 返回纯数据字典
5. Qt 层刷新色块、坐标、RGB 标签
```

### 7.3 Mermaid 预览数据流

```text
1. 用户打开 MermaidWindow
2. 本地 HTML 预览页加载离线 Mermaid 资源
3. 用户修改左侧文本
4. Qt 通过 bridge 把 Mermaid 文本发给本地页面
5. 页面在 QWebEngineView 中重新渲染图形
```

---

## 8. 单实例设计要求

V1 中必须具备单实例能力，满足以下行为：

1. 已存在实例时，新实例不再完整启动。
2. 新实例应把“唤起主窗口”的意图传递给已存在实例。
3. 单实例机制应尽量使用 Qt 自带能力或最小依赖方案。

**建议优先级**：

- 首选 Qt 友好方案
- 其次是本地锁文件或本地命名资源
- 避免引入大型跨平台依赖仅为解决单实例问题

---

## 9. 离线 Web 画布要求

### 9.1 必须满足

- 所有 JS / HTML / CSS 资源本地化
- 不从 CDN 拉脚本
- 不假定外网可用
- 页面渲染不依赖远端接口

### 9.2 可选补充

- 若某些图表库必须通过本地服务访问，可引入回环地址服务
- 该服务必须只服务本地资源
- 该服务不得成为普通 Qt 工具的前置依赖

---

## 10. 架构红线

| 编号 | 规则 | 说明 |
| :-- | :-- | :-- |
| S1 | `core/` 不得依赖 Qt / WebView | 保证纯逻辑可测试 |
| S2 | 高频交互不得走 Web 画布 | 保证取色等工具延迟可控 |
| S3 | 所有工具窗口必须继承 `ToolWindow` | 统一生命周期 |
| S4 | Launcher 与主程序不得维护两份工具清单 | 注册表必须唯一 |
| S5 | Web 画布必须离线可运行 | 与产品定位一致 |
| S6 | V1 必须支持单实例 | 保证桌面入口稳定 |
| S7 | 架构实现优先简单清晰 | 方便人工维护 |

---

## 11. V1 里程碑

### 11.1 V1 范围

1. 启动应用并显示 Launcher
2. 基于注册表生成工具列表
3. 打开和复用工具窗口
4. 单实例生效
5. ColorPicker 接入 `ChestPyTools`
6. Mermaid 预览使用离线本地资源

### 11.2 V1 之后

- 全局热键恢复评估
- 项目看板接入仓库扫描
- 色度图工具实现
- 系统托盘补充

---

## 12. 实施建议

建议按照下面顺序开发：

1. `ToolSpec` 与 `tool_registry.py`
2. `LauncherWindow` 改为读取注册表
3. `main.py` 接入统一窗口管理
4. 单实例机制
5. ColorPickerWindow 接入 `ChestPyTools`
6. MermaidWindow 接入离线本地画布

这条顺序的重点是：**先搭稳定骨架，再接工具能力**。
