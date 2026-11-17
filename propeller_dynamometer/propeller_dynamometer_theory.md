# Thrust-Stand (Propeller Dynamometer) Theory

How a propeller dynamometer measures thrust, torque, speed and electrical power accurately, and why: load paths and
flexures, sensor dynamics against rotor excitation, torque by reaction arm, the calibration matrix, the uncertainty
budget, derived performance quantities, thrust-lag measurement, the electronics chain, installation aerodynamics and
rotor-burst energy.

Theory only. Our dyno design with numbers: [the design document](propeller_dynamometer_design.md); numbers from
[`dynamometer_sizing.py`](dynamometer_sizing.py). Rotor aerodynamics: [multirotor dynamics §2 (drone documents)](../../nodemcu/projects/drone_esp32/docs/theory/multirotor_dynamics.md#2-rotor-aerodynamics).
Every section lists its symbols; torque is $M$ (on the stand) or $Q$ (rotor drag torque), $\tau$ is a time constant.

---

## 1. What a dynamometer measures, and what follows from it

| Symbol | Meaning | Unit |
|---|---|---|
| $T$ | Thrust | N |
| $Q$ | Rotor shaft torque (equal and opposite to the reaction on the stand) | N·m |
| $\Omega$, $n = \Omega/2\pi$ | Rotor speed | rad/s, rev/s |
| $V$, $I$ | Bus voltage and current into the ESC | V, A |
| $P_\text{mech} = Q\Omega$ | Shaft power | W |
| $P_\text{el} = VI$ | Electrical power | W |
| $\eta_\text{drive} = P_\text{mech}/P_\text{el}$ | Motor + ESC efficiency | — |
| $\rho$, $D$, $A = \pi D^2/4$ | Air density, prop diameter, disc area | kg/m³, m, m² |
| $C_T$, $C_Q$ | Thrust and torque coefficients, $T = C_T\rho n^2D^4$, $Q = C_Q\rho n^2D^5$ | — |
| FM | Figure of merit | — |
| $T/P_\text{el}$ | Specific thrust | N/W (or g/W) |

Measured directly: $T$, $Q$, $\Omega$, $V$, $I$ (plus temperatures and vibration). Everything else follows:
- $C_T = T/(\rho n^2D^4)$ and $C_Q = Q/(\rho n^2D^5)$ characterise the prop independently of speed.
- **Figure of merit**, ideal hover power over actual: momentum theory gives the ideal induced power
  $P_\text{ideal} = T^{3/2}/\sqrt{2\rho A}$, so

$$
\text{FM} = \frac{T^{3/2}}{P_\text{mech}\sqrt{2\rho A}} .
$$

- $\eta_\text{drive}$ separates motor and ESC losses from the prop's; specific thrust $T/P_\text{el}$ is what sets endurance.
- **Motor constants:** with the prop off, $K_e \approx V_e/\Omega$ from the back-EMF (or the no-load speed), the phase resistance
  from a DC measurement, and the no-load current $I_0$ ([multirotor dynamics §6.1 (drone documents)](../../nodemcu/projects/drone_esp32/docs/theory/multirotor_dynamics.md#61-electrical-and-mechanical-model)).

---

## 2. Load path and flexures

### 2.1 Parasitic stiffness: how much force reaches the sensor

| Symbol | Meaning | Unit |
|---|---|---|
| $F$ | Force applied to the floating part | N |
| $k_s$ | Stiffness of the sensor (load cell) along the measured axis | N/m |
| $k_p$ | Parasitic stiffness in parallel: guiding flexures, cables, hoses | N/m |
| $F_s$ | Force through the sensor | N |
| $x$ | Displacement of the floating part | m |

The floating part (motor, prop, mount) is guided by flexures and connected to ground through the sensor. Both deflect by
the same $x$, so $F = (k_s + k_p)x$ and

$$
\frac{F_s}{F} = \frac{k_s}{k_s + k_p} = \frac{1}{1 + k_p/k_s} .
$$

The sensor sees only the fraction $1/(1 + k_p/k_s)$. A **constant** $k_p$ is a gain error that calibration with the parts
installed removes exactly. What calibration cannot remove is $k_p$ that changes (cables that move, hysteresis in
flexures or wire insulation, temperature). **Design rule: $k_p/k_s$ of a few per cent at most, and calibrate with every cable
in its flying position.**

### 2.2 The guided-blade (parallel) flexure

| Symbol | Meaning | Unit |
|---|---|---|
| $n_b$ | Number of blades | — |
| $E$ | Young's modulus of the blade material | Pa |
| $w$, $t$, $L$ | Blade width, thickness, free length | m |
| $I_b = wt^3/12$ | Second moment of area of one blade | m⁴ |
| $\delta$ | Displacement along the measured axis | m |
| $k_\text{flex}$ | Flexure stiffness along the measured axis | N/m |
| $\sigma_{\max}$ | Peak bending stress | Pa |

Blades clamped at both ends and parallel, so the floating plate translates without rotating: each blade is a
fixed–guided beam. The tip force for a tip deflection $\delta$ is $12EI_b\delta/L^3$, so

$$
k_\text{flex} = n_b\frac{12EI_b}{L^3} = n_b\frac{Ewt^3}{L^3} .
$$

The bending moment is largest at the clamps, $M_b = 6EI_b\delta/L^2$, and the stress $\sigma = M_b(t/2)/I_b$:

$$
\sigma_{\max} = \frac{3Et\,\delta}{L^2} .
$$

Stiffness rises with $t^3$ but stress only with $t$, so **thin, long blades** give low parasitic stiffness at low stress.
In their own plane the blades are very stiff, so they carry the weight, side loads and moments without loading the sensor.
*Shortcomings:* clamp compliance, blade buckling under in-plane compression, and the small parasitic rotation of real
(non-ideal) parallel flexures.

### 2.3 The spoke (rotational) flexure

| Symbol | Meaning | Unit |
|---|---|---|
| $K_\theta$ | Rotational stiffness about the thrust axis | N·m/rad |
| $r_m$ | Mean radius of the blades | m |
| $\theta$ | Rotation of the floating hub | rad |
| $n_b, E, I_b, L$ | As in §2.2 | — |

Blades lying in planes that contain the thrust axis, joining a hub to a rim, let the hub turn about the axis while staying
stiff axially and radially. Approximating each blade as fixed–guided with tangential deflection $r_m\theta$, and noting its tip
force acts at radius $r_m$:

$$
K_\theta \approx n_b\frac{12EI_b}{L^3}\,r_m^2 .
$$

It is a rough estimate (the blade ends also rotate), so treat the result as an order of magnitude and calibrate it out.

### 2.4 Overload stops
A load cell deflects only ~0.1–0.3 mm at rated load. Hard stops set just beyond that deflection (in both directions) take
crash, prop-strike and handling loads before the cell yields. They must not touch in normal operation, or they become a
large, variable $k_p$.

---

## 3. Sensor dynamics against rotor excitation

| Symbol | Meaning | Unit |
|---|---|---|
| $m$ | Moving mass on the sensor (motor, prop, floating plates) | kg |
| $k$ | Total stiffness, $k_s + k_p$ | N/m |
| $c$ | Damping coefficient | N·s/m |
| $\omega_n = \sqrt{k/m}$, $f_n = \omega_n/2\pi$ | Natural frequency | rad/s, Hz |
| $\zeta = c/(2\sqrt{km})$ | Damping ratio | — |
| $Q_r = 1/(2\zeta)$ | Resonance amplification | — |
| $F(t)$, $x(t)$ | Applied force and displacement | N, m |
| $H(s)$ | Sensor transfer function, applied force → measured force | — |
| $r = f/f_n$ | Frequency ratio | — |
| $N_b$, $f_r$ | Blades, rotor rotation frequency | —, Hz |

The floating part on its sensor is a mass–spring–damper: $m\ddot x + c\dot x + kx = F(t)$, and the sensor reports $kx$. Laplace
domain:

$$
H(s) = \frac{kX}{F} = \frac{\omega_n^2}{s^2 + 2\zeta\omega_ns + \omega_n^2},\qquad
\lvert H(j\omega)\rvert = \frac{1}{\sqrt{(1 - r^2)^2 + (2\zeta r)^2}} .
$$

- **Below $f_n$** ($r \ll 1$) the sensor reads the true force; the error at $r$ is ≈ $r^2$ (10 % at $r$ = 0.3).
- **At $f_n$** it amplifies by $Q_r = 1/(2\zeta)$: lightly damped metal structures have $\zeta$ ≈ 0.01–0.05, i.e. 10–50×.
- **Above $f_n$** it attenuates as $1/r^2$: the sensor is isolated from that vibration.

A rotor excites the stand at its rotation frequency $f_r$ (imbalance), at the blade-pass frequency $N_bf_r$, and their
multiples. Consequences:
1. **The mean (steady) reading is unaffected** by resonance, because the system is linear; but amplified vibration raises
   peak loads (overload, fatigue) and, if large, nonlinear errors.
2. **Avoid dwelling** where $f_r$ or $N_bf_r$ is within about ±20 % of $f_n$; sweep through such bands.
3. **Dynamic measurements** (thrust lag, §6) need $f_n$ well above the band of interest: at least ~3× it, and correct the
   remainder with the identified $H(s)$.
4. **Raise $f_n$** with a stiffer sensor or less moving mass; **lower $Q_r$** with added damping (constrained-layer or
   elastomer damping, eddy-current dampers).
5. **Identify $H(s)$** on the assembled stand with a tap (impulse) test: the ringing frequency gives $f_n$, its decay gives $\zeta$.

---

## 4. Torque by reaction arm, crosstalk and the calibration matrix

| Symbol | Meaning | Unit |
|---|---|---|
| $M$ | Reaction torque on the stand (= rotor torque $Q$) | N·m |
| $F_Q$ | Tangential force on the torque cell | N |
| $r_a$ | Torque-arm radius | m |
| $K_\theta$, $k_Q$ | Rotational flexure stiffness; torque-cell stiffness | N·m/rad, N/m |
| $y = [y_T, y_Q]^\top$ | Raw readings of the thrust and torque channels | counts |
| $u = [T, M]^\top$ | True loads | N, N·m |
| $C$, $y_0$ | 2×2 calibration matrix and zero offsets | — |
| $j$ | Index of a calibration load case | — |

The motor sits on a rotational flexure (§2.3); a radial arm of radius $r_a$ is stopped tangentially by a load cell, so
$M = F_Qr_a$ while the cell path dominates. The parasitic fraction is $K_\theta/(k_Qr_a^2)$ (§2.1 with $k_s = k_Qr_a^2$).

Real stands have **crosstalk**: misalignment and flexure asymmetry make thrust leak into the torque reading and vice versa.
Model the readings as linear:

$$
y = C\,u + y_0 .
$$

**Calibration:** apply known loads $u_j$ (dead weights over a pulley for thrust; weights on a calibration arm at a known radius,
both directions, for torque, also combined with thrust), record $y_j$, and solve for $C$ and $y_0$ by least squares. In use,
$u = C^{-1}(y - y_0)$. Checks: the off-diagonal terms (crosstalk) should be small and repeatable; non-linearity appears as
residuals growing with load.

---

## 5. Uncertainty budget

| Symbol | Meaning | Unit |
|---|---|---|
| $u_i$ | Standard uncertainty (1σ) of contribution $i$ | N |
| $u_c = \sqrt{\sum u_i^2}$ | Combined standard uncertainty | N |
| $U = k_c u_c$ | Expanded uncertainty, coverage factor $k_c$ (2 for ≈ 95 %) | N |
| FS | Rated capacity of the sensor | N |

The GUM method: list every independent error source as a standard uncertainty, combine by root-sum-square. Typical sources:
- **sensor class:** combined non-linearity, hysteresis and repeatability, a fraction of FS;
- **temperature:** zero drift per °C times the change since the last zero (zero often);
- **calibration masses:** their class tolerance;
- **residual crosstalk** after the matrix;
- **parasitic stiffness and hysteresis** not removed by calibration (cables);
- **noise** after averaging a steady point;
- **misalignment:** cosine error $1 - \cos\varphi$ (0.5° gives 4×10⁻⁵, usually negligible).

Most sources scale with FS, not with the reading, so **a sensor run at a small fraction of its capacity has a large relative
error**. This sets the cell size: just large enough for the overload margin and the stiffness target (§3).

---

## 6. Measuring thrust lag

| Symbol | Meaning | Unit |
|---|---|---|
| $\tau_T$ | Time constant of thrust following a command step | s |
| $T_\text{dly}$ | Pure delay (command transmission, ESC) | s |
| $T_\text{cmd}$, $T_\text{meas}$ | Commanded and measured thrust | N |
| $H(s)$ | Sensor dynamics (§3) | — |
| $f_c = 1/(2\pi\tau_T)$ | Corner frequency of the lag | Hz |

A rotor's thrust lag can differ from its speed lag (inflow takes time to build), so the control-relevant actuator model
needs thrust itself. Command small steps around the operating point and fit, in the Laplace domain,

$$
\frac{T_\text{meas}}{T_\text{cmd}} = \frac{e^{-sT_\text{dly}}}{\tau_Ts + 1}\,H(s),
$$

with $H(s)$ fixed from the tap test, by the same separable least squares as the audio method
([motor identification from audio §7 (drone documents)](../../nodemcu/projects/drone_esp32/docs/theory/motor_id_from_audio.md#7-the-model-fitted-to-each-step)). Because the stand knows when it sent the
command, the delay $T_\text{dly}$ **is** measured here, unlike in audio. To resolve $\tau_T$ well the sensor must be flat to roughly
10× $f_c$ (30 Hz for a 50 ms lag), hence the $f_n$ target of §3.

---

## 7. The electronics chain

| Symbol | Meaning | Unit |
|---|---|---|
| $S$ | Bridge sensitivity, output per volt of excitation at full scale | mV/V |
| $V_\text{exc}$ | Bridge excitation | V |
| $V_\text{FS} = SV_\text{exc}$ | Bridge output at full scale | V |
| $G_a$ | Front-end amplifier gain | — |
| $V_\text{ref}$ | ADC input range (reference) | V |
| $e_n$ | Input-referred noise (RMS over the bandwidth) | V |
| $N_\text{eff}$ | Effective resolution, $\log_2(V_\text{FS}/e_n)$ | bits |
| $R_\text{sh}$ | Current-shunt resistance | Ω |
| $f_s$ | Sample rate | Hz |

- **Strain-gauge bridge:** output $V_\text{FS} = SV_\text{exc}$, e.g. 2 mV/V × 5 V = 10 mV at full scale. Measure **ratiometrically**
  (output divided by the measured excitation) so excitation drift cancels.
- **Resolution:** to resolve a fraction $\varepsilon$ of FS the input-referred noise must be $e_n < \varepsilon V_\text{FS}$; $10^{-5}$ of 10 mV is
  100 nV, about 17 effective bits. A low-noise instrumentation amplifier ($G_a$ ≈ 100) in front of a 24-bit delta-sigma ADC
  achieves this; averaging $N$ samples of white noise lowers it by $\sqrt N$.
- **Simultaneous sampling** of thrust, torque, voltage and current (one shared clock) keeps power and efficiency consistent
  during transients.
- **Current:** a shunt dissipates $I^2R_\text{sh}$ and sits in the power path; a closed-loop Hall transducer is isolated and
  dissipates nothing, at some offset drift. Either needs a bandwidth well above the ESC's input ripple or a filter before
  sampling.
- **Speed:** count optical pulses (one or more marks per revolution) with a hardware timer; period measurement gives
  resolution independent of speed. ESC telemetry (electrical RPM) is a cross-check.
- **Grounding and isolation:** hundreds of amps of switching current share the power ground; isolate the data link to the
  PC and keep sensor grounds separate from power returns, or ground loops add noise in the microvolt range that matters.
- **Anti-aliasing:** filter every channel below $f_s/2$ before (or inside, for delta-sigma) the ADC
  ([control theory §9 (drone documents)](../../nodemcu/projects/drone_esp32/docs/theory/control_theory.md#9-sampling-and-aliasing)).

---

## 8. Installation aerodynamics

| Symbol | Meaning | Unit |
|---|---|---|
| $T_\text{IGE}/T_\text{OGE}$ | Thrust in ground effect ÷ out of ground effect, same power | — |
| $R$ | Rotor radius | m |
| $z$ | Distance from the rotor to a surface facing its wake | m |

- **Wake obstruction.** A surface across the wake raises thrust at a given power. For a rotor at height $z$ over the ground,
  the Cheeseman–Bennett estimate is

$$
\frac{T_\text{IGE}}{T_\text{OGE}} = \frac{1}{1 - (R/4z)^2},
$$

  1.6 % at $z = 2R$ (one diameter), 0.4 % at $z = 4R$. Point the wake into open space, away from the stand.
- **Blockage.** Structure in the inflow or the wake disturbs the flow; keep the stand upstream (in the slower inflow), slim,
  and at least a radius or so from the disc.
- **Recirculation.** Indoors the wake returns as inflow and drifts the readings over a run; use a large space, an open-ended
  duct for the wake, or test outdoors in calm air. Check by repeating a point after long runs.

---

## 9. Rotor-burst energy and containment

| Symbol | Meaning | Unit |
|---|---|---|
| $m_p$ | Prop mass | kg |
| $I_p \approx m_pD^2/12$ | Prop inertia (each blade as a rod from hub to tip) | kg·m² |
| $E_\text{rot} = \tfrac12I_p\Omega^2$ | Rotational energy | J |
| $v_\text{tip} = \pi Dn$ | Tip speed | m/s |

A failed prop releases $E_\text{rot}$ as fragments leaving in the plane of rotation. Large props at speed store hundreds of joules
(a 9 mm pistol round has about 500 J). **Nobody stands in the plane of rotation; the operator controls the stand remotely
from behind a barrier; the rotor plane is enclosed by a structure rated for the fragment energy; and the stand's software
and a hardwired emergency stop cut power on any abnormal reading.**

---

## 10. Shortcomings
- Linear models for flexures and sensors; real ones show hysteresis, creep and temperature effects that only careful
  calibration and frequent zeroing control.
- Static (axial-flow-free) testing: no forward-flight inflow, no rotor–rotor interaction, no airframe blockage.
- Ground-effect and blockage estimates are approximate; verify installation effects by moving the stand.
