"""
core — Foundation module for sketch-based CAD-as-Code.
"""

from .base import Component
from .ports import Port, attach
from .display import show
from .booleans import (
    to_shape,
    to_workplane,
    duplicate,
    fuse_all,
    find_junction_edges,
    CustomSelector,
)

__all__ = [
    "Component",
    "Port",
    "attach",
    "show",
    "to_shape",
    "to_workplane",
    "duplicate",
    "fuse_all",
    "find_junction_edges",
    "CustomSelector",
]
