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

# ... your parameters ...
arm_length = 60
arm_width = 15
arm_thickness = 5
arm_angle_degrees = -30
arm_end_length = 10
arm_end_thickness = 2

# 1. Create and Rotate Arm
arm = create_solid_box(arm_length, arm_width, arm_thickness).rotate(cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), arm_angle_degrees)

# --- FIX IS HERE ---
# Instead of edges(">X and >Z"), we do:
# 1. faces(">X") -> Select the end face
# 2. edges(">Z") -> Select the top edge OF that face
# 3. tag(...)    -> Name it
# 4. end().end() -> Go back up the stack (Edge -> Face -> Solid) so 'arm' remains the whole object
arm.faces(">X").tag("main_arm_face").end()
# arm.faces(">X").edges("<Z").tag("hinge_edge_A_B").end()

upper_arm_end = create_hollow_box(arm_end_length, arm_width, arm_thickness, arm_end_thickness)

# Same fix for the other part (Consistency is key)
upper_arm_end.faces("<X").tag("end_arm_face").end()
# upper_arm_end.faces("<X").edges("<Z").tag("hinge_edge_B_B").end()

# 2. Create Assembly
assembled = cq.Assembly()
assembled.add(arm, color="red", name="main_arm", loc=cq.Location((0,0,0)))
assembled.add(upper_arm_end, color="blue", name="upper_arm_end")

# 3. Constraints (These are correct for a hinge!)
# Point: Snaps the midpoint of Edge A to the midpoint of Edge B
assembled.constrain("main_arm?main_arm_face", "upper_arm_end?end_arm_face", "Point")
# assembled.constrain("upper_arm_end?end_arm_face", "main_arm?main_arm_face", "Axis")
# assembled.constrain("main_arm?hinge_edge_A", "upper_arm_end?hinge_edge_B", "Point")

# Axis: Aligns the direction of the edges (so they are colinear)
# assembled.constrain("main_arm?hinge_edge_A", "upper_arm_end?hinge_edge_B", "Axis")
# assembled.constrain("main_arm?hinge_edge_A", "upper_arm_end?hinge_edge_B", "Axis")

assembled.solve()

show_object(assembled)
# assembled.export("export/extra_parts.stl", "STL")
# 11,8,1,3
# 8
# 8
# 8