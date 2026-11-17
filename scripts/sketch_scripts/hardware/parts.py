
import cadquery as cq
from core import Component, fuse_all, show, place_on
from sketches import *
from features import BearingHousing
from hardware.standards import BEARINGS
from operations.slots import *

class InnerGimbalConnector(Component):
  bearing = "608"
  bearing_tolerance = 0.2

  def __init__(self, length: float, width: float, height: float, connectorLength: float, connectorWidth: float, connectorDepth: float, bearing="608", name="gimbalConnector") -> None:
    super().__init__(name)
    self.length = length
    self.width = width
    self.depth = connectorDepth
    self.connectorLength = connectorLength
    self.connectorWidth = connectorWidth
    self.height = height
    self.bearing = bearing
    self.build()

  def _build(self) -> cq.Workplane:
    bearing_center_z = self.height/2
    outer_sketch = rounded_rect(self.length, self.width, 0)
    inner_sketch = (
      rounded_rect(self.connectorLength, self.connectorWidth, 0)
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
        .circle((BEARINGS[self.bearing].outer_dia) / 2.0)
        .cutThruAll()
    )
    self.add_port("bearing_mount_outer", origin=( self.length / 2.0, 0, bearing_center_z), normal=( 1, 0, 0))
    self.add_port("bearing_mount_inner", origin=( -self.length / 2.0, 0, bearing_center_z), normal=( -1, 0, 0))
    bearing_cup_r = BearingHousing(bearing=self.bearing, wall_thickness=3.0, clearance=0.2, name="__bearing1")
    bearing_cup_l = BearingHousing(bearing=self.bearing, wall_thickness=3.0, clearance=0.2, name="__bearing2")

    bearing_cup_r.mate("top_face", to=self.local_port("bearing_mount_outer"))
    bearing_cup_l.mate("top_face", to=self.local_port("bearing_mount_inner"))
    
    fused = fuse_all( bearing_cup_r,
                    bearing_cup_l,
                      connector
                    )
    self.add_port("upper_connector", origin=( 0, 0, (self.height) - self.depth), normal=( 0, 0, 1))
    self.add_port("lower_connector", origin=( 0, 0, self.depth), normal=( 0, 0, -1))
    return fused


class GimbalQuarterCurve(Component):
  connector_tolerance = 0.2

  def __init__(self, length: float, width: float, radius: float, connectorDepth: float, connectorLength: float, connectorWidth: float, arcDegrees: float = 90, name="gimbalQuarterCurve") -> None:
    super().__init__(name)
    self.length = length
    self.width = width
    self.radius = radius
    self.arcDegrees = arcDegrees
    self.connector_depth = connectorDepth
    self.connectorLength = connectorLength
    self.connectorWidth = connectorWidth
    self.build()

  def _build(self) -> cq.Workplane:
    curved_sketch = rounded_rect(self.length, self.width, 0)
    lower_connector_sketch = (
      rounded_rect(self.connectorLength - self.connector_tolerance, self.connectorWidth - self.connector_tolerance, 0)
    )
    upper_connector_sketch = (
          rounded_rect(self.connectorWidth - self.connector_tolerance, self.connectorLength - self.connector_tolerance, 0)
        )
    gimbal_hand = (
        cq.Workplane("XY")
        .placeSketch(curved_sketch)
        .revolve(self.arcDegrees, cq.Vector(self.radius, 0, 0), cq.Vector(self.radius, 1, 0))
    )
    gimbal_hand = (
        gimbal_hand.faces(">X").workplane(centerOption="CenterOfMass")
        .placeSketch(upper_connector_sketch)
        .extrude(self.connector_depth)
    )

    gimbal_hand = (
            gimbal_hand.faces("<Z").workplane(centerOption="CenterOfMass")
            .placeSketch(lower_connector_sketch)
            .extrude(self.connector_depth)
        )

    right_face_origin = gimbal_hand.faces(">X").workplane(centerOption="CenterOfMass").plane.location.toTuple()[0]
    self.add_port("right_face", origin=right_face_origin, normal=(1, 0, 0))
    self.add_port("bottom_face", origin=(0, -self.connector_depth, 0), normal=(0, 0, -1))
    return gimbal_hand


class YawQuarterCurve(Component):
  connector_tolerance = 0.2
  bearing_tolerance = 0.1

  def __init__(self, length: float, width: float, radius: float, connectorDepth: float, connectorLength: float, connectorWidth: float, arcDegrees: float = 90, bearing = "608", name="gimbalQuarterCurve") -> None:
    super().__init__(name)
    self.length = length
    self.width = width
    self.radius = radius
    self.arcDegrees = arcDegrees
    self.connector_depth = connectorDepth
    self.connectorLength = connectorLength
    self.connectorWidth = connectorWidth
    self.bearing = bearing
    self.build()

  def _build(self) -> cq.Workplane:
    curved_sketch = rounded_rect(self.length, self.width, 0)
    connector_sketch = (
      rounded_rect(self.connectorLength - self.connector_tolerance, self.connectorWidth - self.connector_tolerance, 0)
    )
    gimbal_hand = (
        cq.Workplane("XY")
        .placeSketch(curved_sketch)
        .revolve(self.arcDegrees, cq.Vector(self.radius, 0, 0), cq.Vector(self.radius, 1, 0))
    )
    # gimbal_hand = (
    #     gimbal_hand.faces(">X").workplane(centerOption="CenterOfMass")
    #     .placeSketch(connector_sketch)
    #     .extrude(self.connector_depth)
    # )
    gimbal_hand = (
        gimbal_hand.faces("<Z").workplane(centerOption="CenterOfMass")
        .placeSketch(connector_sketch)
        .extrude(self.connector_depth)
      )

    pivot_connector = InnerGimbalConnector(length=self.length, width=self.width, height=self.connector_depth, connectorLength=self.connectorLength, connectorWidth=self.connectorWidth, connectorDepth=0.01, bearing="6000",name="yawBearing")
    pivot_connector = pivot_connector.build().rotateAboutCenter(cq.Vector(0, 1, 0), 90)
    
    # print(gimbal_hand.faces(">X").workplane(centerOption="CenterOfMass").val().Center())
    pivot_connector = pivot_connector.translate(gimbal_hand.faces(">X").val().Center() - cq.Vector(-self.connector_depth/2 + 1, 0, self.connectorLength/2)) # type: ignore
    gimbal_hand = gimbal_hand.union(pivot_connector)

    right_face_origin = gimbal_hand.faces(">X").workplane(centerOption="CenterOfMass").plane.location.toTuple()[0]
    self.add_port("right_face", origin=right_face_origin, normal=(1, 0, 0))
    self.add_port("bottom_face", origin=(0, -self.connector_depth, 0), normal=(0, 0, -1))
    return gimbal_hand


class YawQuarterCurveExtender(Component):
  connector_tolerance = 0.2
  bearing_tolerance = 0.1

  def __init__(self, length: float, width: float, height: float, connectorDepth: float, connectorLength: float, connectorWidth: float, name="gimbalQuarterCurve") -> None:
    super().__init__(name)
    self.length = length
    self.width = width
    self.height = height
    self.arcDegrees = 90
    self.connector_depth = connectorDepth
    self.connectorLength = connectorLength
    self.connectorWidth = connectorWidth
    self.build()

  def _build(self) -> cq.Workplane:
    curved_sketch = rounded_rect(self.length, self.width, 0)
    connector_sketch = (
      rounded_rect(self.connectorLength - self.connector_tolerance, self.connectorWidth - self.connector_tolerance, 0)
    )
    gimbal_hand = (
        cq.Workplane("XY")
        .placeSketch(curved_sketch)
        .extrude(self.height)
    )
    gimbal_hand = (
        gimbal_hand.faces(">Z").workplane(centerOption="CenterOfMass")
        .placeSketch(connector_sketch)
        .cutBlind(-self.connector_depth)
    )
    gimbal_hand = (
        gimbal_hand.faces("<Z").workplane(centerOption="CenterOfMass")
        .placeSketch(connector_sketch)
        .extrude(self.connector_depth)
                
      )
    return gimbal_hand


class GimbalStand(Component):

  def __init__(self, length: float, width: float, height: float, rodConnectorDepth: float, rodConnectorRadius, name="gimbalStand") -> None:
    super().__init__(name)
    self.length = length
    self.width = width
    self.height = height
    self.rodConnectorDepth = rodConnectorDepth
    self.rodConnectorRadius = rodConnectorRadius
    self.build()

  def _build(self) -> cq.Workplane:
    stand_sketch = rounded_rect(self.length, self.width, 5)
    gimbal_stand = (
      cq.Workplane("XY")
      .placeSketch(stand_sketch)
      .extrude(self.height)
    )
    gimbal_stand_plane_1 = gimbal_stand.faces(">Z").workplane().plane
    
    gimbal_stand = (
      gimbal_stand.copyWorkplane(cq.Workplane(gimbal_stand_plane_1))
      .circle(self.rodConnectorRadius)
      .circle(5)
      .extrude(self.rodConnectorDepth)
      .faces(">Z").workplane(centerOption="CenterOfBoundBox")
      .circle(12).cutBlind(-7)
      )
    gimbal_stand = (
      gimbal_stand.copyWorkplane(cq.Workplane(gimbal_stand_plane_1))
      .circle(5)
      .cutBlind(-self.height/2.5)
    )
    
    gimbal_stand = (
      gimbal_stand.copyWorkplane(cq.Workplane(gimbal_stand_plane_1))
      .pushPoints([(-self.length/3, 0), (self.length/3, 0)])
      .rect(3, self.width)
      .cutBlind(-5)
    )
    gimbal_stand = (
      gimbal_stand.copyWorkplane(cq.Workplane(gimbal_stand_plane_1))
      .pushPoints([(0, -self.length/3), (0, self.length/3)])
      .rect(self.width, 3)
      .cutBlind(-5)
    )
    # self.plane = gimbal_stand_plane_1

    return gimbal_stand


class TetherColumn(Component):
  padding = 0
  pad_height = 5
  pad_length = 14
  pad_width = 10.5
  def __init__(self, length: float, width: float, height: float, rodConnectorLength: float, rodConnectorRadius, eyeRadius: float, eyeTubeRadius: float, eyeSink: float, name="tetherStand") -> None:
    super().__init__(name)
    self.length = length
    self.width = width
    self.height = height
    self.rodConnectorLength = rodConnectorLength
    self.rodConnectorRadius = rodConnectorRadius
    self.eyeRadius = eyeRadius
    self.eyeTubeRadius = eyeTubeRadius
    self.eyeSink = eyeSink
    self.build()

  def _build(self) -> cq.Workplane:
    column_plate_sketch = rounded_rect(self.length, self.width, 5)
    # upright eye loop in the XZ plane, bottom on Z=0
    connector_ring = cq.Solid.makeTorus(
      self.eyeRadius, self.eyeTubeRadius,
      pnt=cq.Vector(0, 0, self.eyeRadius + self.eyeTubeRadius),
      dir=cq.Vector(0, 1, 0),
    )
    column_plate = (
      cq.Workplane("XY")
      .placeSketch(column_plate_sketch)
      .extrude(self.height)
    )
    column_plate_plane_1 = column_plate.faces(">Z").workplane().plane
    # column_plate = (
    #   column_plate.copyWorkplane(cq.Workplane(column_plate_plane_1))
    #   .circle(self.rodConnectorRadius)
    #   .extrude(self.rodConnectorLength)
    #   )
    # column_plate_plane_2 = column_plate.faces(">Z").workplane().plane
    # column_plate = place_on(column_plate, connector_ring, column_plate_plane_2, sink=self.eyeSink)
    column_plate = (
      column_plate.copyWorkplane(cq.Workplane(column_plate_plane_1))
      .pushPoints([(0, -(self.width - self.pad_width)/2 + self.padding, 0), (0, (self.width - self.pad_width)/2 - self.padding, 0)])
      .placeSketch(cq.Sketch().rect(self.pad_length, self.pad_width).vertices().fillet(1))
      .extrude(self.pad_height)
    )
    column_plate = (
      column_plate.copyWorkplane(cq.Workplane(column_plate_plane_1))
      .pushPoints([(-(self.length - self.pad_width)/2 + self.padding,  0, 0), ((self.length - self.pad_width)/2 - self.padding,  0, 0)])
      .placeSketch(cq.Sketch().rect(self.pad_width, self.pad_length).vertices().fillet(1))
      .extrude(self.pad_height)
      )
    # self.plane = gimbal_stand_plane_1

    return column_plate


class TetherPlate(Component):
  
  def __init__(self, length: float, width: float, height: float, eyeRadius: float, eyeTubeRadius: float, eyeSink: float, name="tetherPlate") -> None:
    super().__init__(name)
    self.length = length
    self.width = width
    self.height = height
    self.eyeRadius = eyeRadius
    self.eyeTubeRadius = eyeTubeRadius
    self.eyeSink = eyeSink
    self.build()

  def _build(self) -> cq.Workplane:
    column_plate_sketch = rounded_rect(self.length, self.width, 5)
    # upright eye loop in the XZ plane, bottom on Z=0
    connector_ring = cq.Solid.makeTorus(
      self.eyeRadius, self.eyeTubeRadius,
      pnt=cq.Vector(0, 0, self.eyeRadius + self.eyeTubeRadius),
      dir=cq.Vector(0, 1, 0),
    )
    column_plate = (
      cq.Workplane("XY")
      .placeSketch(column_plate_sketch)
      .extrude(self.height)
    )
    column_plate_plane_1 = column_plate.faces(">Z").workplane().plane
    column_plate = place_on(column_plate, connector_ring, column_plate_plane_1, sink=self.eyeSink)

    # self.plane = gimbal_stand_plane_1

    return column_plate


class DroneStand(Component):

  def __init__(self, length: float, width: float, height: float, radius: float, connectorLength: float, connectorWidth: float, connectorDepth: float, droneLength: float, droneWidth: float, droneDepth: float, name="droneStand") -> None:
    super().__init__(name)
    self.length = length
    self.width = width
    self.height = height
    self.radius = radius
    self.connectorLength = connectorLength
    self.connectorWidth = connectorWidth
    self.connectorDepth = connectorDepth
    self.droneLength = droneLength
    self.droneWidth = droneWidth
    self.droneDepth = droneDepth
    self.build()

  def _build(self) -> cq.Workplane:
    drone_stand_sketch = rounded_rect(self.length, self.width, self.radius)
    connector_sketch = rounded_rect(self.connectorWidth, self.connectorLength, 5)
    connector_sketch_2 = rounded_rect(self.connectorLength, self.connectorWidth, 5)
    drone_sketch = rounded_rect(self.droneLength, self.droneWidth, 2)
    drone_stand = (
        cq.Workplane("XY")
        .placeSketch(drone_stand_sketch)
        .extrude(self.height)
    )
    drone_stand_plane_up = drone_stand.faces(">Z").workplane().plane
    drone_stand_plane_left = drone_stand.faces("<X").workplane().plane
    drone_stand_plane_right = drone_stand.faces(">X").workplane().plane
    drone_stand_plane_front = drone_stand.faces(">Y").workplane().plane
    drone_stand_plane_back = drone_stand.faces("<Y").workplane().plane

    drone_arm_left = (
      cq.Workplane(drone_stand_plane_left)
      .pushPoints([(0, self.height/2, 0)])
      .placeSketch(connector_sketch)
      .revolve(90, cq.Vector(0, self.height*2, 0), cq.Vector(-10, self.height*2, 0))
    )
    drone_arm_right = (
      cq.Workplane(drone_stand_plane_right)
      .pushPoints([(0, self.height/2, 0)])
      .placeSketch(connector_sketch)
      .revolve(90, cq.Vector(0, self.height*2, 0), cq.Vector(-10, self.height*2, 0))
    )
    drone_arm_left_plane_up = drone_arm_left.faces(">Z").workplane(centerOption="CenterOfBoundBox").plane
    drone_arm_right_plane_up = drone_arm_right.faces(">Z").workplane(centerOption="CenterOfBoundBox").plane

    drone_stand = drone_stand.add(drone_arm_left).add(drone_arm_right)

    drone_arm_left_2 = (
      cq.Workplane(drone_arm_left_plane_up)
      .placeSketch(connector_sketch_2)
      .revolve(90, cq.Vector(-self.height*2, 0, 0), cq.Vector(-self.height*2, -10, 0))
    )
    drone_arm_right_2 = (drone_stand.copyWorkplane(cq.Workplane(drone_arm_right_plane_up))
                   .placeSketch(connector_sketch_2)
                   .revolve(90, cq.Vector(self.height*2, 0, 0), cq.Vector(self.height*2, 10, 0))
                   )
    drone_arm_left_plane_up_2 = drone_arm_left_2.faces(">Z").workplane(centerOption="CenterOfBoundBox").plane
    drone_arm_right_plane_up_2 = drone_arm_right_2.faces(">Z").workplane(centerOption="CenterOfBoundBox").plane

    drone_stand = drone_stand.add(drone_arm_left_2).add(drone_arm_right_2)

    drone_stand = (drone_stand.copyWorkplane(cq.Workplane(drone_stand_plane_up))
                   .placeSketch(drone_sketch)
                   .cutBlind(-self.droneDepth)
                   )
    drone_stand = (drone_stand.copyWorkplane(cq.Workplane(drone_stand_plane_up)).transformed(offset=cq.Vector(0, 0, 0), rotate=(0, 0, 45))
                    .placeSketch(drone_sketch)
                    .cutBlind(-self.droneDepth)
                    )

    drone_stand = (drone_stand.copyWorkplane(cq.Workplane(drone_arm_left_plane_up_2))
                    .placeSketch(connector_sketch)
                    .extrude(self.connectorDepth)
                    .pushPoints([(0, 0, 0)])
                    .circle(5)
                    .cutBlind(self.connectorDepth)
                  )
    drone_stand = (drone_stand.copyWorkplane(cq.Workplane(drone_arm_right_plane_up_2))
                        .placeSketch(connector_sketch)
                        .extrude(self.connectorDepth)
                        .pushPoints([(0, 0, 0)])
                        .circle(5)
                        .cutBlind(self.connectorDepth)
                      )
    # drone_stand, slot_planes = create_rectangular_slot(drone_stand, slot_properties, ["<X", ">X", "<Y", ">Y"], slotName="droneStandSlots")
    # self.add_ports_from_planes(slot_planes)   # ports such as "droneStandSlots.<X.floor", placed with the stand

    # print(type(drone_stand))
    return drone_stand


class YawQuarterCurveExtenderLong(Component):
  connector_tolerance = 0.2
  bearing_tolerance = 0.1

  def __init__(self, length: float, width: float, height: float, connectorDepth: float, connectorLength: float, connectorWidth: float, name="gimbalQuarterCurve") -> None:
    super().__init__(name)
    self.length = length
    self.width = width
    self.height = height
    self.arcDegrees = 90
    self.connector_depth = connectorDepth
    self.connectorLength = connectorLength
    self.connectorWidth = connectorWidth
    self.build()

  def _build(self) -> cq.Workplane:
    curved_sketch = rounded_rect(self.length, self.width, 0)
    connector_sketch = (
      rounded_rect(self.connectorLength - self.connector_tolerance, self.connectorWidth - self.connector_tolerance, 0)
    )
    gimbal_hand = (
        cq.Workplane("XY")
        .placeSketch(curved_sketch)
        .extrude(self.height)
    )
    gimbal_hand = (
        gimbal_hand.faces(">Z").workplane(centerOption="CenterOfMass")
        .placeSketch(connector_sketch)
        .cutBlind(-self.connector_depth)
    )
    gimbal_hand = (
        gimbal_hand.faces("<X").workplane(origin=(cq.Vector(0, 0, 25)))
        .hole(9.8)
        # .extrude(self.connector_depth)
                
      )
    return gimbal_hand


class GimbalYawHub(Component):
  bearing = "608"
  bearing_tolerance = 0.1

  def __init__(self, thickness: float, height: float, connectorThickness: float, connectorDepth: float, bearing="608", name="gimbalConnector") -> None:
    super().__init__(name)
    self.length = thickness
    self.depth = connectorDepth
    self.connectorThickness = connectorThickness
    self.height = height
    self.bearing = bearing
    self.build()

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

    bearing_cup_r.mate("top_face", to=self.local_port("bearing_mount_outer"))
    bearing_cup_l.mate("top_face", to=self.local_port("bearing_mount_inner"))
    
    fused = fuse_all( bearing_cup_r,
                    bearing_cup_l,
                      connector
                    )
    self.add_port("upper_connector", origin=( 0, 0, (self.height) - self.depth), normal=( 0, 0, -1))
    self.add_port("lower_connector", origin=( 0, 0, self.depth), normal=( 0, 0, 1))
    return fused

