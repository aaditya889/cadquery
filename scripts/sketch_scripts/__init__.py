"""
sketch_scripts — Parametric, sketch-first CAD-as-Code framework.
"""

from .core import (
    Component,
    show,
    to_shape,
    to_workplane,
    duplicate,
    fuse_all,
    find_junction_edges,
    CustomSelector,
)
from .sketches import (
    rounded_rect,
    chamfered_rect,
    slotted_hole,
    regular_polygon,
    trapezoid,
    u_channel,
    l_profile,
    i_beam,
    bolt_circle_pattern,
    slotted_grille,
    hex_grid_pattern,
)
from .hardware import (
    FASTENERS,
    BEARINGS,
    get_fastener,
    get_bearing,
)
from .features import (
    BearingHousing,
    ScrewBoss,
    MountingPlate,
)
