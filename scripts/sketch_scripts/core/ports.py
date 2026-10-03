"""
core/ports.py — Semantic 3D Port & Mating Engine for CadQuery.

Eliminates manual coordinate math (translate, rotate) by allowing parts to define
named attachment points (Ports) and snap together automatically via coordinate transforms.
"""

from __future__ import annotations
from typing import Any
import cadquery as cq
from core import Component
from cadMath import *
from utils.debug_print import *

class Port:
    """
    A named 3D coordinate frame (Position + Orientation) representing a mating port.
    """
    origin_coordinates: cq.Vector
    normal_vector: cq.Vector
    
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
            # TODO: CHECK WHETHER NORMAL IS CORRECT (IMPORTANT!!)
            self.origin_coordinates = cq.Vector(origin.toTuple()[0])
            self.normal_vector = cq.Vector(origin.toTuple()[1])
            
        elif isinstance(origin, cq.Plane):
            self.location = origin.location
            # TODO: CHECK WHETHER NORMAL IS CORRECT (IMPORTANT!!)
            self.origin_coordinates = origin.origin
            self.normal_vector = origin.zDir
        else:
            orig_v = cq.Vector(*origin) if isinstance(origin, (tuple, list)) else origin
            norm_v = cq.Vector(*normal) if isinstance(normal, (tuple, list)) else normal
            norm_v = norm_v.normalized()
            
            # if x_dir is None:
            #     # TODO: Confirm this value for 0.9, if it should be 1.0 or 0.9, or some other threshold
            #     if abs(norm_v.dot(cq.Vector(0, 0, 1))) > 0.9:
            #         x_v = cq.Vector(1, 0, 0)
            #     else:
            #         x_v = cq.Vector(0, 0, 1).cross(norm_v).normalized()
            # else:
            #     x_v = cq.Vector(*x_dir) if isinstance(x_dir, (tuple, list)) else x_dir

            # plane = cq.Plane(origin=orig_v, xDir=x_v, normal=norm_v)
            plane = cq.Plane(origin=orig_v, normal=norm_v)
            self.location = plane.location
            self.origin_coordinates = orig_v
            self.normal_vector = norm_v

    @property
    def origin(self) -> cq.Vector:
        """Returns the 3D position vector of the port."""
        return self.location.toTuple()[0] # type: ignore

    def transform(self, parent_transform: cq.Location) -> Port:
        """Returns a new Port transformed by parent_transform."""
        return Port(self.name, origin=parent_transform * self.location)

    def invert_normal(self):
        print(f"Before inversion: {self} and normal: {self.normal_vector}")
        self.normal_vector = self.normal_vector * -1
        self.location = cq.Plane(origin=self.origin, normal=(self.normal_vector*-1)).location
        print(f"After inversion: {self} and normal: {self.normal_vector}")

    def __repr__(self) -> str:
        return f"<Port '{self.name}' at {self.location.toTuple()}>"


def attach(
    child: Component,
    child_port: str,
    to: Component,
    to_port: str,
    invert: bool = False
) -> tuple[cq.Workplane, dict[str, Port], dict[str, cq.Workplane]]:
    """
    Snaps `child` onto `to` so that `child_port` aligns with `to_port`.
    
    Returns:
        (transformed_child_workplane, transformed_child_ports_dict)
    """
    # 1. Resolve child port
    d_print(child.name, "gConn1", f"Moving {child.name}:{child_port} to {to.name}:{to_port} D1")
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

    if (invert):
        print(f"Inverting normal for {to.name}")
        print(f"Before inversion: {p_port}")
        print(f"Transform: {(p_port.location * c_port.location.inverse).toTuple()}")
        p_port.invert_normal()
        c_port.invert_normal()
        print(f"After inversion: {p_port}")
        print(f"Transform: {(p_port.location * c_port.location.inverse).toTuple()}")

    d_print(child.name, "gConn1", f"Moving {child.name}:{child_port} to {to.name}:{to_port} D2")
    d_print(child.name, "gConn1", f"Child workplanes: {child.workplanes.items()}, parent workplanes: {to.workplanes.items()}")
    # 3. Compute mating transformation: T = L_target * L_child^(-1)
    transform: cq.Location = p_port.location * c_port.location.inverse
    # 4. Transform geometry
    shape = child.build().val()
    # print(f"Transforming {child.name} from {child._cached_solid.plane.location.toTuple()} to: ")
    mated_wp = cq.Workplane(obj=shape.moved(transform)) # type: ignore
    # print(f"{p_port.location.toTuple()} ||||| Final transform: {transform.toTuple()} AND new_wp: {mated_wp.plane.location.toTuple()}")
    # 5. Transform child's remaining ports into world coordinates
    mated_ports: dict[str, Port] = {}
    for name, port_obj in child.ports.items():
        mated_ports[name] = port_obj.transform(transform)

    mated_wps: dict[str, cq.Workplane] = {}
    for name, wp_obj in child.workplanes.items():
        d_print(child.name, "gConn1", "TRNASFORMING!!")
        # print(f"({child.name}: {name}) wp_obj.plane.location: {wp_obj.plane.location.toTuple()} || p_port.location: {p_port.location.toTuple()} || c_port.location: {c_port.location.toTuple()}")
        d_print(child.name, "gConn1", f"Transforming ({child.name}: {name}) {wp_obj.plane.location.toTuple()} to {get_new_workplane(transform * wp_obj.plane.location).plane.location.toTuple()}")
        mated_wps[name] = get_new_workplane(transform * wp_obj.plane.location)
        # print(f"Done: {mated_wps[name].plane.location.toTuple()}")
    return mated_wp, mated_ports, mated_wps

