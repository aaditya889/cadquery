import cadquery as cq
from cadquery import exporters
from cq_server.ui import ui, show_object

# ============================================================
# EDITABLE PARAMETERS — Adjust these to fit YOUR sink
# All geometry is computed from these values.
# ============================================================

# --- Sink rim (MEASURE THESE!) ---
sink_rim_thickness = 8.0     # mm — thickness of your sink rim/edge
hook_clearance = 1.5         # mm — gap around rim for easy slide-on
hook_drop = 25.0             # mm — depth of inner arm (prevents tilting outward)

# --- Caddy body ---
caddy_length = 200.0         # mm — total width (left to right)
caddy_depth = 80.0           # mm — front to back
caddy_height = 100.0         # mm — wall height
wall = 2.0                   # mm — wall thickness (2 perimeters @ 1mm nozzle)
corner_fillet = 4.0          # mm — rounded vertical edges

# --- Compartments (inner widths, left to right) ---
sponge_width = 82.0          # mm — sponge compartment
brush_width = 52.0           # mm — scrub brush compartment
# soap_width auto-calculated from remaining space

# --- Drainage ---
drain_dia = 5.0              # mm — drainage hole diameter
drain_spacing = 12.0         # mm — center-to-center spacing


# ============================================================
# COMPUTED (derived from parameters — don't edit)
# ============================================================

# Compartment X boundaries (left edge of mat is -caddy_length/2)
c1_start = -caddy_length / 2 + wall
c1_end = c1_start + sponge_width
div1_x = c1_end + wall / 2

c2_start = c1_end + wall
c2_end = c2_start + brush_width
div2_x = c2_end + wall / 2

c3_start = c2_end + wall
c3_end = caddy_length / 2 - wall
soap_width = c3_end - c3_start

# Hook profile coordinates (YZ plane)
back_inner = caddy_depth / 2 - wall
back_outer = caddy_depth / 2
ch_back = back_outer + hook_clearance + sink_rim_thickness + hook_clearance
arm_outer = ch_back + wall
hook_h = hook_drop + wall


# ============================================================
# BUILD
# ============================================================

# 1. Main body — hollow box, open at top
outer = (
    cq.Workplane("XY")
    .box(caddy_length, caddy_depth, caddy_height, centered=(True, True, False))
    .edges("|Z").fillet(corner_fillet)
)
inner_void = (
    cq.Workplane("XY")
    .workplane(offset=wall)
    .box(caddy_length - 2 * wall, caddy_depth - 2 * wall, caddy_height,
         centered=(True, True, False))
)
body = outer.cut(inner_void)

# 2. Internal dividers — two walls splitting into 3 compartments
for dx in [div1_x, div2_x]:
    div = (
        cq.Workplane("XY")
        .workplane(offset=wall)
        .center(dx, 0)
        .box(wall, caddy_depth - 2 * wall, caddy_height - wall,
             centered=(True, True, False))
    )
    body = body.union(div)

# 3. Hook — 2D profile in YZ plane, extruded along caddy length
#
#    Profile (side view, Y+ = toward sink, Z+ = up):
#
#       P2 ──────────── P3
#       │                │
#  P1 ──┘   P7 ── P6    └── P4    ← bridge + inner arm
#  │        │      │         │
#  │        │ RIM  │    P5 ──┘    ← arm bottom
#  │        │ SLOT │
#  P8 ──────┘      │
#                   │
#  (caddy back wall continues down)

hook_len = caddy_length - 2 * corner_fillet

P1 = (back_inner, caddy_height)
P2 = (back_inner, caddy_height + hook_h)
P3 = (arm_outer,  caddy_height + hook_h)
P4 = (arm_outer,  caddy_height + wall)
P5 = (ch_back,    caddy_height + wall)
P6 = (ch_back,    caddy_height + hook_h - wall)
P7 = (back_outer, caddy_height + hook_h - wall)
P8 = (back_outer, caddy_height)

hook = (
    cq.Workplane("YZ")
    .workplane(offset=-hook_len / 2)
    .moveTo(*P1)
    .lineTo(*P2).lineTo(*P3).lineTo(*P4)
    .lineTo(*P5).lineTo(*P6).lineTo(*P7).lineTo(*P8)
    .close()
    .extrude(hook_len)
)
body = body.union(hook)

# 4. Drainage holes — grid in each compartment floor
compartments = [
    ((c1_start + c1_end) / 2, sponge_width),
    ((c2_start + c2_end) / 2, brush_width),
    ((c3_start + c3_end) / 2, soap_width),
]
inner_d = caddy_depth - 2 * wall

for cx, cw in compartments:
    nx = max(1, int((cw - 2 * drain_dia) / drain_spacing) + 1)
    ny = max(1, int((inner_d - 2 * drain_dia) / drain_spacing) + 1)
    holes = (
        cq.Workplane("XY")
        .center(cx, 0)
        .rarray(drain_spacing, drain_spacing, nx, ny)
        .circle(drain_dia / 2)
        .extrude(wall + 1)
    )
    body = body.cut(holes)

# 5. Smooth top edges
try:
    body = body.edges(
        cq.selectors.BoxSelector(
            (-caddy_length / 2 - 1, -caddy_depth / 2 - 1, caddy_height - 0.5),
            (caddy_length / 2 + 1, caddy_depth / 2 - wall, caddy_height + 0.5),
        )
    ).fillet(0.8)
except Exception:
    pass


# ============================================================
# Display and Export
# ============================================================

show_object(body)
exporters.export(body, "export/sink_caddy.stl")
