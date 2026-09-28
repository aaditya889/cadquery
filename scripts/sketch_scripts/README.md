# Sketch-First CAD-as-Code Framework

A modular, scalable, and crash-proof CAD library built with **CadQuery 2.0 Sketch API**. Designed to build complex mechanical assemblies with "the speed of thought" through clean, reusable building blocks.

---

## 🏗️ Architecture Overview

```text
sketch_scripts/
│
├── core/                        # Engine & fundamental primitives
│   ├── base.py                  # Component ABC with caching, ports, export
│   ├── booleans.py              # fuse_all(), find_junction_edges(), duplicate()
│   └── display.py               # Crash-proof show() for cq-server & OCP
│
├── sketches/                    # Reusable 2D geometric sketches
│   ├── profiles.py              # rounded_rect, slotted_hole, u_channel, etc.
│   └── patterns.py              # hex_grid_pattern, bolt_circle_pattern, etc.
│
├── hardware/                    # Standard hardware tables & tolerances
│   └── standards.py             # ISO Metric fasteners (M2-M6), Bearings (608, 624, etc.)
│
├── features/                    # Parametric 3D mechanical components
│   ├── mounts.py                # BearingHousing, ScrewBoss
│   └── plates.py                # MountingPlate
│
├── projects/                    # Full assemblies & product designs
│   └── drone_gimbal.py          # Parametric drone gimbal test stand
│
└── export/                      # Exported STL / STEP files
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

---

## 🖥️ Browser Preview

To start the live interactive viewer:
```bash
cq-server run sketch_scripts/projects/drone_gimbal.py
```
Open [http://localhost:5000](http://localhost:5000) in your browser.
