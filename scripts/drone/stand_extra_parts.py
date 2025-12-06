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

rod_radius = 5
rod_height = 50
extra_margin = 3
platform_length = 100 + rod_radius*2 + extra_margin
platform_width = 80 + rod_radius*2 + extra_margin
platform_height = 4
rod_margin_multiplier = 2

# rod_distance_from_center = 20

main_rod = create_solid_cylinder(rod_radius*2, rod_height, "XY").translate(cq.Vector(0, 0, (platform_height + rod_height)/2))
rod1 = create_solid_cylinder(rod_radius, rod_height, "XY").translate(cq.Vector((platform_length/2 - rod_radius*rod_margin_multiplier), platform_width/2 - rod_radius*rod_margin_multiplier, (platform_height + rod_height)/2))
rod2 = create_solid_cylinder(rod_radius, rod_height, "XY").translate(cq.Vector(-platform_length/2 + rod_radius*rod_margin_multiplier, platform_width/2 - rod_radius*rod_margin_multiplier, (platform_height + rod_height)/2))
rod3 = create_solid_cylinder(rod_radius, rod_height, "XY").translate(cq.Vector(-platform_length/2 + rod_radius*rod_margin_multiplier, -platform_width/2 + rod_radius*rod_margin_multiplier, (platform_height + rod_height)/2))
rod4 = create_solid_cylinder(rod_radius, rod_height, "XY").translate(cq.Vector(platform_length/2 - rod_radius*rod_margin_multiplier, -platform_width/2 + rod_radius*rod_margin_multiplier, (platform_height + rod_height)/2))
platform = create_solid_box(platform_length, platform_width, platform_height)
assembled = cq.Assembly()
assembled.add(platform, color="red", name="platform")
# assembled.add(main_rod, color="blue", name="main_rod")
assembled.add(rod1, color="blue", name="rod1")
assembled.add(rod2, color="blue", name="rod2")
assembled.add(rod3, color="blue", name="rod3")
assembled.add(rod4, color="blue", name="rod4")
# y_assembled.add(y_ball_bearing_cylinder, color="blue", name="ball")

show_object(assembled)
assembled.export("export/extra_parts.stl", "STL")
# exporters.export(assembled, "export/extra_parts.stl")