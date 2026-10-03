from cq_server.ui import ui, show_object
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core import Component, show, fuse_all, find_junction_edges, attach
from hardware.parts import *
from features import BearingHousing
import cadquery as cq

g1 = InnerGimbalConnector(thickness=50.0, height=150.0, connectorThickness=40, connectorDepth=40, bearing="6000",name="gConn1")
# g2 = InnerGimbalConnector(thickness=50.0, height=100.0, connectorThickness=30, connectorDepth=30, bearing="608",name="gConn2")

q1 = GimbalQuarterCurve(thickness=40, radius=200, connectorDepth=40, connectorThickness=40, name="quarterConn1")
# q1 = GimbalQuarterCurve(thickness=25, radius=200, connectorDepth=40, connectorThickness=15, name="quarterConn1")
# q2 = GimbalQuarterCurve(thickness=40, radius=40, connectorDepth=30, connectorThickness=30, name="quarterConn2")
# b1 = BearingHousing(bearing="608", wall_thickness=3.0, clearance=0.2, name="Bearing1")
# b2 = BearingHousing(bearing="608", wall_thickness=3.0, clearance=0.2, name="Bearing2")

# b1.mate("mount_face", to=g, to_port="upper_connector")
# b2.mate("mount_face", to=g, to_port="lower_connector")

# _q = q1.workplanes["right_face"].pushPoints([(0, 0, 0)]).circle(1).extrude(20)
# __q = q1.workplanes["bottom_face"].pushPoints([(0, 0, 0)]).circle(1).extrude(20)

# g1.mate("upper_connector", to=q1, to_port="right_face", invert=False)
# q2.mate("right_face", to=g1, to_port="lower_connector", invert=False)

# _ = g1.workplanes["upper_connector"].pushPoints([(0, 0, 0)]).rect(2, 2).extrude(20)
# __ = g1.workplanes["lower_connector"].pushPoints([(0, 0, 0)]).circle(2).extrude(20)

show(
      # g1,
      # g2,
      q1,
      # _, 
      # __,
      # g2,
      # q2,
      # _q, __q
    )

os.makedirs("export/drone_gimbal", exist_ok=True)
cq.exporters.export(fuse_all(g1), "export/drone_gimbal/gimbal_connector.stl")
cq.exporters.export(fuse_all(q1), "export/drone_gimbal/quarter_arm.stl")

print("✅ Tag-based assembly compiled and exported successfully to " \
"export/drone_gimbal/gimbal_connector.stl and export/drone_gimbal/quarter_arm.stl")