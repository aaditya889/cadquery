"""
core/ports.py — Named attachment frames (Ports) and mating.

A Port is an immutable frame (origin, in-plane x direction, normal) stored as one cq.Location, in its component's
LOCAL coordinates. Mating never moves geometry or ports: it only sets the child component's `location`.
World positions are computed when asked for (Component.world(), Component.port()).
"""

from __future__ import annotations
from typing import TYPE_CHECKING
import cadquery as cq
from OCP.gp import gp_Pnt, gp_Dir

if TYPE_CHECKING:
    from .base import Component

# 180° about the port's own x axis: normal (z) and y reversed, x kept. Used for face-to-face mates.
FLIP = cq.Location(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 180)


def plane_from_location(loc: cq.Location) -> cq.Plane:
    """Location → Plane, keeping the in-plane x direction (no Euler-angle round trip)."""
    t = loc.wrapped.Transformation()
    o = gp_Pnt(0, 0, 0).Transformed(t)
    x = gp_Dir(1, 0, 0).Transformed(t)
    z = gp_Dir(0, 0, 1).Transformed(t)
    return cq.Plane(origin=(o.X(), o.Y(), o.Z()), xDir=(x.X(), x.Y(), x.Z()), normal=(z.X(), z.Y(), z.Z()))


class Port:
    """
    A named frame. Build it from a cq.Location, a cq.Plane, or an origin + normal (+ optional x_dir).
    Without x_dir, CadQuery's default x direction for that normal is used (deterministic).
    """
    __slots__ = ("name", "loc")

    def __init__(
        self,
        name: str,
        origin: tuple | cq.Vector | cq.Location | cq.Plane = (0, 0, 0),
        normal: tuple | cq.Vector = (0, 0, 1),
        x_dir: tuple | cq.Vector | None = None,
    ) -> None:
        self.name = name
        if isinstance(origin, cq.Location):
            self.loc = origin
        elif isinstance(origin, cq.Plane):
            self.loc = cq.Location(origin)
        else:
            self.loc = cq.Location(cq.Plane(origin=cq.Vector(origin), xDir=None if x_dir is None else cq.Vector(x_dir),
                                            normal=cq.Vector(normal)))

    # ── Derived views (never stored) ──
    @property
    def location(self) -> cq.Location:
        return self.loc

    @property
    def plane(self) -> cq.Plane:
        return plane_from_location(self.loc)

    @property
    def origin(self) -> cq.Vector:
        return self.plane.origin

    @property
    def normal_vector(self) -> cq.Vector:
        return self.plane.zDir

    @property
    def x_dir(self) -> cq.Vector:
        return self.plane.xDir

    def moved(self, by: cq.Location) -> Port:
        """A new Port expressed in another frame: by * self."""
        return Port(self.name, by * self.loc)

    def workplane(self) -> cq.Workplane:
        """A fresh workplane on this frame (for new geometry; to edit a solid use solid.copyWorkplane(...))."""
        return cq.Workplane(self.plane)

    def __repr__(self) -> str:
        o, z = self.origin, self.normal_vector
        return f"<Port '{self.name}' origin=({o.x:.3f}, {o.y:.3f}, {o.z:.3f}) normal=({z.x:.3f}, {z.y:.3f}, {z.z:.3f})>"


def _frame(target, port_name: str | None) -> cq.Location:
    """Resolve a mating target to a frame: a Component + port name (world), a Port, a Location or a Plane (as given)."""
    if isinstance(target, cq.Location):
        return target
    if isinstance(target, cq.Plane):
        return cq.Location(target)
    if isinstance(target, Port):
        return target.loc
    if port_name is None:
        raise ValueError(f"Mating to {target!r} needs a port name.")
    return target.location * target.local_port(port_name).loc


def attach(child: Component, child_port: str, to, to_port: str | None = None, invert: bool = False) -> None:
    """
    Places `child` so that its port `child_port` coincides with the target frame.

    `to` is a Component (with `to_port`, resolved in world coordinates), or a Port / cq.Location / cq.Plane used as
    given. Inside a parent's `_build`, pass the parent's LOCAL port (self.local_port(...)) so the child is placed in
    the parent's own frame. `invert=True` mates face to face: the child's frame is turned 180° about its x axis, so
    the normals oppose. Only `child.location` changes; nothing is mutated, so repeating a mate is harmless.
    """
    target = _frame(to, to_port)
    flip = FLIP if invert else cq.Location()
    child.location = target * flip * child.local_port(child_port).loc.inverse
