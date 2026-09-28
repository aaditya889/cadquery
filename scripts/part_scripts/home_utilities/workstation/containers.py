import cadquery as cq


def create_lidded_box(
    inner_length: float = 40,
    inner_width: float = 30,
    inner_depth: float = 15,
    wall_thickness: float = 2,
    floor_thickness: float = 2,
    lid_thickness: float = 2,
    lip_depth: float = 3,
    clearance: float = 0.3,
    corner_radius: float = 3,
    finger_notch: bool = True,
    finger_notch_radius: float = 8,
) -> dict:
    """Create a box with a drop-in lid.

    The lid has a lip that sits inside the box walls. Clearance accounts for
    FDM print tolerance so the lid fits without being too tight.

    Returns dict with 'box' and 'lid' as separate cq.Workplane solids,
    plus 'lid_offset_z' for how high to place the lid above the box origin.
    """
    outer_length = inner_length + wall_thickness * 2
    outer_width = inner_width + wall_thickness * 2
    outer_height = inner_depth + floor_thickness

    # --- Box (bottom face at Z=0) ---
    box = (
        cq.Workplane("XY")
        .box(outer_length, outer_width, outer_height, centered=(True, True, False))
        .edges("|Z")
        .fillet(min(corner_radius, wall_thickness * 0.9))
    )
    box = (
        box
        .faces(">Z")
        .workplane()
        .rect(inner_length, inner_width)
        .cutBlind(-inner_depth)
    )

    # --- Lid ---
    # The lip fits inside the box walls with clearance on each side
    lip_length = inner_length - clearance * 2
    lip_width = inner_width - clearance * 2

    # --- Lid (bottom face at Z=0, lip hangs below into negative Z when standalone) ---
    lid_cap = (
        cq.Workplane("XY")
        .box(outer_length, outer_width, lid_thickness, centered=(True, True, False))
        .edges("|Z")
        .fillet(min(corner_radius, wall_thickness * 0.9))
    )
    lip = (
        cq.Workplane("XY")
        .rect(lip_length, lip_width)
        .extrude(-lip_depth)
        .edges("|Z")
        .fillet(min(corner_radius - wall_thickness + 0.5, lip_depth * 0.4, 1.5))
    )
    lid = lid_cap.union(lip)

    if finger_notch:
        notch = (
            cq.Workplane("XZ")
            .workplane(offset=outer_width / 2 + 0.1)
            .circle(finger_notch_radius)
            .extrude(-wall_thickness - 0.2)
        )
        lid = lid.cut(notch)

    lid_offset_z = outer_height

    return {
        "box": box,
        "lid": lid,
        "lid_offset_z": lid_offset_z,
        "outer_length": outer_length,
        "outer_width": outer_width,
        "outer_height": outer_height + lid_thickness,
    }
