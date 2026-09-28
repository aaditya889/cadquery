from cq_server.ui import ui, show_object
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core import Component, show, fuse_all, find_junction_edges, attach
from hardware.parts import InnerGimbalConnector
from features import BearingHousing

g = InnerGimbalConnector(length=50.0, width=35.0, height=100.0)
b1 = BearingHousing(bearing="608", wall_thickness=3.0, clearance=0.2)
b2 = BearingHousing(bearing="608", wall_thickness=3.0, clearance=0.2)

b1.mate("mount_face", to=g, to_port="upper_connector")
b2.mate("mount_face", to=g, to_port="lower_connector")

show(g, b1, b2)
