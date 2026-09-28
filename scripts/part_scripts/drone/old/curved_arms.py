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

multiplier = 1
drone_base_thickness_mm = 10 * multiplier
motor_base_thickness_mm = 4 * multiplier
motor_base_radius_mm = 29/2 * multiplier
motor_screw_radius_mm = 1.4 * multiplier
motor_shaft_radius_mm = 4 * multiplier
motor_holder_height_mm = (drone_base_thickness_mm - motor_base_thickness_mm) * multiplier
motor_holder_wire_pocket_length_mm = 15
motor_screw_distance_from_center_mm = 8 * multiplier
motor_screw_coordinates = [(0, motor_screw_distance_from_center_mm), 
                           (motor_screw_distance_from_center_mm + 1, 0), 
                           (-motor_screw_distance_from_center_mm - 1, 0), 
                           (0, -motor_screw_distance_from_center_mm)]

motor_holder_total_radius = motor_base_radius_mm + motor_base_thickness_mm
# Parameters
arm_sweep_radius = 50       # How wide the arc is
arm_sweep_angle = 90         # How much of a circle (degrees)
arm_thickness = 10    # Z height of the arm
arm_width = 20         # Width of the arm

# 1. Create the Path (The invisible line the arm follows)
# We start at (radius, 0) and arc towards the Y axis
path = (cq.Workplane("YZ")
        .moveTo(0, 0)
        .center(arm_sweep_radius, arm_sweep_radius) # Set center of arc to origin
        .ellipseArc(x_radius=arm_sweep_radius, y_radius=arm_sweep_radius*1.6, angle1=0, angle2=arm_sweep_angle)
        )

# 2. Create the Profile (The shape of the arm cross-section)
# We draw this on "YZ" so it stands perpendicular to the start of the path
profile = (cq.Workplane("XZ")
           .workplane(offset=0) # Move out to the start of the path
           .rect(arm_width, arm_thickness)
           )

# 3. Sweep!
arm = profile.sweep(path, isFrenet=True)

# Optional: Tag the end face for your assembly
arm = arm.faces(">>Z").tag("arm_end").end() 

motor_holder = cq.Workplane("XY").circle(motor_holder_total_radius).center(0, 0).extrude(motor_base_thickness_mm)
motor_holder = motor_holder.pushPoints([motor_screw_coordinates[0], motor_screw_coordinates[1], motor_screw_coordinates[2], motor_screw_coordinates[3]]).circle(motor_screw_radius_mm).cutThruAll()
motor_holder = motor_holder.pushPoints([(0, 0)]).circle(motor_shaft_radius_mm).cutThruAll()
motor_holder = motor_holder.faces(">Z").circle(motor_holder_total_radius).circle(motor_base_radius_mm).extrude(motor_holder_height_mm)
# wire_pocket = cq.Workplane("YZ", origin=cq.Vector(motor_base_radius_mm + motor_base_thickness_mm/2, 0, 0)).box(motor_holder_wire_pocket_length_mm, motor_holder_height_mm + motor_base_thickness_mm + drone_base_thickness_mm, motor_base_thickness_mm + 1.5)
wire_pocket = cq.Workplane("YZ", origin=cq.Vector(motor_holder_total_radius, 0,  motor_holder_height_mm + motor_base_thickness_mm/2)).box(motor_holder_wire_pocket_length_mm, motor_holder_height_mm + motor_base_thickness_mm, motor_base_thickness_mm + drone_base_thickness_mm)
wire_pocket = wire_pocket.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 135)
motor_holder = motor_holder.cut(wire_pocket)
motor_holder.faces("<<Z").tag("motorHolderBottom").end()


assembled = cq.Assembly()
assembled.add(arm, color="red", name="arm1", loc=cq.Location((0,0,0)))
assembled.add(motor_holder, color="blue", name="motor_holder1")
assembled.constrain("arm1?arm_end", "motor_holder1?motorHolderBottom", "Point")
assembled.solve()


show_object(assembled)


