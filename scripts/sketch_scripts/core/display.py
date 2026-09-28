"""
core/display.py — Universal, crash-proof viewer for cq-server and OCP CAD Viewer.

Solves the cq-server assembly tessellation bug where show_object(cq.Assembly)
crashes or renders colorless models. Automatically extracts individual solids,
preserves component colors, and works with Workplanes, Compounds, and Assemblies.
"""

from __future__ import annotations
import cadquery as cq

try:
    from cq_server.ui import show_object as _cq_server_show_object
    HAS_CQ_SERVER = True
except ImportError:
    HAS_CQ_SERVER = False

try:
    from ocp_vscode import show_object as _ocp_show_object
    HAS_OCP = True
except ImportError:
    HAS_OCP = False


DEFAULT_COLORS = [
    (0.20, 0.60, 0.86),  # Blue
    (0.90, 0.49, 0.13),  # Orange
    (0.18, 0.80, 0.44),  # Green
    (0.60, 0.35, 0.71),  # Purple
    (0.95, 0.77, 0.06),  # Yellow
    (0.91, 0.30, 0.24),  # Red
    (0.58, 0.65, 0.65),  # Gray
]


def show(*objects, names: list[str] | None = None, colors: list[tuple] | None = None) -> None:
    """
    Universal display function. Handles cq.Workplane, cq.Solid, cq.Compound, 
    and cq.Assembly seamlessly without crashing cq-server or OCP viewer.

    Usage:
        show(my_part)
        show(part_a, part_b, colors=[(0.2, 0.7, 0.2), (0.8, 0.2, 0.2)])
        show(assembly)
    """
    for i, obj in enumerate(objects):
        name = names[i] if names and i < len(names) else f"part_{i}"
        color = colors[i] if colors and i < len(colors) else DEFAULT_COLORS[i % len(DEFAULT_COLORS)]

        if isinstance(obj, cq.Assembly):
            _show_assembly_nodes(obj)
        elif hasattr(obj, "build"):  # ParametricComponent instance
            _show_single_object(obj.build(), name=name, color=color)
        else:
            _show_single_object(obj, name=name, color=color)


def _show_single_object(obj, name: str, color: tuple) -> None:
    if HAS_CQ_SERVER:
        _cq_server_show_object(obj, name=name, options={"color": color})
    elif HAS_OCP:
        _ocp_show_object(obj, name=name, options={"color": color})


def _show_assembly_nodes(node: cq.Assembly, default_color=(0.85, 0.85, 0.85)) -> None:
    """Recursively walk assembly nodes and display each solid with preserved colors."""
    if node.obj is not None:
        color = default_color
        if node.color is not None:
            rgba = node.color.toTuple()
            color = rgba[:3]
        _show_single_object(node.obj, name=node.name or "node", color=color)

    for child in node.children:
        _show_assembly_nodes(child, default_color)
