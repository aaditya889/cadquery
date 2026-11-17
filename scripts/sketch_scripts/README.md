# Sketch-First CAD-as-Code Framework

A modular, scalable, and crash-proof CAD library built with **CadQuery 2.0 Sketch API**. Designed to build complex mechanical assemblies with "the speed of thought" through clean, reusable building blocks.

---

## 🏗️ Architecture Overview

```text
sketch_scripts/
│
├── core/                        # Engine & fundamental primitives
│   ├── base.py                  # Component ABC: cached local build, local ports, one `location`, world(), export
│   ├── ports.py                 # Port (immutable frame stored as cq.Location), attach() / mating
│   ├── booleans.py              # to_shape(), fuse_all(), place_on(), find_junction_edges(), duplicate()
│   └── display.py               # Crash-proof show() for cq-server & OCP
│
├── sketches/                    # Reusable 2D geometric sketches
│   ├── profiles.py              # rounded_rect, slotted_hole, u_channel, etc.
│   └── patterns.py              # hex_grid_pattern, bolt_circle_pattern, etc.
│
├── hardware/                    # Standard hardware tables & project parts
│   ├── standards.py             # ISO Metric fasteners (M2-M6), Bearings (608, 624, etc.)
│   └── parts.py                 # Gimbal and stand parts (InnerGimbalConnector, GimbalQuarterCurve, DroneStand, ...)
│
├── features/                    # Parametric 3D mechanical components
│   ├── mounts.py                # BearingHousing, ScrewBoss
│   └── plates.py                # MountingPlate
│
├── operations/slots.py          # create_rectangular_slot(): cuts slots, returns their planes (register them as ports)
├── cadMath/                     # transform_vector() (Euler rotation helper)
├── utils/debug_print.py         # d_print() keyed debug output
│
├── projects/                    # Full assemblies & product designs
│   ├── drone_gimbal.py          # Parametric drone gimbal test stand
│   ├── gimbal_parts.py          # Gimbal / tether parts and exports
│   └── prop_dyno.py             # Propeller dynamometer (frame, boom, flexure head, guard)
│
├── tests/test_core.py           # Port / mate / rebuild / feature checks: python3 tests/test_core.py
│
└── docs/core-bugs-and-fixes.md  # Review of the port engine and the fixes applied
```

---

## ⚡ Quick Start: Creating a New Part in 30 Seconds

```python
import cadquery as cq
from core import show, fuse_all, find_junction_edges
from sketches import rounded_rect, bolt_circle_pattern
from features import BearingHousing

# 1. Draw 2D cross-section sketch (2D fillets NEVER fail)
sketch = (
    rounded_rect(length=120.0, width=60.0, radius=8.0)
    .face(bolt_circle_pattern(radius=20.0, count=4, hole_dia=3.4), mode="s")
)

# 2. Extrude to 3D
base = cq.Workplane("XY").placeSketch(sketch).extrude(6.0)

# 3. Add parametric hardware features
bearing_mount = BearingHousing(bearing="608", wall_thickness=3.0).build()
bearing_mount = bearing_mount.translate((0, 0, 6.0))

# 4. Fuse & fillet seam transitions smoothly
final_part = fuse_all(base, bearing_mount)
final_part = find_junction_edges(final_part, base, bearing_mount).fillet(2.0)

# 5. Render in cq-server
show(final_part)
```

---

## 🎯 Core Principles & Rules

1. **2D Sketches First**: Define 80% of geometry in 2D (`cq.Sketch`) and apply 2D fillets before extruding. This eliminates 3D OpenCASCADE boolean/fillet crashes.
2. **Universal Fusion**: Use `fuse_all(part_a, part_b, ...)` to convert any collection of parts into a single watertight solid.
3. **Automated Seam Filleting**: Use `find_junction_edges(fused_model, part_a, part_b).fillet(r)` to smooth transitions where components meet.
4. **Standard Hardware Specs**: Never hardcode bearing/screw hole sizes. Use `get_fastener("M3")` or `get_bearing("608")` to guarantee correct fit and 3D printing clearances.
5. **Universal Preview**: Always use `show(part1, part2, ...)` — it handles Workplanes, Compounds, Solids, and Assemblies without tessellation crashes.
6. **Ports are local, placement is one Location**: register ports with `add_port()` inside `_build()`, in the part's own
   coordinates. `part.mate(my_port, to=other, to_port=...)` only sets `part.location`; nothing is moved in place, so mates
   can be repeated and rebuilds keep solid and ports together. `part.world()` / `part.port(name)` give placed geometry
   and frames; `part.build()` / `part.local_port(name)` give local ones. Inside a parent's `_build`, mate children to
   `self.local_port(...)`. `invert=True` mates face to face (normals opposed, in-plane x direction kept).
7. **Call `self.build()`, never `self._build()`**, from `__init__`.

Run the checks after touching `core/`: `python3 tests/test_core.py` (from `sketch_scripts/`).

---

## 🖥️ Browser Preview

To start the live interactive viewer:
```bash
cq-server run sketch_scripts/projects/drone_gimbal.py
```
Open [http://localhost:5000](http://localhost:5000) in your browser.
