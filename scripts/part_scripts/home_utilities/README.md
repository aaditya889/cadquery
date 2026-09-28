# Home Utilities — CadQuery Scripts

## Soldering Station Mat

`soldering_station.py` — A 3D-printable soldering workstation mat with modular tool holders, storage trays, and lidded boxes. Designed for the **Ender 3 Max** (300x300x340mm build volume).

### Layout

All tool holders sit in the **top half** of the mat (two rows), leaving the **bottom half** as open workspace for PCB work.

```
 _______________________________________________________________
|                                                               |
|  [Comp. Tray]  [PCB Holder]  [Iron Rest]  [Spool]            |
|  [Tweezers] [Flux] [Pump]  [Box 2] [Box 1]                   |
|                                                               |
|                                                               |
|                    (open workspace)                            |
|                                                               |
|_______________________________________________________________|
```

### How to modify

All dimensions are **named variables at the top** of `soldering_station.py`. Change any value and re-run to regenerate the model.

#### Resize existing components

Edit the parameter section (lines 20-82). Examples:

```python
# Make the tray bigger: 3 rows, 4 cols
tray_rows = 3
tray_cols = 4

# Deeper V-notch to hold the iron more securely
iron_notch_depth = 16

# Larger spool peg for a bigger spool
spool_peg_radius = 12
spool_base_radius = 20
```

#### Add another component

1. Build it using a library function:
   ```python
   extra_tray = create_compartment_tray(rows=1, cols=5, cell_length=15, cell_depth=6)
   ```

2. Compute its position (use `cursor_x` pattern or manual coordinates):
   ```python
   extra_tray_x = 0
   extra_tray_y = -mat_width / 2 + 30
   ```

3. Add to assembly:
   ```python
   station.add(extra_tray,
       loc=cq.Location(cq.Vector(extra_tray_x, extra_tray_y, z_on_mat)),
       name="extra_tray", color=cq.Color(0.3, 0.6, 0.3))
   ```

#### Remove a component

Comment out or delete the `station.add(...)` call for that component. You can also remove its build step and parameters if you want to clean up.

### Export

The script exports to `export/soldering_station.stl` and also calls `show_object(station)` for the OCP VSCode viewer.

---

## Workstation Library Reference (`lib/workstation/`)

All functions live in `lib/workstation/` and are importable:

```python
import sys
sys.path.append('/path/to/scripts')
from lib.workstation import (
    create_base_mat,
    create_compartment_tray,
    create_pcb_slot,
    create_iron_rest,
    create_spool_holder,
    create_item_slot,
    create_lidded_box,
)
```

Every function returns a `cq.Workplane` (except `create_lidded_box` which returns a dict). All components have their **bottom face at Z=0** so placement is straightforward — just set the Z coordinate to the surface height you're placing on.

---

### `create_base_mat()` — `lib/workstation/base.py`

Flat rectangular base with optional raised perimeter rim.

| Parameter | Default | Description |
|---|---|---|
| `length` | 280 | Mat length along X (mm) |
| `width` | 200 | Mat width along Y (mm) |
| `thickness` | 4 | Flat base thickness (mm) |
| `rim_height` | 2 | Height of the raised perimeter rim (0 to disable) |
| `rim_width` | 3 | Rim wall thickness (mm) |
| `corner_radius` | 8 | Rounded corner radius (mm) |

**Returns:** `cq.Workplane`

---

### `create_compartment_tray()` — `lib/workstation/trays.py`

Grid of recessed wells for sorting small parts (screws, SMD components, etc.).

| Parameter | Default | Description |
|---|---|---|
| `rows` | 2 | Number of cell rows |
| `cols` | 3 | Number of cell columns |
| `cell_length` | 30 | Length of each cell along X (mm) |
| `cell_width` | 25 | Width of each cell along Y (mm) |
| `cell_depth` | 10 | Depth of each well (mm) |
| `wall_thickness` | 1.5 | Thickness of walls between cells (mm) |
| `corner_radius` | 2 | Fillet on cell top edges (mm) |

**Returns:** `cq.Workplane`

**Outer dimensions (derived):**
- `outer_length = cols * cell_length + (cols + 1) * wall_thickness`
- `outer_width = rows * cell_width + (rows + 1) * wall_thickness`
- `outer_height = cell_depth + wall_thickness`

---

### `create_pcb_slot()` — `lib/workstation/holders.py`

Raised block with parallel oblong slots. Insert a PCB edge into any slot to hold it upright.

| Parameter | Default | Description |
|---|---|---|
| `slot_length` | 80 | Length of each slot along X (mm) — should match your longest PCB |
| `slot_width` | 2.0 | Width of slot opening (mm) — match PCB thickness (1.6mm standard + clearance) |
| `slot_depth` | 8 | How deep the slot goes (mm) — deeper = more grip |
| `base_length` | 0 | Outer block length (0 = auto: slot_length + 10) |
| `base_width` | 12 | Outer block width along Y (mm) |
| `base_height` | 12 | Outer block height (mm) |
| `count` | 3 | Number of parallel slots |
| `spacing` | 10 | Distance between slot centers along Y (mm) |

**Returns:** `cq.Workplane`

---

### `create_iron_rest()` — `lib/workstation/holders.py`

Two V-notch supports on a base plate. Lay the soldering iron barrel across both notches. Place near the mat edge so the handle hangs off.

| Parameter | Default | Description |
|---|---|---|
| `notch_depth` | 12 | Depth of the V-notch (mm) — deeper = more secure |
| `notch_width` | 14 | Width of V opening at top (mm) — should exceed iron barrel diameter |
| `support_thickness` | 8 | Thickness of each support wall along X (mm) |
| `support_spacing` | 50 | Distance between the two support centers (mm) |
| `base_length` | 0 | Outer base length (0 = auto: spacing + thickness + 10) |
| `base_width` | 0 | Outer base width (0 = auto: notch_width + 10) |
| `base_height` | 5 | Height of flat base plate (mm) |
| `notch_angle` | 45 | V-notch opening angle in degrees (wider = easier to drop in, narrower = more grip) |

**Returns:** `cq.Workplane`

---

### `create_spool_holder()` — `lib/workstation/holders.py`

Vertical peg on a wider base. Drop a solder spool over the peg.

| Parameter | Default | Description |
|---|---|---|
| `peg_height` | 25 | Height of the peg (mm) — should be taller than spool width |
| `peg_radius` | 10 | Peg radius (mm) — should fit inside the spool hole |
| `base_radius` | 18 | Base disc radius (mm) — wider than peg for stability |
| `base_height` | 4 | Base disc height (mm) |

**Returns:** `cq.Workplane`

---

### `create_item_slot()` — `lib/workstation/holders.py`

Generic recessed slot for holding a tool or item. Three shape options.

| Parameter | Default | Description |
|---|---|---|
| `slot_length` | 40 | Inner slot length along X (mm) |
| `slot_width` | 15 | Inner slot width along Y (mm). For `circle` shape, this is the diameter. |
| `slot_depth` | 10 | Slot depth (mm) |
| `wall_thickness` | 2 | Wall around the slot (mm) |
| `corner_radius` | 3 | Corner fillet (mm) |
| `shape` | `"rect"` | `"rect"` = rectangular, `"round"` = stadium/oblong, `"circle"` = circular |

**Returns:** `cq.Workplane`

**Outer dimensions (for rect/round):** `(slot_length + wall_thickness*2)` x `(slot_width + wall_thickness*2)`

---

### `create_lidded_box()` — `lib/workstation/containers.py`

Box and lid as **separate printable parts**. The lid has a lip that drops inside the box walls, with a finger notch for easy removal.

| Parameter | Default | Description |
|---|---|---|
| `inner_length` | 40 | Interior cavity length (mm) |
| `inner_width` | 30 | Interior cavity width (mm) |
| `inner_depth` | 15 | Interior cavity depth (mm) |
| `wall_thickness` | 2 | Box wall thickness (mm) |
| `floor_thickness` | 2 | Box floor thickness (mm) |
| `lid_thickness` | 2 | Lid cap plate thickness (mm) |
| `lip_depth` | 3 | How deep the lid lip drops inside the box (mm) |
| `clearance` | 0.3 | Gap per side for FDM tolerance (mm) — increase if lid is too tight |
| `corner_radius` | 3 | Corner fillet (mm) |
| `finger_notch` | True | Whether to cut a semicircle on one edge for easier lid removal |
| `finger_notch_radius` | 8 | Size of the finger notch (mm) |

**Returns:** `dict` with keys:
- `"box"` — `cq.Workplane` of the box (bottom at Z=0)
- `"lid"` — `cq.Workplane` of the lid (lip hangs into negative Z)
- `"lid_offset_z"` — Z offset to place the lid on top of the box
- `"outer_length"`, `"outer_width"`, `"outer_height"` — bounding dimensions

**Assembly usage:**
```python
result = create_lidded_box(inner_length=50, inner_width=35, inner_depth=20)

assembly.add(result["box"],
    loc=cq.Location(cq.Vector(x, y, z)),
    name="my_box")
assembly.add(result["lid"],
    loc=cq.Location(cq.Vector(x, y, z + result["lid_offset_z"])),
    name="my_lid")
```

---

## Writing new library components

When adding a new reusable function to `lib/workstation/`:

1. **All dimensions must be parameters** with sensible defaults — no magic numbers in the function body.
2. **Bottom face at Z=0** — use `centered=(True, True, False)` with `.box()`, or `.extrude()` from the XY plane.
3. **Return `cq.Workplane`** (or a dict if the component has multiple printable parts).
4. **Export from `__init__.py`** — add the import so it's available via `from lib.workstation import your_function`.

---

## Other scripts in this folder

| Script | Description |
|---|---|
| `bathroom_shelf.py` | Bathroom shelf hook assembly |
| `pump_holder.py` | Faucet-mounted pump base with semicircular clamp |
| `soap_dispenser_hangar.py` | Soap dispenser hanger with mic-style holders |
