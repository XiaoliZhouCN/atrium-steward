# ChestSteward/core/tool_registry.py
"""
工具注册表。

这里是 ChestSteward 当前唯一的工具清单来源：
- Launcher 根据它渲染按钮
- 主程序根据它实例化窗口
"""
from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True, slots=True)
class ToolSpec:
    """描述一个可在 Launcher 中展示的工具。"""

    tool_id: str
    title: str
    module_path: str
    class_name: str
    enabled: bool = True


TOOL_REGISTRY: Final[tuple[ToolSpec, ...]] = (
    ToolSpec(
        tool_id="colorpicker",
        title="取色器",
        module_path="qt.tools.colorpicker_window",
        class_name="ColorPickerWindow",
    ),
    ToolSpec(
        tool_id="mermaid",
        title="Mermaid",
        module_path="qt.tools.mermaid_window",
        class_name="MermaidWindow",
    ),
)

_TOOL_MAP: Final[dict[str, ToolSpec]] = {
    spec.tool_id: spec for spec in TOOL_REGISTRY
}


def get_enabled_tools() -> tuple[ToolSpec, ...]:
    """返回当前启用的工具列表。"""
    return tuple(spec for spec in TOOL_REGISTRY if spec.enabled)


def get_tool_spec(tool_id: str) -> ToolSpec | None:
    """根据工具 ID 获取工具描述。"""
    return _TOOL_MAP.get(tool_id)
