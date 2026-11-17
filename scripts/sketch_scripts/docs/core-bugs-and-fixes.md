# CadQuery Library: Core Bugs & Fixes

_Reviewed 2026-10-10_

## Overview

The overall direction is good. The main risk is mutable state in `core/ports.py` and `core/base.py`, not the parts themselves.

Parametric `Component` classes, named ports, and operations that return both geometry and the frames they create match how mature code-CAD tools work (build123d joints, CadQuery's `cq.Assembly`). The plane-returning `create_rectangular_slot` in `operations/slots.py` is the right pattern.

The problem: geometry, ports and workplanes are changed in place. That is fine for 3 parts but produces order-dependent, hard-to-trace bugs at 30. Bugs 1 and 2 below are the ones to fix first; everything else builds on them.

## Status (30 Oct 2026)

All five bugs and the smaller items below are fixed except the `@dataclass` parameter refactor of the existing parts
(new code such as `projects/prop_dyno.py` uses dataclasses) and the assembly-output layer.

| Item | Fix applied | Verified by |
|---|---|---|
| Bug 1 | `Component.location` is the only placement; `attach()` sets `child.location = target * flip * child_port.inverse`; ports and solids are never moved | `tests/test_core.py`: repeatable mates, rebuild after placement |
| Bug 2 | `Port` stores one `cq.Location`; `plane` / `normal_vector` / `x_dir` are derived with `plane_from_location()` (no Euler round trip); `x_dir` is honoured | tests: x direction kept through construction, moves and mates |
| Bug 3 | `self.workplanes` removed; `component.workplane(port)` / `port.workplane()` create one on demand | — |
| Bug 4 | `add_ports_from_planes()` registers slot planes as ports (`"droneStandSlots.<X.floor"`); `tagged_planes` removed | tests: slot ports move with the part |
| Bug 5 | `build()` clears and re-registers ports on every (re)build; parts call `self.build()` in `__init__` | tests: rebuild keeps solid and ports together |
| `MountingPlate` | called a non-existent `register_port`; now `add_port` | tests: plate builds, ports present |
| `ports.py` | imported `Component` from `core` (circular); removed, with the debug prints | — |
| `cadMath.get_new_workplane` | dead after the fix and flipped normals; removed | — |
| `__pycache__` | untracked from git (`*.pyc` already ignored) | `git ls-files` |
| `projects/drone_gimbal.py` | failed on the old core (`KeyError: Port 'bottom_mount'`: ports read before the part was built); now runs, and the pillar `x_dir` is honoured so both bearing cups sit symmetrically | run |

Existing parts in `hardware/parts.py` build to identical volumes and bounding boxes before and after the change.

## Bug 1: Mating changes state in place, so results depend on call order

**Where:** `attach()` in `core/ports.py`, `Port.invert_normal`

**Problems**

- `attach()` overwrites `child._cached_solid` and calls `port.transform()` on every child port. Calling `mate` twice stacks the moves.
- `build(force_rebuild=True)` moves the solid back to the origin while the ports stay moved, so solid and ports disagree.
- `attach(..., invert=True)` calls `p_port.invert_normal()` on the **parent's** port, changing it permanently. A second part mated to the same port with `invert=True` flips it back.

**Fix**

Keep each component's geometry and ports in **local** coordinates and never change them. Give each component a single `self.location: cq.Location`. Mating only sets that location:

```python
flip = cq.Location((0, 0, 0), (1, 0, 0), 180) if invert else cq.Location()
child.location = parent.location * p_port.loc * flip * c_port.loc.inverse
```

Compute world positions only when asked:

```python
world_solid = component.build().val().moved(component.location)
world_port  = component.location * port.loc
```

Result: mates no longer depend on order, can be repeated safely, and a rebuild can't leave ports out of step with the solid. The flip is applied per mate, so no stored port is ever mutated.

## Bug 2: Port loses its in-plane direction (xDir)

**Where:** `Port.__init__` (Location branch) and `Port.transform` in `core/ports.py`

**Problem**

Both paths convert the location to Euler angles, recompute a normal with `cadMath.transform_vector`, then build `cq.Plane(origin, normal)`. That discards `xDir`, so CadQuery picks one arbitrarily. Rectangular slots and connectors can come out rotated 90° around the normal, and the Euler round-trip is a second source of error.

**Fix**

- Store a `cq.Location` as the single source of truth on each port.
- Plane → Location: `cq.Location(plane)` (supported in the installed CadQuery).
- Location → Plane: transform the origin, and the points origin + `xDir` and origin + `zDir`, then rebuild `cq.Plane(origin, xDir, normal)`.
- Remove `transform_vector` from this path entirely.

## Bug 3: Ports and workplanes are two sources of truth

**Where:** `Component.add_port` in `core/base.py`, the workplane loop in `attach()`

**Problem:** `add_port` stores both a `Port` and a `Workplane`. The workplane loop in `attach()` is just `pass`, so `self.workplanes` goes stale after any mate.

**Fix:** Remove `self.workplanes`. Create a workplane on demand from the port: `cq.Workplane(port.plane)`.

## Bug 4: Slot planes aren't ports

**Where:** `DroneStand._build` in `hardware/parts.py`, `Component` in `core/base.py`

**Problems**

- `DroneStand` stores slot planes in `self.tagged_planes`, but `Component` declares `tagged_workplanes`. The names don't match.
- Neither attribute is moved by mating, so slot planes stay at the stand's original position.

**Fix:** Register each slot plane with `add_port`, using structured names such as `"droneStandSlots.<X.floor"`. Anything can then be mated to a slot, and the planes move with the stand.

## Bug 5: `_build()` has side effects and runs twice

**Where:** `DroneStand.__init__` and `DroneStand._build` in `hardware/parts.py`

**Problems**

- `__init__` calls `self._build()` directly, so nothing is cached and `build()` runs it again later.
- `_build` also sets the slot planes as a side effect, so the planes and the cached solid can drift apart.

**Fix (pick one)**

- Call `self.build()` in `__init__` instead of `self._build()`.
- Better: have `_build` return `(solid, ports)` and let `Component.build` store both. `_build` then has no side effects.

## Smaller improvements

| Area | Issue | Suggestion |
| --- | --- | --- |
| Parameters | Constructors take ~10 keyword arguments; shared dimensions live in the `yaw_connector_meas` dict | Use `@dataclass` parameter objects, e.g. a `ConnectorSpec(length, width, depth, tolerance)` passed as one value |
| Tests | Core bugs (like 1 and 2) only show up after changing the core | A few `pytest` asserts per part: volume within tolerance, mated port at expected coordinates, `.val().isValid()` |
| Repo | `*.pyc` is in `.gitignore` but was committed earlier, so it still shows as modified | `git rm -r --cached '**/__pycache__'`; consider keeping STL exports out of git too |
| Assembly | Location, nesting, colours and STEP export are being rebuilt by hand | Have the port/mate layer output a `cq.Assembly` at the end for free multi-part STEP export and optional constraint solving |

## Background: store planes, not faces or workplanes

Tagged attachment frames should be stored as `cq.Plane` (or `cq.Location`), wrapped in a `Port`.

| Store | Problem |
| --- | --- |
| Face | Belongs to one specific solid; the next cut, union or fillet makes a new solid without it. Has no `xDir`, so rectangles can't be oriented against it. |
| Workplane | Carries a parent chain back to the solid as it was when created. Its stack is empty, so `.faces()` selects nothing. `cutBlind`/`extrude` on it would combine with the old, uncut solid. |
| Plane | Just an origin, `xDir` and normal. Independent of solid history, cheap, usable for both new geometry and mating. |

Why `.faces()` on a stored workplane selects nothing: `.faces()` only searches `self.objects`, and `.workplane()` returns a new object with a plane and a parent but an empty stack (`cq.py`, `_selectObjects` and line 652).

**New standalone object on a slot**

```python
plane = drone_stand.tagged_planes["droneStandSlots"]["<X"]["floor"]
peg = cq.Workplane(plane).rect(10, 5).extrude(8)
```

**Changing the stand itself on that plane** (`copyWorkplane` keeps the current solid as context)

```python
stand = drone_stand.build()
stand = stand.copyWorkplane(cq.Workplane(plane)).circle(2).cutThruAll()
```

**Getting the real face when needed**

```python
floor_face = stand.faces(cq.selectors.NearestToPointSelector(plane.origin.toTuple()))
```

**Related pitfall:** a generator expression is used up by the first `for` loop, so passing it to `show(*gen)` afterwards shows nothing. Use a list.

## Suggested order of work

- [x] Bug 2: make `cq.Location` the single source of truth in `Port`, keeping `xDir`
- [x] Bug 1: immutable local ports plus a `location` per component; mating sets only the location
- [x] Bug 3: remove `self.workplanes`
- [x] Bug 5: `_build` may return `(solid, ports)`; `build()` re-registers ports on every build
- [x] Bug 4: register slot planes as ports
- [x] Add checks for port positions after mating (`tests/test_core.py`, runs with or without pytest)
- [x] Untrack `__pycache__` from git
- [ ] `@dataclass` parameter objects for the existing parts in `hardware/parts.py`
- [ ] Output a `cq.Assembly` from the port/mate layer
