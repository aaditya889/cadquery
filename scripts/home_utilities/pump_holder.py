import cadquery as cq
from ocp_vscode import show_object
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)
from lib.curved_parts import *

pump_base_length = 140
pump_base_width = 125
pump_base_height = 20
faucet_radius = 13
faucet_width = 30
faucet_thickness = 5

pump_base = cq.Workplane("XY").box(pump_base_length, pump_base_width, pump_base_height)
faucet_clamp = create_semicircular_ring(faucet_radius, faucet_radius + faucet_width, faucet_thickness)

final_part = cq.Assembly()
final_part.add(pump_base, loc=(cq.Location(cq.Vector((0, 0, 0)))), color=cq.Color("blue"), name="pump_base")
final_part.add(faucet_clamp.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), -90), loc=(cq.Location(cq.Vector((0, pump_base_width/2 - faucet_thickness, faucet_radius + faucet_width/2 + pump_base_height/2 )))), color=cq.Color("red"), name="faucet_clamp")

final_part.export("export/pump_holder.stl", "STL")
show_object(final_part)