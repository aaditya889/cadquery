import cadquery as cq
from cadquery import exporters
from ocp_vscode import show_object
import os, sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)
from lib.solid import *
from lib.parts import *

drone_width = 40
error_margin = 10
stand_part_width = 6
stand_part_height = 5



y_rotation_stand_base = create_solid_box(drone_width + error_margin, stand_part_width, stand_part_height)
y_rotation_stand_pillar1 = create_solid_box(drone_width + error_margin, stand_part_width, stand_part_height, workplane="ZY", origin=((drone_width + error_margin + stand_part_height)/2, 0, (drone_width + error_margin - stand_part_height)/2))
y_rotation_stand_pillar2 = create_solid_box(drone_width + error_margin, stand_part_width, stand_part_height, workplane="ZY", origin=(-(drone_width + error_margin + stand_part_height)/2, 0, (drone_width + error_margin - stand_part_height)/2))

y_assembled = cq.Assembly()
y_assembled.add(y_rotation_stand_base, color="yellow", name="y_base")
y_assembled.add(y_rotation_stand_pillar1, color="red", name="y_pillar_1")
y_assembled.add(y_rotation_stand_pillar2, color="green", name="y_pillar_2")

assy = AssembledPart(y_assembled)
x_assembled = assy.clone_and_rotate(axis="X", angle=69)
y_assembled.add(x_assembled, name="x_assembled")
# for i in test_ass.objects.values():
#   if (not i.name.startswith("y")):
#     continue
#   print(i.name)
#   i.loc *= rotation_vector
# x_assembled = y_assembled.toCompound().rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 90).translate(cq.Vector(0, 0, -(drone_width + error_margin/2)))
# y_assembled = y_assembled.add(x_assembled, name="x_assembled", color="red")
show_object(y_assembled)