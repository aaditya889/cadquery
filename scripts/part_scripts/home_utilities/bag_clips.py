import cadquery as cq
from cadquery import exporters
from cq_server.ui import ui, show_object

# ============================================================
# EDITABLE PARAMETERS — Adjust these to your needs
# All geometry is computed from these values.
# ============================================================

# --- Clip dimensions ---
clip_width = 80.0            # mm — how wide the clip opens (across the bag)
clip_depth = 25.0            # mm — how deep the bag slides in
jaw_thickness = 2.0          # mm — thickness of each jaw (2 perimeters @ 1mm nozzle)
jaw_gap = 7.0                # mm — gap between jaws (fits folded bags up to ~6mm thick)
spine_thickness = 3.0        # mm — thickness of the connecting spine
entry_bump = 1.0             # mm — inward bump near opening (helps retain bag)
bump_zone = 6.0              # mm — how far the entry bump extends from opening

# --- Grip ridges (inner jaw surfaces) ---
ridge_height = 0.6           # mm — ridge protrusion
ridge_width = 1.5            # mm — ridge thickness
ridge_count = 7              # number of ridges across the clip width

# --- Label tab (at spine end) ---
tab_length = 12.0            # mm — extension beyond spine for finger grip
tab_fillet = 3.0             # mm — rounding on the tab

# --- Clip rack ---
num_clips = 6                # number of clip slots on the rack
slot_clearance = 1.0         # mm — extra room in each slot
rack_wall = 3.0              # mm — rack wall thickness
slot_spacing = 10.0          # mm — gap between adjacent slots
screw_dia = 4.0              # mm — mounting screw hole diameter
screw_head_dia = 8.0         # mm — countersink diameter


# ============================================================
# COMPUTED (derived from parameters)
# ============================================================

clip_total_height = 2 * jaw_thickness + jaw_gap
clip_total_length = spine_thickness + clip_depth

# Rack dimensions
slot_width = clip_width + slot_clearance
slot_depth = clip_total_length + slot_clearance
rack_length = num_clips * slot_width + (num_clips + 1) * slot_spacing + 2 * rack_wall
rack_height = slot_depth + rack_wall
rack_depth = clip_total_height + rack_wall + 2


# ============================================================
# BUILD — Bag Clip
# ============================================================

# 1. Main U-channel body (solid block minus the jaw gap)
clip_body = (
    cq.Workplane("XY")
    .box(clip_total_length, clip_width, clip_total_height, centered=(False, True, False))
)

# Cut the jaw gap (open at the +X end, closed at X=0 spine end)
gap_cut = (
    cq.Workplane("XY")
    .workplane(offset=jaw_thickness)
    .center(spine_thickness + (clip_depth) / 2, 0)
    .box(clip_depth + 1, clip_width + 2, jaw_gap, centered=(True, True, False))
)
clip = clip_body.cut(gap_cut)

# 2. Entry bumps — small wedges near the opening to retain the bag
# Bottom jaw bump (tapers from opening inward)
bottom_bump = (
    cq.Workplane("XZ")
    .workplane(offset=-clip_width / 2 + 2)
    .moveTo(clip_total_length, jaw_thickness)
    .lineTo(clip_total_length - bump_zone, jaw_thickness)
    .lineTo(clip_total_length, jaw_thickness + entry_bump)
    .close()
    .extrude(clip_width - 4)
)
clip = clip.union(bottom_bump)

# Top jaw bump (mirror on the top jaw inner surface)
top_bump = (
    cq.Workplane("XZ")
    .workplane(offset=-clip_width / 2 + 2)
    .moveTo(clip_total_length, jaw_thickness + jaw_gap)
    .lineTo(clip_total_length - bump_zone, jaw_thickness + jaw_gap)
    .lineTo(clip_total_length, jaw_thickness + jaw_gap - entry_bump)
    .close()
    .extrude(clip_width - 4)
)
clip = clip.union(top_bump)

# 3. Grip ridges — raised lines on inner jaw surfaces
if ridge_count > 0:
    ridge_spacing = (clip_width - 4) / (ridge_count + 1)
    ridge_len = clip_depth - bump_zone - 2

    for i in range(ridge_count):
        ry = -clip_width / 2 + 2 + (i + 1) * ridge_spacing

        # Bottom jaw ridge
        br = (
            cq.Workplane("XY")
            .workplane(offset=jaw_thickness)
            .center(spine_thickness + ridge_len / 2 + 1, ry)
            .box(ridge_len, ridge_width, ridge_height, centered=(True, True, False))
        )
        clip = clip.union(br)

        # Top jaw ridge
        tr = (
            cq.Workplane("XY")
            .workplane(offset=jaw_thickness + jaw_gap - ridge_height)
            .center(spine_thickness + ridge_len / 2 + 1, ry)
            .box(ridge_len, ridge_width, ridge_height, centered=(True, True, False))
        )
        clip = clip.union(tr)

# 4. Label tab — extension at spine end for finger grip
tab = (
    cq.Workplane("XY")
    .center(-tab_length / 2, 0)
    .box(tab_length, clip_width, clip_total_height, centered=(True, True, False))
    .edges("|Z").fillet(tab_fillet)
)
clip = clip.union(tab)

# 5. Round the edges for comfort
try:
    clip = clip.edges(">X").fillet(0.8)
except Exception:
    pass

try:
    clip = clip.edges("<X").fillet(1.0)
except Exception:
    pass


# ============================================================
# BUILD — Clip Rack (wall-mounted)
# ============================================================

# 1. Main rack body — solid block
rack = (
    cq.Workplane("XY")
    .box(rack_length, rack_height, rack_depth, centered=(True, False, False))
    .edges("|Z").fillet(2)
)

# 2. Cut slots from the top — clips slide in vertically
for i in range(num_clips):
    sx = -rack_length / 2 + rack_wall + slot_spacing + i * (slot_width + slot_spacing) + slot_width / 2
    slot = (
        cq.Workplane("XY")
        .workplane(offset=rack_wall)
        .center(sx, rack_height - slot_depth / 2)
        .box(slot_width, slot_depth + 1, rack_depth, centered=(True, True, False))
    )
    rack = rack.cut(slot)

# 3. Screw holes for wall mounting (countersunk)
screw_y = rack_height / 2
for sx in [-rack_length / 2 + 12, rack_length / 2 - 12]:
    # Through hole
    rack = rack.cut(
        cq.Workplane("XY")
        .center(sx, screw_y)
        .circle(screw_dia / 2)
        .extrude(rack_depth + 1)
    )
    # Countersink on front face
    rack = rack.cut(
        cq.Workplane("XY")
        .workplane(offset=rack_depth - rack_wall)
        .center(sx, screw_y)
        .circle(screw_head_dia / 2)
        .extrude(rack_wall + 1)
    )


# ============================================================
# Display and Export
# ============================================================

assembly = cq.Assembly()
assembly.add(clip, name="bag_clip", color=cq.Color(0.2, 0.6, 0.3))
assembly.add(rack,
             loc=cq.Location(cq.Vector(0, -rack_height - 20, 0)),
             name="clip_rack", color=cq.Color(0.3, 0.3, 0.5))

show_object(assembly)

exporters.export(clip, "export/bag_clip.stl")
exporters.export(rack, "export/clip_rack.stl")
