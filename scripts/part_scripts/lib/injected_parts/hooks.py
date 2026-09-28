import cadquery as cq
import os, sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(parent_dir)
from lib.solid import *


def create_male_u_hook():
  hook_outer_length = 21
  hook_outer_thickness = 3.5
  hook_wing_extrusion_length = 3
  hook_outer_width = 17 - hook_wing_extrusion_length * 2
  hook_wing_thickness = 2
  hook_square_extrusion_height = 12.5

  male_hook = create_solid_box(hook_outer_length, hook_outer_width, hook_outer_thickness)
  male_hook = male_hook.faces("<Y").workplane(origin=cq.Vector(hook_square_extrusion_height - hook_outer_length/2, 0, hook_outer_thickness/2)).rect(-hook_square_extrusion_height, -hook_wing_thickness, centered=False).extrude(hook_wing_extrusion_length)
  male_hook = male_hook.faces(">Y").workplane(origin=cq.Vector(hook_square_extrusion_height - hook_outer_length/2, 0, hook_outer_thickness/2)).rect(hook_square_extrusion_height, -hook_wing_thickness, centered=False).extrude(hook_wing_extrusion_length)
  male_hook = male_hook.faces(">Z").workplane(origin=cq.Vector(hook_square_extrusion_height - hook_outer_length/2, -hook_outer_width/2, 0)).rect(hook_square_extrusion_height, hook_outer_width/4, centered=False).cutThruAll()
  male_hook = male_hook.faces("<Z").workplane(origin=cq.Vector(hook_square_extrusion_height - hook_outer_length/2, hook_outer_width/2, 0)).rect(hook_square_extrusion_height, hook_outer_width/4, centered=False).cutThruAll()
  male_hook = male_hook.faces(">X").edges("<Y").fillet(hook_outer_width/4 - 0.1)
  male_hook = male_hook.faces(">X").edges(">Y").fillet(hook_outer_width/4 - 0.1)
  male_hook = male_hook.fillet(0.2)

  return male_hook
