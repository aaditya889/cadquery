import cadquery as cq


def create_base_mat(
    length: float = 280,
    width: float = 200,
    thickness: float = 4,
    rim_height: float = 2,
    rim_width: float = 3,
    corner_radius: float = 8,
) -> cq.Workplane:
    """Create a flat rectangular mat base with raised rim and rounded corners.

    The rim runs along the perimeter and keeps small parts from rolling off.
    """
    base = (
        cq.Workplane("XY")
        .rect(length, width)
        .extrude(thickness)
        .edges("|Z")
        .fillet(corner_radius)
    )

    if rim_height > 0 and rim_width > 0:
        rim_outer = (
            cq.Workplane("XY")
            .workplane(offset=thickness)
            .rect(length, width)
            .extrude(rim_height)
            .edges("|Z")
            .fillet(corner_radius)
        )
        rim_inner = (
            cq.Workplane("XY")
            .workplane(offset=thickness)
            .rect(length - rim_width * 2, width - rim_width * 2)
            .extrude(rim_height)
            .edges("|Z")
            .fillet(max(corner_radius - rim_width, 1))
        )
        rim = rim_outer.cut(rim_inner)
        base = base.union(rim)

    return base
