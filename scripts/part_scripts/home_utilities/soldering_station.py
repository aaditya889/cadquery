import cadquery as cq
from cadquery import exporters
from ocp_vscode import show_object
import os, sys
from cq_server.ui import ui, show_object

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)

from lib.workstation import (
    create_base_mat,
    create_compartment_tray,
    create_pcb_slot,
    create_spool_holder,
    create_lidded_box,
    create_safety_iron_holder,
    create_consolidated_tool_holder,
    create_hot_air_holder,
)

# --- Base mat (fits Ender 3 Max 300x300 bed) ---
mat_length = 290
mat_width = 280
mat_thickness = 2
mat_rim_height = 1.5
mat_rim_width = 3

mat_corner_radius = 8



# --- Component trays (split left/right) ---
tray1_rows = 4
tray1_cols = 1

tray2_rows = 1
tray2_cols = 1


tray_cell_length = 25
tray_cell_width = 20
tray_cell_depth = 8
tray_wall = 2.0       # 2 perimeters with 1mm nozzle


# --- PCB holder (center-right) ---
pcb_slot_length = 80
pcb_slot_width = 1.8
pcb_slot_depth = 5
pcb_holder_base_width = 14
pcb_holder_base_height = 8
pcb_slot_count = 4
pcb_slot_spacing = 3

# --- Safety soldering iron holder parameters ---
iron_holder_inner_dia = 22
iron_holder_outer_dia = 28
iron_holder_length = 50

iron_tilt_angle = 35  # degrees tilted from vertical (around Y)
iron_sponge_dia = 67  # 65mm tool + 2mm clearance

iron_sponge_depth = 13
iron_base_height = 18

# --- Consolidated tool holder parameters ---
tool_pump_dia = 22.0
tool_flux_dia = 15.0
tool_tweezers_w = 8.0
tool_tweezers_t = 20.0
tool_tip_dia = 6.0
tool_block_height = 18.0


# --- Spool holder (top-right) ---
spool_peg_height = 20
spool_peg_radius = 8
spool_base_radius = 15

# --- Lidded storage boxes ---
# Box 1: SMD components / small ICs
box1_inner_length = 45
box1_inner_width = 30
box1_inner_depth = 12
box1_wall = 2.0       # 2 perimeters with 1mm nozzle
box1_clearance = 0.3

# Box 2: smaller box for tips, flux, etc.
box2_inner_length = 30
box2_inner_width = 25
box2_inner_depth = 10
box2_wall = 2.0
box2_clearance = 0.3

# Box 3: large box behind the tool holder
box3_inner_length = 80
box3_inner_width = 30
box3_inner_depth = 12
box3_wall = 2.0
box3_clearance = 0.3




# ============================================================
# Build components
# ============================================================

base = create_base_mat(
    length=mat_length,
    width=mat_width,
    thickness=mat_thickness,
    rim_height=mat_rim_height,
    rim_width=mat_rim_width,
    corner_radius=mat_corner_radius,
)

# Cut a large shallow pocket covering the front workspace area
# Top Y = 14 to stay 3mm below box1 bottom (Y=17)
pocket_width = 278.0
pocket_height = 145.0
pocket_depth = 1.2
pocket = (
    cq.Workplane("XY")
    .workplane(offset=mat_thickness - pocket_depth)
    .center(0, -65.5)
    .rect(pocket_width, pocket_height)
    .extrude(5.0)
    .edges("|Z")
    .fillet(3)
)
base = base.cut(pocket)

tray1 = create_compartment_tray(
    rows=tray1_rows,
    cols=tray1_cols,
    cell_length=tray_cell_length,
    cell_width=tray_cell_width,
    cell_depth=tray_cell_depth,
    wall_thickness=tray_wall,
)

tray2 = create_compartment_tray(
    rows=tray2_rows,
    cols=tray2_cols,
    cell_length=22,       # narrower to fit right of wider iron holder
    cell_width=57,
    cell_depth=23.5,      # tall 25mm height
    wall_thickness=tray_wall,
)

pcb_holder = create_pcb_slot(
    slot_length=pcb_slot_length,
    slot_width=pcb_slot_width,
    slot_depth=pcb_slot_depth,
    base_width=pcb_holder_base_width,
    base_height=pcb_holder_base_height,
    count=pcb_slot_count,
    spacing=pcb_slot_spacing,
)

iron_holder = create_safety_iron_holder(
    holder_inner_diameter=iron_holder_inner_dia,
    holder_outer_diameter=iron_holder_outer_dia,
    holder_length=iron_holder_length,
    tilt_angle=iron_tilt_angle,
    sponge_diameter=iron_sponge_dia,
    sponge_depth=iron_sponge_depth,
    spool_peg_height=spool_peg_height,
    spool_peg_radius=spool_peg_radius,
    spool_base_radius=spool_base_radius,
    base_height=3.0,
    # defaults: base_length=75 (max(28,65)+10), base_width=108 (28+65+15)
)

hot_air_holder = create_hot_air_holder(
    inner_diameter=27.0,   # fits 2.5cm gun with 2mm clearance
    outer_diameter=33.0,
    base_thickness=3.0,
    base_size=50.0,
)

tool_holder = create_consolidated_tool_holder(
    pump_dia=tool_pump_dia,
    flux_dia=tool_flux_dia,
    tweezers_w=tool_tweezers_w,
    tweezers_t=tool_tweezers_t,
    tip_dia=tool_tip_dia,
    block_height=tool_block_height,
)

storage_box_1 = create_lidded_box(
    inner_length=box1_inner_length,
    inner_width=box1_inner_width,
    inner_depth=box1_inner_depth,
    wall_thickness=box1_wall,
    clearance=box1_clearance,
)

storage_box_2 = create_lidded_box(
    inner_length=box2_inner_length,
    inner_width=box2_inner_width,
    inner_depth=box2_inner_depth,
    wall_thickness=box2_wall,
    clearance=box2_clearance,
)

storage_box_3 = create_lidded_box(
    inner_length=box3_inner_length,
    inner_width=box3_inner_width,
    inner_depth=box3_inner_depth,
    wall_thickness=box3_wall,
    clearance=box3_clearance,
)


# ============================================================
# Layout — compact column-based layout with bounding-box math
# ============================================================

margin = 6
gap = 3
z_on_mat = mat_thickness

# Component outer dimensions
tray1_outer_l = tray1_cols * tray_cell_length + (tray1_cols + 1) * tray_wall   # 28
tray1_outer_w = tray1_rows * tray_cell_width + (tray1_rows + 1) * tray_wall   # 87.5
tray2_outer_l = tray2_cols * 22 + (tray2_cols + 1) * tray_wall                # 26
tray2_outer_w = tray2_rows * 57 + (tray2_rows + 1) * tray_wall               # 61
tool_holder_l = 85
tool_holder_w = 38
iron_holder_l = 77.0   # default: max(28,67)+10
iron_holder_w = 110.0  # default: 28+67+15
hot_air_size = 50.0
box3_outer_l = box3_inner_length + 2 * box3_wall   # 83
box3_outer_w = box3_inner_width + 2 * box3_wall     # 33
box1_outer_l = box1_inner_length + 2 * box1_wall   # 48
box1_outer_w = box1_inner_width + 2 * box1_wall     # 33
box2_outer_l = box2_inner_length + 2 * box2_wall   # 33
box2_outer_w = box2_inner_width + 2 * box2_wall     # 28

# Boundaries
back_y_edge = mat_width / 2 - margin   # 134
left_x_edge = -mat_length / 2 + margin  # -139
right_x_edge = mat_length / 2 - margin  # 139

# ---- COLUMN 1 (Far Left): Tray1 (4x1 vertical) ----
tray_x = left_x_edge + tray1_outer_l / 2
tray_y = back_y_edge - tray1_outer_w / 2

# ---- COLUMN 2 (Left-Center): Hot Air, Box2, Box1 stacked vertically ----
col2_left = left_x_edge + tray1_outer_l + gap
hot_air_x = col2_left + hot_air_size / 2
hot_air_y = back_y_edge - hot_air_size / 2

box2_x = hot_air_x
box2_y = hot_air_y - hot_air_size / 2 - gap - box2_outer_w / 2

box1_x = hot_air_x
box1_y = box2_y - box2_outer_w / 2 - gap - box1_outer_w / 2

# ---- COLUMN 3 (Center): Box3, Tool Holder, PCB Holder stacked vertically ----
col3_left = col2_left + hot_air_size + gap
box3_x = col3_left + box3_outer_l / 2
box3_y = back_y_edge - box3_outer_w / 2

tool_x = box3_x
tool_y = box3_y - box3_outer_w / 2 - gap - tool_holder_w / 2

pcb_x = tool_x
pcb_y = tool_y - tool_holder_w / 2 - gap - pcb_holder_base_width / 2

# ---- COLUMN 4 (Right): Iron Holder (75x108 base) ----
col4_left = col3_left + box3_outer_l + gap
iron_x = col4_left + iron_holder_l / 2       # ~68.5
iron_y = back_y_edge - iron_holder_w / 2     # ~80

# ---- Tray2 (tall hollow box): RIGHT of iron holder ----
# Positioned at Y=68 so it's below the tilted cylinder (Y~117) — no intersection
tray2_x = iron_x + iron_holder_l / 2 + gap + tray2_outer_l / 2
tray2_y = 68.0

# ---- Sponge pocket: small raised tray on mat, below Tray2 ----
sponge_pocket_x = tray2_x
sponge_pocket_y = tray2_y - tray2_outer_w / 2 - gap - 11.0
sponge_pocket = (
    cq.Workplane("XY")
    .workplane(offset=mat_thickness)
    .center(sponge_pocket_x, sponge_pocket_y)
    .rect(34, 20)
    .extrude(5)
    .faces(">Z").workplane()
    .rect(30, 16)
    .cutBlind(-4)
    .edges("|Z").fillet(1.5)
)
base = base.union(sponge_pocket)


# ============================================================
# Assemble
# ============================================================

# 1. Complete assembly for browser preview (including lids)
station = cq.Assembly()
station.add(base, name="base", color=cq.Color(0.25, 0.25, 0.28))
station.add(tray1, loc=cq.Location(cq.Vector(tray_x, tray_y, z_on_mat)), name="component_tray_1", color=cq.Color(0.3, 0.5, 0.3))
station.add(tray2, loc=cq.Location(cq.Vector(tray2_x, tray2_y, z_on_mat)), name="component_tray_2", color=cq.Color(0.3, 0.5, 0.3))
station.add(hot_air_holder, loc=cq.Location(cq.Vector(hot_air_x, hot_air_y, z_on_mat)), name="hot_air_holder", color=cq.Color(0.25, 0.25, 0.25))
station.add(pcb_holder, loc=cq.Location(cq.Vector(pcb_x, pcb_y, z_on_mat)), name="pcb_holder", color=cq.Color(0.2, 0.4, 0.6))
station.add(iron_holder, loc=cq.Location(cq.Vector(iron_x, iron_y, z_on_mat)), name="iron_holder", color=cq.Color(0.6, 0.2, 0.2))
station.add(tool_holder, loc=cq.Location(cq.Vector(tool_x, tool_y, z_on_mat)), name="tool_holder", color=cq.Color(0.4, 0.3, 0.5))

station.add(storage_box_1["box"], loc=cq.Location(cq.Vector(box1_x, box1_y, z_on_mat)), name="storage_box_1", color=cq.Color(0.55, 0.35, 0.2))
station.add(storage_box_1["lid"], loc=cq.Location(cq.Vector(box1_x, box1_y, z_on_mat + storage_box_1["lid_offset_z"])), name="storage_lid_1", color=cq.Color(0.65, 0.45, 0.25))

station.add(storage_box_2["box"], loc=cq.Location(cq.Vector(box2_x, box2_y, z_on_mat)), name="storage_box_2", color=cq.Color(0.55, 0.35, 0.2))
station.add(storage_box_2["lid"], loc=cq.Location(cq.Vector(box2_x, box2_y, z_on_mat + storage_box_2["lid_offset_z"])), name="storage_lid_2", color=cq.Color(0.65, 0.45, 0.25))

station.add(storage_box_3["box"], loc=cq.Location(cq.Vector(box3_x, box3_y, z_on_mat)), name="storage_box_3", color=cq.Color(0.55, 0.35, 0.2))
station.add(storage_box_3["lid"], loc=cq.Location(cq.Vector(box3_x, box3_y, z_on_mat + storage_box_3["lid_offset_z"])), name="storage_lid_3", color=cq.Color(0.65, 0.45, 0.25))

show_object(station)

# 2. Export assembly WITHOUT lids (saves material and separates prints)
export_station = cq.Assembly()
export_station.add(base, name="base")
export_station.add(tray1, loc=cq.Location(cq.Vector(tray_x, tray_y, z_on_mat)), name="component_tray_1")
export_station.add(tray2, loc=cq.Location(cq.Vector(tray2_x, tray2_y, z_on_mat)), name="component_tray_2")
export_station.add(hot_air_holder, loc=cq.Location(cq.Vector(hot_air_x, hot_air_y, z_on_mat)), name="hot_air_holder")
export_station.add(pcb_holder, loc=cq.Location(cq.Vector(pcb_x, pcb_y, z_on_mat)), name="pcb_holder")
export_station.add(iron_holder, loc=cq.Location(cq.Vector(iron_x, iron_y, z_on_mat)), name="iron_holder")
export_station.add(tool_holder, loc=cq.Location(cq.Vector(tool_x, tool_y, z_on_mat)), name="tool_holder")
export_station.add(storage_box_1["box"], loc=cq.Location(cq.Vector(box1_x, box1_y, z_on_mat)), name="storage_box_1")
export_station.add(storage_box_2["box"], loc=cq.Location(cq.Vector(box2_x, box2_y, z_on_mat)), name="storage_box_2")
export_station.add(storage_box_3["box"], loc=cq.Location(cq.Vector(box3_x, box3_y, z_on_mat)), name="storage_box_3")

exporters.export(export_station.toCompound(), "export/soldering_station.stl")

# 3. Export lids in a separate file (flat at Z=0 for easy printing)
export_lids = cq.Assembly()
export_lids.add(storage_box_1["lid"], loc=cq.Location(cq.Vector(-70, 0, 0)), name="lid_1")
export_lids.add(storage_box_2["lid"], loc=cq.Location(cq.Vector(-20, 0, 0)), name="lid_2")
export_lids.add(storage_box_3["lid"], loc=cq.Location(cq.Vector(45, 0, 0)), name="lid_3")

exporters.export(export_lids.toCompound(), "export/storage_lids.stl")