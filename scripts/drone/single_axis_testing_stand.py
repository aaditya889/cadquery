import cadquery as cq
from cadquery import exporters
from ocp_vscode import show_object
import os, sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)
from lib.solid import *
from lib.hollow import *
from lib.parts import *

drone_width = 300
drone_height = 200
# base_part_height = 25
error_margin = 0
stand_part_width = 40
stand_part_height = 130
# base_part_width = 7
stand_part_thickness = 7
ball_bearing_radius = 13.5
ball_bearing_thickness = 2
ball_bearing_height = 5
wing_length = 100
wing_width = 30
wing_pillar_height = 100
wing_pillar_thickness = 5


topmost_point = cq.Vector(0, 0, stand_part_height/2)
stand_base_point = cq.Vector(0, 0, -stand_part_height/2)
pillar_ball_bearing_origin = topmost_point - cq.Vector(0, 0, ball_bearing_radius + ball_bearing_thickness + 0.5 * ball_bearing_radius)
y_ball_bearing_cylinder = create_hollow_cylinder_with_two_open_faces(ball_bearing_radius, ball_bearing_height, ball_bearing_thickness, "XZ")
ball_bearing_cylinder = create_hollow_cylinder_with_two_open_faces(ball_bearing_radius, ball_bearing_height, ball_bearing_thickness, "YZ")

stand_base = create_solid_box(drone_width + error_margin, stand_part_thickness, stand_part_width, workplane="XZ")
# stand_base = stand_base.faces(">Y").workplane().circle(ball_bearing_radius + ball_bearing_thickness/2).cutThruAll()

pillar_parts = create_solid_box(stand_part_height, stand_part_width, stand_part_thickness, workplane="ZY")
pillar_parts = pillar_parts.faces(">X").workplane(origin=pillar_ball_bearing_origin).circle(ball_bearing_radius + ball_bearing_thickness/2).cutThruAll()
# pillar_parts = pillar_parts.faces(">X").workplane(origin=stand_base_point + cq.Vector(0, 0, base_part_height/2)).rect(base_part_width, base_part_height + 2).cutThruAll()

# stand_base = cq.Assembly().add(stand_base, name="base").add(y_ball_bearing_cylinder).toCompound()
stand_pillar = cq.Assembly()
stand_pillar.add(pillar_parts, name="main_pillar")
stand_pillar.add(ball_bearing_cylinder, loc=cq.Location(pillar_ball_bearing_origin), name="ball_bearing", color="blue")
stand_pillar = stand_pillar.toCompound()

stand_pillar1 = stand_pillar.translate(cq.Vector((drone_width + error_margin + stand_part_thickness)/2, 0, (stand_part_height - stand_part_thickness)/2))
stand_pillar2 = stand_pillar.translate(cq.Vector(-(drone_width + error_margin + stand_part_thickness)/2, 0, (stand_part_height - stand_part_thickness)/2))

wing = create_solid_box(wing_width, stand_part_thickness, wing_length, workplane="XZ")
wing_pillar1 = create_solid_box(wing_width, wing_pillar_thickness, wing_pillar_height, origin=(0, (wing_length + (stand_part_width - wing_pillar_thickness)/2), (wing_pillar_height + stand_part_thickness)/2))
wing_pillar2 = create_solid_box(wing_width, wing_pillar_thickness, wing_pillar_height, origin=(0, -(wing_length + (stand_part_width - wing_pillar_thickness)/2), (wing_pillar_height + stand_part_thickness)/2))
wing1 = wing.translate(cq.Vector(0, (stand_part_width + wing_length)/2, 0))
wing2 = wing.translate(cq.Vector(0, -(stand_part_width + wing_length)/2, 0))

y_assembled = cq.Assembly()
y_assembled.add(stand_base, color="yellow", name="y_base")
y_assembled.add(stand_pillar1, color="red", name="pillar_1")
y_assembled.add(stand_pillar2, color="green", name="pillar_2")
y_assembled.add(wing1, color="orange", name="wing1")
y_assembled.add(wing2, color="orange", name="wing2")
y_assembled.add(wing_pillar1, color="brown", name="wing_pillar1")
y_assembled.add(wing_pillar2, color="brown", name="wing_pillar2")

# y_assembled.add(y_ball_bearing_cylinder, color="blue", name="ball")

show_object(y_assembled)
y_assembled.export("export/single_axis_testing_stand.stl", "STL")
# exporters.export(stand_pillar1, "export/stand_pillar.stl")


