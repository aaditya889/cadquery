"""
features/mounts.py — Parametric bearing housings, screw bosses, and standoffs.
"""

from __future__ import annotations
import cadquery as cq
from core.base import Component
from hardware.standards import get_bearing, get_fastener


class BearingHousing(Component):
    """
    Parametric ball bearing housing with optional retaining lip and through-shaft hole.
    """
    def __init__(
        self,
        bearing: str = "608",
        wall_thickness: float = 3.0,
        clearance: float = 0.2,
        lip_thickness: float = 1.5,
        lip_inset: float = 1.0,
    ) -> None:
        super().__init__("bearingHouse")
        spec = get_bearing(bearing)
        self.inner_dia = spec.inner_dia
        self.bearing_dia = spec.outer_dia
        self.depth = spec.thickness
        self.wall_thickness = wall_thickness
        self.clearance = clearance
        self.lip_thickness = lip_thickness
        self.lip_inset = lip_inset
        self.build()

    @property
    def outer_dia(self) -> float:
        return self.bearing_dia + 2 * (self.wall_thickness + self.clearance)

    @property
    def total_height(self) -> float:
        return self.depth + self.lip_thickness

    def _build(self) -> cq.Workplane:
        bore_dia = self.bearing_dia + 2 * self.clearance
        shaft_through_dia = self.inner_dia + 2 * self.lip_inset

        housing = (
            cq.Workplane("XY")
            .cylinder(self.total_height, self.outer_dia / 2.0)
            # Bearing cup pocket
            .faces(">Z")
            .workplane()
            .hole(bore_dia, self.depth)
            # Shaft pass-through hole in the retaining lip
            .faces(">Z")
            .workplane()
            .hole(shaft_through_dia)
        )
        
        # Register attachtop_facement ports
        self.add_port("center", origin=(0, 0, 0), normal=(0, 0, 1))
        self.add_port("top_face", origin=(0, 0, self.total_height / 2.0), normal=(0, 0, 1))
        self.add_port("mount_face", origin=(0, 0, -self.total_height / 2.0), normal=(0, 0, -1))
        self.add_port("shaft_axis", origin=(0, 0, 0), normal=(0, 0, 1))
        
        return housing


class ScrewBoss(Component):
    """
    Parametric mounting boss for direct tapping, clearance pass-through, or heat-set inserts.
    """
    def __init__(
        self,
        fastener: str = "M3",
        height: float = 10.0,
        boss_type: str = "heat_set",  # 'heat_set', 'tap', 'clearance'
        wall_thickness: float = 2.5,
    ) -> None:
        super().__init__()
        self.spec = get_fastener(fastener)
        self.height = height
        self.boss_type = boss_type
        self.wall_thickness = wall_thickness

    @property
    def hole_dia(self) -> float:
        if self.boss_type == "heat_set":
            return self.spec.insert_hole
        elif self.boss_type == "tap":
            return self.spec.tap_hole
        else:
            return self.spec.clearance_hole

    @property
    def hole_depth(self) -> float:
        if self.boss_type == "heat_set":
            return min(self.height, self.spec.insert_depth)
        return self.height

    @property
    def outer_dia(self) -> float:
        return self.hole_dia + 2 * self.wall_thickness

    def _build(self) -> cq.Workplane:
        boss = (
            cq.Workplane("XY")
            .cylinder(self.height, self.outer_dia / 2.0)
            .faces(">Z")
            .workplane()
            .hole(self.hole_dia, self.hole_depth)
        )
        
        self.add_port("top_face", origin=(0, 0, self.height / 2.0), normal=(0, 0, 1))
        self.add_port("mount_face", origin=(0, 0, -self.height / 2.0), normal=(0, 0, -1))
        return boss
