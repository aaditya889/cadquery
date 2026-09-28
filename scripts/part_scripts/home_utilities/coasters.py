import cadquery as cq
from cadquery import exporters
from cq_server.ui import ui, show_object

# ============================================================
# EDITABLE PARAMETERS — Change these to fit your bottles/bowls
# ============================================================

# --- Bottle Coaster ---
bottle_dia = 110.0            # mm — outer diameter (fits most water/soda bottles)
bottle_base = 3.0             # mm — base thickness
bottle_rim_h = 4.0            # mm — rim height (catches condensation)
bottle_rim_w = 3.0            # mm — rim wall thickness

# --- Bowl Coaster ---
bowl_dia = 180.0              # mm — outer diameter (large serving bowls)
bowl_base = 3.0               # mm — base thickness
bowl_rim_h = 5.0              # mm — taller rim for bigger volume
bowl_rim_w = 3.0              # mm — rim wall thickness

# --- Surface grip rings (concentric grooves prevent suction sticking) ---
ring_depth = 0.6              # mm — groove depth
ring_width = 1.5              # mm — groove width
ring_margin = 10.0            # mm — innermost ring offset from center

# --- Print settings ---
wall = 2.0                    # mm — (all rims use this as minimum; 2 perimeters @ 1mm nozzle)


# ============================================================
# COASTER BUILDER
# ============================================================

def create_coaster(diameter, base_thickness, rim_height, rim_width,
                   num_rings=3):
    """
    Parametric round coaster with raised rim and grip grooves.
    Changing any parameter cleanly rebuilds the geometry.
    """
    r_outer = diameter / 2
    r_inner = r_outer - max(rim_width, wall)

    # 1. Base disc
    coaster = (
        cq.Workplane("XY")
        .circle(r_outer)
        .extrude(base_thickness)
    )

    # 2. Raised rim — hollow cylinder sitting on the base
    rim = (
        cq.Workplane("XY")
        .workplane(offset=base_thickness)
        .circle(r_outer)
        .circle(r_inner)
        .extrude(rim_height)
    )
    coaster = coaster.union(rim)

    # 3. Concentric grip grooves on the base surface
    usable_radius = r_inner - ring_margin
    if num_rings > 0 and usable_radius > ring_width:
        spacing = usable_radius / (num_rings + 1)
        for i in range(num_rings):
            r = ring_margin + (i + 1) * spacing
            r_out = r + ring_width / 2
            r_in = max(1.0, r - ring_width / 2)
            groove = (
                cq.Workplane("XY")
                .workplane(offset=base_thickness - ring_depth)
                .circle(r_out)
                .circle(r_in)
                .extrude(ring_depth + 0.5)
            )
            coaster = coaster.cut(groove)

    # 4. Bottom chamfer — easy to pick up off surfaces
    try:
        coaster = coaster.edges("<Z").chamfer(0.5)
    except Exception:
        pass

    # 5. Inner rim fillet — smooth transition, easy to wipe clean
    try:
        coaster = (
            coaster.edges(
                cq.selectors.NearestToPointSelector((0, 0, base_thickness + 0.1))
            ).fillet(0.8)
        )
    except Exception:
        pass

    return coaster


# ============================================================
# CREATE COASTERS
# ============================================================

bottle_coaster = create_coaster(
    diameter=bottle_dia,
    base_thickness=bottle_base,
    rim_height=bottle_rim_h,
    rim_width=bottle_rim_w,
    num_rings=3,
)

bowl_coaster = create_coaster(
    diameter=bowl_dia,
    base_thickness=bowl_base,
    rim_height=bowl_rim_h,
    rim_width=bowl_rim_w,
    num_rings=4,  # more rings for bigger surface
)


# ============================================================
# Display and Export
# ============================================================

assembly = cq.Assembly()
assembly.add(bottle_coaster, name="bottle_coaster",
             color=cq.Color(0.35, 0.28, 0.2))
assembly.add(bowl_coaster,
             loc=cq.Location(cq.Vector(200, 0, 0)),
             name="bowl_coaster",
             color=cq.Color(0.25, 0.35, 0.22))

show_object(assembly)

exporters.export(bottle_coaster, "export/bottle_coaster.stl")
exporters.export(bowl_coaster, "export/bowl_coaster.stl")
