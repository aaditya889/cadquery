
import cadquery as cq
from core import Component, fuse_all, show
from sketches import *
from features import BearingHousing
from hardware.standards import BEARINGS

class InnerGimbalConnector(Component):
  bearing = "608"
  def __init__(self, length: float = 140.0, width: float = 35.0, height: float = 8.0, bearing="608") -> None:
    super().__init__("gimbalConnector")
    self.length = length
    self.width = width
    self.height = height
    self.bearing = bearing
    self._build()

  def _build(self) -> cq.Workplane:
    bearing_center_z = self.length
    depth = 30
    sketch1 = rounded_rect(self.length, self.length, 0)
    sketch = (
      rounded_rect(self.length - 10, self.length - 10, 0)
    )
    pillar = (
        cq.Workplane("XY")
        .placeSketch(sketch1)
        .extrude(self.height)
        .faces("<Z")
        .placeSketch(sketch)
        .cutBlind(depth)
        .faces(">Z")
        .placeSketch(sketch)
        .cutBlind(-depth)
        .faces(">X")
        .workplane(centerOption="CenterOfBoundBox")
        .circle(BEARINGS[self.bearing].outer_dia / 2.0)
        .cutThruAll()
    )
    self.add_port("bearing_mount_outer", origin=( self.length / 2.0, 0, bearing_center_z), normal=( 1, 0, 0))
    self.add_port("bearing_mount_inner", origin=( -self.length / 2.0, 0, bearing_center_z), normal=( -1, 0, 0))
    # self.sketch_obj = pillar
    bearing_cup_r = BearingHousing(bearing="608", wall_thickness=3.0, clearance=0.2)
    bearing_cup_l = BearingHousing(bearing="608", wall_thickness=3.0, clearance=0.2)

    bearing_cup_r.mate("top_face", to=self, to_port="bearing_mount_outer")
    bearing_cup_l.mate("top_face", to=self, to_port="bearing_mount_inner")
    
    fused = fuse_all( bearing_cup_r,
                    bearing_cup_l,
                      pillar
                    )
    self.add_port("upper_connector", origin=( 0, 0, (self.height) - depth), normal=( 0, 0, -1))
    self.add_port("lower_connector", origin=( 0, 0, depth), normal=( 0, 0, 1))
    # show(fused, pillar, bearing_cup_l, bearing_cup_r)
    # show(pillar, bearing_cup_r, bearing_cup_l)
    return fused

