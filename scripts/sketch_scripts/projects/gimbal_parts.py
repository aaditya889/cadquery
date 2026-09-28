from cq_server.ui import ui, show_object
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core import Component, show, fuse_all, find_junction_edges, attach
from hardware.parts import *
from features import BearingHousing
import cadquery as cq

g = InnerGimbalConnector(thickness=50.0, height=100.0, connectorThickness=10, connectorDepth=30, name="gConn1")
q = GimbalQuarterCurve(thickness=10, radius=40, name="quarterConn1")
# b1 = BearingHousing(bearing="608", wall_thickness=3.0, clearance=0.2, name="Bearing1")
# b2 = BearingHousing(bearing="608", wall_thickness=3.0, clearance=0.2, name="Bearing2")

# b1.mate("mount_face", to=g, to_port="upper_connector")
# b2.mate("mount_face", to=g, to_port="lower_connector")

_ = g.workplanes["upper_connector"].pushPoints([(0, 0, 0)]).circle(2).extrude(20)
__ = g.workplanes["lower_connector"].pushPoints([(0, 0, 0)]).circle(2).extrude(20)

show(
      g, 
      # q
      # b1, b2, 
      _, __
    )
