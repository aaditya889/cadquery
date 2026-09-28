from cq_server.ui import ui, show_object
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core import Component, show, fuse_all, find_junction_edges, attach
from hardware.parts import *
from features import BearingHousing
import cadquery as cq

g1 = InnerGimbalConnector(thickness=50.0, height=100.0, connectorThickness=30, connectorDepth=30, name="gConn1")
g2 = InnerGimbalConnector(thickness=50.0, height=100.0, connectorThickness=30, connectorDepth=30, name="gConn2")
q1 = GimbalQuarterCurve(thickness=30, radius=40, name="quarterConn1")
q2 = GimbalQuarterCurve(thickness=30, radius=40, name="quarterConn2")
# b1 = BearingHousing(bearing="608", wall_thickness=3.0, clearance=0.2, name="Bearing1")
# b2 = BearingHousing(bearing="608", wall_thickness=3.0, clearance=0.2, name="Bearing2")

# b1.mate("mount_face", to=g, to_port="upper_connector")
# b2.mate("mount_face", to=g, to_port="lower_connector")

# _ = b1.workplanes["mount_face"].pushPoints([(0, 0, 0)]).circle(2).extrude(-20)
# __ = b2.workplanes["mount_face"].pushPoints([(0, 0, 0)]).circle(2).extrude(-20)

# _q = q1.workplanes["right_face"].pushPoints([(0, 0, 0)]).circle(1).extrude(20)
# __q = q1.workplanes["bottom_face"].pushPoints([(0, 0, 0)]).circle(1).extrude(20)

g1.mate("upper_connector", to=q1, to_port="right_face")
q2.mate("bottom_face", to=g1, to_port="lower_connector")

show(
      g1,
      q1,
      # g2,
      q2,
      # _q, __q
    )
