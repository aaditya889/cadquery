"""
lib/show.py — cq-server compatible assembly display helpers

cq-server's show_object() crashes when passed a cq.Assembly because it
re-wraps it with a flat color override, corrupting tessellation metadata.

Use show_assembly() here instead of show_object(assembly) everywhere.
It recursively walks the assembly tree and calls show_object() on each
solid with the correct per-part color preserved.

Usage:
    from lib.show import show_assembly
    
    assembled = cq.Assembly()
    assembled.add(body_a, name="base", color=cq.Color(0.2, 0.7, 0.2))
    assembled.add(body_b, name="arm",  color=cq.Color(0.8, 0.1, 0.1))
    
    show_assembly(assembled)   # ← works in cq-server AND ocp_vscode
"""

from __future__ import annotations
from cq_server.ui import show_object
import cadquery as cq


def show_assembly(assembly: cq.Assembly, _default_color=(0.85, 0.85, 0.85)) -> None:
    """
    Recursively walk a cq.Assembly and call show_object() on every solid
    leaf with its own color preserved.  Works around the cq-server bug
    where passing an Assembly directly mangles tessellation metadata.
    """
    _walk(assembly, _default_color)


def _walk(node: cq.Assembly, default_color: tuple) -> None:
    """Depth-first traversal of an assembly tree."""
    if node.obj is not None:
        # Resolve this node's color
        if node.color is not None:
            if type(node.color) is not str:
              rgba = node.color.toTuple()
              color = rgba[:3]         # drop alpha — cq-server ignores it anyway
            else:
                color = node.color
        else:
            color = default_color

        show_object(node.obj, name=node.name, options={"color": color})

    for child in node.children:
        _walk(child, default_color)
