from cq_server.ui import ui, show_object
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core import Component, show, fuse_all, find_junction_edges, attach
from hardware.parts import *
from features import BearingHousing
import cadquery as cq

gimbal_connector = InnerGimbalConnector(length=50.0, width=50.0, height=150.0, connectorLength=40, connectorWidth=40, connectorDepth=40, bearing="6000",name="gConn1")
quarter_arm = GimbalQuarterCurve(length=40, width=40, radius=200, connectorDepth=40, connectorLength=40, connectorWidth=40, name="quarterConn1")


yaw_connector_meas = {
  "length": 120,
  "width": 50,
  "height": 100,
  "connectorLength": 40,
  "connectorWidth": 32,
  "connectorDepth": 40,
  "armRadius": 215
}

yaw_gimbal_extender = YawQuarterCurveExtender(length=yaw_connector_meas["connectorLength"]+10, width=yaw_connector_meas["connectorWidth"]+20, height=60, connectorDepth=yaw_connector_meas["connectorDepth"], connectorLength=yaw_connector_meas["connectorLength"], connectorWidth=yaw_connector_meas["connectorWidth"], name="yawExtender")
yaw_connector = InnerGimbalConnector(length=yaw_connector_meas["height"], width=yaw_connector_meas["width"], height=yaw_connector_meas["length"], connectorLength=yaw_connector_meas["connectorLength"], connectorWidth=yaw_connector_meas["connectorWidth"], connectorDepth=yaw_connector_meas["connectorDepth"], bearing="6000",name="yawConnector")
yaw_quarter_arm = YawQuarterCurve(length=yaw_connector_meas["connectorLength"], width=yaw_connector_meas["connectorWidth"], radius=yaw_connector_meas["armRadius"], connectorDepth=yaw_connector_meas["connectorDepth"], connectorLength=yaw_connector_meas["connectorLength"], connectorWidth=yaw_connector_meas["connectorWidth"], name="yawQuarterArm")
yaw_gimbal_extender_long = YawQuarterCurveExtenderLong(length=yaw_connector_meas["connectorLength"]+10, width=yaw_connector_meas["connectorWidth"]+20, height=170, connectorDepth=yaw_connector_meas["connectorDepth"], connectorLength=yaw_connector_meas["connectorLength"], connectorWidth=yaw_connector_meas["connectorWidth"], name="yawExtender")

drone_stand = DroneStand(length=160, width=160, height=15, connectorLength=15, connectorWidth=30, connectorDepth=40, radius=10, droneLength = 140, droneWidth=82, droneDepth = 2, name="droneStand")
gimbal_stand = GimbalStand(length=130, width=130, height=30, rodConnectorDepth=60, rodConnectorRadius=20, name="gimbalStand")

# quarter_arm_test = GimbalQuarterCurve(length=40, width=40, radius=200, connectorDepth=40, connectorLength=40, connectorWidth=40, name="quarterArmTest")
# b1 = BearingHousing(bearing="608", wall_thickness=3.0, clearance=0.2, name="Bearing1")
# b2 = BearingHousing(bearing="608", wall_thickness=3.0, clearance=0.2, name="Bearing2")

# b1.mate("mount_face", to=g, to_port="upper_connector")
# b2.mate("mount_face", to=g, to_port="lower_connector")

# _q = q1.workplanes["right_face"].pushPoints([(0, 0, 0)]).circle(1).extrude(20)
# __q = q1.workplanes["bottom_face"].pushPoints([(0, 0, 0)]).circle(1).extrude(20)

# gimbal_connector.mate("lower_connector", to=quarter_arm, to_port="right_face", invert=True)
# quarter_arm_test.mate("right_face", to=gimbal_connector, to_port="upper_connector", invert=True)

# _ = g1.workplanes["upper_connector"].pushPoints([(0, 0, 0)]).rect(2, 2).extrude(20)
# __ = g1.workplanes["lower_connector"].pushPoints([(0, 0, 0)]).circle(2).extrude(20)

print(f"g1.port('lower_connector').normal_vector: {gimbal_connector.port('lower_connector').normal_vector}")
print(f"g1.port('upper_connector').normal_vector: {gimbal_connector.port('upper_connector').normal_vector}")

# print(f"g2.port('lower_connector').normal_vector: {g2.port('lower_connector').normal_vector}")
# print(f"g2.port('upper_connector').normal_vector: {g2.port('upper_connector').normal_vector}")


print(f"q1.port('right_face').normal_vector: {quarter_arm.port('right_face').normal_vector}")
print(f"q1.port('bottom_face').normal_vector: {quarter_arm.port('bottom_face').normal_vector}")

# print(f"q3.port('right_face').normal_vector: {q3.port('right_face').normal_vector}")
# print(f"q3.port('bottom_face').normal_vector: {q3.port('bottom_face').normal_vector}")
# drone_stand.build()
# slot_ps = drone_stand.tagged_planes["droneStandSlots"]["<X"]

# slot_faces = [
#     drone_stand._cached_solid.faces(cq.selectors.NearestToPointSelector(p.origin.toTuple()))
#     for p in slot_ps.values()
# ]
# wp: cq.Workplane

# for wp in drone_stand_workplanes:
#   print(wp.plane.location.toTuple())
show(
      # g1,
      # yaw_gimbal_extender,
      # yaw_gimbal_extender_long,
      # yaw_connector,
      # yaw_quarter_arm,
      drone_stand,
      # *slot_faces,
      #  drone_stand.build().faces(">Z"),
      # gimbal_stand,
      # gimbal_stand.plane
    )

os.makedirs("export/drone_gimbal", exist_ok=True)
cq.exporters.export(fuse_all(drone_stand), "export/drone_gimbal/drone_stand.stl")
# cq.exporters.export(fuse_all(q3), "export/drone_gimbal/yaw_quarter_arm.stl")

print("✅ Tag-based assembly compiled and exported successfully to " \
"export/drone_gimbal/gimbal_connector.stl and export/drone_gimbal/yaw_quarter_arm.stl")