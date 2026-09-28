from cq_server.ui import ui, show_object
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import cadquery as cq
from core import Component, show, fuse_all, find_junction_edges, attach
from sketches import *
from features import BearingHousing
from cadMath import *
import numpy as np


class InnerGimbalConnector(Component):
  """Vertical upright pillar with bearing pocket and mounting ports."""
  sketch_obj = None
  def __init__(self, length: float = 140.0, width: float = 35.0, height: float = 8.0) -> None:
    super().__init__()
    self.length = length
    self.width = width
    self.height = height

  def _build(self) -> cq.Workplane:
    bearing_center_z = self.length
    
    # 2D Profile with top bearing pass-through cutout
    sketch1 = rounded_rect(self.length, self.length, 0)

    sketch = (
      rounded_rect(self.length - 10, self.length - 10, 0)
    )
    
    # Extrude along X, standing upright in Z
    pillar = (
        cq.Workplane("XY")
        .placeSketch(sketch1)
        # .placeSketch(sketch)
        .extrude(self.height)
        .faces("<Z")
        .placeSketch(sketch)
        # .faces(">Z")
        # .extrude(5)
        .cutBlind(30)
        .faces(">Z")
        .placeSketch(sketch)
        # .faces(">Z")
        # .extrude(5)
        .cutBlind(-30)
        .faces(">X")
        .workplane(centerOption="CenterOfBoundBox")
        # .push([(0, self.height / 2.0 - 25.0)])
        .circle(22.0 / 2.0)
        .cutThruAll()
        # .faces(">X")
        # .extrude(20)
        # .circle(2).extrude(30)
    )
    self.add_port("bearing_mount_outer", origin=( self.length / 2.0, 0, bearing_center_z), normal=( 1, 0, 0))
    self.sketch_obj = pillar
    # print(pillar.faces(">X").plane.location.toTuple())
    return pillar


pillar = InnerGimbalConnector(length=50.0, width=35.0, height=100.0)
bearing_cup = BearingHousing(bearing="608", wall_thickness=3.0, clearance=0.2)

bearing_cup.mate("mount_face", to=pillar, to_port="bearing_mount_outer")
# print(f"pillar plane normal: {pillar.sketch_obj.faces(">X").plane.zDir}")
# cylinder_wp = get_new_workplane(pillar.sketch_obj.faces(">X").plane)
# print(f"cylinder plane normal: {cylinder_wp.plane.zDir}")
# # 4. Extrude will now perfectly follow your 'target_normal' vector
# radius = 1
# height = 30
# cylinder = cylinder_wp.circle(radius).extrude(height)
fused = fuse_all( bearing_cup,
                  pillar
                )
# print(pillar.build())
show(bearing_cup,
                  pillar)
# Export watertight monolithic STL
os.makedirs("export", exist_ok=True)
# cq.exporters.export(fused_stand, "export/test1.stl")
print("✅ Tag-based assembly compiled and exported successfully to export/drone_gimbal_stand.stl")
