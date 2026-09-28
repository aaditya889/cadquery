import cadquery as cq


def create_compartment_tray(
    rows: int = 2,
    cols: int = 3,
    cell_length: float = 30,
    cell_width: float = 25,
    cell_depth: float = 10,
    wall_thickness: float = 1.5,
    corner_radius: float = 2,
) -> cq.Workplane:
    """Create a grid of compartment wells for small parts storage.

    Returns a solid tray block with recessed cells. The outer dimensions are
    derived from the cell count and sizes.
    """
    outer_length = cols * cell_length + (cols + 1) * wall_thickness
    outer_width = rows * cell_width + (rows + 1) * wall_thickness
    outer_height = cell_depth + wall_thickness

    tray = (
        cq.Workplane("XY")
        .box(outer_length, outer_width, outer_height, centered=(True, True, False))
        .edges("|Z")
        .fillet(min(corner_radius, wall_thickness * 0.9))
    )

    cell_points = []
    x_start = -outer_length / 2 + wall_thickness + cell_length / 2
    y_start = -outer_width / 2 + wall_thickness + cell_width / 2
    for r in range(rows):
        for c in range(cols):
            cx = x_start + c * (cell_length + wall_thickness)
            cy = y_start + r * (cell_width + wall_thickness)
            cell_points.append((cx, cy))

    tray = (
        tray
        .faces(">Z")
        .workplane()
        .pushPoints(cell_points)
        .rect(cell_length, cell_width)
        .cutBlind(-cell_depth)
    )

    if corner_radius > 0:
        try:
            tray = tray.edges(">Z").fillet(min(corner_radius, cell_depth * 0.4))
        except Exception:
            pass

    return tray
