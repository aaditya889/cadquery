"""
features/plates.py — Parametric baseplates, mounting brackets, and structural panels.
"""

from __future__ import annotations
import cadquery as cq
from core.base import Component
from sketches.profiles import rounded_rect


class MountingPlate(Component):
    """
    Parametric rectangular mounting plate with rounded corners, perimeter grid holes,
    and center cutouts.
    """
    def __init__(
        self,
        length: float = 120.0,
        width: float = 80.0,
        thickness: float = 4.0,
        corner_radius: float = 6.0,
        center_hole_dia: float = 0.0,
        corner_holes_dia: float = 3.4,
        corner_holes_inset: float = 8.0,
    ) -> None:
        super().__init__()
        self.length = length
        self.width = width
        self.thickness = thickness
        self.corner_radius = corner_radius
        self.center_hole_dia = center_hole_dia
        self.corner_holes_dia = corner_holes_dia
        self.corner_holes_inset = corner_holes_inset

    def _build(self) -> cq.Workplane:
        # Build base from 2D Sketch
        base_sketch = rounded_rect(self.length, self.width, self.corner_radius)
        
        plate = (
            cq.Workplane("XY")
            .placeSketch(base_sketch)
            .extrude(self.thickness)
        )
        
        # Center hole if requested
        if self.center_hole_dia > 0:
            plate = plate.faces(">Z").workplane().hole(self.center_hole_dia)
            
        # Corner mounting holes
        if self.corner_holes_dia > 0 and self.corner_holes_inset > 0:
            hx = self.length / 2.0 - self.corner_holes_inset
            hy = self.width / 2.0 - self.corner_holes_inset
            hole_pts = [(-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy)]
            plate = (
                plate.faces(">Z")
                .workplane()
                .pushPoints(hole_pts)
                .hole(self.corner_holes_dia)
            )
            
        # Register standard ports
        self.register_port("center", cq.Vector(0, 0, self.thickness / 2.0))
        self.register_port("top_face", cq.Vector(0, 0, self.thickness))
        self.register_port("bottom_face", cq.Vector(0, 0, 0))
        
        return plate
