import cadquery as cq


def create_pcb_slot(
    slot_length: float = 80,
    slot_width: float = 2.0,
    slot_depth: float = 8,
    base_length: float = 0,
    base_width: float = 12,
    base_height: float = 12,
    count: int = 3,
    spacing: float = 10,
) -> cq.Workplane:
    """Create a raised block with parallel slots for holding PCB edges.

    Multiple slots are cut side-by-side so you can hold several boards
    or one board at different widths.
    """
    if base_length <= 0:
        base_length = slot_length + 10

    holder = (
        cq.Workplane("XY")
        .box(base_length, base_width, base_height, centered=(True, True, False))
        .edges("|Z")
        .fillet(2)
    )

    slot_points = []
    total_span = (count - 1) * spacing
    y_start = -total_span / 2
    for i in range(count):
        slot_points.append((0, y_start + i * spacing))

    holder = (
        holder
        .faces(">Z")
        .workplane()
        .pushPoints(slot_points)
        .slot2D(slot_length, slot_width, angle=0)
        .cutBlind(-slot_depth)
    )

    return holder


def create_iron_rest(
    notch_depth: float = 12,
    notch_width: float = 14,
    support_thickness: float = 8,
    support_spacing: float = 50,
    base_length: float = 0,
    base_width: float = 0,
    base_height: float = 5,
    notch_angle: float = 45,
) -> cq.Workplane:
    """Create a V-notch iron rest with two supports.

    Two raised V-notched supports on a base plate. The soldering iron barrel
    rests across the V-notches. Place near the mat edge so the handle hangs
    off and the tip points toward the workspace.

    notch_depth: how deep the V goes (controls how securely the iron sits)
    notch_width: width of the V opening at the top
    support_thickness: thickness of each support along X
    support_spacing: distance between the two support centers
    """
    import math

    if base_length <= 0:
        base_length = support_spacing + support_thickness + 10
    if base_width <= 0:
        base_width = notch_width + 10

    support_height = base_height + notch_depth

    # Base plate
    base = (
        cq.Workplane("XY")
        .box(base_length, base_width, base_height, centered=(True, True, False))
        .edges("|Z")
        .fillet(2)
    )

    # Build one V-notch support
    support_block = (
        cq.Workplane("XY")
        .box(support_thickness, base_width, support_height, centered=(True, True, False))
    )

    # V-notch cut from the top: two angled planes meeting at the bottom
    half_angle = math.radians(notch_angle / 2)
    cut_depth = notch_depth + 2
    cut_half_width = cut_depth * math.tan(half_angle)

    v_cut = (
        cq.Workplane("XZ")
        .workplane(offset=0)
        .center(0, support_height)
        .lineTo(cut_half_width, 0)
        .lineTo(0, -cut_depth)
        .lineTo(-cut_half_width, cut_depth)
        .close()
        .extrude(support_thickness + 2, both=True)
    )

    support = support_block.cut(v_cut)

    # Place two supports on the base
    support_left = support.translate((-support_spacing / 2, 0, 0))
    support_right = support.translate((support_spacing / 2, 0, 0))

    result = base.union(support_left).union(support_right)
    return result


def create_spool_holder(
    peg_height: float = 25,
    peg_radius: float = 10,
    base_radius: float = 18,
    base_height: float = 4,
) -> cq.Workplane:
    """Create a vertical peg to hold a solder spool.

    A wider base for stability with a narrower peg that the spool sits on.
    """
    base = (
        cq.Workplane("XY")
        .circle(base_radius)
        .extrude(base_height)
    )

    peg = (
        cq.Workplane("XY")
        .workplane(offset=base_height)
        .circle(peg_radius)
        .extrude(peg_height)
    )

    holder = base.union(peg)

    try:
        holder = holder.edges(">Z").fillet(min(1.5, peg_radius * 0.3))
    except Exception:
        pass

    return holder


def create_item_slot(
    slot_length: float = 40,
    slot_width: float = 15,
    slot_depth: float = 10,
    wall_thickness: float = 2,
    corner_radius: float = 3,
    shape: str = "rect",
) -> cq.Workplane:
    """Create a single recessed slot to hold a tool or item.

    shape: 'rect' for rectangular, 'round' for stadium/oblong,
           'circle' for circular (uses slot_width as diameter).
    """
    if shape == "circle":
        diameter = slot_width
        outer_d = diameter + wall_thickness * 2
        block = (
            cq.Workplane("XY")
            .circle(outer_d / 2)
            .extrude(slot_depth + wall_thickness)
        )
        block = (
            block
            .faces(">Z")
            .workplane()
            .circle(diameter / 2)
            .cutBlind(-slot_depth)
        )
        return block

    outer_length = slot_length + wall_thickness * 2
    outer_width = slot_width + wall_thickness * 2
    outer_height = slot_depth + wall_thickness

    block = (
        cq.Workplane("XY")
        .box(outer_length, outer_width, outer_height, centered=(True, True, False))
        .edges("|Z")
        .fillet(min(corner_radius, wall_thickness * 0.9))
    )

    if shape == "round":
        block = (
            block
            .faces(">Z")
            .workplane()
            .slot2D(slot_length, slot_width, angle=0)
            .cutBlind(-slot_depth)
        )
    else:
        block = (
            block
            .faces(">Z")
            .workplane()
            .rect(slot_length, slot_width)
            .cutBlind(-slot_depth)
        )

    return block


def create_safety_iron_holder(
    holder_inner_diameter: float = 22,
    holder_outer_diameter: float = 28,
    holder_length: float = 65,
    tilt_angle: float = 35,  # degrees tilted from vertical (around Y)
    sponge_diameter: float = 55,
    sponge_depth: float = 13,
    spool_peg_height: float = 20,
    spool_peg_radius: float = 8,
    spool_base_radius: float = 14,
    base_height: float = 3.0,  # thin base plate
    base_length: float = 0,
    base_width: float = 0,
) -> cq.Workplane:
    """Create a safety soldering iron holder with an integrated brass sponge pocket
    and a vertical solder spool holder peg on a thin, material-efficient base.
    """
    if base_length <= 0:
        base_length = max(holder_outer_diameter, sponge_diameter) + 10 # 65 mm
    if base_width <= 0:
        base_width = holder_outer_diameter + sponge_diameter + 15 # 102 mm

    # 1. Thin base plate
    base = (
        cq.Workplane("XY")
        .box(base_length, base_width, base_height, centered=(True, True, False))
        .edges("|Z")
        .fillet(3)
    )

    # 2. Sponge cup (raised ring on top of base plate)
    sponge_x = 0.0
    sponge_y = -base_width / 2 + sponge_diameter / 2 + 5
    sponge_cup = (
        cq.Workplane("XY")
        .workplane(offset=base_height)
        .center(sponge_x, sponge_y)
        .circle((sponge_diameter + 4) / 2) # 2mm wall thickness
        .extrude(sponge_depth)
        .faces(">Z")
        .workplane()
        .circle(sponge_diameter / 2)
        .cutBlind(-sponge_depth) # Hollow it out down to the base plate
    )
    base = base.union(sponge_cup)

    # 3. Slanted holder cylinder (starts at Z=0 to merge fully with the base plate)
    holder_x = base_length / 2 - holder_outer_diameter / 2 - 5
    holder_y = base_width / 2 - holder_outer_diameter / 2 - 5
    holder = (
        cq.Workplane("XY")
        .center(holder_x, holder_y)
        .transformed(rotate=cq.Vector(0, tilt_angle, 0))
        .circle(holder_outer_diameter / 2)
        .extrude(holder_length)
    )

    # Hollow out the holder
    holder = (
        holder.faces(">Z")
        .workplane()
        .circle(holder_inner_diameter / 2)
        .cutBlind(-holder_length + base_height)
    )

    base = base.union(holder)

    # 4. Solder Spool Peg
    spool_x = -base_length / 2 + spool_base_radius
    if base_length > 75.0:
        spool_x += 5
    spool_y = base_width / 2 - spool_base_radius - 2.0
    
    # Small base collar for stability
    spool_collar = (
        cq.Workplane("XY")
        .workplane(offset=base_height)
        .center(spool_x, spool_y)
        .circle(spool_base_radius)
        .extrude(2)
    )
    
    # Peg itself
    spool_peg = (
        cq.Workplane("XY")
        .workplane(offset=base_height + 2)
        .center(spool_x, spool_y)
        .circle(spool_peg_radius)
        .extrude(spool_peg_height)
    )
    
    try:
        spool_peg = spool_peg.edges(">Z").fillet(1.5)
    except Exception:
        pass

    base = base.union(spool_collar).union(spool_peg)

    # 5. Flat rectangular sponge holder (under slanted cylinder tilt)
    # NOTE: Disabled — with sponge_dia >= 65mm, the tray overlaps the cup geometry
    if base_length >= 999.0:
        sponge_tray_w = 25.0
        sponge_tray_l = 40.0
        sponge_tray_h = 7.0
        sponge_tray_d = 5.0
        sponge_tray_x = 32.0
        sponge_tray_y = 0.0
        
        sponge_tray = (
            cq.Workplane("XY")
            .workplane(offset=base_height)
            .center(sponge_tray_x, sponge_tray_y)
            .rect(sponge_tray_w + 4, sponge_tray_l + 4)
            .extrude(sponge_tray_h)
            .faces(">Z")
            .workplane()
            .rect(sponge_tray_w, sponge_tray_l)
            .cutBlind(-sponge_tray_d)
        )
        base = base.union(sponge_tray)

    # Final cut to clean up the bottom face in case of cylinder protrusions
    base = base.cut(
        cq.Workplane("XY")
        .workplane(offset=-10)
        .box(base_length + 20, base_width + 20, 10, centered=(True, True, False))
    )

    return base



def create_consolidated_tool_holder(
    pump_dia: float = 22.0,
    flux_dia: float = 15.0,
    tweezers_w: float = 8.0,
    tweezers_t: float = 20.0,
    tip_dia: float = 6.0,
    block_height: float = 18.0,
    base_thickness: float = 2.0,
) -> cq.Workplane:
    """Create a hollow skeletonized tool holder with individual raised tubes."""
    # 1. Base plate
    base = (
        cq.Workplane("XY")
        .box(85, 38, base_thickness, centered=(True, True, False))
        .edges("|Z")
        .fillet(3)
    )

    # Tube heights
    tube_height = block_height - base_thickness # 16 mm

    # 2. Pump tube (centered at -25, 0)
    pump_tube = (
        cq.Workplane("XY")
        .workplane(offset=base_thickness)
        .center(-25, 0)
        .circle((pump_dia + 4) / 2) # 2mm wall
        .extrude(tube_height)
        .faces(">Z")
        .workplane()
        .circle(pump_dia / 2)
        .cutBlind(-tube_height)
    )
    base = base.union(pump_tube)

    # 3. Flux pen tube (centered at -1, 0)
    flux_tube = (
        cq.Workplane("XY")
        .workplane(offset=base_thickness)
        .center(-1, 0)
        .circle((flux_dia + 4) / 2) # 2mm wall
        .extrude(tube_height)
        .faces(">Z")
        .workplane()
        .circle(flux_dia / 2)
        .cutBlind(-tube_height)
    )
    base = base.union(flux_tube)

    # 4. Tweezers tube (centered at 18, 0)
    tweezers_tube = (
        cq.Workplane("XY")
        .workplane(offset=base_thickness)
        .center(18, 0)
        .rect(tweezers_w + 4, tweezers_t + 4) # 2mm wall
        .extrude(tube_height)
        .faces(">Z")
        .workplane()
        .rect(tweezers_w, tweezers_t)
        .cutBlind(-tube_height)
    )
    base = base.union(tweezers_tube)

    # 5. Tip holder block (centered at 32, 0)
    tip_block = (
        cq.Workplane("XY")
        .workplane(offset=base_thickness)
        .center(32, 0)
        .rect(10, 30)
        .extrude(tube_height)
        .faces(">Z")
        .workplane()
        .pushPoints([(0, 10), (0, 0), (0, -10)])
        .circle(tip_dia / 2)
        .cutBlind(-tube_height + 2) # slightly shallower
    )
    base = base.union(tip_block)

    return base


def create_hot_air_holder(
    inner_diameter: float = 36.0,
    outer_diameter: float = 42.0,
    length: float = 45.0,
    tilt_angle: float = 25.0,
    base_thickness: float = 3.0,
    base_size: float = 50.0,
) -> cq.Workplane:
    """Create a hot air gun holder with a slanted sleeve on a thin base."""
    base = (
        cq.Workplane("XY")
        .box(base_size, base_size, base_thickness, centered=(True, True, False))
        .edges("|Z")
        .fillet(3)
    )

    # Slanted sleeve (starts at Z=0 to merge fully with the base plate)
    sleeve = (
        cq.Workplane("XY")
        .center(0, 0)
        .transformed(rotate=cq.Vector(-tilt_angle, 0, 0)) # Tilt back
        .circle(outer_diameter / 2)
        .extrude(length)
    )

    # Hollow out the sleeve
    sleeve = (
        sleeve.faces(">Z")
        .workplane()
        .circle(inner_diameter / 2)
        .cutBlind(-length + base_thickness)
    )

    # Combine
    base = base.union(sleeve)

    # Clean up bottom face in case of cylinder protrusions
    base = base.cut(
        cq.Workplane("XY")
        .workplane(offset=-10)
        .box(base_size + 20, base_size + 20, 10, centered=(True, True, False))
    )

    return base



