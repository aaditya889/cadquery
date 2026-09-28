import cadquery as cq
from ocp_vscode import show_object
import os
import sys
import math

# Ensure library is in the import path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from lib.armrest_stand import (
    create_armrest_clamp_top,
    create_armrest_clamp_bottom,
    create_double_hinge_arm,
    create_laptop_tray,
    create_tray_mount_bracket,
    create_locking_knob,
)

# ==============================================================================
# PARAMETERS SECTION - Modify these to customize the stand
# ==============================================================================
# 1. Hinge & Joint Configuration
hinge_radius = 20.0        # Radius of the locking toothed discs (mm)
hinge_thickness = 8.0     # Thickness of the toothed discs (mm)
num_teeth = 24            # Number of teeth (24 teeth = 15-degree adjustment steps)
tooth_width = 2.5         # Width of V-teeth (mm)
tooth_depth = 1.2         # Depth of V-teeth (mm)
hole_radius = 3.2         # Central hole for joint pivot (3.2mm for M6 bolt)
hex_pocket_radius = 6.0   # Captive hex nut radius (6.0mm for M6 nut clearance)
hex_pocket_depth = 5.0    # Captive hex pocket depth (mm)

# 2. Armrest Clamp Dimensions (Adjust to fit your chair)
clamp_length = 120.0      # Length of clamping plate along the armrest (mm)
clamp_width = 65.0        # Width of clamping plate (mm)
clamp_thickness = 10.0    # Thickness of clamp plates (mm)
bolt_hole_radius = 3.2    # Clamping bolt hole radius (3.2mm for M6)
bolt_spacing_x = 95.0     # Bolt spacing along the armrest length (mm)
bolt_spacing_y = 45.0     # Bolt spacing across the armrest width (mm)

# 3. Articulation Arms (Length center-to-center)
arm1_length = 180.0       # First arm segment length (mm)
arm2_length = 150.0       # Second arm segment length (mm)
arm_width = 24.0          # Arm structural width (mm)
arm_thickness = 14.0      # Arm structural thickness (mm)

# 4. Laptop / Book Tray Dimensions (Ender 3 Max has a 300x300mm build area!)
tray_length = 280.0       # Width of tray surface for laptop/book (mm)
tray_width = 195.0        # Height of tray surface (mm)
tray_thickness = 4.0      # Thickness of tray flat area (mm)
lip_height = 15.0         # Height of front lip to stop items from sliding (mm)
lip_thickness = 4.0       # Thickness of front lip (mm)
bracket_bolt_spacing = 40.0 # Spacing for M3 screws to mount the bracket (mm)
bracket_bolt_radius = 1.6  # Hole radius for M3 screws (1.6mm)

# ==============================================================================
# MODEL GENERATION
# ==============================================================================
print("Generating 3D models for Armrest Laptop Stand...")

# 1. Generate Armrest Clamp Top and Bottom
clamp_top = create_armrest_clamp_top(
    clamp_length=clamp_length,
    clamp_width=clamp_width,
    clamp_thickness=clamp_thickness,
    bolt_hole_radius=bolt_hole_radius,
    bolt_spacing_x=bolt_spacing_x,
    bolt_spacing_y=bolt_spacing_y,
    hinge_radius=hinge_radius,
    hinge_thickness=hinge_thickness,
    hinge_num_teeth=num_teeth,
    hinge_tooth_width=tooth_width,
    hinge_tooth_depth=tooth_depth,
    hinge_hole_radius=hole_radius
)

clamp_bottom = create_armrest_clamp_bottom(
    clamp_length=clamp_length,
    clamp_width=clamp_width,
    clamp_thickness=clamp_thickness,
    bolt_hole_radius=bolt_hole_radius,
    bolt_spacing_x=bolt_spacing_x,
    bolt_spacing_y=bolt_spacing_y,
    nut_pocket_radius=hex_pocket_radius,
    nut_pocket_depth=hex_pocket_depth
)

# 2. Generate Articulation Arms
# Arm 1: Connects to vertical clamp hinge (vertical ear) and terminates in a vertical hinge.
# Both joints are vertical (pitch adjustments).
arm1 = create_double_hinge_arm(
    arm_length=arm1_length,
    radius=hinge_radius,
    thickness=hinge_thickness,
    num_teeth=num_teeth,
    tooth_width=tooth_width,
    tooth_depth=tooth_depth,
    hole_radius=hole_radius,
    arm_width=arm_width,
    arm_thickness=arm_thickness,
    ear1_type="vertical",
    ear2_type="vertical",
    ear1_teeth_face="-",  # Mates with clamp top's "+" face
    ear2_teeth_face="+"   # Mates with Arm 2's "-" face
)

# Arm 2: Connects to Arm 1 and terminates at the tray bracket.
# Both joints are vertical, allowing a gorgeous vertical scissor/pantograph lift!
arm2 = create_double_hinge_arm(
    arm_length=arm2_length,
    radius=hinge_radius,
    thickness=hinge_thickness,
    num_teeth=num_teeth,
    tooth_width=tooth_width,
    tooth_depth=tooth_depth,
    hole_radius=hole_radius,
    arm_width=arm_width,
    arm_thickness=arm_thickness,
    ear1_type="vertical",
    ear2_type="vertical",
    ear1_teeth_face="-",
    ear2_teeth_face="+"
)

# 3. Generate Laptop Tray and Mount Bracket
tray = create_laptop_tray(
    length=tray_length,
    width=tray_width,
    thickness=tray_thickness,
    lip_height=lip_height,
    lip_thickness=lip_thickness,
    bracket_bolt_spacing=bracket_bolt_spacing,
    bolt_hole_radius=bracket_bolt_radius
)

tray_bracket = create_tray_mount_bracket(
    bracket_width=60.0,
    bracket_length=60.0,
    bracket_thickness=6.0,
    bracket_bolt_spacing=bracket_bolt_spacing,
    bolt_hole_radius=bracket_bolt_radius,
    hinge_radius=hinge_radius,
    hinge_thickness=hinge_thickness,
    hinge_num_teeth=num_teeth,
    hinge_tooth_width=tooth_width,
    hinge_tooth_depth=tooth_depth,
    hinge_hole_radius=hole_radius
)

# 4. Generate Joint Tightening Knobs
knob = create_locking_knob(
    outer_radius=18.0,
    thickness=12.0,
    bolt_hole_radius=hole_radius,
    hex_pocket_radius=hex_pocket_radius,
    hex_pocket_depth=hex_pocket_depth,
    flutes_count=7,
    flute_radius=3.5
)

# ==============================================================================
# ASSEMBLY AND VISUALIZATION
# ==============================================================================
print("Assembling the full articulated system in 3D space...")
assembly = cq.Assembly()

# 1. Base Clamp Bottom (underneath)
# Center-positioned, facing downwards (offset Z by -clamp_thickness)
# Assuming armrest thickness of 40mm
armrest_thickness = 40.0
assembly.add(
    clamp_bottom,
    loc=cq.Location(cq.Vector(0, 0, -armrest_thickness - clamp_thickness)),
    name="clamp_bottom",
    color=cq.Color(0.2, 0.2, 0.2) # Dark grey
)

# 2. Base Clamp Top (on top of armrest)
assembly.add(
    clamp_top,
    loc=cq.Location(cq.Vector(0, 0, 0)),
    name="clamp_top",
    color=cq.Color(0.3, 0.5, 0.7) # Muted blue
)

# 3. Arm 1 - Pivoted at Clamp Hinge (0, 0, clamp_thickness + hinge_radius)
# To showcase joint articulation, let's rotate Arm 1 upward by 30 degrees!
# Center of the joint shifted to the right edge of the clamp top (gives 180° rotation clearance!)
joint_offset_x = clamp_length / 2.0 - hinge_radius

arm1_pivot_z = clamp_thickness + hinge_radius
arm1_loc = cq.Location(cq.Vector(joint_offset_x, 0, arm1_pivot_z)) * cq.Location(cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), 30)
# Note: The model ear1 center is at -arm1_length/2. We translate to align that center to the pivot.
arm1_positioned = arm1.translate((arm1_length / 2, 0, 0))

assembly.add(
    arm1_positioned,
    loc=arm1_loc,
    name="arm_1",
    color=cq.Color(0.9, 0.5, 0.2) # Orange
)

# 4. Arm 2 - Pivoted at the end of Arm 1
# The end of Arm 1 is at (arm1_length/2, 0, 0) in its local coordinates.
# With 30 degrees tilt, the global position of Arm 1's end is:
angle1_rad = math.radians(30)
arm2_pivot_x = joint_offset_x + arm1_length * math.cos(angle1_rad)
arm2_pivot_z = arm1_pivot_z + arm1_length * math.sin(angle1_rad)

# Let's rotate Arm 2 relative to Arm 1. Let's make it horizontal (rotate -30 degrees relative to Arm 1, so total rotation 0)
arm2_loc = cq.Location(cq.Vector(arm2_pivot_x, 0, arm2_pivot_z)) * cq.Location(cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), 0)
arm2_positioned = arm2.translate((arm2_length / 2, 0, 0))

assembly.add(
    arm2_positioned,
    loc=arm2_loc,
    name="arm_2",
    color=cq.Color(0.8, 0.4, 0.1) # Darker orange
)

# 5. Tray Bracket - Pivoted at the end of Arm 2
tray_pivot_x = arm2_pivot_x + arm2_length
tray_pivot_z = arm2_pivot_z

bracket_loc = cq.Location(cq.Vector(tray_pivot_x, 0, tray_pivot_z + hinge_radius))
# Translate the bracket model so its hinge center aligns with the origin
bracket_positioned = tray_bracket.translate((0, 0, hinge_radius))

assembly.add(
    bracket_positioned,
    loc=bracket_loc,
    name="tray_bracket",
    color=cq.Color(0.4, 0.4, 0.4) # Grey
)

# 6. Laptop/Book Tray - Mounted flat on top of the bracket (Z = tray_pivot_z + hinge_radius + bracket_thickness)
tray_loc = cq.Location(cq.Vector(tray_pivot_x, 0, tray_pivot_z + hinge_radius + 6.0)) # bracket thickness is 6.0
assembly.add(
    tray,
    loc=tray_loc,
    name="laptop_tray",
    color=cq.Color(0.9, 0.8, 0.2) # Yellow
)

# 7. Add Clamping Knobs at the Hinge Joints
# Joint 1: Base pivot
assembly.add(
    knob,
    loc=cq.Location(cq.Vector(joint_offset_x, hinge_thickness + 6, arm1_pivot_z)),
    name="knob_joint_1",
    color=cq.Color(0.8, 0.1, 0.1) # Bright red
)

# Joint 2: Elbow pivot
assembly.add(
    knob,
    loc=cq.Location(cq.Vector(arm2_pivot_x, hinge_thickness + 6, arm2_pivot_z)),
    name="knob_joint_2",
    color=cq.Color(0.8, 0.1, 0.1)
)

# Joint 3: Tray pivot
assembly.add(
    knob,
    loc=cq.Location(cq.Vector(tray_pivot_x, hinge_thickness + 6, tray_pivot_z)),
    name="knob_joint_3",
    color=cq.Color(0.8, 0.1, 0.1)
)

# ==============================================================================
# EXPORTS AND RENDERING
# ==============================================================================
# Ensure export directory exists
export_dir = os.path.join(parent_dir, "export", "armrest_stand")
os.makedirs(export_dir, exist_ok=True)

print(f"Exporting individual printable parts (STLs and STEPs) to {export_dir}...")
# 1. STL Exports (For 3D printing slicers)
cq.exporters.export(clamp_top, os.path.join(export_dir, "1_clamp_top.stl"))
cq.exporters.export(clamp_bottom, os.path.join(export_dir, "2_clamp_bottom.stl"))
cq.exporters.export(arm1, os.path.join(export_dir, "3_articulation_arm_1.stl"))
cq.exporters.export(arm2, os.path.join(export_dir, "4_articulation_arm_2.stl"))
cq.exporters.export(tray_bracket, os.path.join(export_dir, "5_tray_mount_bracket.stl"))
cq.exporters.export(tray, os.path.join(export_dir, "6_laptop_tray.stl"))
cq.exporters.export(knob, os.path.join(export_dir, "7_joint_locking_knob.stl"))

# 2. STEP Exports (For CAD & Finite Element Analysis)
cq.exporters.export(clamp_top, os.path.join(export_dir, "1_clamp_top.step"), "STEP")
cq.exporters.export(clamp_bottom, os.path.join(export_dir, "2_clamp_bottom.step"), "STEP")
cq.exporters.export(arm1, os.path.join(export_dir, "3_articulation_arm_1.step"), "STEP")
cq.exporters.export(arm2, os.path.join(export_dir, "4_articulation_arm_2.step"), "STEP")
cq.exporters.export(tray_bracket, os.path.join(export_dir, "5_tray_mount_bracket.step"), "STEP")
cq.exporters.export(tray, os.path.join(export_dir, "6_laptop_tray.step"), "STEP")
cq.exporters.export(knob, os.path.join(export_dir, "7_joint_locking_knob.step"), "STEP")
assembly.save(os.path.join(export_dir, "armrest_stand_assembly.step"))



print("Export complete!")

# Render in VS Code OCP Cad Viewer
try:
    show_object(assembly)
    print("3D Model successfully loaded in OCP CAD Viewer!")
except Exception as e:
    print(f"\nNote: STL files exported successfully. OCP VSCode viewer is not running or accessible (headless mode): {e}")
