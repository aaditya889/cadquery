"""
core/base.py — Base class for all parametric CAD components.

Provides a unified interface for defining parametric parts with:
- Cached builds
- Anchor / Mating Ports
- Direct STL and STEP exporting
- Clean transformations (translate, rotate, locate)
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
import os
import cadquery as cq
from cadquery import exporters
from .booleans import to_shape, to_workplane


class Component(ABC):
    """
    Abstract Base Class for parametric CAD parts.
    
    Subclasses should define their parameters in __init__ / dataclass
    and implement the `_build()` method.
    """

    def __init__(self) -> None:
        self._cached_solid: cq.Workplane | None = None
        self.ports: dict[str, Any] = {}

    @abstractmethod
    def _build(self) -> cq.Workplane:
        """Internal construction method returning the solid as a cq.Workplane."""
        pass

    def build(self, force_rebuild: bool = False) -> cq.Workplane:
        """Returns the constructed solid, using a cached version if available."""
        if self._cached_solid is None or force_rebuild:
            self._cached_solid = self._build()
        return self._cached_solid

    def val(self) -> cq.Shape:
        """Returns the underlying OpenCASCADE Shape."""
        return self.build().val()

    def bounding_box(self) -> cq.BoundBox:
        """Returns the 3D bounding box of the component."""
        return self.val().BoundingBox()

    def add_port(
        self,
        name: str,
        origin: tuple | cq.Vector | cq.Location | cq.Plane = (0, 0, 0),
        normal: tuple | cq.Vector = (0, 0, 1),
        x_dir: tuple | cq.Vector | None = None,
    ) -> None:
        """Registers a named attachment port on the component."""
        from .ports import Port
        self.ports[name] = Port(name, origin=origin, normal=normal, x_dir=x_dir)

    def port(self, name: str):
        """Retrieves a named attachment port."""
        # Ensure model is built so ports are registered
        self.build()
        if name not in self.ports:
            raise KeyError(f"Port '{name}' not found on {self.__class__.__name__}. Available ports: {list(self.ports.keys())}")
        return self.ports[name]

    def mate(self, my_port: str, to: Component, to_port: str | Any | None = None) -> None:
        """
        Snaps this component onto another part so that `my_port` aligns with `to_port`.
        
        Usage:
            pillar_left, pillar_ports = pillar.mate('bottom', to=base, to_port='pillar_mount_left')
            cup_left, _ = bearing.mate('mount_face', to=pillar_ports['bearing_mount_inner'])
        """
        from .ports import attach
        self._cached_solid, self.ports = attach(self, child_port=my_port, to=to, to_port=to_port)

    def translate(self, vec: tuple | cq.Vector) -> cq.Workplane:
        """Returns the built solid translated by vec."""
        if isinstance(vec, tuple):
            vec = cq.Vector(*vec)
        return self.build().translate(vec)

    def rotate(self, axis_start: tuple, axis_end: tuple, angle: float) -> cq.Workplane:
        """Returns the built solid rotated around an axis."""
        return self.build().rotate(axis_start, axis_end, angle)

    def export(self, filepath: str, export_type: str = "STL") -> str:
        """
        Exports the built component to an STL or STEP file.
        Automatically creates parent directories if needed.
        """
        dir_name = os.path.dirname(filepath)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
            
        solid = self.build()
        if export_type.upper() == "STL":
            exporters.export(solid, filepath)
        elif export_type.upper() in ["STEP", "STP"]:
            exporters.export(solid.val(), filepath, exporters.ExportTypes.STEP)
        else:
            exporters.export(solid, filepath)
            
        return filepath
