
import cadquery as cq
from core import Component, fuse_all, show
from sketches import *
from features import BearingHousing
from hardware.standards import BEARINGS

class InnerGimbalConnector(Component):
  bearing = "608"
  bearing_tolerance = 0.3

  def __init__(self, thickness: float, height: float, connectorThickness: float, connectorDepth: float, bearing="608", name="gimbalConnector") -> None:
    super().__init__(name)
    self.length = thickness
    self.depth = connectorDepth
    self.connectorThickness = connectorThickness
    self.height = height
    self.bearing = bearing
    self._build()

  def _build(self) -> cq.Workplane:
    bearing_center_z = self.height/2
    outer_sketch = rounded_rect(self.length, self.length, 0)
    inner_sketch = (
      rounded_rect(self.connectorThickness, self.connectorThickness, 0)
    )
    connector = (
        cq.Workplane("XY")
        .placeSketch(outer_sketch)
        .extrude(self.height)
        .faces("<Z")
        .placeSketch(inner_sketch)
        .cutBlind(self.depth)
        .faces(">Z")
        .placeSketch(inner_sketch)
        .cutBlind(-self.depth)
        .faces(">X")
        .workplane(centerOption="CenterOfBoundBox")
        .circle((BEARINGS[self.bearing].outer_dia + self.bearing_tolerance) / 2.0)
        .cutThruAll()
    )
    self.add_port("bearing_mount_outer", origin=( self.length / 2.0, 0, bearing_center_z), normal=( 1, 0, 0))
    self.add_port("bearing_mount_inner", origin=( -self.length / 2.0, 0, bearing_center_z), normal=( -1, 0, 0))
    bearing_cup_r = BearingHousing(bearing=self.bearing, wall_thickness=3.0, clearance=0.2, name="__bearing1")
    bearing_cup_l = BearingHousing(bearing=self.bearing, wall_thickness=3.0, clearance=0.2, name="__bearing2")

    bearing_cup_r.mate("top_face", to=self, to_port="bearing_mount_outer")
    bearing_cup_l.mate("top_face", to=self, to_port="bearing_mount_inner")
    
    fused = fuse_all( bearing_cup_r,
                    bearing_cup_l,
                      connector
                    )
    self.add_port("upper_connector", origin=( 0, 0, (self.height) - self.depth), normal=( 0, 0, -1))
    self.add_port("lower_connector", origin=( 0, 0, self.depth), normal=( 0, 0, 1))
    return fused


class GimbalQuarterCurve(Component):
  connector_tolerance = 0.4

  def __init__(self, thickness: float, radius: float, connectorDepth: float, connectorThickness: float, arcDegrees: float = 90, name="gimbalQuarterCurve") -> None:
    super().__init__(name)
    self.thickness = thickness
    self.radius = radius
    self.arcDegrees = arcDegrees
    self.connector_depth = connectorDepth
    self.connector_thickness = connectorThickness
    self._build()

  def _build(self) -> cq.Workplane:
    curved_sketch = rounded_rect(self.thickness, self.thickness, 0)
    connector_sketch = (
      rounded_rect(self.connector_thickness - self.connector_tolerance, self.connector_thickness - self.connector_tolerance, 0)
    )
    gimbal_hand = (
        cq.Workplane("XY")
        .placeSketch(curved_sketch)
        .revolve(self.arcDegrees, cq.Vector(self.radius, 0, 0), cq.Vector(self.radius, 1, 0))
    )
    gimbal_hand = (
        gimbal_hand.faces(">X").workplane(centerOption="CenterOfMass")
        .placeSketch(connector_sketch)
        .extrude(self.connector_depth)
    )
    gimbal_hand = (
            gimbal_hand.faces("<Z").workplane(centerOption="CenterOfMass")
            .placeSketch(connector_sketch)
            .extrude(self.connector_depth)
        )

    right_face_origin = gimbal_hand.faces(">X").workplane(centerOption="CenterOfMass").plane.location.toTuple()[0]
    self.add_port("right_face", origin=right_face_origin, normal=(1, 0, 0))
    self.add_port("bottom_face", origin=(0, -self.connector_depth, 0), normal=(0, 0, -1))
    return gimbal_hand

