# AtriumSteward

AtriumSteward 是 `Manager` 工作区中的桌面总控器，当前阶段按 `Launcher First / Offline First` 的 v4 基线推进。

当前已落地的主链路：

- `Launcher` 主面板
- 轻量工具注册表
- `ColorPicker` 工具窗口
- `Mermaid` 占位窗口

当前仍在演进中的能力：

- 单实例约束
- 真正的离线 Web 画布
- 配置加载与仓库扫描

## 技术基线

- Python 3.11+
- PySide6
- 本地工作区依赖：`AtriumPyTools/tools/colorpicker`

说明：

- 当前代码通过 `from colorpicker import sample_at_cursor` 直接依赖 `colorpicker` 顶层包。
- 因此这里应安装 `AtriumPyTools/tools/colorpicker` 这个子包，而不是仅安装 `AtriumPyTools` 仓库根包。

## 目录结构

```text
AtriumSteward/
├── core/
├── qt/
│   ├── resources/
│   └── tools/
├── web/
├── Docs/
├── main.py
├── config.yaml
└── requirements.txt
```

## 安装

本项目约定使用共享虚拟环境：`D:\Repositories\.venv`。

### 1. 检查共享虚拟环境

PowerShell:

```powershell
Get-ChildItem "D:\Repositories\.venv\bin"
& "D:\Repositories\.venv\bin\python.exe" -V
```

说明：

- 这个环境虽然在 Windows 上，但可执行文件位于 `bin/`，不是常见的 `Scripts/`。

### 2. 安装项目依赖

在 `AtriumSteward` 根目录执行：

```powershell
& "D:\Repositories\.venv\bin\python.exe" -m pip install --upgrade pip
& "D:\Repositories\.venv\bin\python.exe" -m pip install -r "D:\Repositories\Manager\AtriumSteward\requirements.txt"
```

当前验证结果：

- `D:\Repositories\.venv` 的 Python 兼容标签为 `cp312-*-mingw_x86_64_ucrt_gnu`
- `PySide6` 官方 wheel 不提供这组 Windows MinGW 标签
- 因此上述命令在当前共享环境中会卡在 `PySide6` 安装阶段，项目无法完整落依赖

也就是说，`requirements.txt` 写法本身没有问题，但这个共享虚拟环境当前不适合作为 AtriumSteward 的 Qt 运行环境。

`requirements.txt` 中已经包含本地可编辑依赖：

```text
-e ../AtriumPyTools/tools/colorpicker
```

这表示 `pip` 会从当前工作区直接安装 `colorpicker`，适合联动开发。

### 3. 如需手动单独安装本地包

如果你只想先安装 `colorpicker`，可以单独执行：

```powershell
& "D:\Repositories\.venv\bin\python.exe" -m pip install -e "D:\Repositories\Manager\AtriumPyTools\tools\colorpicker"
```

### 4. 推荐的可运行方案

如果你要马上运行 AtriumSteward，推荐二选一：

1. 重建 `D:\Repositories\.venv`，使用官方 Windows CPython 3.11 或 3.12 创建共享环境
2. 直接使用项目内已可用的 `D:\Repositories\Manager\AtriumSteward\.venv`

项目内环境的依赖现状已经包含：

- `PySide6`
- `keyboard`
- `pywin32`
- `colorpicker`

## 运行

共享环境重建完成后可执行：

```powershell
& "D:\Repositories\.venv\bin\python.exe" "D:\Repositories\Manager\AtriumSteward\main.py"
```

当前立即可执行的替代命令：

```powershell
& "D:\Repositories\Manager\AtriumSteward\.venv\Scripts\python.exe" "D:\Repositories\Manager\AtriumSteward\main.py"
```

## 当前依赖说明

- `PySide6`：Qt 桌面界面
- `keyboard`：当前热键注册实现
- `pywin32`：`colorpicker` 的 Windows 鼠标坐标读取依赖
- `colorpicker`：来自 `AtriumPyTools/tools/colorpicker` 的本地包

## 当前实现状态

当前仓库已经基本切到 v4 方向，但还没有完全对齐规范，主要差异有：

- `main.py` 仍保留全局热键和系统托盘逻辑，而这两项在 v4 中不是 V1 优先级
- 还没有单实例实现
- `web/flask_app.py` 仍是旧探索代码，与“默认不引入 Flask”的基线不一致
- `core/` 目录尚未补齐 `config_loader.py`、`repo_scanner.py`、`models.py`
- `tests/` 目录目前为空

## 文档

- 工作区规范：[Docs/WORKSPACE_SPECIFICATION-v4.md](file:///D:/Repositories/Manager/AtriumSteward/Docs/WORKSPACE_SPECIFICATION-v4.md)
- 架构设计：[Docs/ARCHITECTURE_DESIGN-v4.md](file:///D:/Repositories/Manager/AtriumSteward/Docs/ARCHITECTURE_DESIGN-v4.md)
