#!/usr/bin/env python3
"""Numbers behind propeller_dynamometer_design.md: loads per rotor class, load-cell and torque-arm selection, structural
natural frequency against rotor frequencies, flexure parasitic stiffness and stress, measurement uncertainty, and
propeller burst energy. Method: propeller_dynamometer_theory.md.

Every input marked ASSUMED is a representative value; replace it with datasheet, CAD or measured values.
Run from cadquery/propeller_dynamometer/: python3 dynamometer_sizing.py
"""
import math

RHO, G = 1.225, 9.81
FM, ETA = 0.65, 0.85               # figure of merit, motor x ESC efficiency (ASSUMED)
CQ_CT = 0.085                      # C_Q / C_T, so kappa = CQ_CT * D (ASSUMED, multirotor_dynamics.md §2.1)
OVERLOAD = 1.5                     # cell capacity >= OVERLOAD x max load
FN_MIN = 100.0                     # Hz, thrust-axis natural frequency target (3x the 30 Hz band of interest)
CELL_KG = [1, 2, 3, 5, 10, 20, 30, 50, 100, 200]     # standard load-cell capacities
ARMS_M = {"S": [0.05, 0.10], "L": [0.10, 0.15]}        # torque-arm radii each head can carry (CAD)
CELL_FS_DEFLECTION = 0.2e-3        # m, deflection at rated load (ASSUMED, typical S-beam / single-point)
E_STEEL = 200e9                    # Pa, spring-steel flexure blades
FATIGUE_LIMIT = 500e6              # Pa, spring steel, fully reversed (ASSUMED; check the chosen grade)
FS_ADC_TARGET = 2000               # Hz, sample rate of the acquisition board

classes = [
    # name, D m, blades, C_T, hover thrust N, max thrust N, bus V, thrust-axis moving mass kg, prop mass kg.
    # Moving mass = thrust stage from the CAD (S 0.240 kg, L 1.290 kg; prop_dyno.py, 4 Nov 2026) + motor + prop (ASSUMED).
    # Delivery prototype: hover 6.9 N per motor (700 g, MN4006 + 15x5 table); max 22 N ASSUMED (about 2.2 kg at 100 %).
    dict(name="15\" delivery prototype (MN4006, 6S)", D=0.381, Nb=2, CT=0.10, Th=6.9, Tmax=22.0, V=22.2,
         m=0.240 + 0.12 + 0.02, mp=0.02),
    dict(name="MK30-like (37.8 kg hex)", D=0.60, Nb=2, CT=0.10, Th=61.8, Tmax=124.0, V=44.4, m=1.290 + 0.5 + 0.15, mp=0.15),
    dict(name="FlyCart-like (95 kg, 8 rotors)", D=1.37, Nb=2, CT=0.10, Th=116.0, Tmax=233.0, V=44.4, m=1.290 + 1.5 + 0.6,
         mp=0.6),
]

# Flexures per head (ASSUMED geometry; the CAD model uses the same numbers)
heads = {
    "S": dict(thrust_blades=dict(n=4, w=0.015, t=0.15e-3, L=0.035), torque_blades=dict(n=4, w=0.010, t=0.15e-3, L=0.025, r_m=0.025), rim_width=0.010),
    "L": dict(thrust_blades=dict(n=4, w=0.050, t=0.50e-3, L=0.050), torque_blades=dict(n=4, w=0.040, t=0.40e-3, L=0.040, r_m=0.060), rim_width=0.012),
}

# Uncertainty contributions, 1 sigma (ASSUMED typical values; replace with the chosen parts' datasheets)
U = dict(cell_combined=0.0005,   # of capacity: micro S-type, 0.05 % FS combined (non-linearity + hysteresis + repeatability)
         cell_temp_zero=0.00002,  # of capacity per degC, zero drift; x the temperature change since the last zero
         dT=2.0,                  # degC change between zero and reading
         cal_mass=5e-5,           # relative: M1-class calibration weights
         crosstalk=0.001,         # of the other channel's reading, residual after the calibration matrix
         parasitic_res=0.0005,    # of capacity: wire drag and flexure hysteresis after calibration
         noise_fs=2e-6)           # of capacity, RMS after averaging a 1 s steady point


def n_rev(T, D, CT):                 # rotation rate for thrust T, rev/s, from T = C_T rho n^2 D^4
    return math.sqrt(T / (CT * RHO * D**4))


def power(T, D):                     # electrical power from momentum theory, W
    A = math.pi * D**2 / 4
    return T * math.sqrt(T / (2 * RHO * A)) / FM / ETA


def pick_cell(load_n, moving_mass):  # smallest capacity with the overload margin and f_n >= FN_MIN
    for kg in CELL_KG:
        fn = math.sqrt(kg * G / CELL_FS_DEFLECTION / moving_mass) / (2 * math.pi)
        if kg * G >= OVERLOAD * load_n and fn >= FN_MIN:
            return kg
    return None


def min_arm(head):                  # the arm must reach past the torque flexure's collar: r_m + L/2 + collar width + 10 mm
    b = heads[head]["torque_blades"]
    return b["r_m"] + b["L"] / 2 + heads[head]["rim_width"] + 0.010


def pick_torque(Qmax, r_min, head):  # smallest cell, then the arm that uses most of it while keeping the overload margin
    best = None
    for kg in CELL_KG:
        for r in (a for a in ARMS_M[head] if a >= r_min):
            cap = kg * G * r
            if cap >= OVERLOAD * Qmax and (best is None or cap < best[2]):
                best = (kg, r, cap)
    return best


def flexure_parallel(b):             # guided-blade flexure: k = n E w t^3 / L^3; stress at deflection d: 3 E t d / L^2
    k = b["n"] * E_STEEL * b["w"] * b["t"]**3 / b["L"]**3
    return k, lambda d: 3 * E_STEEL * b["t"] * d / b["L"]**2


def flexure_spoke(b):                # rotational stiffness ~ n * (12 E I / L^3) * r_m^2, I = w t^3 / 12 (approximation)
    I = b["w"] * b["t"]**3 / 12
    return b["n"] * 12 * E_STEEL * I / b["L"]**3 * b["r_m"]**2


def row(cells):
    print("| " + " | ".join(cells) + " |")


print("Loads and rotor frequencies per class\n")
row(["Class", "D (m)", "blades", "hover / max thrust (N)", "rotor n hover / max (rev/s)", "1x / blade-pass at max (Hz)",
     "max torque (N·m)", "max power (kW)", "max current (A)", "tip speed at max (m/s)"])
row(["---"] * 10)
res = []
for c in classes:
    nh, nm = n_rev(c["Th"], c["D"], c["CT"]), n_rev(c["Tmax"], c["D"], c["CT"])
    Qmax = CQ_CT * c["D"] * c["Tmax"]
    Pm = power(c["Tmax"], c["D"])
    res.append(dict(c, nh=nh, nm=nm, Qmax=Qmax, Pm=Pm, Im=Pm / c["V"]))
    row([c["name"], f"{c['D']:.3f}", str(c["Nb"]), f"{c['Th']:.1f} / {c['Tmax']:.1f}", f"{nh:.0f} / {nm:.0f}",
         f"{nm:.0f} / {c['Nb'] * nm:.0f}", f"{Qmax:.2f}", f"{Pm / 1000:.2f}", f"{Pm / c['V']:.0f}", f"{math.pi * c['D'] * nm:.0f}"])

print(f"\nLoad cells and torque arm (capacity ≥ {OVERLOAD}x max load and thrust-axis f_n ≥ {FN_MIN:.0f} Hz; head S for the delivery prototype, head L for the others)\n")
row(["Class", "head", "thrust cell (kg)", "hover thrust / capacity", "torque cell (kg) x arm (mm)", "torque capacity (N·m)",
     "max torque / capacity", "current sensor rating (A)"])
row(["---"] * 8)
for i, r in enumerate(res):
    r["head"] = "S" if i < 1 else "L"
    r["Tcell"] = pick_cell(r["Tmax"], r["m"])
    r["Qcell"] = pick_torque(r["Qmax"], min_arm(r["head"]), r["head"])
    kg, arm, cap = r["Qcell"]
    row([r["name"], r["head"], str(r["Tcell"]), f"{r['Th'] / (r['Tcell'] * G) * 100:.1f} %", f"{kg} x {arm * 1000:.0f}",
         f"{cap:.2f}", f"{r['Qmax'] / cap * 100:.0f} %", f"{OVERLOAD * r['Im']:.0f}"])

print("\nThrust-axis dynamics: natural frequency against rotor frequencies\n")
row(["Class", "cell stiffness (MN/m)", "moving mass (kg)", "f_n (Hz)", "f_n / (1x at max)", "f_n / (blade-pass at max)",
     "rotor speed band to avoid (rev/s)"])
row(["---"] * 7)
for r in res:
    k = r["Tcell"] * G / CELL_FS_DEFLECTION
    fn = math.sqrt(k / r["m"]) / (2 * math.pi)
    lo, hi = fn / 1.2 / r["Nb"], fn / 0.8 / r["Nb"]          # blade-pass within ±20 % of f_n
    lo1, hi1 = fn / 1.2, fn / 0.8                            # 1x within ±20 % of f_n
    band = []
    for a, b in ((lo, hi), (lo1, hi1)):
        if a < r["nm"]:
            band.append(f"{a:.0f}–{min(b, r['nm']):.0f}")
    r["fn"] = fn
    row([r["name"], f"{k / 1e6:.2f}", f"{r['m']:.2f}", f"{fn:.0f}", f"{fn / r['nm']:.2f}", f"{fn / (r['Nb'] * r['nm']):.2f}",
         ", ".join(band) if band else "none below max speed"])

print("\nFlexure parasitic stiffness and blade stress (spring steel)\n")
row(["Class", "thrust flexure k (kN/m)", "parasitic / cell", "blade stress at 1.5x FS deflection (MPa)",
     "torque flexure K (N·m/rad)", "cell path K = k r² (N·m/rad)", "parasitic / cell path"])
row(["---"] * 7)
for r in res:
    h = heads[r["head"]]
    kf, stress = flexure_parallel(h["thrust_blades"])
    kc = r["Tcell"] * G / CELL_FS_DEFLECTION
    Kt = flexure_spoke(h["torque_blades"])
    kg, arm, _ = r["Qcell"]
    Kc = kg * G / CELL_FS_DEFLECTION * arm**2
    s = stress(1.5 * CELL_FS_DEFLECTION)
    row([r["name"], f"{kf / 1e3:.1f}", f"{kf / kc * 100:.2f} %", f"{s / 1e6:.0f} ({s / FATIGUE_LIMIT * 100:.0f} % of fatigue limit)",
         f"{Kt:.1f}", f"{Kc:.0f}", f"{Kt / Kc * 100:.2f} %"])

# Boom: square steel tube along the thrust axis, cantilevered from the frame's front node (ASSUMED sections, overhangs)
# One boom for both heads (CAD). Head mass at the tip = head frame + torque stage (CAD, 4 Nov 2026); the thrust stage,
# motor and prop are in each class's moving mass. Overhang per class: the boom slides in the saddle, and MK30-size props
# run at 0.35 m so the boom's lateral mode stays clear of their blade-pass frequency.
BOOM = {"S": dict(a=0.100, t=0.004, head_mass=2.289 + 0.744), "L": dict(a=0.100, t=0.004, head_mass=4.452 + 4.776)}
OVERHANG = {"15\" delivery prototype (MN4006, 6S)": 0.265, "MK30-like (37.8 kg hex)": 0.35,
            "FlyCart-like (95 kg, 8 rotors)": 0.465}
print("\nBoom lateral (bending) mode with the head, motor and prop at its tip\n")
row(["Class", "boom (mm)", "overhang (m)", "tip mass (kg)", "lateral stiffness (MN/m)", "f_lat (Hz)", "f_lat / (1x at max)",
     "f_lat / (blade-pass at max)"])
row(["---"] * 8)
for r in res:
    b = BOOM[r["head"]]
    I = (b["a"]**4 - (b["a"] - 2 * b["t"])**4) / 12
    k = 3 * E_STEEL * I / OVERHANG[r["name"]]**3
    m_tip = b["head_mass"] + r["m"]
    f = math.sqrt(k / m_tip) / (2 * math.pi)
    row([r["name"], f"{b['a'] * 1000:.0f} × {b['t'] * 1000:.0f}", f"{OVERHANG[r['name']]:.2f}", f"{m_tip:.2f}", f"{k / 1e6:.2f}",
         f"{f:.0f}", f"{f / r['nm']:.2f}", f"{f / (r['Nb'] * r['nm']):.2f}"])

print("\nThrust uncertainty at hover, 1 sigma (RSS of the contributions)\n")
row(["Class", "cell", "temp. zero", "cal. mass", "crosstalk", "parasitic", "noise", "total (N)", "total / hover"])
row(["---"] * 9)
for r in res:
    cap = r["Tcell"] * G
    parts = [U["cell_combined"] * cap, U["cell_temp_zero"] * U["dT"] * cap, U["cal_mass"] * r["Th"],
             U["crosstalk"] * r["Qmax"] / r["Qcell"][1] * 0.1,       # torque-channel force x 10 % geometric coupling (ASSUMED)
             U["parasitic_res"] * cap, U["noise_fs"] * cap]
    tot = math.sqrt(sum(p * p for p in parts))
    row([r["name"]] + [f"{p:.4f}" for p in parts] + [f"{tot:.3f}", f"{tot / r['Th'] * 100:.2f} %"])

print("\nPropeller burst energy at max speed (blade as a rod, I = m D² / 12)\n")
row(["Class", "prop mass (kg)", "inertia (kg·m²)", "rotational energy (J)", "per blade (J)"])
row(["---"] * 5)
for r in res:
    I = r["mp"] * r["D"]**2 / 12
    E = 0.5 * I * (2 * math.pi * r["nm"])**2
    row([r["name"], f"{r['mp']:.3f}", f"{I:.2e}", f"{E:.0f}", f"{E / r['Nb']:.0f}"])

print(f"\nSampling: {FS_ADC_TARGET} Hz per channel; thrust-lag measurements need a flat response to ≈ 30 Hz "
      f"(10x the corner of a 50 ms lag, 1/(2π·0.05) = {1 / (2 * math.pi * 0.05):.1f} Hz).")
