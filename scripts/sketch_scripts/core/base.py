"""
core/base.py — Base class for all parametric CAD components.

A Component has:
- local geometry, built once by `_build()` and cached (`build()`);
- named ports in the same local coordinates, registered with `add_port()` inside `_build()`;
- one placement, `location` (a cq.Location), set directly or by `mate()`.

Nothing is ever moved in place. World geometry and world ports are computed on demand: `world()`, `port(name)`.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
import os
import cadquery as cq
from cadquery import exporters
from .booleans import to_workplane
from .ports import Port, attach


class Component(ABC):
    """
    Abstract base class for parametric parts.

    Subclasses set their parameters in __init__ and implement `_build()`, which returns the solid in local
    coordinates and may call `add_port()`. `_build()` may also return (solid, {name: Port}). Call `self.build()`
    (never `self._build()`) from __init__ if the part should be built eagerly.
    """

    def __init__(self, name: str = "") -> None:
        self.name = name
        self.location = cq.Location()
        self._solid: cq.Workplane | None = None
        self._ports: dict[str, Port] = {}
        self._building = False

    @abstractmethod
    def _build(self) -> cq.Workplane | tuple[cq.Workplane, dict[str, Port]]:
        """Construct the solid in local coordinates."""

    # ── Geometry ──
    def build(self, force_rebuild: bool = False) -> cq.Workplane:
        """The solid in LOCAL coordinates, cached. A rebuild re-registers the ports, so solid and ports always agree."""
        if self._solid is None or force_rebuild:
            self._ports = {}
            self._building = True
            try:
                result = self._build()
            finally:
                self._building = False
            if isinstance(result, tuple):
                result, ports = result
                self._ports.update(ports)
            self._solid = to_workplane(result)
        return self._solid

    def world(self) -> cq.Workplane:
        """The solid placed at `location`."""
        return cq.Workplane(obj=self.build().val().moved(self.location))

    def val(self) -> cq.Shape:
        """The placed OpenCASCADE shape."""
        return self.world().val()

    def bounding_box(self) -> cq.BoundBox:
        return self.val().BoundingBox()

    # ── Ports ──
    def add_port(
        self,
        name: str,
        origin: cq.Plane | cq.Location | tuple | cq.Vector = (0, 0, 0),
        normal: tuple | cq.Vector = (0, 0, 1),
        x_dir: tuple | cq.Vector | None = None,
    ) -> Port:
        """Registers a named port in local coordinates (call inside `_build`)."""
        port = Port(name, origin=origin, normal=normal, x_dir=x_dir)
        self._ports[name] = port
        return port

    def add_ports_from_planes(self, planes: dict, prefix: str = "") -> None:
        """Registers every cq.Plane in a nested dict as a port named by its key path, e.g. 'droneStandSlots.<X.floor'."""
        for key, value in planes.items():
            name = f"{prefix}.{key}" if prefix else str(key)
            if isinstance(value, dict):
                self.add_ports_from_planes(value, name)
            else:
                self.add_port(name, origin=value)

    def _ensure_built(self) -> None:
        if self._solid is None and not self._building:
            self.build()

    def local_port(self, name: str) -> Port:
        """A port in local coordinates."""
        self._ensure_built()
        if name not in self._ports:
            raise KeyError(f"Port '{name}' not found on {self.__class__.__name__}. Available ports: {list(self._ports)}")
        return self._ports[name]

    def port(self, name: str) -> Port:
        """A port in world coordinates (placed at `location`)."""
        return self.local_port(name).moved(self.location)

    @property
    def ports(self) -> dict[str, Port]:
        """All ports in world coordinates."""
        self._ensure_built()
        return {name: p.moved(self.location) for name, p in self._ports.items()}

    def workplane(self, port_name: str) -> cq.Workplane:
        """A fresh workplane on a world port (for new geometry)."""
        return self.port(port_name).workplane()

    # ── Placement ──
    def mate(self, my_port: str, to, to_port: str | None = None, invert: bool = False) -> Component:
        """
        Places this component so `my_port` coincides with the target frame (see core.ports.attach).

        Usage:
            pillar.mate("bottom_mount", to=base, to_port="pillar_mount_left")
            cup.mate("top_face", to=self.local_port("bearing_mount_outer"))     # inside a parent's _build
        """
        attach(self, my_port, to, to_port, invert)
        return self

    def translate(self, vec: tuple | cq.Vector) -> Component:
        """Moves the placement by vec (world axes)."""
        self.location = cq.Location(cq.Vector(vec)) * self.location
        return self

    def rotate(self, axis_start: tuple, axis_end: tuple, angle: float) -> Component:
        """Rotates the placement about a world axis through axis_start and axis_end, angle in degrees."""
        start, end = cq.Vector(axis_start), cq.Vector(axis_end)
        about = cq.Location(start) * cq.Location(cq.Vector(0, 0, 0), end - start, angle) * cq.Location(-start)
        self.location = about * self.location
        return self

    # ── Export ──
    def export(self, filepath: str, export_type: str = "STL") -> str:
        """Exports the placed component to STL or STEP, creating parent directories."""
        dir_name = os.path.dirname(filepath)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        solid = self.world()
        if export_type.upper() in ("STEP", "STP"):
            exporters.export(solid, filepath, exporters.ExportTypes.STEP)
        else:
            exporters.export(solid, filepath)
        return filepath
