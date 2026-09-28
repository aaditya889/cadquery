import cadquery as cq
import math

def create_toothed_disc_only(
    radius: float = 20,
    thickness: float = 8,
    num_teeth: int = 24,
    tooth_width: float = 2.5,
    tooth_depth: float = 1.2,
    hole_radius: float = 3.2,
) -> cq.Workplane:
    """
    Create a circular disc with radial locking V-teeth (Hirth-style joint).
    When two mating discs are pressed together, they lock at discrete angular increments
    and cannot rotate or slip under high torque loads.
    """
    # Create base cylinder centered at origin
    disc = cq.Workplane("XY").cylinder(height=thickness, radius=radius)
    
    # Create a V-groove cutter along the X-axis
    # Profile on YZ plane, extruding along positive X
    # In YZ plane: Local X maps to global Y, Local Y maps to global Z.
    cutter = (
        cq.Workplane("YZ")
        .moveTo(-tooth_width / 2, thickness / 2 + 0.1)
        .lineTo(0, thickness / 2 - tooth_depth)
        .lineTo(tooth_width / 2, thickness / 2 + 0.1)
        .close()
        .extrude(radius + 2)
    )
    
    # Cut radial V-grooves in a polar array
    for i in range(num_teeth):
        angle = i * (360.0 / num_teeth)
        rotated_cutter = cutter.rotate((0, 0, 0), (0, 0, 1), angle)
        disc = disc.cut(rotated_cutter)
        
    # Cut central pivot hole for the bolt
    disc = disc.faces(">Z").workplane().circle(hole_radius).cutThruAll()
    
    return disc


def create_toothed_hinge_ear(
    radius: float = 20,
    thickness: float = 8,
    num_teeth: int = 24,
    tooth_width: float = 2.5,
    tooth_depth: float = 1.2,
    hole_radius: float = 3.2,
    arm_width: float = 24,
    arm_thickness: float = 12,
    arm_length: float = 30,
    hex_pocket_radius: float = 6.0,
    hex_pocket_depth: float = 4.5,
    hex_pocket_side: str = "back", # "back" (opposite of teeth), "teeth", or "none"
) -> cq.Workplane:
    """
    Create a modular hinge ear consisting of a toothed locking disc and
    an extension arm block with optional hex pockets for nut/bolt capture.
    """
    # 1. Create base cylinder
    disc = cq.Workplane("XY").cylinder(height=thickness, radius=radius)
    
    # 2. Cut teeth on top face
    cutter = (
        cq.Workplane("YZ")
        .moveTo(-tooth_width / 2, thickness / 2 + 0.1)
        .lineTo(0, thickness / 2 - tooth_depth)
        .lineTo(tooth_width / 2, thickness / 2 + 0.1)
        .close()
        .extrude(radius + 2)
    )
    for i in range(num_teeth):
        angle = i * (360.0 / num_teeth)
        rotated_cutter = cutter.rotate((0, 0, 0), (0, 0, 1), angle)
        disc = disc.cut(rotated_cutter)
        
    # 3. Create the extension arm block
    # Start at X = 0, go to X = arm_length
    arm = (
        cq.Workplane("XY")
        .box(arm_length, arm_width, arm_thickness, centered=(False, True, True))
        .translate((-radius - arm_length + 2, 0, 0)) # Position it to overlap with the disc
    )
    
    # Union disc and arm
    ear = disc.union(arm)
    
    # 4. Cut central bolt hole
    ear = ear.faces(">Z").workplane().circle(hole_radius).cutThruAll()
    
    # 5. Add hex pocket for nut capture
    if hex_pocket_side == "back" and hex_pocket_depth > 0:
        # Cut on bottom face (Z = -thickness/2)
        ear = (
            ear
            .faces("<Z")
            .workplane()
            .polygon(6, hex_pocket_radius * 2)
            .cutBlind(hex_pocket_depth)
        )
    elif hex_pocket_side == "teeth" and hex_pocket_depth > 0:
        # Cut on top face (Z = thickness/2)
        ear = (
            ear
            .faces(">Z")
            .workplane()
            .polygon(6, hex_pocket_radius * 2)
            .cutBlind(hex_pocket_depth)
        )
        
    # Apply a smooth fillet at the arm connection
    try:
        ear = ear.edges("|Z").fillet(3)
    except Exception:
        pass
        
    return ear


def create_double_hinge_arm(
    arm_length: float = 200,
    radius: float = 20,
    thickness: float = 8,
    num_teeth: int = 24,
    tooth_width: float = 2.5,
    tooth_depth: float = 1.2,
    hole_radius: float = 3.2,
    arm_width: float = 24,
    arm_thickness: float = 12,
    ear1_type: str = "horizontal", # "horizontal" (XY) or "vertical" (XZ)
    ear2_type: str = "vertical",   # "horizontal" (XY) or "vertical" (XZ)
    ear1_teeth_face: str = "+",    # "+" for normal Z/Y facing teeth, "-" for opposite
    ear2_teeth_face: str = "+",
) -> cq.Workplane:
    """
    Create a heavy-duty arm connecting two interlocking hinge ears.
    The orientations of the ears can be vertical or horizontal,
    allowing full 3D multi-axis adjustments!
    """
    # 1. Create central connecting beam running along X
    beam_length = arm_length - 2 * radius + 10
    beam = cq.Workplane("XY").box(beam_length, arm_width, arm_thickness, centered=(True, True, True))
    
    # Smooth long edges for premium ergonomics and aesthetics
    beam = beam.edges("|X").fillet(2)
    
    # 2. Build Ear 1 (Left end, centered at -arm_length/2, 0, 0)
    disc1 = create_toothed_disc_only(radius, thickness, num_teeth, tooth_width, tooth_depth, hole_radius)
    
    if ear1_type == "horizontal":
        if ear1_teeth_face == "-":
            disc1 = disc1.rotate((0, 0, 0), (1, 0, 0), 180)
        ear1 = disc1.translate((-arm_length / 2, 0, 0))
    else:
        rot_angle = 90 if ear1_teeth_face == "+" else -90
        ear1 = disc1.rotate((0, 0, 0), (1, 0, 0), rot_angle).translate((-arm_length / 2, 0, 0))
        
    # 3. Build Ear 2 (Right end, centered at arm_length/2, 0, 0)
    disc2 = create_toothed_disc_only(radius, thickness, num_teeth, tooth_width, tooth_depth, hole_radius)
    
    if ear2_type == "horizontal":
        if ear2_teeth_face == "-":
            disc2 = disc2.rotate((0, 0, 0), (1, 0, 0), 180)
        ear2 = disc2.translate((arm_length / 2, 0, 0))
    else:
        rot_angle = 90 if ear2_teeth_face == "+" else -90
        ear2 = disc2.rotate((0, 0, 0), (1, 0, 0), rot_angle).translate((arm_length / 2, 0, 0))
        
    # Union beam and ears
    arm = beam.union(ear1).union(ear2)
    
    return arm


def create_armrest_clamp_top(
    clamp_length: float = 120,
    clamp_width: float = 60,
    clamp_thickness: float = 10,
    bolt_hole_radius: float = 3.2, # M6 bolts
    bolt_spacing_x: float = 100,
    bolt_spacing_y: float = 40,
    hinge_radius: float = 20,
    hinge_thickness: float = 8,
    hinge_num_teeth: int = 24,
    hinge_tooth_width: float = 2.5,
    hinge_tooth_depth: float = 1.2,
    hinge_hole_radius: float = 3.2,
) -> cq.Workplane:
    """
    Create the top clamp plate with an integrated vertical toothed hinge ear.
    This plate clamps onto the top of the office chair's armrest.
    """
    # 1. Create base plate
    plate = (
        cq.Workplane("XY")
        .box(clamp_length, clamp_width, clamp_thickness, centered=(True, True, False))
        .edges("|Z")
        .fillet(5)
    )
    
    # 2. Add bolt holes at the corners
    bolt_points = [
        (bolt_spacing_x / 2, bolt_spacing_y / 2),
        (-bolt_spacing_x / 2, bolt_spacing_y / 2),
        (bolt_spacing_x / 2, -bolt_spacing_y / 2),
        (-bolt_spacing_x / 2, -bolt_spacing_y / 2)
    ]
    plate = (
        plate
        .faces(">Z")
        .workplane()
        .pushPoints(bolt_points)
        .circle(bolt_hole_radius)
        .cutThruAll()
    )
    
    # 3. Create the integrated vertical hinge ear on the top face
    disc = create_toothed_disc_only(hinge_radius, hinge_thickness, hinge_num_teeth, hinge_tooth_width, hinge_tooth_depth, hinge_hole_radius)
    
    # Center the joint near the right edge of the clamp plate to give the arm 180° rotation clearance!
    joint_offset_x = clamp_length / 2.0 - hinge_radius
    
    # Support pedestal on top of the plate
    # We make it cover only the back half of the disc (Y from 0 to hinge_thickness/2)
    # The teeth are on the -Y face (from -4 to 0), so this leaves them completely unobstructed!
    support = (
        cq.Workplane("XY")
        .box(hinge_radius, hinge_thickness / 2.0, hinge_radius, centered=(True, False, False))
        .translate((joint_offset_x, 0, clamp_thickness))
    )
    
    # Rotate disc to stand vertically (in XZ plane, teeth facing +Y)
    rotated_disc = (
        disc
        .rotate((0, 0, 0), (1, 0, 0), 90)
        .translate((joint_offset_x, 0, clamp_thickness + hinge_radius))
    )
    
    clamp_top = plate.union(support).union(rotated_disc)
    
    # Ensure the center hole is completely clear by cutting it again through the combined body
    hole_cutter = (
        cq.Workplane("XY")
        .cylinder(hinge_thickness * 4, hinge_hole_radius)
        .rotate((0, 0, 0), (1, 0, 0), 90)
        .translate((joint_offset_x, 0, clamp_thickness + hinge_radius))
    )
    clamp_top = clamp_top.cut(hole_cutter)
    
    return clamp_top


def create_armrest_clamp_bottom(
    clamp_length: float = 120,
    clamp_width: float = 60,
    clamp_thickness: float = 10,
    bolt_hole_radius: float = 3.2,
    bolt_spacing_x: float = 100,
    bolt_spacing_y: float = 40,
    nut_pocket_radius: float = 6.0,
    nut_pocket_depth: float = 5.0,
) -> cq.Workplane:
    """
    Create the matching bottom clamp plate with recessed hex pockets for capture nuts,
    ensuring a flush bottom profile that won't scratch legs or snag clothing.
    """
    # 1. Base plate
    plate = (
        cq.Workplane("XY")
        .box(clamp_length, clamp_width, clamp_thickness, centered=(True, True, False))
        .edges("|Z")
        .fillet(5)
    )
    
    bolt_points = [
        (bolt_spacing_x / 2, bolt_spacing_y / 2),
        (-bolt_spacing_x / 2, bolt_spacing_y / 2),
        (bolt_spacing_x / 2, -bolt_spacing_y / 2),
        (-bolt_spacing_x / 2, -bolt_spacing_y / 2)
    ]
    
    # 2. Cut bolt holes through
    plate = (
        plate
        .faces(">Z")
        .workplane()
        .pushPoints(bolt_points)
        .circle(bolt_hole_radius)
        .cutThruAll()
    )
    
    # 3. Cut nut hex pockets on the bottom face (Z = 0)
    plate = (
        plate
        .faces("<Z")
        .workplane()
        .pushPoints(bolt_points)
        .polygon(6, nut_pocket_radius * 2)
        .cutBlind(nut_pocket_depth)
    )
    
    return plate


def create_laptop_tray(
    length: float = 280,
    width: float = 200,
    thickness: float = 4,
    lip_height: float = 16,
    lip_thickness: float = 4,
    bracket_bolt_spacing: float = 40,
    bolt_hole_radius: float = 1.6, # M3 bolts
    slot_width: float = 8,
    slot_spacing: float = 16,
) -> cq.Workplane:
    """
    Create a beautiful laptop/book tray plate with a front retaining lip,
    cooling slots to reduce weight and heat, and central mounting holes
    for the arm bracket.
    """
    # 1. Create flat base tray plate
    plate = (
        cq.Workplane("XY")
        .box(length, width, thickness, centered=(True, True, False))
        .edges("|Z")
        .fillet(8)
    )
    
    # 2. Add the retaining lip on the front edge
    lip = (
        cq.Workplane("XY")
        .box(length, lip_thickness, lip_height + thickness, centered=(True, False, False))
        .translate((0, -width / 2, 0))
    )
    
    try:
        lip = lip.edges(">Z").fillet(1.5)
    except Exception:
        pass
        
    tray = plate.union(lip)
    
    # 3. Add ventilation slots for aesthetic and laptop cooling
    slot_points = []
    # Left slot zone
    x_start_left = -length / 2 + 25
    x_end_left = -50
    # Right slot zone
    x_start_right = 50
    x_end_right = length / 2 - 25
    
    y_start = -width / 2 + 30
    y_end = width / 2 - 30
    slot_length = y_end - y_start
    
    # Generate slot centers
    x = x_start_left
    while x <= x_end_left:
        slot_points.append((x, 0))
        x += slot_spacing
        
    x = x_start_right
    while x <= x_end_right:
        slot_points.append((x, 0))
        x += slot_spacing
        
    # Cut slots
    tray = (
        tray
        .faces(">Z")
        .workplane()
        .pushPoints(slot_points)
        .slot2D(slot_length, slot_width, angle=90)
        .cutThruAll()
    )
    
    # 4. Add central mounting holes for the separate bracket
    bracket_holes = [
        (bracket_bolt_spacing / 2, bracket_bolt_spacing / 2),
        (-bracket_bolt_spacing / 2, bracket_bolt_spacing / 2),
        (bracket_bolt_spacing / 2, -bracket_bolt_spacing / 2),
        (-bracket_bolt_spacing / 2, -bracket_bolt_spacing / 2)
    ]
    tray = (
        tray
        .faces(">Z")
        .workplane()
        .pushPoints(bracket_holes)
        .circle(bolt_hole_radius)
        .cutThruAll()
    )
    
    return tray


def create_tray_mount_bracket(
    bracket_width: float = 60,
    bracket_length: float = 60,
    bracket_thickness: float = 6,
    bracket_bolt_spacing: float = 40,
    bolt_hole_radius: float = 1.6, # M3 bolts
    hinge_radius: float = 20,
    hinge_thickness: float = 8,
    hinge_num_teeth: int = 24,
    hinge_tooth_width: float = 2.5,
    hinge_tooth_depth: float = 1.2,
    hinge_hole_radius: float = 3.2,
) -> cq.Workplane:
    """
    Create a bracket that bolts flat onto the underside of the tray
    and provides a vertical toothed hinge ear facing downward.
    """
    # 1. Base plate
    plate = (
        cq.Workplane("XY")
        .box(bracket_length, bracket_width, bracket_thickness, centered=(True, True, False))
        .edges("|Z")
        .fillet(4)
    )
    
    # 2. Bolt holes to attach to the tray
    bracket_holes = [
        (bracket_bolt_spacing / 2, bracket_bolt_spacing / 2),
        (-bracket_bolt_spacing / 2, bracket_bolt_spacing / 2),
        (bracket_bolt_spacing / 2, -bracket_bolt_spacing / 2),
        (-bracket_bolt_spacing / 2, -bracket_bolt_spacing / 2)
    ]
    plate = (
        plate
        .faces(">Z")
        .workplane()
        .pushPoints(bracket_holes)
        .circle(bolt_hole_radius)
        .cutThruAll()
    )
    
    # 3. Add integrated vertical hinge ear on the bottom face (facing down, Z decreasing)
    disc = create_toothed_disc_only(hinge_radius, hinge_thickness, hinge_num_teeth, hinge_tooth_width, hinge_tooth_depth, hinge_hole_radius)
    
    # Pedestal extending downwards
    # We make it cover only the back half of the disc (Y from 0 to hinge_thickness/2)
    # The teeth are on the -Y face (from -4 to 0), so this leaves them completely unobstructed!
    support = (
        cq.Workplane("XY")
        .box(hinge_radius, hinge_thickness / 2.0, hinge_radius, centered=(True, False, False))
        .translate((0, 0, -hinge_radius))
    )
    
    # Rotate disc to stand vertically (XZ plane, teeth facing +Y)
    rotated_disc = (
        disc
        .rotate((0, 0, 0), (1, 0, 0), 90)
        .translate((0, 0, -hinge_radius))
    )
    
    bracket = plate.union(support).union(rotated_disc)
    
    # Ensure the center hole is completely clear by cutting it again through the combined body
    hole_cutter = (
        cq.Workplane("XY")
        .cylinder(hinge_thickness * 4, hinge_hole_radius)
        .rotate((0, 0, 0), (1, 0, 0), 90)
        .translate((0, 0, -hinge_radius))
    )
    bracket = bracket.cut(hole_cutter)
    
    return bracket


def create_locking_knob(
    outer_radius: float = 20,
    thickness: float = 12,
    bolt_hole_radius: float = 3.2, # M6 bolt
    hex_pocket_radius: float = 6.0, # M6 nut
    hex_pocket_depth: float = 6.0,
    flutes_count: int = 6,
    flute_radius: float = 4.0,
) -> cq.Workplane:
    """
    Create an ergonomic hand knob with finger grip flutes and a central
    hex pocket to capture a nut or bolt head, enabling tool-less joint adjustments.
    """
    # 1. Create base cylinder
    knob = cq.Workplane("XY").cylinder(height=thickness, radius=outer_radius)
    
    # 2. Cut finger grip flutes
    flute_distance = outer_radius
    flute_cutter = cq.Workplane("XY").cylinder(height=thickness + 2, radius=flute_radius)
    
    for i in range(flutes_count):
        angle = i * (360.0 / flutes_count)
        rotated_flute = flute_cutter.translate((flute_distance, 0, 0)).rotate((0, 0, 0), (0, 0, 1), angle)
        knob = knob.cut(rotated_flute)
        
    # 3. Cut central bolt hole
    knob = knob.faces(">Z").workplane().circle(bolt_hole_radius).cutThruAll()
    
    # 4. Cut the hex pocket on bottom face (Z = -thickness/2)
    knob = (
        knob
        .faces("<Z")
        .workplane()
        .polygon(6, hex_pocket_radius * 2)
        .cutBlind(hex_pocket_depth)
    )
    
    # Fillet the top edge for comfortable hand usage
    try:
        knob = knob.edges(">Z").fillet(1.5)
    except Exception:
        pass
        
    return knob
