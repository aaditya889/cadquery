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
import numpy as np


class Port:
    """
    A named 3D coordinate frame (Position + Orientation) representing a mating port.
    """
    origin_coordinates: cq.Vector
    normal_vector: cq.Vector
    plane: cq.Plane
    
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
            rotation_vector = origin.toTuple()[1]
            rot_x = np.deg2rad(rotation_vector[0])
            rot_y = np.deg2rad(rotation_vector[1])
            rot_z = np.deg2rad(rotation_vector[2])
            self.normal_vector = transform_vector(rot_x, rot_y, rot_z, np.array([[0, 0, 1]]).T)
            self.plane = cq.Plane(origin=self.origin_coordinates, normal=self.normal_vector)
            
        elif isinstance(origin, cq.Plane):
            self.location = origin.location
            # TODO: CHECK WHETHER NORMAL IS CORRECT (IMPORTANT!!)
            self.origin_coordinates = origin.origin
            self.normal_vector = origin.zDir
            self.plane = origin
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
            self.plane = plane
            self.location = plane.location
            self.origin_coordinates = orig_v
            self.normal_vector = norm_v

    @property
    def origin(self) -> cq.Vector:
        """Returns the 3D position vector of the port."""
        return self.location.toTuple()[0] # type: ignore

    def transform(self, parent_transform: cq.Location) -> None:
        """Returns a new Port transformed by parent_transform."""
        new_location = parent_transform * self.location
        self.location = new_location
        self.origin_coordinates = cq.Vector(new_location.toTuple()[0])
        rotation_vector = new_location.toTuple()[1]
        rot_x = np.deg2rad(rotation_vector[0])
        rot_y = np.deg2rad(rotation_vector[1])
        rot_z = np.deg2rad(rotation_vector[2])
        self.normal_vector = transform_vector(rot_x, rot_y, rot_z, np.array([[0, 0, 1]]).T)
        self.plane = cq.Plane(origin=self.origin_coordinates, normal=self.normal_vector)

    def invert_normal(self):
        self.normal_vector = self.normal_vector * -1
        self.location = cq.Plane(origin=self.origin, normal=(self.normal_vector)).location

    def __repr__(self) -> str:
        return f"<Port '{self.name}' at {self.location.toTuple()}>"


def attach(
    child: Component,
    child_port: str,
    to: Component,
    to_port: str,
    invert: bool = False
) -> None:
    """
    Snaps `child` onto `to` so that `child_port` aligns with `to_port`.
    
    Returns:
        (transformed_child_workplane, transformed_child_ports_dict)
    """
    # 1. Resolve child port
    # d_print(child.name, "gConn1", f"Moving {child.name}:{child_port} to {to.name}:{to_port} D1")
    c_port: Port
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

    # d_print(child.name, "gConn1", f"Transforming:: p_port.location: {p_port.location.toTuple()} c_port.location: {c_port.location.toTuple()}, p_port.normal: {p_port.normal_vector}, c_port.normal {c_port.normal_vector}")
    # d_print(child.name, "gConn1", f"Transforming ({child_port}):: p_port.location: {p_port.location.toTuple()} c_port.location: {c_port.location.toTuple()}, c_port.location.inverse: {c_port.location.inverse.toTuple()}, p_port.normal: {p_port.normal_vector}")
    shape = child.build().val()
    d_print(child.name, "quarterConn2", f"Before Transforming ({child_port}):: c_port_x_dir: {child._cached_solid.plane.xDir}, c_port_z_dir: {child._cached_solid.plane.zDir}, c_port_y_dir: {child._cached_solid.plane.yDir}")
    if (invert):
        pass
        p_port.invert_normal()
        # d_print(child.name, "gConn1", f"After inversion of parent ({child_port}):: p_port.location: {p_port.location.toTuple()}, p_port.normal: {p_port.normal_vector}")
        # c_port.invert_normal()

    # d_print(child.name, "gConn1", f"Moving {child.name}:{child_port} to {to.name}:{to_port} D2")
    # d_print(child.name, "gConn1", f"Child workplanes: {child.workplanes.items()}, parent workplanes: {to.workplanes.items()}")
    # 3. Compute mating transformation: T = L_target * L_child^(-1)
    transform: cq.Location = p_port.location * c_port.location.inverse
    # d_print(child.name, "gConn1", f"{c_port}")
    # d_print(child.name, "gConn1", f"{child}")
    # 4. Transform geometry
    
    # child.build()
    # child._cached_solid.transformed(transform.toTuple()[1], transform.toTuple()[0]) # type: ignore

    child._cached_solid = cq.Workplane(obj=shape.moved(transform)) # type: ignore

    # 5. Transform child's remaining ports into world coordinates
    # mated_ports: dict[str, Port] = {}
    for name, port_obj in child.ports.items():
        port_obj.transform(transform)

    d_print(child.name, "quarterConn2", f"Transforming ({child_port}):: c_port_x_dir: {child._cached_solid.plane.xDir}, c_port_z_dir: {child._cached_solid.plane.zDir}, c_port_y_dir: {child._cached_solid.plane.yDir}")

    mated_wps: dict[str, cq.Workplane] = {}
    for name, wp_obj in child.workplanes.items():
        # d_print(child.name, "gConn1", "TRNASFORMING!!")
        # d_print(child.name, "gConn1", f"Transforming ({child.name}: {name}) {wp_obj.plane.location.toTuple()} to {get_new_workplane(transform * wp_obj.plane.location).plane.location.toTuple()}")
        # mated_wps[name] = get_new_workplane(transform * wp_obj.plane.location)
        pass
    
    c_port = child.port(child_port)
    # d_print(child.name, "gConn1", f"{c_port}")
    # d_print(child.name, "gConn1", f"{child}")
    # d_print(child.name, "gConn1", f"After ({child.name}: {child_port}):: p_port.location: {p_port.location.toTuple()} c_port.location: {c_port.location.toTuple()}, p_port.normal: {p_port.normal_vector}, c_port.normal {c_port.normal_vector}")

