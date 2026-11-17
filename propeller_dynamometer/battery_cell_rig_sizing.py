#!/usr/bin/env python3
"""Numbers behind the cell and pack rig in propeller_dynamometer_design.md §12: per-cell load of the delivery mission, load and
heat-sink rating, current-shunt and coulomb-counting uncertainty, voltage and DCIR resolution, cell heating, and battery
cost per delivery. Method: battery_cell_rig_theory.md.

Every input marked ASSUMED is a representative value; replace it with datasheet, purchase or measured values.
Run from cadquery/propeller_dynamometer/: python3 battery_cell_rig_sizing.py
"""
import math

# Cells (ASSUMED from the makers' datasheets; verify against the datasheet of the batch actually bought)
cells = [
    # name, capacity Ah, nominal / max / cutoff V, max continuous A, mass kg, DC resistance ohm (ASSUMED until measured)
    dict(name="Molicel P42A (21700)", Q=4.2, Vn=3.6, Vmax=4.2, Vmin=2.5, Imax=45.0, m=0.070, R=0.015),
    dict(name="Molicel P45B (21700)", Q=4.5, Vn=3.6, Vmax=4.2, Vmin=2.5, Imax=45.0, m=0.070, R=0.013),
    dict(name="Samsung 50S (21700)", Q=5.0, Vn=3.6, Vmax=4.2, Vmin=2.5, Imax=25.0, m=0.069, R=0.020),
    dict(name="Samsung 35E (18650, radio)", Q=3.4, Vn=3.6, Vmax=4.2, Vmin=2.65, Imax=8.0, m=0.048, R=0.035),
]
packs = [
    # name, series, parallel, cell (index into cells or a dict), mass kg, price INR (ASSUMED unless noted)
    dict(name="Delivery pack 6S2P P42A (bought)", S=6, P=2, cell=0, m=0.90, price=7659),     # price: Robu, 31 Oct 2026
    dict(name="Drone 1 3S 2200 mAh LiPo", S=3, P=1, cell=dict(Q=2.2, Vn=3.7, Vmax=4.2, Vmin=3.3, Imax=88.0, R=0.008), m=0.19, price=None),
    dict(name="12S4P P45B (MK30-class, future)", S=12, P=4, cell=1, m=3.4, price=None),
]

# Delivery mission (0.5 kg payload, 5 km radius; ASSUMED profile). Hover power from the MN4006 + 15x5 table (64 W per motor
# at 700 g) plus 15 W of avionics; power after the drop scales as mass^1.5 (momentum theory).
P_HOVER = 4 * 64 + 15
P_LIGHT = 4 * 64 * (2.3 / 2.8) ** 1.5 + 15
P_FULL = 4 * 360 + 15                                 # all four motors at full throttle (table: 15 A, 360 W each)
mission = [  # phase, duration s, electrical power W
    ("take-off and climb to 60 m", 30, 1.6 * P_HOVER),
    ("cruise out, 5 km at 10 m/s", 500, 1.0 * P_HOVER),
    ("descend, drop, climb", 60, 1.1 * P_HOVER),
    ("cruise back", 500, 1.0 * P_LIGHT),
    ("descend and land", 40, 0.9 * P_LIGHT),
]

# Rig (ASSUMED until parts are chosen)
RIG = dict(V=60.0, I=50.0, P_cont=300.0, P_pulse=1000.0, t_pulse=10.0, n_fet=10, Rth_jcs=0.6, Ta=45.0, Tj_max=125.0,
           sink_kg=1.5, c_al=900.0)
SHUNT = dict(R=1e-3, tol_after_cal=0.0005, tcr=20e-6, Rth=10.0, adc_fs=0.075, adc_gain_drift=0.0001, v_off=1e-6)
V_NOISE = 5e-6           # V RMS on the cell-voltage channel after a 10-sample average (ASSUMED)
V_UNC = 0.5e-3           # V, cell-voltage uncertainty after calibration against a 6.5-digit DMM (ASSUMED)
OCV_SLOPE = 6e-3         # V per % SoC, mid-range of an NMC cell (ASSUMED; measured by test C4)
LTC6813_ERR = 2.2e-3     # V, group-voltage total measurement error, LTC6813-1 class (ASSUMED; check the datasheet)
CELL_C = 1000.0          # J/(kg K), cell specific heat (ASSUMED)
H_CONV = 10.0            # W/(m^2 K), still air (ASSUMED)
CYCLES = 300             # cycles to 80 % capacity on the mission profile (ASSUMED; measured by test C6)
INR_PER_KWH, CHARGE_EFF = 8.0, 0.85


def row(c):
    print("| " + " | ".join(c) + " |")


def cell_of(p):
    return cells[p["cell"]] if isinstance(p["cell"], int) else p["cell"]


# 1. Mission load on the delivery pack, per cell
pk = packs[0]
c0 = cell_of(pk)
n_cells = pk["S"] * pk["P"]
print("Delivery mission on the 6S2P P42A pack, per cell (cell voltage taken as nominal 3.6 V)\n")
row(["Phase", "duration (s)", "pack power (W)", "pack current (A)", "cell power (W)", "cell current (A)", "cell C-rate", "energy (Wh)"])
row(["---"] * 8)
E_mis = 0.0
for name, t, P in mission:
    Ipk = P / (pk["S"] * c0["Vn"])
    Ic = Ipk / pk["P"]
    E_mis += P * t / 3600
    row([name, f"{t}", f"{P:.0f}", f"{Ipk:.1f}", f"{P / n_cells:.1f}", f"{Ic:.1f}", f"{Ic / c0['Q']:.2f}", f"{P * t / 3600:.1f}"])
Ifull_cell = P_FULL / (pk["S"] * c0["Vn"]) / pk["P"]
E_pack = pk["S"] * pk["P"] * c0["Q"] * c0["Vn"]
print(f"\nMission energy {E_mis:.0f} Wh of {E_pack:.0f} Wh nominal ({E_mis / E_pack * 100:.0f} %); "
      f"full throttle on all motors: {P_FULL:.0f} W, {Ifull_cell:.1f} A per cell ({Ifull_cell / c0['Q']:.1f} C, "
      f"{Ifull_cell / c0['Imax'] * 100:.0f} % of the cell's rated {c0['Imax']:.0f} A).")

# 2. Load rating: what each test asks of the rig
print("\nWhat each test asks of the load (continuous unless marked)\n")
row(["Test object", "max V", "current (A)", "power (W)", "within 300 W / 50 A / 60 V?"])
row(["---"] * 5)
for c in cells:
    P = c["Imax"] * c["Vmax"]
    row([f"{c['name']}, at rated max current", f"{c['Vmax']:.1f}", f"{c['Imax']:.0f}", f"{P:.0f}",
         "yes" if P <= RIG["P_cont"] and c["Imax"] <= RIG["I"] else "no"])
for p in packs:
    c = cell_of(p)
    V = p["S"] * c["Vmax"]
    for label, k, lim in (("1C", 1.0, RIG["P_cont"]), ("2C pulse, 10 s", 2.0, RIG["P_pulse"])):
        I = k * c["Q"] * p["P"]
        row([f"{p['name']}, {label}", f"{V:.1f}", f"{I:.1f}", f"{V * I:.0f}",
             "yes" if V * I <= lim and I <= RIG["I"] and V <= RIG["V"] else "no"])

# 3. Heat sink: N linear MOSFETs share the power; Tj = Ta + P Rth_sa + (P/N) Rth_jcs <= Tj_max
r = RIG
dT_dev = r["P_cont"] / r["n_fet"] * r["Rth_jcs"]
Rth_sa = (r["Tj_max"] - r["Ta"] - dT_dev) / r["P_cont"]
dT_pulse_dev = r["P_pulse"] / r["n_fet"] * r["Rth_jcs"]
dT_sink = r["P_pulse"] * r["t_pulse"] / (r["sink_kg"] * r["c_al"])
Tj_pulse = r["Ta"] + dT_sink + dT_pulse_dev        # cold sink; device impedance taken at its steady value (conservative)
print(f"\nHeat sink: {r['n_fet']} linear-mode MOSFETs, {r['Rth_jcs']} K/W junction-to-sink each, ambient {r['Ta']:.0f} °C, "
      f"Tj ≤ {r['Tj_max']:.0f} °C.\n"
      f"- Continuous {r['P_cont']:.0f} W: {dT_dev:.1f} K across each device, so the sink needs Rth_sa ≤ {Rth_sa:.3f} K/W "
      f"(a fan-cooled extruded sink).\n"
      f"- Pulse {r['P_pulse']:.0f} W for {r['t_pulse']:.0f} s from a cold {r['sink_kg']} kg aluminium sink: sink +{dT_sink:.1f} K, "
      f"device +{dT_pulse_dev:.1f} K, so Tj ≈ {Tj_pulse:.0f} °C.")

# 4. Current shunt and coulomb counting
s = SHUNT
print(f"\nShunt {s['R'] * 1e3:.1f} mΩ: {r['I'] * s['R'] * 1e3:.0f} mV and {r['I']**2 * s['R']:.1f} W at {r['I']:.0f} A "
      f"({r['I'] * s['R'] / s['adc_fs'] * 100:.0f} % of the ±{s['adc_fs'] * 1e3:.0f} mV ADC range at gain 16).\n")
print("Charge (capacity) uncertainty, 1 sigma, P42A cell\n")
row(["Test current", "A", "shunt cal.", "shunt TCR (self-heating)", "ADC gain", "offset", "total"])
row(["---"] * 7)
for label, I in (("C/20 (OCV)", c0["Q"] / 20), ("0.2C", 0.2 * c0["Q"]), ("1C", c0["Q"]),
                 ("mission cruise", P_HOVER / (pk["S"] * c0["Vn"]) / pk["P"]), ("max rated", c0["Imax"])):
    dT = I**2 * s["R"] * s["Rth"]
    parts = [s["tol_after_cal"], s["tcr"] * dT, s["adc_gain_drift"], s["v_off"] / s["R"] / I]
    tot = math.sqrt(sum(p * p for p in parts))
    row([label, f"{I:.2f}"] + [f"{p * 100:.3f} %" for p in parts] + [f"{tot * 100:.3f} %"])

# 5. Voltage, OCV and DCIR resolution
dI = c0["Q"]
print(f"\nVoltage: ±{V_UNC * 1e3:.1f} mV after calibration ≈ ±{V_UNC / OCV_SLOPE:.2f} % SoC on the OCV curve "
      f"(slope {OCV_SLOPE * 1e3:.0f} mV per %).\n"
      f"DCIR from a 1C step ({dI:.1f} A) on a {c0['R'] * 1e3:.0f} mΩ cell: ΔV = {dI * c0['R'] * 1e3:.0f} mV; "
      f"resolution 2·noise/ΔI = {2 * V_NOISE / dI * 1e6:.1f} µΩ ({2 * V_NOISE / dI / c0['R'] * 100:.3f} %).\n"
      f"Pack group voltages (LTC6813-1 class): ±{LTC6813_ERR * 1e3:.1f} mV, ≈ ±{LTC6813_ERR / OCV_SLOPE:.1f} % SoC per group.")

# 6. Cell heating on the mission (heat I^2 R; R_10s ~ 1.5 R0 ASSUMED)
A = math.pi * 0.021 * 0.070 + 2 * math.pi * 0.0105**2
Rth = 1 / (H_CONV * A)
mc = c0["m"] * CELL_C
print(f"\nCell heating (21700 in still air: Rth ≈ {Rth:.0f} K/W, heat capacity {mc:.0f} J/K, time constant {mc * Rth / 60:.0f} min; "
      f"inside a pack it is worse)\n")
row(["Case", "cell current (A)", "heat (W)", "steady rise (K)", "adiabatic rise over the phase (K)"])
row(["---"] * 5)
for label, I, t in (("cruise (whole mission)", P_HOVER / (pk["S"] * c0["Vn"]) / pk["P"], sum(m[1] for m in mission)),
                    ("climb, 30 s", mission[0][2] / (pk["S"] * c0["Vn"]) / pk["P"], 30),
                    ("full throttle, 30 s", Ifull_cell, 30)):
    q = I**2 * 1.5 * c0["R"]
    row([label, f"{I:.1f}", f"{q:.2f}", f"{q * Rth:.1f}", f"{q * t / mc:.1f}"])

# 7. Battery cost per delivery
wear = pk["price"] / CYCLES
energy = E_mis / 1000 / CHARGE_EFF * INR_PER_KWH
print(f"\nCost per delivery: pack wear ₹{pk['price']} / {CYCLES} cycles = ₹{wear:.1f}; charging energy "
      f"{E_mis:.0f} Wh / {CHARGE_EFF} × ₹{INR_PER_KWH}/kWh = ₹{energy:.1f}. Wear dominates, so cycle life (test C6) sets the cost.")
