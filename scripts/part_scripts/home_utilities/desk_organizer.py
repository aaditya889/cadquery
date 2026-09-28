import cadquery as cq
from cadquery import exporters
import os
from cq_server.ui import ui, show_object

# Create export directory
os.makedirs("export/desk_organizer", exist_ok=True)

# --- Basket Dimensions ---
basket_length = 250.0         # mm — inner length (X)
basket_width = 200.0          # mm — inner width (Y) (expanded for extra room)
basket_height = 90.0          # mm — inner height (Z)

# --- Mesh/Grid Parameters (optimized for 3D printing) ---
frame_w = 4.0                 # mm — width of top/bottom frame borders (exactly 4 perimeters @ 1mm nozzle)
frame_h = 4.0                 # mm — height of top/bottom frame borders (exactly 10 layers @ 0.4mm height)
post_size = 6.0               # mm — corner post thickness (exactly 6 perimeters @ 1mm nozzle)
rod_w = 4.0                   # mm — thickness of mesh rods (exactly 2 perimeters @ 1mm nozzle)
grid_spacing_x = 35.0         # mm — spacing between vertical rods (wider for faster print)
grid_spacing_y = 35.0         # mm — spacing between vertical rods (wider for faster print)
num_horiz_rows = 1            # number of intermediate horizontal support bands (1 is enough for 75mm height)

# --- Hanging Brackets (C-Clamps) ---
desk_thickness_max = 45.0     # mm — maximum desk thickness to accommodate
bracket_width = 20.0          # mm — width of the bracket arm
bracket_thickness = 6.0       # mm — thickness of clamp arms (high strength)
clamp_depth = 45.0            # mm — how far the clamp slides onto the desk
clearance_above_desk = desk_thickness_max + 2   # mm — vertical drop from desk top to basket top

# --- T-Slot Connector ---
tslot_w = 20.0                # mm — T-slot outer block width
tslot_h = 50.0                # mm — T-slot length

# ============================================================
# DERIVED VALUES
# ============================================================
outer_l = basket_length + 2 * frame_w
outer_w = basket_width + 2 * frame_w
total_h = basket_height + 2 * frame_h

# Centerlines of the four walls
y_front = -outer_w / 2 + frame_w / 2
y_back = outer_w / 2 - frame_w / 2
x_left = -outer_l / 2 + frame_w / 2
x_right = outer_l / 2 - frame_w / 2

# Span of windows (between corner posts)
post_span_x = outer_l - 2 * post_size
post_span_y = outer_w - 2 * post_size
window_h = basket_height

# Bracket slot positions (symmetrical along X)
bracket_offset_x = 60.0


# ============================================================
# 1. BUILD THE BASKET (Additive Wire-Mesh Assembly)
# ============================================================

# --- Bottom Frame Rim ---
bottom_frame = (
    cq.Workplane("XY")
    .rect(outer_l, outer_w)
    .rect(basket_length, basket_width)
    .extrude(frame_h)
)
basket = bottom_frame

# --- Top Frame Rim ---
top_frame = (
    cq.Workplane("XY")
    .workplane(offset=total_h - frame_h)
    .rect(outer_l, outer_w)
    .rect(basket_length, basket_width)
    .extrude(frame_h)
)
basket = basket.union(top_frame)

# --- Corner Posts ---
for xs in [-1, 1]:
    for ys in [-1, 1]:
        px = xs * (outer_l / 2 - post_size / 2)
        py = ys * (outer_w / 2 - post_size / 2)
        post = (
            cq.Workplane("XY")
            .workplane(offset=frame_h)
            .center(px, py)
            .box(post_size, post_size, window_h, centered=(True, True, False))
        )
        basket = basket.union(post)

# --- Vertical Rods (Front & Back Walls) ---
window_l = outer_l - 2 * post_size
num_rods_x = int(window_l / grid_spacing_x)
for i in range(num_rods_x):
    rx = -window_l / 2 + (i + 1) * window_l / (num_rods_x + 1)
    for y_pos in [y_front, y_back]:
        # Starts 0.5mm inside bottom frame, ends 0.5mm inside top frame
        rod = (
            cq.Workplane("XY")
            .workplane(offset=frame_h - 0.5)
            .center(rx, y_pos)
            .box(rod_w, rod_w, window_h + 1.0, centered=(True, True, False))
        )
        basket = basket.union(rod)

# --- Vertical Rods (Left & Right Walls) ---
window_w = outer_w - 2 * post_size
num_rods_y = int(window_w / grid_spacing_y)
for i in range(num_rods_y):
    ry = -window_w / 2 + (i + 1) * window_w / (num_rods_y + 1)
    for x_pos in [x_left, x_right]:
        # Starts 0.5mm inside bottom frame, ends 0.5mm inside top frame
        rod = (
            cq.Workplane("XY")
            .workplane(offset=frame_h - 0.5)
            .center(x_pos, ry)
            .box(rod_w, rod_w, window_h + 1.0, centered=(True, True, False))
        )
        basket = basket.union(rod)

# --- Horizontal Rods (All Walls) ---
horiz_spacing = window_h / (num_horiz_rows + 1)
for r in range(num_horiz_rows):
    rz = frame_h + (r + 1) * horiz_spacing
    # Front and back horizontal bands (overlap corner posts by 0.5mm on each end)
    for y_pos in [y_front, y_back]:
        band = (
            cq.Workplane("XY")
            .workplane(offset=rz - rod_w / 2)
            .center(0, y_pos)
            .box(post_span_x + 1.0, rod_w, rod_w, centered=(True, True, False))
        )
        basket = basket.union(band)
    # Left and right horizontal bands (overlap corner posts by 0.5mm on each end)
    for x_pos in [x_left, x_right]:
        band = (
            cq.Workplane("XY")
            .workplane(offset=rz - rod_w / 2)
            .center(x_pos, 0)
            .box(rod_w, post_span_y + 1.0, rod_w, centered=(True, True, False))
        )
        basket = basket.union(band)

# --- Floor Grid (Ribs across the bottom frame) ---
# X-direction ribs (overlap outer frames by 0.5mm on each end)
for i in range(num_rods_x):
    rx = -window_l / 2 + (i + 1) * window_l / (num_rods_x + 1)
    rib = (
        cq.Workplane("XY")
        .workplane(offset=frame_h / 2 - rod_w / 2)
        .center(rx, 0)
        .box(rod_w, basket_width + frame_w + 1.0, rod_w, centered=(True, True, False))
    )
    basket = basket.union(rib)

# Y-direction ribs (overlap outer frames by 0.5mm on each end)
for i in range(num_rods_y):
    ry = -window_w / 2 + (i + 1) * window_w / (num_rods_y + 1)
    rib = (
        cq.Workplane("XY")
        .workplane(offset=frame_h / 2 - rod_w / 2)
        .center(0, ry)
        .box(basket_length + frame_w + 1.0, rod_w, rod_w, centered=(True, True, False))
    )
    basket = basket.union(rib)

# --- Side wall cable routing holes with bezel rings ---
side_hole_dia = 46.0           # mm — cable hole diameter
ring_outer_dia = side_hole_dia + 6.0

for x_pos in [x_left, x_right]:
    # Solid ring/bezel aligned with wall thickness
    ring = (
        cq.Workplane("YZ")
        .workplane(offset=x_pos - frame_w / 2)
        .center(0, total_h / 2)
        .circle(ring_outer_dia / 2)
        .circle(side_hole_dia / 2)
        .extrude(frame_w)
    )
    basket = basket.union(ring)

# Cut the actual holes through the rings and intersecting mesh rods
for x_pos in [x_left, x_right]:
    hole = (
        cq.Workplane("YZ")
        .workplane(offset=x_pos - frame_w / 2 - 1.0)
        .center(0, total_h / 2)
        .circle(side_hole_dia / 2)
        .extrude(frame_w + 2.0)
    )
    basket = basket.cut(hole)


# ============================================================
# 2. ADD T-SLOT TRACKS TO THE BACK WALL
# ============================================================

def add_tslot_track(obj, x_pos):
    # Outer block housing the slot
    track_block = (
        cq.Workplane("XY")
        .workplane(offset=total_h - tslot_h)
        .center(x_pos, -outer_w / 2 - 4.0)
        .box(tslot_w, 8.0, tslot_h, centered=(True, True, False))
    )
    obj = obj.union(track_block)
    
    # Cut out the T-slot profile
    # Wide part of T inside
    t_wide = (
        cq.Workplane("XY")
        .workplane(offset=total_h - tslot_h + 4.0)  # leaves 4mm stopper at bottom
        .center(x_pos, -outer_w / 2 - 2.0)
        .box(13.0, 4.0, tslot_h, centered=(True, True, False))
    )
    obj = obj.cut(t_wide)
    
    # Narrow slot neck opening to the outside
    t_narrow = (
        cq.Workplane("XY")
        .workplane(offset=total_h - tslot_h + 4.0)
        .center(x_pos, -outer_w / 2 - 6.0)
        .box(7.0, 4.5, tslot_h, centered=(True, True, False))
    )
    obj = obj.cut(t_narrow)
    
    return obj

basket = add_tslot_track(basket, -bracket_offset_x)
basket = add_tslot_track(basket, bracket_offset_x)


# ============================================================
# 3. BUILD DETACHABLE C-CLAMP BRACKETS
# ============================================================
# Profile path of the C-clamp arm in YZ plane
clamp_mouth = desk_thickness_max + 6.0
total_clamp_height = clearance_above_desk + tslot_h

t_base_width = 3.0
t_base_thickness = 5.0
t_flat_thickness = 2.0
t_width = 10.0
t_height = 49.0

clamp_vertical_thickness = 3.0
clamp_vertical_extra_thickness = 1.0
clamp_bottom_vertical_extra_thickness = 1.0
upper_clamp_extra_thickness = 0.0

bracket_profile = (
    cq.Workplane("YZ")
    .moveTo(0, 0)
    .lineTo(clamp_depth, 0)
    .lineTo(clamp_depth, bracket_thickness + upper_clamp_extra_thickness)
    .lineTo(-clamp_vertical_thickness - clamp_vertical_extra_thickness, bracket_thickness + upper_clamp_extra_thickness)
    .lineTo(-clamp_vertical_thickness - clamp_vertical_extra_thickness, -total_clamp_height)
    .lineTo(clamp_bottom_vertical_extra_thickness, -total_clamp_height)
    .lineTo(clamp_bottom_vertical_extra_thickness, -total_clamp_height + tslot_h)
    .lineTo(0, -total_clamp_height + tslot_h)
    .lineTo(0, -clamp_mouth)
    .lineTo(clamp_depth - 10.0, -clamp_mouth)
    .lineTo(clamp_depth - 10.0, -clamp_mouth + 4.0)
    .lineTo(0, -clamp_mouth + 4.0)
    .lineTo(0, 0)
    .close()
)

bracket = bracket_profile.extrude(bracket_width)
bracket = bracket.translate((-bracket_width / 2, 0, 0))

# Add the T-connector onto the bracket spine
t_connector = (
    cq.Workplane("XY")
    .workplane(offset=-total_clamp_height)
    .center(0, -clamp_vertical_thickness - clamp_bottom_vertical_extra_thickness - (t_base_thickness/2))
    .box(t_base_width, t_base_thickness, t_height, centered=(True, True, False))
)
t_head = (
    cq.Workplane("XY")
    .workplane(offset=-total_clamp_height)
    .center(0, - clamp_vertical_thickness - clamp_bottom_vertical_extra_thickness - (t_flat_thickness/2) -(t_base_thickness))
    .box(t_width, t_flat_thickness, t_height, centered=(True, True, False))
)
bracket = bracket.union(t_connector).union(t_head)

# Rotate bracket to vertical assembly orientation
bracket = bracket.rotate((0, 0, 0), (1, 0, 0), -90)
bracket = bracket.translate((0, -outer_w / 2 - 4.0, total_h))


# ============================================================
# 4. BUILD THE LOCKING WEDGES
# ============================================================

def create_locking_wedge(max_thickness):
    w_len = clamp_depth - 5.0
    w_width = bracket_width - 1.0
    slope_depth = 4.0
    
    # Start the profile in XZ
    wp = (
        cq.Workplane("XZ")
        .moveTo(0, slope_depth)
        .lineTo(w_len, 0)
        .lineTo(w_len, max_thickness)
    )
    
    # Generate ridge centers from right to left (descending X)
    centers = sorted([x for x in range(5, int(w_len) - 5, 6)], reverse=True)
    
    for cx in centers:
        wp = (
            wp.lineTo(cx + 1.0, max_thickness)
            .lineTo(cx + 1.0, max_thickness + 1.0)
            .lineTo(cx - 1.0, max_thickness + 1.0)
            .lineTo(cx - 1.0, max_thickness)
        )
        
    wp = wp.lineTo(0, max_thickness).close()
    wedge_solid = wp.extrude(w_width)
    
    # Center the wedge in Y to match bracket alignment
    # Since XZ extrudes in -Y, we translate by +w_width/2 to center it around Y=0
    wedge_solid = wedge_solid.translate((0, w_width / 2, 0))
    
    return wedge_solid

wedge_thin = create_locking_wedge(12.0)
wedge_thick = create_locking_wedge(20.0)


# ============================================================
# DISPLAY & EXPORTS
# ============================================================

# cq-server cannot tessellate an Assembly passed to show_object() —
# it re-wraps it with a flat color and mangles the internal metadata.
# Workaround: pass each solid individually with color as an options tuple.

# Position the two brackets symmetrically for preview
bracket_left  = bracket.translate((-bracket_offset_x, 0, 0))
bracket_right = bracket.translate(( bracket_offset_x, 0, 0))

show_object(basket,        options={"color": (0.85, 0.85, 0.85)})
show_object(bracket_left,  options={"color": (0.8,  0.1,  0.1)})
show_object(bracket_right, options={"color": (0.8,  0.1,  0.1)})
show_object(wedge_thin.translate((0,  outer_w / 2 + 40, 0)), options={"color": (0.2, 0.6, 0.2)})
show_object(wedge_thick.translate((0, outer_w / 2 + 70, 0)), options={"color": (0.2, 0.6, 0.2)})

# Export STL files
exporters.export(basket, "export/desk_organizer/mesh_basket.stl")
bracket_flat = bracket.rotate((0, 0, 0), (1, 0, 0), 90).translate((0, 0, 0))
exporters.export(bracket_flat, "export/desk_organizer/bracket.stl")
exporters.export(wedge_thin, "export/desk_organizer/wedge_thin.stl")
exporters.export(wedge_thick, "export/desk_organizer/wedge_thick.stl")
