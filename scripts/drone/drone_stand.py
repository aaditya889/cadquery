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

hook_radius = 5.5
hook_thickness = 3
hook_height = 14
platform_length = 90
platform_width = 80
platform_height = 3

_stand_hook = create_hollow_cylinder_with_two_open_faces(hook_radius, hook_height, hook_thickness, workplane="YZ")
_hook_cut = create_solid_box(hook_height, 1.5*hook_radius, 3*hook_thickness, origin=(0, 0, -(2*hook_radius + hook_thickness)/2))
_stand_hook = _stand_hook.cut(_hook_cut)
stand_hook1 = _stand_hook.translate(cq.Vector(-0.7*platform_length/2, 0, 0))
stand_hook2 = _stand_hook.translate(cq.Vector(0, 0, 0))
stand_hook3 = _stand_hook.translate(cq.Vector(0.7*platform_length/2, 0, 0))

platform = create_solid_box(platform_length, platform_width, platform_height).translate(cq.Vector(0, 0, hook_radius + hook_thickness))
# platform = platform.edges().fillet(2)

full_stand_base = create_solid_box(290, 290, 2)
_rectangle_cut = create_solid_box(200, 200, 10, origin=(-100, -100, -5)).rotate((0,0,0), (0,0,1), 45)
_rectangle_cut = _rectangle_cut.translate(cq.Vector(0, 0, 1))
full_stand_base = full_stand_base.cut(_rectangle_cut)
full_stand_base = full_stand_base.cut(_rectangle_cut.rotate((0,0,0), (0,0,1), 90))
full_stand_base = full_stand_base.cut(_rectangle_cut.rotate((0,0,0), (0,0,1), 180))
full_stand_base = full_stand_base.cut(_rectangle_cut.rotate((0,0,0), (0,0,1), 270))
full_stand_base = full_stand_base.translate(cq.Vector(0, 0, -1))

assembled = cq.Assembly()
assembled.add(stand_hook1, name="hook1", color="blue")
assembled.add(stand_hook2, name="hook2", color="blue")
assembled.add(stand_hook3, name="hook3", color="blue")
assembled.add(platform, name="platform", color="green")
# assembled.add(_hook_cut, name="hook_cut", color="red")
show_object(assembled)
assembled.export("export/drone_stand.stl")
# cq.exporters.export(assembled, "export/full_stand_base.stl")