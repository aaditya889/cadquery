# Battery Cell and Pack Characterisation Theory

How to measure what a lithium-ion cell or pack delivers, and why each measurement is done the way it is: capacity and energy,
the equivalent-circuit model, internal resistance from current steps, the open-circuit-voltage curve, why capacity falls with
current, coulomb counting and its errors, cell heating, series–parallel packs, ageing and cost per cycle, and how the model
gives the remaining flight time.

Theory only. Our rig with numbers: [design §12](propeller_dynamometer_design.md#12-cell-and-pack-rig); numbers
from [`battery_cell_rig_sizing.py`](battery_cell_rig_sizing.py). Every section lists its symbols; $\tau$ is always a time
constant, and the time domain is used throughout (no Laplace variable here).

---

## 1. What is measured, and what follows from it

| Symbol | Meaning | Unit |
|---|---|---|
| $v(t)$, $i(t)$ | Terminal voltage and current; $i > 0$ is discharge | V, A |
| $C_\text{Ah}$ | Capacity: charge delivered from full to the cutoff voltage | Ah |
| $E$ | Energy delivered over the same discharge | Wh |
| $V_\text{max}$, $V_\text{cut}$ | Charge voltage limit, discharge cutoff voltage | V |
| $C_\text{nom}$ | Rated capacity | Ah |
| C-rate | Current in units of $C_\text{nom}$ per hour: 1C on a 4.2 Ah cell is 4.2 A | 1/h |
| SoC | State of charge: fraction of the capacity still in the cell | — |
| $m$ | Cell or pack mass | kg |
| $\eta_C$, $\eta_E$ | Coulombic and energy efficiency of a full cycle | — |

Measured directly: $v$, $i$, temperature and time. Everything else follows:

$$
C_\text{Ah} = \frac{1}{3600}\int_0^{t_\text{cut}} i\,dt, \qquad
E = \frac{1}{3600}\int_0^{t_\text{cut}} v\,i\,dt, \qquad
\bar v = \frac{E}{C_\text{Ah}},
$$

where $t_\text{cut}$ is when $v$ first reaches $V_\text{cut}$. $E/m$ is the **specific energy** (Wh/kg), which sets range;
$\eta_C$ is charge out ÷ charge in over a cycle (near 1 for healthy Li-ion), and $\eta_E$ is energy out ÷ energy in (lower, because
the cell charges at a higher voltage than it discharges). **The capacity is not a fixed number:** it depends on the current, the
temperature and the cutoff (§5), so every capacity is reported with all three.

---

## 2. The equivalent-circuit model

| Symbol | Meaning | Unit |
|---|---|---|
| $\text{OCV}(z, T)$ | Open-circuit voltage at SoC $z$ and temperature $T$, after a long rest | V |
| $z$ | SoC | — |
| $R_0$ | Ohmic resistance: electrolyte, current collectors, tabs, contacts | Ω |
| $R_k$, $C_k$ | Resistance and capacitance of polarisation branch $k$ | Ω, F |
| $\tau_k = R_kC_k$ | Time constant of branch $k$ | s |
| $v_k$ | Voltage across branch $k$ | V |
| $Q_\text{cap} = 3600\,C_\text{Ah}$ | Capacity in coulombs | C |

A cell behaves like a voltage source that depends on how full it is, behind a resistance that responds partly at once and partly
slowly. The slow part comes from charge-transfer at the electrode surfaces (milliseconds to seconds) and lithium diffusion in
the particles (seconds to minutes); each is lumped into one resistor–capacitor branch:

$$
v = \text{OCV}(z, T) - iR_0 - \sum_k v_k, \qquad
\frac{dv_k}{dt} = -\frac{v_k}{\tau_k} + \frac{i}{C_k}, \qquad
\frac{dz}{dt} = -\frac{i}{Q_\text{cap}} .
$$

**Intuition:** draw a current and the voltage drops at once by $iR_0$, then keeps sagging as each branch charges toward $iR_k$
with time constant $\tau_k$; stop the current and the voltage recovers the same way, toward the OCV. Two branches (one fast,
one slow) fit Li-ion cells well over a flight. **Shortcomings:** the parameters change with SoC, temperature, current direction
and age, so they are tabulated against SoC and temperature (§3); the model omits voltage hysteresis between charge and
discharge (§4) and is linear in current, which fails at very high rates.

---

## 3. Internal resistance from a current step (DCIR and HPPC)

| Symbol | Meaning | Unit |
|---|---|---|
| $\Delta I$ | Current step | A |
| $\Delta v(t)$ | Voltage change since the step | V |
| $R_\text{dc}(t)$ | DC resistance read at time $t$ after the step | Ω |
| $\sigma_v$ | Voltage noise per reading | V |

Apply a step $\Delta I$ from rest. Solving the branch equations of §2 with $v_k(0) = 0$ (each branch charges exponentially) gives

$$
\Delta v(t) = -\Delta I\left[R_0 + \sum_k R_k\left(1 - e^{-t/\tau_k}\right)\right] .
$$

So $R_\text{dc}(t) = -\Delta v(t)/\Delta I$ rises from $R_0$ at the instant of the step to $R_0 + \sum R_k$ after all branches settle.
**"Internal resistance" therefore needs a time stamp:** $R_0$ is read in the first millisecond (after the load's own rise
time), and the commonly quoted DCIR is read at 10 s. The 1 kHz AC resistance of a hand-held meter is close to $R_0$; it is a fast
incoming check, not a model parameter.

**Resolution:** two readings each with noise $\sigma_v$ give $\delta R \approx \sqrt2\,\sigma_v/\Delta I$; bigger steps resolve better, at the cost of
heating and of a slightly different operating point.

**HPPC (hybrid pulse power characterisation):** at each SoC step (every 10 %), a discharge pulse, a rest, a charge pulse and a rest.
Fitting the equation above to each pulse by least squares gives $R_0$, $R_k$ and $\tau_k$ against SoC and temperature: the full model
of §2. The ratio of charge to discharge resistance, and its change with temperature, comes out of the same test.

---

## 4. The open-circuit-voltage curve

| Symbol | Meaning | Unit |
|---|---|---|
| $\text{OCV}_\text{d}(z)$, $\text{OCV}_\text{c}(z)$ | Voltage measured during very slow discharge and charge | V |
| $s = d\,\text{OCV}/dz$ | Slope of the OCV curve | V per unit SoC |
| $\delta v$, $\delta z$ | Voltage error and the resulting SoC error | V, — |

The OCV is the voltage with no current flowing and every branch relaxed. Two ways to measure it:
- **Slow sweep:** discharge and charge at C/20; at that current $iR$ is a few millivolts, and the average of the two curves cancels
  the remaining $iR$ to first order, $\text{OCV} \approx \tfrac12(\text{OCV}_\text{d} + \text{OCV}_\text{c})$.
- **Rest steps (GITT-like):** remove 5 % SoC, rest until the voltage stops moving (an hour or more), record, repeat. Slower, more
  accurate, and it also shows the relaxation, which identifies the slow branch.

**Why it matters:** voltage is the only direct window on SoC. A voltage error $\delta v$ maps into an SoC error
$\delta z = \delta v/s$. Li-ion curves are flattest in the middle, so the voltage measurement must be best there; LFP cells are so flat
that voltage alone barely locates SoC. The gap between charge and discharge curves that survives long rests is **hysteresis**;
it is small for NMC cells and must be measured, not assumed.

---

## 5. Why usable capacity falls with current and with cold

| Symbol | Meaning | Unit |
|---|---|---|
| $R_\text{eff}$ | Effective resistance over the discharge, about $R_0 + \sum R_k$ | Ω |
| $z_\text{cut}$ | SoC left in the cell when the terminal voltage reaches $V_\text{cut}$ | — |
| $I$ | Constant discharge current | A |

At constant current the polarisation settles, and the discharge stops when $\text{OCV}(z) - IR_\text{eff} = V_\text{cut}$. The charge that
remains is therefore

$$
z_\text{cut} = \text{OCV}^{-1}\!\left(V_\text{cut} + IR_\text{eff}\right) .
$$

**Intuition:** the larger the current, the higher the open-circuit voltage at which the terminal voltage hits the cutoff, so the
more charge is stranded. Energy falls faster than capacity, because the delivered voltage is lower by $IR_\text{eff}$ the whole way and
$I^2R_\text{eff}$ is lost as heat. Cold raises $R_\text{eff}$ and so strands more. The stranded charge is not lost: it comes out at a lower
current, which is why a drone that landed on low voltage shows a recovered voltage after a rest. (Peukert's law, an empirical
power law for lead-acid batteries, is not used here; the resistance model explains Li-ion behaviour directly.)

---

## 6. Coulomb counting and its errors

| Symbol | Meaning | Unit |
|---|---|---|
| $R_\text{sh}$ | Current-shunt resistance | Ω |
| $\varepsilon_G$ | Relative gain error of the current measurement (shunt value, temperature coefficient, ADC gain) | — |
| $V_\text{off}$ | Residual offset voltage after zeroing | V |
| $I_\text{off} = V_\text{off}/R_\text{sh}$ | Equivalent current offset | A |
| $\alpha$ | Shunt temperature coefficient | 1/K |

Measured current $i_m = (1 + \varepsilon_G)\,i + I_\text{off}$. Integrating over a test of length $t$ at constant current $I$:

$$
\frac{\delta C_\text{Ah}}{C_\text{Ah}} = \varepsilon_G + \frac{I_\text{off}}{I} .
$$

**Intuition:** a gain error is the same fraction at every current, but an offset is a fixed current that grows in relative
size as the test current falls, so slow tests (C/20 OCV sweeps, long rests) are limited by offset and fast tests by gain.
Shunt self-heating adds a gain error $\alpha\,\Delta T$ with $\Delta T = I^2R_\text{sh}R_\text{th}$, so the shunt must be large enough to read small currents
and small enough not to heat at large ones. Calibrate gain against a reference at several currents; re-zero offset at every rest.

---

## 7. Cell heating

| Symbol | Meaning | Unit |
|---|---|---|
| $\dot q$ | Heat generated in the cell | W |
| $m_c c_p$ | Cell heat capacity | J/K |
| $R_\text{th}$ | Thermal resistance from the cell to the surrounding air | K/W |
| $T$, $T_a$ | Cell and ambient temperature | K |
| $\tau_\text{th} = m_cc_pR_\text{th}$ | Thermal time constant | s |
| $h$, $A_s$ | Convection coefficient, cell surface area | W/(m²·K), m² |

Heat is the power lost in the resistances: $\dot q = i^2R_0 + \sum_k v_k^2/R_k$ (the reversible entropic heat $iT\,\partial\text{OCV}/\partial T$ is a few
per cent of this at flight currents and is neglected). The lumped energy balance

$$
m_cc_p\frac{dT}{dt} = \dot q - \frac{T - T_a}{R_\text{th}}, \qquad R_\text{th} = \frac{1}{hA_s},
$$

has two limits. Short events ($t \ll \tau_\text{th}$) are **adiabatic**, $\Delta T \approx \dot q\,t/(m_cc_p)$; long steady loads settle at
$\Delta T = \dot qR_\text{th}$. A bare 21700 cell in still air has $\tau_\text{th}$ of about 20 minutes, comparable to a delivery flight, so neither limit
holds over a whole flight and the full equation is integrated. Inside a pack, neighbouring cells shield one another, so
$R_\text{th}$ is higher and the centre cells run hottest: measure there.

---

## 8. Series–parallel packs

| Symbol | Meaning | Unit |
|---|---|---|
| $S$, $P$ | Cells in series, cells in parallel per group | — |
| $j$ | Index of a series group | — |
| $v_j$ | Voltage of group $j$ | V |
| $R_{0,i}$ | Ohmic resistance of cell $i$ in a group | Ω |
| $R_\text{ic}$ | Interconnect resistance (strips, welds, wires) | Ω |

- **Scaling:** a pack of $S$ series groups, each of $P$ identical cells in parallel, has $S$ times the voltage, $P$ times the capacity, and resistance $SR/P$ plus the
  interconnects. A pack test therefore checks the cells **and** the build: $R_\text{pack} - SR/P$ is the interconnect resistance.
- **The weakest group ends the discharge.** The protection (or the pilot) stops when the lowest group reaches $V_\text{cut}$, so the usable
  capacity is that of the group with the least charge. The spread of $v_j$ at the end of discharge measures the imbalance.
- **Current sharing inside a group:** at a step, current divides inversely with resistance, $i_i \propto 1/R_{0,i}$, so a low-resistance cell
  works harder, heats more and ages faster; over seconds the shares move toward equal SoC. Matching cells by capacity and
  resistance before building a pack keeps both effects small.

---

## 9. Ageing and cost per cycle

| Symbol | Meaning | Unit |
|---|---|---|
| $N_{80}$ | Cycles until capacity falls to 80 % of new | — |
| $c_\text{pack}$ | Pack price | ₹ |
| $c_\text{del}$ | Battery cost per delivery | ₹ |

Each cycle loses a little capacity and raises the resistance. The rate depends on depth of discharge, current, temperature
(heat accelerates it strongly) and the voltage the cell is kept at. End of life is conventionally 80 % of new capacity, or a
resistance rise large enough to cut the power available at low SoC. If one delivery is one cycle,

$$
c_\text{del} = \frac{c_\text{pack}}{N_{80}},
$$

and for a delivery drone this wear cost is far larger than the electricity to recharge. $N_{80}$ must be measured on the real
mission profile at the real temperatures: datasheet cycle life is usually quoted at gentle rates and 25 °C.

---

## 10. From the model to the remaining flight time

| Symbol | Meaning | Unit |
|---|---|---|
| $\hat z$ | Estimated SoC | — |
| $P_\text{fut}(t)$ | Predicted electrical power for the rest of the flight | W |
| $t_\text{rem}$ | Remaining flight time to $V_\text{cut}$ on the weakest group | s |

The model of §2 with its tables is what turns battery measurements into a safety function. In flight:
1. **Estimate SoC** by coulomb counting (§6) corrected by comparing the measured voltage with the model's predicted voltage;
   a Kalman filter does this optimally, weighting the current integral (good short-term, drifts) against the voltage (noisy,
   absolute through the OCV curve).
2. **Predict** by simulating the model forward under $P_\text{fut}(t)$ (the power needed to fly home and land, from the propulsion
   data); $t_\text{rem}$ is when the predicted voltage of the weakest group reaches $V_\text{cut}$ (§5, §8).
3. **Decide:** return home when $t_\text{rem}$ falls to the time needed plus a reserve.

**Shortcomings:** the prediction is only as good as $P_\text{fut}$ (wind) and the model's temperature and ageing tables, so the
reserve must cover both; the model must be refitted as the pack ages.

---

## 11. Shortcomings

- The two-branch model is linear and averaged; it misses hysteresis and very-high-rate effects, and its parameters vary between
  cells and over life.
- Lab tests at constant temperature differ from flight, where the pack heats and airflow cools it; flight logs must validate
  the model.
- Cycle-life results are slow (weeks) and specific to the profile and temperature tested.
- Safety: lithium cells under test can vent and burn; every rule in the rig design (fire cabinet, independent cutoffs,
  no unattended tests outside it) follows from that.
