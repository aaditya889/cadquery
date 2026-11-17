# Prop dyno and cell rig: manufacturing package

What every vendor needs to make, finish, inspect and deliver the parts of our propeller dynamometer (the "dyno") and its
cell and pack rig, explained so that we understand every requirement we place on them and why.

- Design and every engineering number: [the design document](propeller_dynamometer_design.md).
- Numbers: [`dynamometer_sizing.py`](dynamometer_sizing.py) (loads, cells, frequencies, uncertainty) and
  [`dynamometer_structure.py`](dynamometer_structure.py) (stability, blade-off, containment, members, bolts).
- Geometry, the master for every part: the CadQuery model
  `cadquery/scripts/sketch_scripts/projects/prop_dyno.py`. Run it to get one STEP file per part, the assembly,
  `parts.csv`, `fasteners.csv` and `holes.csv` (`export/prop_dyno/<HEAD>/`), and
  `projects/prop_dyno_drawings.py` for the drawing set (`export/prop_dyno/prop_dyno_drawings.pdf`, one sheet per made or
  outsourced part).

Status, 4 Nov 2026: the mechanical design is complete and self-checked (no two parts overlap, no part is unattached, both
heads). The electronics (acquisition board, cell-rig I/O board) are specified but not designed (§12). Nothing has been
quoted or ordered.

Contents: [1 The machine](#1-the-machine-in-one-page) · [2 Processes and jargon](#2-processes-and-the-words-vendors-use) ·
[3 In numbers](#3-the-dyno-in-numbers) · [4 Parts](#4-parts-list) · [5 Requirements](#5-requirements) ·
[6 Assembly](#6-assembly-in-house) · [7 Acceptance](#7-acceptance-and-commissioning) · [8 Questions](#8-questions-for-vendors-by-industry) ·
[9 Answer log](#9-answer-log) · [10 Open decisions](#10-our-open-decisions) · [11 Cell and pack rig](#11-cell-and-pack-rig) ·
[12 Not yet designed](#12-not-yet-designed)

---

## 1. The machine in one page

A propeller dynamometer spins a motor and prop on a measuring head and records **thrust** (the axial force, N),
**torque** (the reaction twisting moment, N·m), speed, voltage, current, temperatures and vibration. From those come the
motor's and prop's efficiency, the thrust curve, and the motor's response time, which the flight controller's gains are
designed around.

**Layout.** A welded steel base on eight levelling feet carries **twin posts** braced back to the rear by diagonals. A
**saddle** clamps both posts at any height from 0.8 to 1.6 m (index pins every 50 mm) and carries a horizontal **boom**.
The **measuring head** bolts to the boom's front flange. The prop faces away from the stand so its wake blows into open
space. A **portal** (two posts and a top tie, on its own feet) is clamped across the base rails at the prop's plane and
carries the **containment ring** (large head) or the **guard** (small head). It is free-standing: no floor anchors, no
ballast.

**Two heads**, one interface (the boom flange's 4 × M10 and 2 dowels):
- **S head:** props to about 20"; sized for our 15" delivery prototype (MN4006 motors, 6S). Cells 5 kg thrust, 2 kg torque.
- **L head:** props to 1.5 m (MK30-like to FlyCart-like aircraft). Cells 20 or 50 kg thrust, 10 or 30 kg torque.

**How the head measures** (load path, from the boom to the prop):

```
boom flange ─► head frame (fixed) ─► 4 spoke blades ─► torque stage ─► thrust cell + 4 guided blades ─► carriage ─► motor
                     │                (torque flexure)        │               (thrust flexure)
                     └──── torque cell ◄──── torque arm ──────┘
```

- A **flexure** is a part that guides motion by bending a thin blade instead of sliding or rolling: no friction, no play,
  no wear, so forces down to grams are measured repeatably. The **guided blades** (four thin vertical blades) let the
  carriage move only along the thrust axis; the **spoke blades** (four radial blades) let the torque stage turn only about
  the axis.
- A **load cell** is a metal spring with **strain gauges** (thin resistive foils whose resistance changes with stretch)
  bonded on it, wired as a **Wheatstone bridge**: it outputs a small voltage proportional to force. Ours are "micro
  S-type" cells (S-shaped body, threaded M6 at both ends), one family from 1 to 50 kg, 25 × 30 × 12 mm.
- The thrust cell carries only the carriage, the motor and the prop, so the thrust axis is stiff and light: its natural
  frequency is 113–135 Hz in every class (requirement ≥ 100 Hz), which is what lets the dyno measure the motor's response
  time.

---

## 2. Processes and the words vendors use

### 2.1 Steel stock

- **RHS / SHS** (rectangular / square hollow section): steel tube with a square or rectangular cross-section, specified
  as outside size × wall, e.g. "80 × 80 × 4". Indian standard **IS 4923** (dimensions, tolerances); material to **IS 2062**.
- **IS 2062 E250** (≈ EN 10025 S275): the common structural steel; yield strength 250 MPa, weldable. Grade letters A/BR/B0/C
  set the impact toughness; **E250 BR** is enough for us (indoor, room temperature).
- **MTC** (mill test certificate, EN 10204 type 3.1): the steel mill's certificate of the heat's chemistry and strength.
  We ask for it on the plate and tube.
- **Stock tolerances:** RHS outside size is typically ±1 % and its walls may be up to 10 % thin; it is never straight to
  better than about 1 mm per metre. That is why anything precise (the boom flange's face) is machined after welding.

### 2.2 Cutting

- **Sawing** (cold saw or band saw): square or angled cuts of tube; ±0.5 mm length, angle ±0.5°. **Mitre** = an angled end
  cut so a tube meets another at an angle; our diagonals and knee braces have mitred ends (angles in the STEP files).
- **Laser cutting** (fibre laser): plate cut by a focused beam; ±0.1–0.2 mm, small **kerf** (cut width) and a thin
  **HAZ** (heat-affected zone: material whose properties the heat changed). Used for every steel plate part.
- **Plasma / oxy-fuel:** cheaper, rougher, wider HAZ; acceptable for none of our parts (the holes would need re-drilling).
- **Waterjet:** abrasive water stream, no HAZ; used for the aluminium guard rings.

### 2.3 Welding and fabrication

- **MIG/MAG** (GMAW: a wire electrode fed through a gun, shielded by gas): the usual process for our frame. **TIG** (GTAW:
  tungsten electrode, filler rod by hand): slower and neater, for thin parts and the containment-band seam root.
- **Fillet weld:** a triangular weld in the corner between two parts. Its strength is set by the **throat** *a* (the
  smallest thickness of the weld triangle). Our rule: *a* = 0.7 × the thinner wall, welded **all round** (the whole
  joint perimeter), so the weld is as strong as the wall it joins.
- **Butt weld, full penetration (CJP):** the joint is fused through its whole thickness, so it is as strong as the plate.
  Needed on the containment band's seam: a part-penetration seam would split first in a blade strike.
- **Weld quality levels, ISO 5817 B / C / D:** acceptance limits for imperfections (porosity, undercut, lack of fusion).
  C is normal structural quality; B is stringent. We ask C everywhere and B on the containment-band seam.
- **ISO 13920 tolerance classes** (A–D for lengths and angles, E–H for straightness and flatness): general tolerances for
  welded structures, because welds shrink and pull parts out of position. We ask **class B F** (B for lengths and angles,
  F for straightness and flatness).
- **Distortion and jigs:** welding heat shrinks the metal and bends the structure; a **jig** (fixture) holds the parts in
  position while welding, and the welding sequence is balanced side to side. Critical faces are machined after welding.
- **WPS / welder qualification (ISO 9606, AWS D1.1):** a written welding procedure and a tested welder. We ask for both
  for the containment band.
- **Inspection:** **VT** (visual, every weld); **DPT** (dye penetrant: a red dye drawn into surface cracks) or **MPI**
  (magnetic particle: iron powder gathering at cracks in steel); **UT** (ultrasonic: sound pulses reflecting off internal
  flaws), which we ask on the containment-band seam.

### 2.4 Plate rolling (the containment band and the small guard band)

A **3-roll bending machine** curls plate between rollers into a cylinder. The plate ends cannot be curved by the rollers
alone, so they are **pre-bent** (pressed to the radius first) or they stay flat ("**flat spots**"). The rolled band is
closed by a full-penetration butt weld, ground flush, and checked for roundness (the difference between the largest and
smallest diameter, **ovality**). Our band: 10 mm × 300 mm wide, inner Ø 1490 mm; guard band 3 mm × 150 mm, inner Ø 461 mm
(for a 381 mm prop).

### 2.5 CNC machining (in-house; outsourced only if we choose)

- **7075-T6:** a high-strength aluminium alloy (yield ≈ 500 MPa, about twice 6061-T6), used for every head part because
  the head must be stiff and light. "T6" is its heat treatment (solution-treated and artificially aged). It machines well
  but is less corrosion-resistant than 6061, so it is anodised. Plate is supplied **stress-relieved** ("T651": stretched
  after quenching) so it does not warp when pockets are machined.
- **Setups:** each time the part is re-clamped to reach another face. Each setup adds position error; drawings tell how
  many we expect.
- **General tolerances, ISO 2768-mK:** the tolerance on every dimension not toleranced on its own ("m" = medium for lengths,
  e.g. ±0.2 mm for 30–120 mm; "K" for geometrical tolerances such as flatness).
- **IT grades and fits:** **H7** (a hole, e.g. Ø8 +0.015/0) with an **m6** dowel (Ø8 +0.015/+0.006) makes a light press fit:
  the dowel locates the head on the boom flange the same way every time it is refitted.
- **GD&T** (geometric dimensioning and tolerancing) words used on our sheets: **flatness** (a face lies between two parallel
  planes this far apart), **parallelism** (a face stays this parallel to a reference), **concentricity** (two round
  features share an axis), **squareness**.
- **Surface roughness Ra** (average height of the surface texture, µm): 3.2 µm is a normal milled finish; the blade clamp
  faces are ground to 0.4 µm.
- **Tapping:** cutting an internal thread. Thread class **6H** (ISO 965) is the normal fit. In aluminium, the engagement
  (length of thread in the part) must be at least 1.5 × the diameter or the thread strips before the steel screw breaks;
  every tapped depth in the model respects that. Threads that are assembled often (motor adapters) can get **helical
  thread inserts** (Helicoil) for wear.
- **CMM** (coordinate measuring machine): a probe that measures positions to microns; used for the head's first articles.

### 2.6 Wire EDM

**Wire electrical-discharge machining** cuts with sparks between a moving brass wire (0.1–0.25 mm) and the part: no force,
no burr, very accurate (±0.005 mm). We need it for the flexure slots (0.17, 0.42 and 0.52 mm wide, +0.01/0) in the
collars and hubs, which no milling cutter can make to that width and accuracy.

### 2.7 Flexure blades (the most critical parts)

- **Material:** spring steel shim, either **EN42** (≈ C75: high-carbon steel, hardened and tempered to about 45–50 HRC) or
  **AISI 301 full-hard** stainless. A spring steel stays elastic to a high stress, so the blade returns to exactly the
  same shape every time.
- **Cutting:** by **wire EDM** (a stack of shims at once) or **photo-chemical etching** (the outline is printed on the
  shim and the rest dissolved): no heat, no burr, no stress. **Not by laser:** the laser's heat-affected edge loses its
  temper and is where fatigue cracks start.
- **Edges and surface:** deburred; no scratch across the blade's width (a scratch across the bending direction is a crack
  starter). Flatness 0.05 mm over the length.
- **Free length:** the bending length between the clamp edges; it sets the blade's stiffness (proportional to 1 / length³),
  so the clamp edges must be sharp and square, and the length is held by the clamp geometry, not by the blade.

### 2.8 Grinding

**Surface grinding** makes a face flat and smooth with an abrasive wheel: our blade clamp bars' clamp faces are ground
flat to 0.005 mm, so the blade is gripped along its whole width and its free length is exactly where the drawing says.

### 2.9 Surface finishing

- **Steel frame:** shot blast to **Sa 2½** (ISO 8501-1: near-white metal, the rust and mill scale removed), then a zinc
  phosphate or epoxy primer and a polyurethane top coat (or powder coat), 80–120 µm total. The containment ring and guard
  in a high-visibility colour.
- **Aluminium head parts:** clear **anodising, Type II** (sulphuric acid, 10–15 µm): a hard, corrosion-resistant oxide.
  Anodising grows about half its thickness outward, so **tapped holes, H7 holes, flexure slots and clamp faces are masked**
  (protected from the bath) or the threads are chased afterwards.
- **Small steel parts** (clamp bars, straps): zinc plating or black oxide.

### 2.10 Fasteners

- **Property class 8.8 / 12.9** (ISO 898-1): the bolt's strength; 8.8 = 800 MPa tensile, 80 % yield ratio. 12.9 for the
  small socket-head screws in the head, 8.8 for the frame.
- Standards in our list: **ISO 4762** socket head cap screw, **ISO 4017 / 4014** hex bolt (fully / partly threaded), **ISO
  4032** nut, **ISO 4035** thin jam nut, **ISO 7089** washer, **ISO 4026** set screw, **ISO 8734** dowel pin.
- **Preload and tightening torque:** a bolted joint works by being clamped; the torque sets the clamp force. Typical torques
  (VDI 2230 basis, friction 0.14, to confirm with the supplier's table): M8 8.8 25 N·m, M10 8.8 49 N·m, M12 8.8 85 N·m, M16
  8.8 206 N·m; into 7075: M3 12.9 1.5 N·m, M5 12.9 6 N·m, M6 12.9 10 N·m (limited by the aluminium thread).
- **Threadlocker:** medium-strength (Loctite 243 class) on the head's screws and the load-cell studs: vibration loosens them.

### 2.11 Bought components

- **Load cells:** micro S-type, 2 mV/V rated output, 350 Ω bridge, 0.05 % FS combined error, M6 × 1 threads, 2 m shielded
  cable. Each comes with a **calibration certificate** (its own sensitivity, zero and errors).
- **Levelling feet:** M16 stud, swivel base, NBR (rubber) pad; the rubber pad gives the friction the free-standing stand
  relies on (§3).
- **Calibration weights:** **OIML R111 class M1** (a legal-metrology accuracy class: a 1 kg M1 weight is within ±50 mg),
  with a calibration certificate traceable to national standards (in India via an **NABL**-accredited lab).

---

## 3. The dyno in numbers

| Item | Value | Source |
|---|---|---|
| Footprint | 2.5 m (x) × 1.8 m (y); portal 2.46 m tall (room ceiling ≥ 2.6 m) | CAD |
| Mass | 461 kg (L configuration, with the ring); 353 kg (S configuration) | CAD |
| Thrust axis height | 0.8–1.6 m in 50 mm steps (L head with a 1.37 m prop: ≥ 1.4 m) | CAD |
| Free-standing | sliding factor 3.0 at friction 0.3 under 1.5 × 300 N; tipping factor ≥ 4.5; a 490 J blade-off moves it < 1 mm | dynamometer_structure.py |
| Containment ring | S275 10 × 300 mm, inner Ø 1490 mm, 111 kg; 773 J to perforate (conservative plug estimate) against 490 J per blade | dynamometer_structure.py |
| Small guard | S275 3 × 150 mm, inner Ø 461 mm; ≈ 35 J to perforate against 20 J per blade | dynamometer_structure.py |
| Thrust-axis natural frequency | 128 Hz (15" prototype), 113 Hz (MK30-like), 135 Hz (FlyCart-like); requirement ≥ 100 | dynamometer_sizing.py, CAD masses |
| Thrust uncertainty (1σ, at hover) | 0.50 % (prototype), 0.23 %, 0.30 %; requirement ≤ 0.5 % | dynamometer_sizing.py |
| Boom lateral mode | 752 Hz (prototype, 0.265 m overhang), 274 Hz (MK30-like at 0.35 m), 168 Hz (FlyCart-like at 0.465 m) | dynamometer_sizing.py |
| Thrust stage (moving) | 0.240 kg (S), 1.290 kg (L) without motor and prop | CAD |
| Spoke flexure under the carried weight | buckling factor 4.6 (S, 1.1 kg carried), 18.6 (L, 8.2 kg); blade bending ≤ 50 MPa | dynamometer_structure.py |
| Parts | L configuration: 34 part numbers, 79 parts; S configuration: 37 part numbers, 85 parts | CAD |

---

## 4. Parts list

Generated from the CAD's `parts.csv` (4 Nov 2026). "make" = our CNC; "outsource" = a vendor (welding, laser, rolling, EDM,
shim blades); "buy" = catalogue part. Every made or outsourced part has a drawing sheet with its hole table; its STEP file is
the master geometry.

### 4.1 L configuration (large head, containment ring)

| Part | Name | Qty | Material | Made by | Process | Stock | Mass each (kg) | Notes |
|---|---|---|---|---|---|---|---|---|
| W1-01 | Side rail | 2 | S275 (IS 2062 E250) | outsource | saw cut square, weld | RHS 80×80×4 × 2500 | 23.864 | — |
| W1-02 | Cross member | 3 | S275 (IS 2062 E250) | outsource | saw cut square, weld | RHS 80×80×4 × 1120 | 10.691 | — |
| W1-03 | Foot plate | 8 | S275 (IS 2062 E250) | outsource | laser cut, drill, tap M16, weld | plate 12 × 120 × 120 | 1.342 | — |
| W1-04 | Post | 2 | S275 (IS 2062 E250) | outsource | saw cut, drill index holes on a jig, weld | RHS 80×80×4 × 1630 | 15.418 | index holes on 50 mm pitch, ±0.2 mm cumulative |
| W1-05 | Post cap | 2 | S275 (IS 2062 E250) | outsource | laser cut, weld | plate 5 × 80 × 80 | 0.251 | — |
| W1-06 | Post gusset | 2 | S275 (IS 2062 E250) | outsource | laser cut, weld | plate 8 × 150 × 150 | 0.707 | — |
| W1-07 | Post top tie | 1 | S275 (IS 2062 E250) | outsource | saw cut, weld | RHS 60×60×4 × 120 | 0.844 | — |
| W1-08 | Diagonal | 2 | S275 (IS 2062 E250) | outsource | saw cut both ends at 50.1° (on the CAD), weld | RHS 60×60×4 × 2090 | 14.481 | end cuts as modelled; fit-up gap ≤ 2 mm before welding |
| B-01 | Levelling foot M16 × 100, Ø80 swivel base, NBR pad, ≥ 5 kN | 8 | bought | buy | — | catalogue part | 1.1 | — |
| A1-01 | Saddle front plate | 1 | S275 (IS 2062 E250) | outsource | laser cut, drill, weld seat block | plate 15 × 380 × 300 | 13.327 | — |
| A1-02 | Saddle rear plate | 1 | S275 (IS 2062 E250) | outsource | laser cut, drill | plate 15 × 380 × 300 | 13.327 | — |
| A1-03 | Seat block (welded to the front plate) | 1 | S275 (IS 2062 E250) | outsource | saw cut, mill top flat, drill, tap, weld | flat 25 × 160 × 150 | 4.665 | top face flat 0.1 mm and flush with the front plate top |
| A1-04 | Boom strap | 2 | S275 (IS 2062 E250) | make | saw cut, drill | flat 12 × 40 × 160 | 0.585 | — |
| B1-01 | Boom tube | 1 | S275 (IS 2062 E250) | outsource | saw cut square, weld | RHS 100×100×4 × 950 | 11.455 | — |
| B1-02 | Boom flange | 1 | S275 (IS 2062 E250) | outsource | laser cut, weld, then face-mill and drill after welding | plate 20 × 200 × 200 | 4.57 | front face flat 0.05 mm and square to the tube axis 0.1 mm after welding |
| B1-03 | Boom end cap | 1 | S275 (IS 2062 E250) | outsource | laser cut, weld | plate 5 × 100 × 100 | 0.392 | — |
| HL-01 | Head frame (fixed): back wall, torque-flexure collar, torque-cell bracket | 1 | Al 7075-T6 | make | CNC mill from solid, 3 setups; wire-EDM the collar slots | block 96 × 300 × 205 | 4.452 | collar slots 0.42 +0.01/0 wide; collar bore concentric to the dowel holes 0.02 mm |
| HL-02 | Torque stage (one piece): hub, plate, arms, torque arm | 1 | Al 7075-T6 | make | CNC turn the hub, mill the rest from solid; wire-EDM the hub slots | block 148 × 255 × 290 | 4.776 | hub slots 0.42 +0.01/0; rib faces flat 0.01 and parallel 0.01 mm; torque-cell hole at r = 150 ± 0.05 mm |
| HL-03 | Thrust carriage | 1 | Al 7075-T6 | make | CNC mill from solid, 2 setups | block 45 × 125 × 163 | 0.718 | rib faces flat 0.01 mm, parallel to the torque-stage ribs 0.02 mm when assembled; lightest part of the head: no material may be added |
| B-02 | Load cell, micro S-type, 20/50 kg, M6×1, 0.05 % FS (thrust) | 1 | bought | buy | — | catalogue part | 0.071 | ATO DYLY-106 class: 25 × 30 × 12 mm, 2 × M6×1 (datasheet drawing); measure on delivery |
| HL-04 | Thrust flexure blade | 4 | spring steel, EN42 / 301 full-hard | outsource | wire-EDM or photo-etch from shim, deburr | shim 0.5 × 50 × 90 | 0.017 | free length 50 mm between clamp edges; no scratches across the width; edges deburred |
| HL-05 | Blade clamp bar | 8 | S275 (IS 2062 E250) | make | mill, surface-grind the clamp face | flat 8 × 50 × 20 | 0.061 | clamp face ground flat 0.005 mm; clamp edge sharp |
| HL-06 | Torque flexure blade | 4 | spring steel, EN42 / 301 full-hard | outsource | wire-EDM or photo-etch from shim, deburr | shim 0.4 × 40 × 60 | 0.008 | free length 40 mm between slot edges |
| B-03 | Load cell, micro S-type, 10/30 kg, M6×1, 0.05 % FS (torque) | 1 | bought | buy | — | catalogue part | 0.071 | as B-02 |
| HL-07 | Motor adapter (one per motor pattern) | 1 | Al 7075-T6 | make | CNC turn, drill | block 15 × 115 × 115 | 0.256 | motor pattern: placeholder until the motor drawing is in hand; faces parallel 0.02 mm |
| W2-01 | Portal post | 2 | S275 (IS 2062 E250) | outsource | saw cut, drill on a jig, weld | RHS 80×80×4 × 2280 | 21.477 | holes on 50 mm pitch, ±0.2 mm cumulative, both posts drilled as a pair |
| W2-02 | Portal foot | 2 | S275 (IS 2062 E250) | outsource | saw cut, weld | RHS 80×80×4 × 900 | 8.591 | — |
| W2-03 | Portal knee brace | 4 | S275 (IS 2062 E250) | outsource | saw cut both ends (on the CAD), weld | RHS 60×60×4 × 1000 | 6.035 | — |
| W2-04 | Portal top tie | 1 | S275 (IS 2062 E250) | outsource | saw cut, weld | RHS 80×80×4 × 1630 | 15.559 | — |
| W2-05 | Portal beam (on the rails) | 1 | S275 (IS 2062 E250) | outsource | saw cut, drill, weld | RHS 80×80×4 × 1630 | 15.523 | — |
| W2-06 | Rail clamp plate | 2 | S275 (IS 2062 E250) | make | laser cut, drill | plate 12 × 80 × 150 | 1.103 | — |
| R1-01 | Containment band (rolled, butt-welded) | 1 | S275 (IS 2062 E250) | outsource | roll plate to Ø, full-penetration butt weld, grind flush, UT the seam | plate 10 × 300 × 4712 | 110.977 | seam at the bottom; band plate qualified by a coupon impact test before first use (§7) |
| R1-02 | Ring lug plate | 2 | S275 (IS 2062 E250) | outsource | laser cut, drill, weld | plate 20 × 120 × 220 | 4.069 | — |
| R1-03 | Ring lug rib | 4 | S275 (IS 2062 E250) | outsource | laser cut, weld | plate 12 × 90 × 180 | 0.709 | — |
| CL-01 | Thrust calibration plate (replaces the motor adapter) | 1 | Al 7075-T6 | make | CNC turn, drill, tap | block 20 × 91 × 91 | 0.236 | eye bolt DIN 580 M8; pull line on the thrust axis ±0.5 mm |
| CL-02 | Torque calibration bar | 1 | Al 7075-T6 | make | CNC mill, jig-bore the load-pin holes | block 17 × 335 × 29 | 0.259 | load-pin holes at the radii ±0.02 mm from the pattern centre |

### 4.2 Parts only in the S configuration (small head, guard)

| Part | Name | Qty | Material | Made by | Process | Stock | Mass each (kg) | Notes |
|---|---|---|---|---|---|---|---|---|
| HS-01 | Head frame (fixed): back wall, torque-flexure collar, torque-cell bracket | 1 | Al 7075-T6 | make | CNC mill from solid, 3 setups; wire-EDM the collar slots | block 56 × 250 × 205 | 2.289 | collar slots 0.17 +0.01/0 wide; collar bore concentric to the dowel holes 0.02 mm |
| HS-02 | Torque stage (one piece): hub, plate, arms, torque arm | 1 | Al 7075-T6 | make | CNC turn the hub, mill the rest from solid; wire-EDM the hub slots | block 98 × 170 × 159 | 0.744 | hub slots 0.17 +0.01/0; rib faces flat 0.01 and parallel 0.01 mm; torque-cell hole at r = 100 ± 0.05 mm |
| HS-03 | Thrust carriage | 1 | Al 7075-T6 | make | CNC mill from solid, 2 setups | block 35 × 55 × 83 | 0.156 | rib faces flat 0.01 mm, parallel to the torque-stage ribs 0.02 mm when assembled; lightest part of the head: no material may be added |
| HS-04 | Thrust flexure blade | 4 | spring steel, EN42 / 301 full-hard | outsource | wire-EDM or photo-etch from shim, deburr | shim 0.15 × 15 × 55 | 0.001 | free length 35 mm between clamp edges; no scratches across the width; edges deburred |
| HS-05 | Blade clamp bar | 8 | S275 (IS 2062 E250) | make | mill, surface-grind the clamp face | flat 5 × 15 × 10 | 0.006 | clamp face ground flat 0.005 mm; clamp edge sharp |
| HS-06 | Torque flexure blade | 4 | spring steel, EN42 / 301 full-hard | outsource | wire-EDM or photo-etch from shim, deburr | shim 0.15 × 10 × 35 | 0.0 | free length 25 mm between slot edges |
| HS-07 | Motor adapter (one per motor pattern) | 1 | Al 7075-T6 | make | CNC turn, drill | block 10 × 54 × 54 | 0.024 | motor pattern: placeholder until the motor drawing is in hand; faces parallel 0.02 mm |
| G1-01 | Guard band (rolled steel, butt-welded) | 1 | S275 (IS 2062 E250) | outsource | roll sheet to Ø, butt weld, grind flush | sheet 3 × 150 × 1448 | 5.149 | contains a 20 J blade fragment (≈ 35 J to perforate); paint high-visibility |
| G1-02 | Guard flat ring with tabs | 2 | Al 7075-T6 | outsource | laser or waterjet cut, drill | plate 6 | 1.224 | — |
| G1-05 | Guard arm cross plate | 2 | S275 (IS 2062 E250) | outsource | laser cut, weld | plate 10 × 60 × 174 | 0.82 | — |
| G1-06 | Guard fork plate | 4 | S275 (IS 2062 E250) | outsource | laser cut, drill, weld | plate 6 × 50 × 40 | 0.091 | — |
| G1-03 | Guard arm | 2 | S275 (IS 2062 E250) | outsource | saw cut, weld | RHS 60×60×4 | 3.457 | — |
| G1-04 | Guard arm end plate | 2 | S275 (IS 2062 E250) | outsource | laser cut, drill, weld | plate 12 × 120 × 220 | 2.442 | — |
| CS-01 | Thrust calibration plate (replaces the motor adapter) | 1 | Al 7075-T6 | make | CNC turn, drill, tap | block 15 × 54 × 54 | 0.051 | eye bolt DIN 580 M8; pull line on the thrust axis ±0.5 mm |
| CS-02 | Torque calibration bar | 1 | Al 7075-T6 | make | CNC mill, jig-bore the load-pin holes | block 17 × 235 × 29 | 0.18 | load-pin holes at the radii ±0.02 mm from the pattern centre |

### 4.3 Fasteners

L configuration:

| Fastener | Qty | Used in |
|---|---|---|
| Clevis pin Ø12 × 130 + R-clip (index pin) | 2 | saddle index |
| Dowel pin ISO 8734 Ø8 m6 × 30 | 2 | head to boom flange |
| ISO 4014 M12×200 8.8 + 2 washers ISO 7089 + nut ISO 4032 | 4 | portal to rails |
| ISO 4017 M12×130 8.8 + 2 washers ISO 7089 + nut ISO 4032 | 4 | saddle clamp |
| ISO 4017 M16×130 8.8 + 2 washers ISO 7089 + nut ISO 4032 | 4 | ring to portal |
| ISO 4026 M5×16 set screw + jam nut (overload stop) | 4 | overload stops |
| ISO 4762 M10×130 8.8 | 4 | boom straps |
| ISO 4762 M10×30 8.8 | 4 | head to boom flange |
| ISO 4762 M3×12 12.9 (slot pinch screw) | 8 | torque flexure slots |
| ISO 4762 M5×20 12.9 | 8 | blade clamps |
| ISO 4762 M6×16 12.9 | 4 | motor adapter to carriage |
| Nut ISO 4032 M16 (foot lock nut) | 8 | W1 base frame; W2 ring portal |
| Stud: set screw ISO 4026 M6×25 45H + 1 jam nut ISO 4035 M6 | 4 | thrust cell; torque cell |

S configuration:

| Fastener | Qty | Used in |
|---|---|---|
| Clevis pin Ø12 × 130 + R-clip (index pin) | 2 | saddle index |
| Dowel pin ISO 8734 Ø8 m6 × 30 | 2 | head to boom flange |
| ISO 4014 M12×200 8.8 + 2 washers ISO 7089 + nut ISO 4032 | 4 | portal to rails |
| ISO 4017 M12×130 8.8 + 2 washers ISO 7089 + nut ISO 4032 | 4 | saddle clamp |
| ISO 4017 M16×120 8.8 + 2 washers ISO 7089 + nut ISO 4032 | 4 | guard to portal |
| ISO 4017 M8×25 8.8 + washers + nut | 4 | guard fork |
| ISO 4026 M5×16 set screw + jam nut (overload stop) | 4 | overload stops |
| ISO 4762 M10×130 8.8 | 4 | boom straps |
| ISO 4762 M10×30 8.8 | 4 | head to boom flange |
| ISO 4762 M3×12 12.9 | 8 | blade clamps |
| ISO 4762 M3×12 12.9 (slot pinch screw) | 8 | torque flexure slots |
| ISO 4762 M3×8 12.9 | 4 | motor adapter to carriage |
| Nut ISO 4032 M16 (foot lock nut) | 8 | W1 base frame; W2 ring portal |
| Stud: set screw ISO 4026 M6×25 45H + 1 jam nut ISO 4035 M6 | 4 | thrust cell; torque cell |
| Threaded rod M8 × 180 + spacer tube + 2 nuts | 4 | guard tie rods |

Order 10 % spares of every fastener below M8, and keep the M3 pinch and blade-clamp screws as a stocked kit.

### 4.4 Weldments and what the welder receives

| Weldment | Parts welded | Then |
|---|---|---|
| W1 base frame | W1-01 … W1-08 | levelled on a flat floor, painted; feet fitted by us |
| A1 saddle front plate | A1-01 + A1-03 | seat-block top face milled flush with the plate top after welding |
| B1 boom | B1-01 + B1-02 + B1-03 | flange face milled flat and square to the tube after welding; then drilled |
| W2 ring portal | W2-01 … W2-05 + W1-03 (×4) | posts drilled as a pair on a jig after welding |
| R1 containment ring | R1-01 + R1-02 (×2) + R1-03 (×4) | seam UT; lug holes drilled after welding, matched to the portal |
| G1 guard arms | G1-03 + G1-04 + G1-05 + G1-06 (×2), each side | painted |

---

## 5. Requirements

Status: **D** decided, **P** proposed (confirm with the vendor's answer), **O** open (§10).

### 5.1 Fabrication (steel)

| ID | Requirement | Why | Status |
|---|---|---|---|
| F1 | Material IS 2062 E250 BR (plate) and IS 4923 RHS of E250, with MTC 3.1 | Known strength for the calculations; weldable; certified so a weak heat cannot slip in | P |
| F2 | Welds: MAG, fillet throat a = 0.7 × thinner wall, all round, ISO 5817 level C; containment-band seam full penetration, level B, UT 100 % | Joints as strong as the walls; the band is the safety part | D |
| F3 | Welded structures to ISO 13920 class B F | The frame must sit on eight feet without rocking and the posts must be parallel for the saddle to slide | P |
| F4 | Posts (W1-04) parallel and coplanar within 1 mm over their length; index holes on 50 mm pitch ±0.2 mm cumulative | The saddle clamps both posts at once; its index pins must enter both posts' holes | D |
| F5 | Portal posts drilled as a pair on a jig after welding, ±0.2 mm cumulative | The ring's two lugs must bolt at the same height on both sides | D |
| F6 | Boom flange (B1-02) face flat 0.05 mm and square to the tube 0.1 mm, machined after welding; 4 × Ø11 and 2 × Ø8 H7 drilled after | The head's alignment to the thrust axis is set by this face | D |
| F7 | Containment band: inner Ø 1490 ± 3 mm, ovality ≤ 4 mm, seam ground flush, no flat spots > 50 mm | Uniform 60 mm prop-tip clearance all round | P |
| F8 | Surface: Sa 2½ blast, primer, PU top coat 80–120 µm; ring and guard high-visibility | Indoor corrosion; the containment parts must be seen | P |
| F9 | Every part marked with its part number (paint marker or stamp) | Assembly and traceability | D |

### 5.2 Machining (aluminium head, in-house or outsourced)

| ID | Requirement | Why | Status |
|---|---|---|---|
| M1 | 7075-T651 plate / 7075-T6 bar with MTC | Stiff, light, stable after pocketing | D |
| M2 | General tolerances ISO 2768-mK; special tolerances as on each sheet | Position of everything not critical | D |
| M3 | Blade clamp rib faces flat 0.01 mm and parallel 0.01 mm (head frame / torque stage / carriage) | The two blade rows must be parallel so the carriage moves straight; a twist adds parasitic stiffness and crosstalk | D |
| M4 | Flexure slots by wire EDM, width = blade + 0.02 +0.01/0 mm, slot depth ±0.05 | The blade must be held over its whole width with the pinch screw only closing 0.02–0.03 mm | D |
| M5 | Collar bore concentric to the head frame's dowel holes 0.02 mm; torque-cell hole at r = arm radius ±0.05 mm | Torque = cell force × arm radius: 0.05 mm on 100 mm is 0.05 % | D |
| M6 | Threads 6H; engagement ≥ 1.5 d in aluminium (as modelled) | Strength of steel screws in aluminium | D |
| M7 | Clear anodise Type II, 10–15 µm, with tapped holes, H7 holes, slots and clamp faces masked | Corrosion protection without changing the precision features | P |
| M8 | First article of each head part measured on a CMM against the STEP | The head is the instrument: errors here are measurement errors | P |

### 5.3 Flexure blades

| ID | Requirement | Why | Status |
|---|---|---|---|
| X1 | EN42 hardened and tempered 45–50 HRC, or 301 full-hard; thickness ±2 % | The blade stiffness goes as thickness³: 2 % in thickness is 6 % in stiffness | D |
| X2 | Cut by wire EDM or photo-etching; no laser | No heat-affected edge (fatigue) | D |
| X3 | Deburred, no transverse scratches, flat 0.05 mm, holes Ø clearance + 0/+0.05 | Fatigue life; even clamping | D |
| X4 | 4 spares of every blade size | Blades are consumables after an overload | D |

### 5.4 Bought parts

| ID | Requirement | Why | Status |
|---|---|---|---|
| B1 | Load cells: micro S-type 25 × 30 × 12 mm, M6 × 1, 2 mV/V, 350 Ω, 0.05 % FS, individual calibration certificate | One interface for every capacity; known errors | P |
| B2 | Levelling feet M16, ≥ 5 kN, NBR pad, swivel | The free-standing calculation uses the pad's friction | D |
| B3 | Calibration weights OIML M1, NABL-traceable certificate | The dyno is only as accurate as its weights | D |
| B4 | Fasteners from a known brand (Unbrako, TVS or equal), 12.9 socket screws with certificate | Counterfeit high-tensile screws are common; a sheared clamp screw releases a blade | P |

---

## 6. Assembly (in-house)

1. **Frame:** stand W1 on its eight feet on the floor where it will work; level the rails to 1 mm/m with the feet; lock
   the foot nuts. Bolt the portal across the rails with its four M12 rail clamps loose.
2. **Saddle and boom:** fit the saddle plates around the posts at the wanted height, insert both index pins, torque the four
   M12 clamp bolts (85 N·m). Lay the boom on the seat, set the overhang (0.265 m S; 0.35 m MK30-size props; 0.465 m
   FlyCart-size), torque the four M10 strap bolts (49 N·m).
3. **Head (on the bench first):**
   1. Spoke blades into the head frame's collar slots and the torque stage's hub slots, with the hub held concentric in
      the collar by a turned **jig ring** (made with the head); tighten the eight M3 pinch screws (1.5 N·m); remove the jig.
   2. Thrust blades: clamp each blade's upper end to the torque stage's ribs, then its lower end to the carriage's ribs, with
      the carriage held in its working position by **feeler-gauge shims** (so the blades are clamped straight and unstressed);
      M5 or M3 blade screws to 6 / 1.5 N·m with threadlocker.
   3. Load cells on their studs: thread a stud into each cell (threadlocker), screw the cell's stud into the torque stage
      (thrust) or the head frame's bracket (torque) until the cell just touches without preload, then lock with the jam nuts.
      Check with the acquisition board that each cell reads zero ±0.5 % FS after assembly (no built-in preload).
   4. Overload stops: set each M5 stop screw to 1.5 × the cell's full-scale deflection from its tab (0.3 mm feeler gauge),
      lock with the jam nut.
   5. Motor adapter and motor; route the three phase leads as one loose loop from the fixed frame to the motor (design doc
      §3).
4. **Head to boom:** two dowels, four M10 × 30 (49 N·m).
5. **Ring or guard:** slide the portal so the ring's centre plane is on the prop's plane (±5 mm), set its height with the
   M16 lug bolts in the posts' index holes, check the tip clearance all round with a gauge (60 ± 5 mm), torque the portal's
   rail clamps (85 N·m) and the M16 lug bolts (206 N·m).

---

## 7. Acceptance and commissioning

| Test | How | Accept |
|---|---|---|
| Dimensional, weldments | tape and square: post parallelism, index pitch, flange flatness (dial gauge) | §5.1 |
| Weld visual | every weld | ISO 5817 C (B on the band) |
| Band seam | UT report from the fabricator | no recordable flaw |
| Head parts | CMM first article; feeler and dial checks on the assembled head | §5.2 |
| Free-standing | push test: a 450 N horizontal pull at the thrust axis (spring balance) | no sliding or rocking |
| Calibration | design doc §7: weights over a pulley (thrust), weights on the calibration bar (torque), up and down | residuals within the uncertainty budget |
| Tap test | design doc §7: impulse hammer on the carriage with motor and prop fitted | f_n within 10 % of §3 |
| Containment qualification | before the first L-head run: a proof impact on a test coupon of the band plate (10 mm E250) at 1.5 × the blade energy (≈ 750 J; e.g. a drop weight with a blunt 20 mm striker) at an accredited test house | no perforation |

---

## 8. Questions for vendors, by industry

### 8.1 Structural fabricator (cutting, welding, painting): W1, A1, B1, W2, R1, G1

| ID | Question | Why we ask | Good answer |
|---|---|---|---|
| FB1 | Can you work from STEP files and our drawing PDF (no 2D CAD drawings with dimension lines)? | Our master is the 3D model | Yes; they extract dimensions themselves and send questions |
| FB2 | Do you laser-cut in-house? Tolerance on holes? | Holes positions in plates | Fibre laser, ±0.2 mm |
| FB3 | Will you weld W1 and W2 on a jig, and check post parallelism and index pitch before painting? | F4, F5 | Yes, with a measurement record |
| FB4 | Can you machine the boom flange face and drill its holes after welding (or send it to a machine shop)? | F6 | Yes, on a mill |
| FB5 | Can you roll and weld the 10 × 300 mm band to Ø 1490 inner with pre-bent ends, full-penetration seam, and get it UT-tested? | F2, F7 | Yes; a qualified welder and a WPS; UT by an NDT lab |
| FB6 | Can you roll the 3 mm guard band to Ø 461 inner? | G1 | Yes |
| FB7 | Paint system and colours? Blast standard? | F8 | Sa 2½, primer + PU, RAL colours on request |
| FB8 | Lead time, price per weldment, and delivery to our site (the portal is 2.46 m)? | Plan and transport | Itemised |
| FB9 | MTCs for plate and tube? | F1 | Yes, 3.1 |

### 8.2 Wire-EDM job shop: collar and hub slots (if not in-house)

| ID | Question | Why we ask | Good answer |
|---|---|---|---|
| ED1 | Smallest wire? Can you cut 0.17 mm slots 5 mm deep with ±0.005 width? | M4 (S head) | 0.1 mm wire; yes |
| ED2 | Can you locate the slots from our machined datums (the collar bore, the hub's outer diameter) to 0.01 mm? | Blades must sit radially | Yes, with a probe |
| ED3 | Will you cut blades from a shim stack? | X2 | Yes, stacked between plates |

### 8.3 Spring-steel shim and blade supplier

| ID | Question | Why we ask | Good answer |
|---|---|---|---|
| SS1 | EN42 (C75) hardened and tempered shim in 0.15, 0.40, 0.50 mm, or 301 full-hard? Hardness and thickness certificate? | X1 | Yes, with certificate |
| SS2 | Photo-etching or EDM of blades to our DXF? | X2 | Either |
| SS3 | Thickness tolerance? | Stiffness ∝ t³ | ±2 % or better |

### 8.4 Load-cell supplier

| ID | Question | Why we ask | Good answer |
|---|---|---|---|
| LC1 | Micro S-type 2, 5, 10, 20, 30, 50 kg with 25 × 30 × 12 mm body and M6 × 1 threads at both ends? Send the dimension drawing. | One interface for all cells (§2.11) | Yes, drawing attached |
| LC2 | Combined error, creep (30 min), zero and span temperature coefficients, safe and ultimate overload, deflection at rated load? | Uncertainty budget and the overload-stop gap (0.3 mm assumes 0.2 mm deflection) | 0.05 % or better; deflection stated |
| LC3 | Individual calibration certificate per cell? | Traceability | Yes |
| LC4 | A C3-class (0.03 %) option in the same size? | Would bring the prototype's uncertainty from 0.50 % to ≈ 0.4 % | Yes / no with price |

### 8.5 Anodiser and painter (if separate)

| ID | Question | Why we ask | Good answer |
|---|---|---|---|
| AN1 | Type II clear anodising of 7075, with masking of threads, H7 holes and slots? | M7 | Yes; masking by plugs and tape |
| AN2 | Coating thickness control? | Dimensional growth | 10–15 µm, measured |

### 8.6 Fastener supplier

| ID | Question | Why we ask | Good answer |
|---|---|---|---|
| FS1 | Brand and certificate for 12.9 socket screws and 8.8 bolts? | B4 | Known brand, test certificate |
| FS2 | Tightening torque table for your screws? | §2.10 | Supplied |

### 8.7 Calibration lab

| ID | Question | Why we ask | Good answer |
|---|---|---|---|
| CL1 | NABL accreditation scope for mass (M1, 0.1–20 kg) and for DC voltage/current (the reference meter)? | B3, cell-rig calibration | In scope |
| CL2 | Turnaround and price per weight and per meter? | Plan | Itemised |

### 8.8 Test house (containment qualification)

| ID | Question | Why we ask | Good answer |
|---|---|---|---|
| TH1 | Can you run a drop-weight or projectile impact on a 10 mm E250 coupon at 750 J with a blunt 20 mm striker, and report penetration and deformation? | §7 | Yes, with high-speed video |

---

## 9. Answer log

Fill one row per vendor contacted. Keep the question IDs so answers compare directly.

| Vendor | Industry | Contact | Questions answered (ID: answer) | Quote | Lead time | Visited |
|---|---|---|---|---|---|---|
| | Structural fabricator | | | | | |
| | Structural fabricator | | | | | |
| | Wire EDM | | | | | |
| | Spring steel / blades | | | | | |
| | Load cells | | | | | |
| | Anodiser / painter | | | | | |
| | Fasteners | | | | | |
| | Calibration lab | | | | | |
| | Test house | | | | | |

---

## 10. Our open decisions

| ID | Decision | Options and trade-off |
|---|---|---|
| D1 | Build order | One frame for both heads (as designed). Build the frame, saddle, boom, portal and S head first (prototype motors); the L head, ring and containment test before any L-class run |
| D2 | Load cells | The 0.05 % micro S-type family (one interface; the prototype's uncertainty exactly at 0.5 %), or a C3-class cell for the S head only (better accuracy, a second adapter design) |
| D3 | Reference motors and props for the L head | Needed for the L motor adapter's pattern; the current one is a placeholder |
| D4 | Head machining | In-house (our CNC, ≈ 20 parts) vs outsourced; wire EDM probably outsourced |
| D5 | Containment qualification | Coupon test at a test house (cheaper) vs a full prop-burst test on the stand (realistic) |
| D6 | Room | Ceiling ≥ 2.6 m, floor area ≈ 3 × 2.5 m plus the test-cell fence and the operator's barrier |

---

## 11. Cell and pack rig

Everything here is bought, fabricated from simple drawings, or electronics; the design is in
[design §12](propeller_dynamometer_design.md#12-cell-and-pack-rig).

| Item | Specification | Source | What to ask |
|---|---|---|---|
| Fire cabinet | steel, ≥ 1.5 mm walls, gasketed door, vent duct to outside, sand tray, smoke/heat detector, cable glands; inner insulated box with heater, fan and a hardwired over-temperature cut-out (25 / 45 °C) | fabricator (sheet metal) | sheet-metal capability; gland plate; door interlock switch fitted |
| Cell fixture | copper (C110) current clamps for 18650 and 21700, separate spring-loaded sense pins, G10 base, thermocouple port | make (CNC) | — (design is a gap, §12) |
| Linear load modules | 300 W each, 10 linear-mode MOSFETs on a heat sink ≤ 0.21 K/W with fans | electronics (gap, §12) + heat-sink supplier | thermal resistance curve with the fan |
| Current shunt | 1 mΩ four-terminal manganin, 0.1 %, ≤ 20 ppm/K, ≥ 5 W | buy | calibration certificate |
| Programmable supply | 60 V / 18 A, remote-controlled (RD6018 class) + input supply | buy | interface protocol |
| Contactors | 60 V / 60 A DC, two | buy | DC rating at 60 V (AC ratings do not apply) |
| AC resistance meter | 1 kHz, YR1035 class | buy | — |
| Reference meter | 6.5-digit DMM | buy | NABL calibration |

---

## 12. Not yet designed

These are needed for a complete machine and are not in the CAD or in a board design yet:

1. **Acquisition board** (2 off: dyno and cell rig) and **cell-rig I/O board** with the linear-load modules: specified in
   the design doc §5 and §12.3; schematics and layouts to do in our KiCad framework, then
   [the PCB manufacturing package (drone documents)](../../nodemcu/projects/drone_esp32/docs/vendors/pcb_manufacturing.md) applies.
2. **Power path and wiring:** 200 A fuse, precharged contactor, E-stop chain, door interlock, 60 V / 150 A cables, Hall
   current transducer mounting: a wiring diagram and an electrical enclosure.
3. **Test-cell fence and operator barrier:** welded mesh panels and a polycarbonate viewing window around the stand.
4. **Cell fixture CAD** (§11).
5. **L-head motor adapters** for the chosen reference motors (D3), and the **jig ring** for assembling the spoke flexure.
6. **PC software:** test sequences, logging, calibration solving, reports.
