"""
projects/drone_gimbal.py — Parametric drone gimbal testing stand (Tag/Port-Based Assembly).

Features:
- ZERO manual translation/rotation coordinate math in assembly
- 100% semantic mating via named Ports (tags)
- 2D Sketch-based profiles
- Automated junction seam filleting
"""

from cq_server.ui import ui, show_object
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import cadquery as cq
from core import Component, show, fuse_all, find_junction_edges, attach
from sketches import rounded_rect
from features import BearingHousing


# ============================================================
# 1. PARAMETRIC COMPONENTS WITH SEMANTIC PORTS
# ============================================================

class DroneBase(Component):
  """Baseplate with slots and named mounting ports."""
  def __init__(self, span: float = 300.0, width: float = 100.0, thickness: float = 8.0) -> None:
    super().__init__()
    self.span = span
    self.width = width
    self.thickness = thickness

  def _build(self) -> cq.Workplane:
    sketch = rounded_rect(self.span + 60.0, self.width, radius=12.0).slot(60.0, 10.0, mode="s")
    base = cq.Workplane("XY").placeSketch(sketch).extrude(self.thickness)
    
    # Register semantic attachment ports on the top surface
    offset_x = self.span / 2.0
    # Left pillar port oriented inward (+X direction)
    self.add_port("pillar_mount_left",  origin=(-offset_x, 0, self.thickness), normal=(0, 0, 1), x_dir=( 1, 0, 0))
    # Right pillar port oriented inward (-X direction)
    self.add_port("pillar_mount_right", origin=( offset_x, 0, self.thickness), normal=(0, 0, 1), x_dir=(-1, 0, 0))
    self.add_port("center", origin=(0, 0, self.thickness), normal=(0, 0, 1))
    return base


class GimbalPillar(Component):
  """Vertical upright pillar with bearing pocket and mounting ports."""
  def __init__(self, height: float = 140.0, width: float = 35.0, thickness: float = 8.0) -> None:
    super().__init__()
    self.height = height
    self.width = width
    self.thickness = thickness

  def _build(self) -> cq.Workplane:
    bearing_center_z = self.height - 25.0
    
    # 2D Profile with top bearing pass-through cutout
    sketch = (
        rounded_rect(self.width, self.height, radius=6.0)
        .push([(0, self.height / 2.0 - 25.0)])
        .circle(22.0 / 2.0, mode="s")
    )
    
    # Extrude along X, standing upright in Z
    pillar = (
        cq.Workplane("YZ")
        .placeSketch(sketch)
        .extrude(self.thickness)
        .translate((-self.thickness / 2.0, 0, self.height / 2.0))
    )
    
    # Register semantic ports
    self.add_port("bottom_mount", origin=(0, 0, 0), normal=(0, 0, 1))
    self.add_port("bearing_mount_outer", origin=( self.thickness / 2.0, 0, bearing_center_z), normal=( 1, 0, 0))
    self.add_port("bearing_mount_inner", origin=(-self.thickness / 2.0, 0, bearing_center_z), normal=(-1, 0, 0))
    return pillar


# ============================================================
# 2. TAG / PORT-BASED ASSEMBLY (Zero manual coordinate math!)
# ============================================================

# Instantiate component building blocks
base = DroneBase(span=300.0, width=100.0, thickness=8.0)
pillar_l = GimbalPillar(height=140.0, width=35.0, thickness=8.0)
pillar_r = GimbalPillar(height=140.0, width=35.0, thickness=8.0)
bearing_cup_l = BearingHousing(bearing="608", wall_thickness=3.0, clearance=0.2)
bearing_cup_r = BearingHousing(bearing="608", wall_thickness=3.0, clearance=0.2)

# Snap pillars directly to the baseplate ports:
pillar_l.mate("bottom_mount", to=base, to_port="pillar_mount_left")
pillar_r.mate("bottom_mount", to=base, to_port="pillar_mount_right")

# Snap bearing cups directly to the pillar bearing ports:
bearing_cup_l.mate("mount_face", to=pillar_l, to_port="bearing_mount_inner")
bearing_cup_r.mate("mount_face", to=pillar_r, to_port="bearing_mount_inner")


# ============================================================
# 3. FUSION & SEAM FILLETING
# ============================================================

# Fuse all mated components into a single watertight solid
fused_stand = fuse_all(base, pillar_l, pillar_r, 
                       bearing_cup_l,
                         bearing_cup_r
                         )

# Smooth the structural joints where the pillars meet the base
fused_stand = find_junction_edges(fused_stand, base, pillar_l).fillet(3.0)
fused_stand = find_junction_edges(fused_stand, base, pillar_r).fillet(3.0)


# ============================================================
# 4. PREVIEW & EXPORT
# ============================================================

# Live preview in cq-server (Works without crashes!)
show(
    fused_stand,
    names=["drone_gimbal_stand"],
    colors=[(0.20, 0.60, 0.86)]
)

# Export watertight monolithic STL
os.makedirs("export", exist_ok=True)
cq.exporters.export(fused_stand, "export/drone_gimbal_stand.stl")
print("✅ Tag-based assembly compiled and exported successfully to export/drone_gimbal_stand.stl")
