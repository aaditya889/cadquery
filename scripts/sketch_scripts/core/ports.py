"""
core/ports.py — Semantic 3D Port & Mating Engine for CadQuery.

Eliminates manual coordinate math (translate, rotate) by allowing parts to define
named attachment points (Ports) and snap together automatically via coordinate transforms.
"""

from __future__ import annotations
from typing import Any
import cadquery as cq


class Port:
    """
    A named 3D coordinate frame (Position + Orientation) representing a mating port.
    """
    def __init__(
        self,
        name: str,
        origin: tuple | cq.Vector | cq.Location | cq.Plane = (0, 0, 0),
        normal: tuple | cq.Vector = (0, 0, 1),
        x_dir: tuple | cq.Vector | None = None,
    ) -> None:
        self.name = name
        if isinstance(origin, cq.Location):
            self.location = origin
        elif isinstance(origin, cq.Plane):
            self.location = origin.location
        else:
            orig_v = cq.Vector(*origin) if isinstance(origin, (tuple, list)) else origin
            norm_v = cq.Vector(*normal) if isinstance(normal, (tuple, list)) else normal
            norm_v = norm_v.normalized()
            
            if x_dir is None:
                # TODO: Confirm this value for 0.9, if it should be 1.0 or 0.9, or some other threshold
                if abs(norm_v.dot(cq.Vector(0, 0, 1))) > 0.9:
                    x_v = cq.Vector(1, 0, 0)
                else:
                    x_v = cq.Vector(0, 0, 1).cross(norm_v).normalized()
            else:
                x_v = cq.Vector(*x_dir) if isinstance(x_dir, (tuple, list)) else x_dir

            plane = cq.Plane(origin=orig_v, xDir=x_v, normal=norm_v)
            self.location = plane.location

    @property
    def origin(self) -> cq.Vector:
        """Returns the 3D position vector of the port."""
        return self.location.toTuple()[0]

    def transform(self, parent_transform: cq.Location) -> Port:
        """Returns a new Port transformed by parent_transform."""
        return Port(self.name, origin=parent_transform * self.location)

    def __repr__(self) -> str:
        return f"<Port '{self.name}' at {self.location}>"


def attach(
    child,
    child_port: Port | str,
    to: Any,
    to_port: Port | str | None = None,
) -> tuple[cq.Workplane, dict[str, Port]]:
    """
    Snaps `child` onto `to` so that `child_port` aligns with `to_port`.
    
    Returns:
        (transformed_child_workplane, transformed_child_ports_dict)
    """
    # 1. Resolve child port
        
    if isinstance(child_port, str):
        if hasattr(child, "port"):
            c_port = child.port(child_port)
        elif isinstance(child, dict) and child_port in child:
            c_port = child[child_port]
        else:
            raise ValueError(f"Child {child} has no port '{child_port}'.")
    else:
        c_port = child_port

    # 2. Resolve target parent port
    if to_port is None and isinstance(to, Port):
        p_port = to
    elif isinstance(to_port, Port):
        p_port = to_port
    elif isinstance(to_port, str):
        if hasattr(to, "port"):
            p_port = to.port(to_port)
        elif isinstance(to, dict) and to_port in to:
            p_port = to[to_port]
        else:
            raise ValueError(f"Target parent {to} has no port '{to_port}'.")
    else:
        p_port = to_port

    # 3. Compute mating transformation: T = L_target * L_child^(-1)
    transform = p_port.location * c_port.location.inverse
    
    # 4. Transform geometry
    shape = child.val() if hasattr(child, "val") else (child.build().val() if hasattr(child, "build") else child)
    mated_wp = cq.Workplane(obj=shape.moved(transform))

    # 5. Transform child's remaining ports into world coordinates
    mated_ports: dict[str, Port] = {}
    if hasattr(child, "ports"):
        for name, port_obj in child.ports.items():
            mated_ports[name] = port_obj.transform(transform)

    return mated_wp, mated_ports
