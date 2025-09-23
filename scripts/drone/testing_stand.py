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

drone_width = 400
drone_height = 200
base_part_height = 30
error_margin = 5
stand_part_width = 20
base_part_width = 7
stand_part_height = 7
ball_bearing_radius = 6.75
ball_bearing_thickness = 2
ball_bearing_height = 5
# ball_bearing_outer_radius = ball_bearing_radius + ball_bearing_thickness

# test_box = create_solid_box(300, 10, 10)
topmost_point = cq.Vector(0, 0, drone_height/2)
pillar_ball_bearing_origin = topmost_point - cq.Vector(0, 0, ball_bearing_radius + ball_bearing_thickness + 3)

y_rotation_stand_base = create_solid_box(drone_width + error_margin, base_part_width, base_part_height)
y_ball_bearing_cylinder = create_hollow_cylinder_with_two_open_faces(ball_bearing_radius, ball_bearing_height, ball_bearing_thickness, "XZ")
y_rotation_stand_base = y_rotation_stand_base.faces(">Y").workplane().circle(ball_bearing_radius + ball_bearing_thickness/2).cutThruAll()

x_ball_bearing_cylinder_1 = create_hollow_cylinder_with_two_open_faces(ball_bearing_radius, ball_bearing_height, ball_bearing_thickness, "YZ")
pillar_parts = create_solid_box(drone_height, stand_part_width, stand_part_height, workplane="ZY")
pillar_parts = pillar_parts.faces(">X").workplane(origin=pillar_ball_bearing_origin).circle(ball_bearing_radius + ball_bearing_thickness/2).cutThruAll()
stand_pillar = cq.Assembly()
stand_pillar.add(pillar_parts, name="main_pillar")
stand_pillar.add(x_ball_bearing_cylinder_1, loc=cq.Location(pillar_ball_bearing_origin), name="ball_bearing", color="blue")
stand_pillar = stand_pillar.toCompound()
stand_pillar1 = stand_pillar.translate(cq.Vector((drone_width + error_margin + stand_part_height)/2, 0, (drone_height - base_part_height)/2))
stand_pillar2 = stand_pillar.translate(cq.Vector(-(drone_width + error_margin + stand_part_height)/2, 0, (drone_height - base_part_height)/2))

# x_ball_bearing_cylinder_2 = create_hollow_cylinder_with_two_open_faces(ball_bearing_radius, ball_bearing_height, ball_bearing_thickness, "YZ")
# y_rotation_stand_pillar2 = create_solid_box(drone_height, stand_part_width, stand_part_height, workplane="ZY", origin=(-(drone_width + error_margin + stand_part_height)/2, 0, (drone_height - base_part_height)/2))
# y_rotation_stand_pillar2 = y_rotation_stand_pillar2.faces(">X").workplane(origin=pillar_ball_bearing_origin).circle(ball_bearing_radius + ball_bearing_thickness/2).cutThruAll()
# y_rotation_stand_pillar2 = cq.Assembly().add(y_rotation_stand_pillar2, name="main_pillar").add(x_ball_bearing_cylinder_2, loc=cq.Location(cq.Vector(-(drone_width)/2, 0, drone_height - 2*ball_bearing_radius - 2*ball_bearing_thickness)), name="ball_bearing", color="blue")


y_assembled = cq.Assembly()
y_assembled.add(y_rotation_stand_base, color="yellow", name="y_base")
y_assembled.add(stand_pillar1, color="red", name="pillar_1")
y_assembled.add(stand_pillar2, color="green", name="pillar_2")
y_assembled.add(y_ball_bearing_cylinder, color="blue", name="ball")

# assy = AssembledPart(y_assembled)
# x_assembled = assy.clone_and_rotate(axis="Z", angle=90)
# y_assembled.add(x_assembled, name="x_assembled")
# for i in test_ass.objects.values():
#   if (not i.name.startswith("y")):
#     continue
#   print(i.name)
#   i.loc *= rotation_vector
# x_assembled = y_assembled.toCompound().rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 90).translate(cq.Vector(0, 0, -(drone_width + error_margin/2)))
# y_assembled = y_assembled.add(x_assembled, name="x_assembled", color="red")
show_object(y_assembled)
# y_assembled.export("export/testing_stand.stl", "STL")
exporters.export(y_ball_bearing_cylinder, "export/testing_stand.stl")