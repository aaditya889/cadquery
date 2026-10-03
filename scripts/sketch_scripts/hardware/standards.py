"""
hardware/standards.py — Standard mechanical dimensions and clearances.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class FastenerSpec:
    nominal_dia: float
    clearance_hole: float    # Normal through-hole (3D print clearance)
    close_hole: float        # Tight through-hole
    tap_hole: float          # Direct screw thread hole
    head_dia: float          # Socket head cap screw (SHCS) diameter
    head_height: float       # SHCS head height
    nut_width: float         # Hex nut flat-to-flat width
    nut_thickness: float     # Hex nut thickness
    insert_hole: float       # Heat-set insert pilot hole diameter
    insert_depth: float      # Heat-set insert depth


@dataclass(frozen=True)
class BearingSpec:
    inner_dia: float
    outer_dia: float
    thickness: float


# Metric Fasteners Table (ISO metric standard + 3D print clearance defaults)
FASTENERS: dict[str, FastenerSpec] = {
    "M2": FastenerSpec(
        nominal_dia=2.0, clearance_hole=2.4, close_hole=2.2, tap_hole=1.7,
        head_dia=3.8, head_height=2.0, nut_width=4.0, nut_thickness=1.6,
        insert_hole=3.2, insert_depth=4.0
    ),
    "M2.5": FastenerSpec(
        nominal_dia=2.5, clearance_hole=2.9, close_hole=2.7, tap_hole=2.1,
        head_dia=4.5, head_height=2.5, nut_width=5.0, nut_thickness=2.0,
        insert_hole=3.6, insert_depth=4.5
    ),
    "M3": FastenerSpec(
        nominal_dia=3.0, clearance_hole=3.4, close_hole=3.2, tap_hole=2.5,
        head_dia=5.5, head_height=3.0, nut_width=5.5, nut_thickness=2.4,
        insert_hole=4.2, insert_depth=5.7
    ),
    "M4": FastenerSpec(
        nominal_dia=4.0, clearance_hole=4.5, close_hole=4.3, tap_hole=3.3,
        head_dia=7.0, head_height=4.0, nut_width=7.0, nut_thickness=3.2,
        insert_hole=5.6, insert_depth=6.5
    ),
    "M5": FastenerSpec(
        nominal_dia=5.0, clearance_hole=5.5, close_hole=5.3, tap_hole=4.2,
        head_dia=8.5, head_height=5.0, nut_width=8.0, nut_thickness=4.0,
        insert_hole=6.8, insert_depth=7.5
    ),
    "M6": FastenerSpec(
        nominal_dia=6.0, clearance_hole=6.6, close_hole=6.4, tap_hole=5.0,
        head_dia=10.0, head_height=6.0, nut_width=10.0, nut_thickness=5.0,
        insert_hole=8.0, insert_depth=9.0
    ),
}

# Standard Deep Groove Ball Bearings
BEARINGS: dict[str, BearingSpec] = {
    "608": BearingSpec(inner_dia=8.0, outer_dia=22.0, thickness=7.0),      # Standard skate / large gimbal
    "623": BearingSpec(inner_dia=3.0, outer_dia=10.0, thickness=4.0),
    "624": BearingSpec(inner_dia=4.0, outer_dia=13.0, thickness=5.0),
    "625": BearingSpec(inner_dia=5.0, outer_dia=16.0, thickness=5.0),      # V-slot roller bearing
    "688": BearingSpec(inner_dia=8.0, outer_dia=16.0, thickness=5.0),
    "6800": BearingSpec(inner_dia=10.0, outer_dia=19.0, thickness=5.0),
    "6000": BearingSpec(inner_dia=10.0, outer_dia=26.0, thickness=8.0),
    "MR128": BearingSpec(inner_dia=8.0, outer_dia=12.0, thickness=3.5),    # Drone compact bearing
    "MR105": BearingSpec(inner_dia=5.0, outer_dia=10.0, thickness=4.0),
}


def get_fastener(size: str = "M3") -> FastenerSpec:
    """Get standardized fastener dimensions (e.g. 'M3', 'M4')."""
    size_norm = size.upper()
    if size_norm not in FASTENERS:
        raise KeyError(f"Unknown fastener size '{size}'. Available: {list(FASTENERS.keys())}")
    return FASTENERS[size_norm]


def get_bearing(model: str = "608") -> BearingSpec:
    """Get standardized ball bearing dimensions (e.g. '608', '625', 'MR128')."""
    model_norm = model.upper()
    if model_norm not in BEARINGS:
        raise KeyError(f"Unknown bearing model '{model}'. Available: {list(BEARINGS.keys())}")
    return BEARINGS[model_norm]
