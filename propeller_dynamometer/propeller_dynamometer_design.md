# In-House Propeller Dynamometer: Design

A propeller dynamometer ("prop dyno") we can build with our own CNC and fabrication, sized for delivery-class drones
(Amazon MK30 at 37.8 kg up to DJI FlyCart 30 at 95 kg) while measuring our 15" delivery prototype's motors precisely.
Drone 1 (the 3D-printed ESP32 quad) is not a sizing case. It measures
thrust, torque, speed, voltage, current, temperatures and vibration, and it is the test station for our own motor
development and end-of-line motor QA. A **cell and pack rig** (§12) shares its acquisition electronics and benchmarks the
batteries we buy and the packs we build.

Theory behind every rule here: [the theory document](propeller_dynamometer_theory.md). Every number comes from
[`dynamometer_sizing.py`](dynamometer_sizing.py) (`python3 dynamometer_sizing.py`), whose inputs marked ASSUMED are
representative values to replace with chosen parts' datasheets. CAD: `cadquery/scripts/sketch_scripts/projects/prop_dyno.py`
(§11). Every section lists its symbols; torque is $M$ or $Q$, $\tau$ is a time constant.

---

## 1. Requirements

| Symbol | Meaning | Unit |
|---|---|---|
| $T_{\max}$, $Q_\text{max}$ | Largest thrust and torque per rotor in the target classes | N, N·m |
| $D$ | Prop diameter | m |
| $f_n$ | Natural frequency of the thrust axis | Hz |
| $u_c$ | Combined standard uncertainty of thrust | N |

**Target classes** (per rotor, thrust-to-weight 2, script "Loads"):

| Class | $D$ | Hover / max thrust | Max torque | Max power | Max current | Rotor speed at max |
|---|---|---|---|---|---|---|
| 15" delivery prototype (MN4006, 6S) | 0.381 m | 6.9 / 22 N | 0.71 N·m | 0.35 kW | 16 A at 6S | 92 rev/s |
| MK30-like (37.8 kg hexacopter) | 0.60 m (assumed) | 62 / 124 N | 6.3 N·m | 3.0 kW | 68 A at 12S | 88 rev/s |
| FlyCart-like (95 kg, 8 rotors) | 1.37 m (assumed) | 116 / 233 N | 27 N·m | 3.4 kW | 76 A at 12S | 23 rev/s |

The prop diameters of the commercial aircraft are not published; the sizes above are assumptions that bracket them.
The prototype's hover thrust is from the MN4006 + 15×5 table (700 g); its maximum (22 N) is ASSUMED until measured.

**Requirements:**
1. Props up to 1.5 m; thrust to 300 N and torque to 30 N·m on the large head, 33 N and 1.1 N·m on the small one (the
   prototype's maximum with the margin), each with ≥ 1.5× overload margin.
2. Power path rated 60 V and 150 A continuous (≈ 2× the largest class above).
3. Thrust and torque uncertainty ≤ 0.5 % of the hover value (1σ) in every class.
4. Thrust axis $f_n$ ≥ 100 Hz, with its dynamics identified, so thrust lags down to ~50 ms can be measured (theory §6).
5. Simultaneous sampling of thrust, torque, voltage and current at 2 kHz; command and samples on one clock.
6. Remote operation from behind a barrier, a hardwired emergency stop, and containment sized for prop-burst energy
   (up to ≈ 1 kJ, §8).
7. The same station runs end-of-line tests on our own motors (§9.5).
8. Cells and packs (bought and in-house, 1S to 14S) are characterised on the same electronics: capacity, energy, resistance,
   OCV curve, mission-profile discharge, heating and cycle life (§12).

---

## 2. Architecture

| Symbol | Meaning | Unit |
|---|---|---|
| $H_\text{axis}$ | Height of the thrust axis above the floor | m |
| $L_o$ | Boom overhang from the frame's front node to the head | m |
| $D$ | Prop diameter | m |

**Horizontal thrust axis on a boom, wake into open space.** The prop's wake blows away from the stand; the frame sits
upstream in the slower inflow (theory §8). Thrust pulls the head toward the frame, so the boom is loaded **axially**, its
stiffest direction, and the frame is a triangle in the vertical plane of the axis, so every member carries axial load.

```
           wake  ◄────────   prop disc  │  head ══ boom ════════╗  front node
                                        │                      ║╲
                                        │                      ║  ╲  diagonal
                              thrust ──►                post   ║    ╲
                                                               ║      ╲
                         ══════════════════════════ base beam ══╩════════╩══  (anchored / ballasted)
```

- **Frame:** welded steel square hollow section: two side rails and three cross members on eight M16 levelling feet,
  **twin posts** braced by diagonals to the rear cross member, and a ring **portal** clamped to the rails. It is
  **free-standing, with no floor anchors and no ballast**: at 462 kg (CAD) it resists 1.5 × the maximum thrust with a
  sliding factor of 3.0 (friction coefficient 0.3, a pessimistic floor) and a tipping factor of at least 4.5, and a
  blade-off moves it by under 1 mm ([`dynamometer_structure.py`](dynamometer_structure.py)).
- **Boom:** square steel tube in a **saddle** that clamps both posts (index pins every 50 mm), adjustable along the axis;
  $H_\text{axis}$ adjustable from 0.8 to 1.6 m (≥ 1 $D$ for the largest props).
- **Two heads** on one standard boom flange: **S** (props to ≈ 20", cells 1–3 kg) and **L** (props to 1.5 m, cells 10–50 kg).
  Cells within a head swap without re-machining (spacers per cell family).
- **Overhang** $L_o$ = 0.25 m (S) and 0.45 m (L): short enough to keep the boom's bending mode clear of the rotor frequencies
  (§4.2). With the head and motor in front, the prop disc sits 0.42 m (S) or 0.77 m (L) in front of the post: 1.1–2.8 $D$ on the
  S head, 0.56 $D$ for a 1.37 m prop on the L head. Repeat a point with the boom extended to check blockage (theory §8).
- **Containment and test cell** around the rotor plane (§8).

---

## 3. The measuring head

| Symbol | Meaning | Unit |
|---|---|---|
| $k_s$, $k_p$ | Thrust-cell stiffness, parasitic stiffness of the thrust flexure | N/m |
| $K_\theta$ | Rotational stiffness of the torque flexure | N·m/rad |
| $r_a$ | Torque-arm radius | m |
| $n_b$, $w$, $t$, $L$ | Blade count, width, thickness, free length | —, m, m, m |
| $\sigma_{\max}$ | Blade bending stress | MPa |

**Load path** (theory §2): boom flange → **head frame** (fixed; carries the outer **collar** of the torque flexure and the
torque-cell bracket) → four **spoke blades** (torque flexure) → **torque stage** (hub, plate, arms, torque arm: one
machined part) → **thrust cell** and four **guided blades** (thrust flexure) → **thrust carriage** → motor adapter → motor
→ prop.
- **Why this order:** the thrust cell carries only what moves axially in front of it: the carriage, the adapter, the
  motor and the prop. With the opposite order (thrust stage first) the thrust cell also carried the whole torque stage and
  its cell; the CAD showed that gives 52–103 Hz, below requirement 4 (§4.1). The torque stage now carries the thrust stage,
  which only adds rotational inertia to the torque axis (no requirement; tap-tested).
  The spoke blades now carry the weight in front of them (1.1 kg on S, 8.2 kg on L): buckling factor 4.6 and 18.6,
  in-plane bending ≤ 50 MPa ([`dynamometer_structure.py`](dynamometer_structure.py)).
- **Thrust cell:** a micro S-type cell on the axis between the torque stage's plate and the carriage, on two M6 studs with
  jam nuts. The guided blades (thin in $x$, two pairs separated along $x$) let the carriage move axially and hold it rigidly
  in every other direction.
- **Torque cell:** the torque stage's integral arm at radius $r_a$ presses tangentially on a second cell fixed to the head
  frame's bracket. The spoke flexure (four blades in planes containing the axis, held in slots pinched by M3 screws) lets
  the torque stage turn about the axis and carries the thrust axially to the head frame.
- **One cell family:** every cell from 1 to 50 kg is a micro S-type, 25 × 30 × 12 mm, M6 × 1 at both ends (ATO DYLY-106
  class datasheet drawing), so cells swap without re-machining. Accuracy 0.05 % FS combined, worse than OIML C3 (0.03 %);
  §10 uses 0.05 %.
- **Overload stops:** adjustable screws on both sides of the carriage and of the torque arm, set at 1.5× the cells' full-scale
  deflection (≈ 0.3 mm, ASSUMED 0.2 mm at rated load). They never touch in normal operation.
- **Motor adapters:** interchangeable plates with the motor's bolt pattern, screwed to the carriage's webs; the motor's
  screw heads sit in the carriage's open pockets.
- **Calibration features:** a hook point on the axis in front of the hub (thrust, via a pulley) and a bolt-on calibration bar
  with load holes at known radii on both sides (torque).
- **Material:** 7075-T6 aluminium for the head frame, torque stage, carriage and adapters (low moving mass), spring-steel
  shim (EN42 or full-hard 301 stainless) for the blades, clamped between ground steel clamp bars.

**Cell and flexure selection** (script "Load cells", "Flexure"): the smallest thrust cell with ≥ 1.5× overload margin **and** $f_n$ ≥
100 Hz; the smallest torque cell with that margin on an arm that reaches past the torque flexure's rim ($r_a$ ≥ $r_m$ + $L/2$ + rim
width + 10 mm: 50 mm on S, 102 mm on L).

| Class | Head | Thrust cell | Hover / capacity | Torque cell × arm | Torque capacity | Max torque / capacity | Thrust-flexure $k_p/k_s$ | Torque-flexure $K_\theta/(k r_a^2)$ | Blade stress at the stops |
|---|---|---|---|---|---|---|---|---|---|
| 15" delivery prototype | S | 5 kg | 14.1 % | 2 kg × 100 mm | 1.96 N·m | 36 % | 0.39 % | 0.11 % | 22 MPa |
| MK30-like | L | 20 kg | 31.5 % | 10 kg × 150 mm | 14.7 N·m | 43 % | 4.08 % | 1.04 % | 36 MPa |
| FlyCart-like | L | 50 kg | 23.6 % | 30 kg × 150 mm | 44 N·m | 61 % | 1.63 % | 0.35 % | 36 MPa |

Blades: **S** 4 × (15 × 0.15 × 35 mm) for thrust and 4 × (10 × 0.15 × 25 mm) at $r_m$ = 25 mm for torque; **L** 4 × (50 × 0.50 × 50 mm)
and 4 × (40 × 0.40 × 40 mm) at $r_m$ = 60 mm. Parasitic stiffness stays within a few per cent and is calibrated out (theory
§2.1); stresses are under 10 % of the assumed 500 MPa fatigue limit.

**Cables are the largest uncalibratable error.** The ESC sits on the fixed head frame; the three phase leads cross to the
motor as one long loop of fine-strand silicone wire, routed so the head's motion bends rather than pulls them. Calibrate
with the cables in place and check hysteresis by loading up and down (§7).

---

## 4. Dynamics

### 4.1 Thrust axis

| Symbol | Meaning | Unit |
|---|---|---|
| $m$ | Moving mass on the thrust cell (ASSUMED) | kg |
| $f_n$ | Natural frequency, $\frac{1}{2\pi}\sqrt{k_s/m}$ | Hz |
| $N_b$ | Blades per prop | — |

Script "Thrust-axis dynamics" (moving mass = the thrust stage from the CAD, 0.240 kg (S) and 1.290 kg (L), plus the
motor and prop, ASSUMED):

| Class | $m$ | $f_n$ | $f_n$ / 1× at max | $f_n$ / blade-pass at max | Rotor speeds to avoid dwelling at |
|---|---|---|---|---|---|
| 15" delivery prototype | 0.38 kg | 128 Hz | 1.38 | 0.69 | 53–80 rev/s |
| MK30-like | 1.94 kg | 113 Hz | 1.28 | 0.64 | 47–71 rev/s |
| FlyCart-like | 3.39 kg | 135 Hz | 5.83 | 2.91 | none |

Every class meets requirement 4. The prototype hovers at 52 rev/s, just below its band: steady points stay valid (theory §3,
point 1), sweeps pass through the band without dwelling, and dynamic tests are corrected with the tap-tested $H(s)$.

### 4.2 Boom bending

| Symbol | Meaning | Unit |
|---|---|---|
| $f_\text{lat}$ | Lateral bending mode of the boom with head, motor and prop at its tip | Hz |

Script "Boom lateral" (one 100 × 4 mm boom for both heads; tip mass = head frame + torque stage from the CAD plus the
moving mass):

| Class | Overhang | Tip mass | $f_\text{lat}$ | $f_\text{lat}$ / 1× at max | $f_\text{lat}$ / blade-pass at max |
|---|---|---|---|---|---|
| 15" delivery prototype | 0.265 m | 3.41 kg | 752 Hz | 8.15 | 4.07 |
| MK30-like | 0.35 m | 11.17 kg | 274 Hz | 3.10 | 1.55 |
| FlyCart-like | 0.465 m | 12.62 kg | 168 Hz | 7.23 | 3.61 |

**MK30-size props run at 0.35 m overhang:** at 0.465 m the boom mode (178 Hz) would sit on their blade-pass frequency at
full speed (177 Hz). The boom slides in the saddle, so this is a set-up rule, not a part change.
Imbalance excites the boom at 1×, and every class keeps the boom mode at least 1.86× above it. The frame's own modes must be
checked on the built structure with a tap test (and in FEA from the CAD).

---

## 5. Electronics

| Symbol | Meaning | Unit |
|---|---|---|
| $V_\text{exc}$ | Bridge excitation | V |
| $S$ | Load-cell sensitivity | mV/V |
| $f_s$ | Sample rate | Hz |

**Acquisition board (our first in-house measurement PCB):**

| Block | Choice | Why |
|---|---|---|
| MCU | ESP32-S3 | same toolchain and data-ready-locked loop as the flight firmware ([firmware architecture (drone documents)](../../nodemcu/projects/drone_esp32/docs/firmware/architecture.md)) |
| ADC | 2 × TI ADS131M04 (4 simultaneous 24-bit delta-sigma channels each), one shared clock, synchronised | simultaneous sampling of every analog channel at 2 kHz |
| Bridge front end | low-noise instrumentation amplifier (INA828 class), gain ≈ 100, per bridge | 2 mV/V × 5 V = 10 mV full scale must resolve ≈ 10⁻⁵ (theory §7) |
| Excitation | 5 V low-noise reference/LDO, **measured on its own ADC channel** | ratiometric correction in software |
| ADC 1 channels | thrust bridge, torque bridge, excitation sense, spare bridge | |
| ADC 2 channels | bus voltage (divider), bus current (Hall transducer output), two spares | |
| Current | closed-loop Hall transducer rated ≥ 150 A, isolated | no heat in the 150 A path; ESC current telemetry as a cross-check |
| Speed | optical reflective sensor on the bell or prop hub → timer capture; plus ESC eRPM telemetry (bidirectional DShot, AM32) | period measurement, speed-independent resolution |
| Temperatures | 3 × MAX31856 thermocouple (stator, ESC, ambient), 10 Hz | motor thermal limits |
| Vibration | 3-axis low-noise digital accelerometer on the head, 2–4 kHz | balance and bearing QA |
| ESC command | PWM or DShot generated by the same MCU, timestamped with the samples | known command instants for step tests (theory §6) |
| Link | USB through a digital isolator (or isolated Ethernet); the board powered from an isolated DC/DC | no ground loop with the 150 A power path |
| Safety I/O | E-stop and door-interlock inputs, contactor-drive output, beacon | software stop; the hardwired chain is independent (§8) |

Data rate: 8 channels × 2 kHz × 3 bytes ≈ 48 kB/s, plus speed, temperature and vibration, well inside full-speed USB.

**Firmware:** a sample-locked loop (ADC data-ready interrupt → read both ADCs → timestamp → stream), with hard limits
enforced on the board itself: thrust, torque, current, temperature and vibration over limit → throttle to zero and contactor
open. **PC software:** test sequences (§9), logging, calibration-matrix solving, live plots, and the reports.

---

## 6. Power

| Symbol | Meaning | Unit |
|---|---|---|
| $V_\text{bus}$ | Bus voltage | V |
| $I_\text{bus}$ | Bus current | A |

- **Source:** flight-type battery packs (up to 14S) in a fire-resistant box, so tests see a realistic source impedance and
  braking energy has somewhere to go. A bench supply needs a battery in parallel or a braking resistor, because a decelerating
  motor pushes energy back and can trip or damage a supply.
- **Path:** pack → 200 A fuse → **contactor with precharge** → current transducer → ESC. Connectors and cable rated 60 V / 150 A
  continuous.
- **Emergency stop:** hardwired in the contactor coil circuit, together with the door interlock, independent of the MCU and PC.

---

## 7. Calibration

| Symbol | Meaning | Unit |
|---|---|---|
| $C$, $y_0$ | Calibration matrix and zero offsets (theory §4) | — |
| FS | Cell capacity | N, N·m |

1. **After assembly or a head/cell change:**
   - Thrust: M1-class weights over a pulley on the axis, 0–10–25–50–75–100 % FS and back down (linearity and hysteresis).
   - Torque: weights on the calibration bar at known radii, both directions, also combined with thrust loads (crosstalk).
   - Solve $C$, $y_0$ by least squares. Accept if the residuals are within the budget of §10.
   - **Tap test** of the thrust axis with the motor and prop mounted: record $f_n$ and $\zeta$ for the dynamic correction (theory §3).
2. **Every test day:** a two-point check per channel with one weight.
3. **Every run:** zero with the motor stopped before, and read the zero again after, to measure drift.

---

## 8. Safety

| Symbol | Meaning | Unit |
|---|---|---|
| $E_\text{rot}$ | Rotational energy of the prop at max speed | J |
| $v_\text{tip}$ | Tip speed | m/s |

Prop-burst energy at max speed (script "Propeller burst", prop masses ASSUMED):

| Class | Prop mass | $E_\text{rot}$ | Per blade | $v_\text{tip}$ |
|---|---|---|---|---|
| 15" delivery prototype | 0.020 kg | 41 J | 20 J | 111 m/s |
| MK30-like | 0.150 kg | 694 J | 347 J | 167 m/s |
| FlyCart-like | 0.600 kg | 1000 J | 500 J | 100 m/s |

The large classes reach pistol-round energies (theory §9). Therefore:
- **Test cell:** the stand inside a fenced cell; the operator station outside, behind a barrier, never in or near the plane of
  rotation.
- **Containment:** a steel containment ring around the rotor plane on the L head (thickness and width to be sized for 500 J
  fragments by calculation and a qualification test); polycarbonate guards are sufficient only for the S-head classes.
- **Interlocks:** the cell door opens the contactor; the E-stop is hardwired; the board's limits (§5) stop the motor on
  overload, over-temperature, over-current, excessive vibration or loss of the PC link.
- **Procedure:** props inspected and balanced before every session; a new prop type is first run at reduced speed.

---

## 9. Test procedures

| Symbol | Meaning | Unit |
|---|---|---|
| $\tau_T$, $T_\text{dly}$ | Thrust time constant and delay | s |
| FM, $\eta_\text{drive}$ | Figure of merit, motor + ESC efficiency (theory §1) | — |

1. **Static sweep.** Throttle in 5 % steps, 3 s each, averaging the last 1 s: thrust, torque, speed, voltage, current; then $C_T$,
   $C_Q$, FM, $\eta_\text{drive}$, specific thrust. Skip dwelling in the bands of §4.1.
2. **Step response.** ±5 % steps around hover and other operating points, 8 repeats each; fit $\tau_T$ and $T_\text{dly}$ with the
   identified $H(s)$ (theory §6): the actuator lag the flight controller's gains are designed around.
3. **Frequency response.** A throttle chirp, 0.5–20 Hz, small amplitude around hover: the actuator's Bode plot, used directly in
   the gain design ([control theory §12 (drone documents)](../../nodemcu/projects/drone_esp32/docs/theory/control_theory.md#12-designing-the-rate-controller-of-an-integrator-plus-lag-plant)).
4. **Thermal endurance.** Hold hover, and separately the motor-out thrust (≈ 1.5–2× hover for a hexacopter), until the
   temperatures settle.
5. **Motor end-of-line test** (props off, no load cells needed): phase resistance (DC), no-load speed and current against
   voltage (→ $K_V$, $I_0$), back-EMF symmetry between phases, vibration spectrum at three speeds (balance, bearings), and a
   short run-in. Pass/fail limits come from the first production batch's statistics.

---

## 10. Uncertainty budget

| Symbol | Meaning | Unit |
|---|---|---|
| $u_c$ | Combined standard uncertainty of thrust at hover, 1σ | N |

Script "Thrust uncertainty" (contributions ASSUMED: 0.05 % FS cells, M1 weights, 2 °C drift between zeros):

| Class | $u_c$ | $u_c$ / hover thrust | Largest contribution |
|---|---|---|---|
| 15" delivery prototype | 0.035 N | 0.50 % | cell accuracy and cable/flexure hysteresis, equal |
| MK30-like | 0.139 N | 0.23 % | same |
| FlyCart-like | 0.348 N | 0.30 % | same |

Every class meets requirement 3; the prototype exactly, because the 0.05 % cell is the chosen family's accuracy. A C3-class
5 kg cell (0.03 %) would take it to ≈ 0.4 %, but no C3 cell in this size class was found with a published drawing. The
parasitic-hysteresis term is an assumption: measure it at the first calibration, and route the cables as §3 says.

---

## 11. CAD model

The CadQuery model `/home/aaditya/atelier/synchronous/aaditya/cadquery/scripts/sketch_scripts/projects/prop_dyno.py` is
detailed for manufacture: every joint is modelled (welded members with their end cuts, bolted clamps with their holes and
threads, blades in clamp bars, load cells on threaded studs, levelling feet) and every fastener is counted. It checks
itself on every run (no two parts overlap; no part is unattached) and prints the thrust-axis moving mass and natural
frequency. Configurations: `DYNO_HEAD` (S or L), `DYNO_H_AXIS` (800–1600 in 50 mm steps), `DYNO_PROP_D`. Outputs:
`export/prop_dyno_<HEAD>.stl` (the whole stand, one file), and in `export/prop_dyno/<HEAD>/` one STEP per part, the
assembly STEP, `parts.csv`, `fasteners.csv` and `holes.csv`. `projects/prop_dyno_drawings.py` writes one drawing sheet
per made or outsourced part (`export/prop_dyno/prop_dyno_drawings.pdf`). All load cells are one family (micro S-type,
1–50 kg, 25 × 30 × 12 mm, M6 × 1 both ends), so one adapter design fits every capacity. The motor and prop are
placeholders.

**Resolved (4 Nov 2026): thrust-axis natural frequency.** The first detailed head (thrust stage first, torque stage on
the thrust carriage) gave 52–103 Hz against requirement 4. Reversing the load path (§3) gives 113–135 Hz in every class.

---

## 12. Cell and pack rig

Theory: [the battery cell rig theory](battery_cell_rig_theory.md). Numbers: [`battery_cell_rig_sizing.py`](battery_cell_rig_sizing.py)
(`python3 battery_cell_rig_sizing.py`), inputs marked ASSUMED until the parts are chosen and the first cells measured.

| Symbol | Meaning | Unit |
|---|---|---|
| $C_\text{Ah}$, $E$ | Capacity and energy delivered to the cutoff | Ah, Wh |
| $R_0$, $R_\text{dc,10s}$ | Ohmic resistance; DC resistance read 10 s after a current step | Ω |
| OCV | Open-circuit voltage | V |
| $R_\text{sh}$ | Current shunt | Ω |
| $R_\text{th,sa}$ | Heat-sink thermal resistance, sink to air | K/W |
| $T_j$ | MOSFET junction temperature | °C |
| $S$, $P$ | Cells in series, in parallel | — |

### 12.1 What it tests

- **Bought packs and cells**, to check them against their labels and against each other: the delivery pack (Pro-Range 6S2P,
  Molicel P42A), the radio's Samsung 35E cells, and every cell batch before we build a pack from it.
- **Candidate cells** for our own packs (P42A, P45B, Samsung 50S, and higher-energy cells as they appear), on our mission.
- **Our own packs** at end of line: capacity, resistance per group, imbalance.

**Pack or cell?** The rig loads a whole pack at moderate current (1C continuous, 2C pulses for the delivery pack). The full
flight current of a whole pack (60 A at full throttle on the delivery pack) is reproduced **per cell** instead: a 6S2P pack at
60 A is the same stress as one cell at 30 A, which the rig carries. Pack-level effects (interconnect resistance, imbalance,
centre-cell heating) are measured at the moderate pack currents and in flight logs.

### 12.2 Load on a cell during the delivery mission

Script "Delivery mission" (6S2P P42A pack, 0.5 kg payload, 5 km radius; power from the MN4006 + 15×5 test table plus 15 W
avionics; profile ASSUMED):

| Phase | Duration | Pack power | Cell current | Cell C-rate |
|---|---|---|---|---|
| Take-off and climb to 60 m | 30 s | 434 W | 10.0 A | 2.4C |
| Cruise out, 5 km at 10 m/s | 500 s | 271 W | 6.3 A | 1.5C |
| Descend, drop, climb | 60 s | 298 W | 6.9 A | 1.6C |
| Cruise back (payload gone) | 500 s | 206 W | 4.8 A | 1.1C |
| Descend and land | 40 s | 185 W | 4.3 A | 1.0C |

The mission uses **77 Wh of the pack's 181 Wh nominal (42 %)**. Full throttle on all four motors is 1455 W, 33.7 A per cell
(8C, 75 % of the P42A's rated 45 A). This profile, scaled per cell, is the "mission discharge" of test C5.

### 12.3 Hardware

Shares the dyno's acquisition-board design (§5): a **second board** of the same design (the BOM already carries two), so the dyno
and a week-long cycle-life test can run at the same time, plus a **cell-rig I/O board**:

| Block | Choice | Why |
|---|---|---|
| Load | **In-house linear electronic load**: 10 linear-mode-rated MOSFETs (DC safe operating area checked at 60 V, 300 W), each with its own source resistor for current sharing, an analogue constant-current loop, set by a 16-bit DAC (the ESP32-S3 has none). Constant-power and mission profiles run in firmware on top of it. Built as 300 W modules so 12S-class packs get 3–4 modules in parallel | Rated **60 V, 50 A, 300 W continuous, 1 kW for 10 s pulses**: every cell at its rated current and the delivery pack at 1C and 2C (script "Load") |
| Heat sink | Fan-cooled extruded aluminium, **$R_\text{th,sa}$ ≤ 0.21 K/W**, ≈ 1.5 kg, with a thermistor | 300 W at 45 °C ambient keeps $T_j$ ≤ 125 °C; a 1 kW, 10 s pulse from a sink below 50 °C reaches ≈ 112 °C. Pulses are interlocked to the sink temperature |
| Charger | Programmable CC–CV supply, 60 V / 18 A, remote-controlled (Riden RD6018 class with its input supply) | charges cells and packs under the rig's control and logging; packs are balanced with the hobby balance charger before each benchmark |
| Current | **1 mΩ four-terminal manganin shunt**, 0.1 %, ≤ 20 ppm/K, on an ADS131M04 channel at gain 16 (50 mV at 50 A, 2.5 W) | coulomb counting to ≈ 0.06 % at 1C (§12.5); the Hall transducer of §5 has too much offset drift for slow tests |
| Voltage | Four-wire (Kelvin) sense at the cell or pack terminals; a 5 V range for single cells and a 60 V range for packs, on ADS131M04 channels | ±0.5 mV on a cell after calibration, ≈ ±0.08 % SoC on the OCV curve |
| Pack groups | ADI LTC6813-1 class monitor on the balance lead (up to 18 groups), isolated to the board over isoSPI | every series group's voltage, ≈ ±2.2 mV (datasheet value to confirm): imbalance and the weakest group |
| Temperatures | the board's three MAX31856 channels, plus 8 more on the I/O board; thermocouples on the centre cells, the terminals, the shunt and ambient | heating (theory §7) |
| Switching | Contactors for load and charger, interlocked so both can never be on | |
| Cell fixture | CNC-machined copper clamps for 18650 and 21700, separate current and sense contacts | contact resistance stays out of the voltage reading |
| Enclosure | Steel fire cabinet with a vent to outside, sand tray, smoke/heat detector; the cell or pack under test inside, the load and electronics outside it | test cells can vent and burn (theory §11) |
| Thermal chamber | Insulated box inside the cabinet with a heater and fan, 25 °C and 45 °C set points, with its own hardwired over-temperature cutout | Indian summer conditions |
| Incoming check | Hand-held 1 kHz AC resistance meter (YR1035 class) | 20-second check of every cell before matching |

**Hardwired limits, independent of the MCU:** window comparators on the terminal voltage (over-voltage, under-voltage), a
thermal switch on the cell and on the heat sink, and an over-current trip open the contactors directly, as the E-stop does on
the dyno (§6).

### 12.4 Test procedures

| Test | What | How | Output |
|---|---|---|---|
| **C1 Incoming** | every cell | OCV, 1 kHz resistance, mass; reject outliers; sort | matched groups for pack building |
| **C2 Capacity and energy** | cells and packs | CC–CV charge to 4.20 V/cell, cut at C/20; rest 1 h; constant-current discharge to the cutoff at 0.2C, 1C, the mission cruise current and the rated maximum (cells) or 1C (packs) | $C_\text{Ah}$, $E$, Wh/kg, mean voltage against current (theory §1, §5) |
| **C3 HPPC** | cells | at every 10 % SoC: 10 s discharge pulses at 1C and 3C, 40 s rest, 10 s charge pulse at 0.75C, rest | $R_0$, $R_\text{dc,10s}$, the two-branch model against SoC (theory §2, §3) |
| **C4 OCV curve** | cells | C/20 discharge and charge, averaged; or 5 % steps with 1 h rests | OCV(SoC), hysteresis (theory §4) |
| **C5 Mission discharge** | cells | repeat the §12.2 profile per cell until the cutoff, at 25 °C and 45 °C | deliveries per charge, voltage sag, heating, energy left at landing |
| **C6 Cycle life** | cells | C5 plus charge, repeated; C2 and C3 every 25 cycles; until 80 % capacity | $N_{80}$, capacity and resistance against cycles, cost per delivery (theory §9) |
| **C7 Pack benchmark** | bought and in-house packs | balance-charge; rest; 1C discharge logging every group (LTC6813); a 2C, 10 s pulse at 80, 50 and 20 % SoC; mass | pack $C_\text{Ah}$, $E$, Wh/kg, resistance per group and interconnect resistance (theory §8), end-of-discharge group spread, temperature rise; pass or fail against limits from the first batch |

Each run is a scripted sequence on the PC software of §5, which writes a report with the raw log.

### 12.5 Accuracy

Script "Charge uncertainty", "Voltage", "DCIR" (1σ, P42A cell; shunt calibrated to 0.05 %, 1 µV residual offset after zeroing, ASSUMED):

| Test current | Capacity uncertainty | Limited by |
|---|---|---|
| C/20 (OCV sweep) | 0.48 % | offset (theory §6) |
| 0.2C | 0.13 % | offset |
| 1C | 0.056 % | shunt calibration |
| Mission cruise (6.3 A) | 0.053 % | shunt calibration |
| 45 A | 0.065 % | shunt calibration and self-heating |

- DCIR from a 1C step resolves 2.4 µΩ on a 15 mΩ cell (0.016 %); $R_0$ is read in the first millisecond after the step.
- Group voltages ±2.2 mV ≈ ±0.4 % SoC per group: enough to rank groups, not to map the OCV curve (C4 uses the cell channel).
- Calibration: current against a 6.5-digit reference meter in series at 1, 5, 20 and 50 A; voltage against the same meter;
  thermocouples at the ice point; repeated monthly and after any hardware change.

### 12.6 What it tells us now

Script "Cell heating" and "Cost per delivery" (ASSUMED values until C5 and C6 run):
- Cruise heats a bare P42A by about 0.9 W; over the whole mission that is ≈ 14 K adiabatic, so cooling inside the pack decides
  the landing temperature. Full throttle (25 W per cell) is a short-burst condition only.
- **Battery wear dominates the energy cost of a delivery**: ₹7,659 over an assumed 300 cycles is ₹25.5 per delivery, against ₹0.7
  of electricity. Measuring $N_{80}$ on our profile (C6) is the most valuable single number the rig produces.

---

## 13. Build plan

1. **Phase 1, the full frame with the S head + acquisition board v1.** Validate against the MN4006 + 15×5 manufacturer table
   (thrust, current against throttle) and measure the prototype's thrust lag directly.
   **In parallel, the cell rig (§12)** on the second board: it needs no mechanics beyond the cell fixture and cabinet, and the
   delivery pack and its cells can be benchmarked as soon as they arrive.
2. **Phase 2, L head + full frame + test cell and containment.** Qualify the containment; calibrate; tap-test.
3. **Phase 3, motor end-of-line variant:** a compact fixture running procedure 5 for our own motors.

**Bill of materials** (specifications; prices from a quote round):

| Item | Specification | Qty |
|---|---|---|
| Micro S-type load cells, 0.05 % FS, 2 mV/V, M6 × 1 | 2, 5 kg (S head); 10, 20, 30, 50 kg (L head) | 1 each, + 1 spare 5 kg |
| Spring-steel shim | 0.15, 0.40, 0.50 mm, EN42 or full-hard 301 | 1 sheet each |
| 7075-T6 plate | 10–20 mm, head frames, carriages, hubs | — |
| Steel RHS and plate | per the parts list in [the manufacturing package](propeller_dynamometer_manufacturing_package.md) | — |
| Calibration weights | M1 class, 0.1 kg to 20 kg set; pulley with low-friction bearing | 1 set |
| Acquisition PCB | §5 (ESP32-S3, 2 × ADS131M04, INA front ends, isolation) | 2 (one spare) |
| Hall current transducer | closed loop, ≥ 150 A | 1 |
| Thermocouple boards and K-type probes | MAX31856 | 3 |
| Optical speed sensor | reflective, with reflective tape | 2 |
| Accelerometer | 3-axis low-noise digital | 1 |
| Power path | 200 A fuse, contactor with precharge, E-stop, door interlock, 60 V / 150 A cable and connectors | 1 |
| Containment | steel ring (L), polycarbonate guards (S), cell fencing | 1 |
| ESCs | AM32 with bidirectional DShot, per motor class | per class |
| **Cell rig (§12)** | | |
| Cell-rig I/O board | linear-load modules (10 linear-mode MOSFETs, 16-bit DAC, CC loop), LTC6813-1 with isoSPI, 8 thermocouple channels, contactor drivers, hardwired limit comparators | 1 (+ load modules as needed) |
| Heat sink and fans | extruded aluminium, ≤ 0.21 K/W with fans, ≈ 1.5 kg, thermistor | 1 per 300 W module |
| Current shunt | 1 mΩ, four-terminal manganin, 0.1 %, ≤ 20 ppm/K, ≥ 5 W | 1 (+ 1 spare) |
| Programmable CC–CV supply | 60 V / 18 A, remote-controlled (RD6018 class), with input supply | 1 |
| Contactors | load and charger, 60 V / 60 A DC | 2 |
| Cell fixture | CNC copper clamps, 18650 and 21700, separate sense contacts | 2 |
| Fire cabinet | steel, vented outside, sand tray, smoke/heat detector, inner heated box (25 / 45 °C) with hardwired cut-out | 1 |
| AC resistance meter | 1 kHz, hand-held (YR1035 class) | 1 |
| Reference meter | 6.5-digit DMM, for calibration (shared with the dyno) | 1 |

---

## 14. Shortcomings

| Symbol | Meaning | Unit |
|---|---|---|
| $f_n$ | Thrust-axis natural frequency | Hz |

- Commercial load cells limit the thrust-axis stiffness: $f_n$ ≈ 113–135 Hz; the prototype's 1× band starts just above its
  hover speed (§4.1).
- Static test only: no forward-flight inflow, no rotor–rotor or airframe interaction.
- The uncertainty budget and the flexure, mass and prop values are assumptions until the first calibration and tap test.
- Indoor recirculation and blockage must be checked on the installed stand (theory §8).
- The containment ring must be qualified by test, not only calculated.
- The cell rig loads a whole pack only to 1C continuous and 2C pulses; full-flight pack currents are reproduced per cell, so
  pack-level heating and imbalance at full current come from flight logs.
- The mission profile, cell resistances, cycle life and every accuracy figure in §12 are assumptions until C2–C6 run on real
  cells; the LTC6813 accuracy is a datasheet value to confirm.
