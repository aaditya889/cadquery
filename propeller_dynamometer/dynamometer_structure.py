"""Prop dyno structure: free-standing stability, sliding, blade-off impulse, containment ring, members, bolts.

Run from cadquery/propeller_dynamometer/: python3 dynamometer_structure.py
Geometry matches the CAD (cadquery/scripts/sketch_scripts/projects/prop_dyno.py); change both together. Loads from dynamometer_sizing.py
(requirement 1: 300 N, 30 N·m on the L head) with the 1.5x design factor. Every input marked ASSUMED is to be replaced
by a measured or datasheet value. Coordinates: x along the thrust axis toward the prop, y left, z up, origin on the floor
under the twin posts; mm and kg in the geometry, SI in the formulas.
"""
import math

G = 9.81
STEEL_RHO = 7850.0                   # kg/m^3
DESIGN_FACTOR = 1.5                  # on the requirement loads (same as the cells' overload margin)
T_REQ, Q_REQ = 300.0, 30.0           # N, N·m: requirement 1, L head
MU_FLOOR = 0.3                       # rubber foot pad on dusty concrete, lower bound (ASSUMED; dry clean 0.5-0.8)

# ── Geometry (mm) ─────────────────────────────────────────────────────────────────────────────
FOOT_H = 100                         # floor to the underside of the base (levelling feet set mid-range)
RAIL = dict(a=80, t=4, len=2500, y=600, x0=-1400)          # two side rails along x
CROSS = dict(a=80, t=4, len=1120, x=(-1360, 0, 1060))      # three cross members between the rails
POST = dict(a=80, t=4, y=100, top=1760)                    # twin posts, z from the base top to `top`
POST_TIE = dict(a=60, t=4, len=120)                        # tie between the post tops (inner faces 120 apart)
DIAG = dict(a=60, t=4, x_foot=-1300)                       # one diagonal per post, to the rear cross member
BOOM = dict(a=100, t=4, len=950)
H_AXIS = (800, 1600)                                       # thrust-axis height range
PROP = dict(d=1370, mass=0.60, n=23.0, blades=2)           # FlyCart-like class (dynamometer_sizing.py; mass ASSUMED)
PROP_MK30 = dict(d=600, mass=0.15, n=88.0, blades=2)
RING = dict(clear=60, t=10, w=300)                          # containment band: radial clearance, thickness, width
PORTAL = dict(a=80, t=4, foot_len=900, beam_len=1900)       # ring portal posts, feet, cross beam
HEAD_MASS, MOTOR_MASS, SADDLE_MASS = 8.0, 3.0, 25.0        # kg (head and motor from dynamometer_sizing.py; saddle from CAD)
X_DISC = 770                                                # prop disc x on the L head (CAD)

BASE_TOP = FOOT_H + RAIL["a"]


def rhs_kg_per_m(a, t):
    return (a ** 2 - (a - 2 * t) ** 2) * 1e-6 * STEEL_RHO


def rhs_props(a, t):
    """Second moment of area and section modulus of a square hollow section (sharp corners), mm^4 and mm^3."""
    i = (a ** 4 - (a - 2 * t) ** 4) / 12
    return i, i / (a / 2)


# ── Masses and centre of gravity ──────────────────────────────────────────────────────────────
r_i = PROP["d"] / 2 + RING["clear"]
r_o = r_i + RING["t"]
items = []                            # (name, kg, x, y, z) in mm
items += [(f"rail {s:+d}", rhs_kg_per_m(80, 4) * RAIL["len"] / 1e3, RAIL["x0"] + RAIL["len"] / 2, s * RAIL["y"], FOOT_H + 40)
          for s in (-1, 1)]
items += [(f"cross x={x}", rhs_kg_per_m(80, 4) * CROSS["len"] / 1e3, x, 0, FOOT_H + 40) for x in CROSS["x"]]
post_len = POST["top"] - BASE_TOP
items += [(f"post {s:+d}", rhs_kg_per_m(80, 4) * post_len / 1e3, 0, s * POST["y"], BASE_TOP + post_len / 2) for s in (-1, 1)]
diag_len = math.hypot(DIAG["x_foot"] + 40, POST["top"] - 150 - BASE_TOP)
items += [(f"diagonal {s:+d}", rhs_kg_per_m(60, 4) * diag_len / 1e3, (DIAG["x_foot"] - 40) / 2, s * POST["y"],
           BASE_TOP + (POST["top"] - 150 - BASE_TOP) / 2) for s in (-1, 1)]
z_axis = H_AXIS[1]
items += [("saddle", SADDLE_MASS, 0, 0, z_axis - 120),
          ("boom", rhs_kg_per_m(100, 4) * BOOM["len"] / 1e3, -25, 0, z_axis),
          ("head", HEAD_MASS, 560, 0, z_axis), ("motor", MOTOR_MASS, 720, 0, z_axis)]
ring_kg = 2 * math.pi * (r_i + r_o) / 2 * RING["w"] * RING["t"] * 1e-9 * STEEL_RHO
portal_post_len = z_axis + r_o + 60 - BASE_TOP
y_pp = r_o + 60 + PORTAL["a"] / 2
items += [("ring", ring_kg, X_DISC, 0, z_axis)]
items += [(f"portal post {s:+d}", rhs_kg_per_m(80, 4) * portal_post_len / 1e3, X_DISC, s * y_pp,
           BASE_TOP + portal_post_len / 2) for s in (-1, 1)]
items += [("portal top tie", rhs_kg_per_m(80, 4) * 2 * y_pp / 1e3, X_DISC, 0, BASE_TOP + portal_post_len + 40),
          ("portal beam", rhs_kg_per_m(80, 4) * PORTAL["beam_len"] / 1e3, X_DISC, 0, BASE_TOP + 40)]
items += [(f"portal foot {s:+d}", rhs_kg_per_m(80, 4) * PORTAL["foot_len"] / 1e3, X_DISC, s * y_pp, FOOT_H + 40)
          for s in (-1, 1)]
CAD_MASS = 461.0                      # kg, L configuration without fasteners (prop_dyno.py export, 4 Nov 2026)
M = CAD_MASS                          # weight from the CAD; centre of gravity from the member list above
cg = [sum(m * p[k] for _, m, *p in items) / sum(m for _, m, *_ in items) for k in range(3)]
W = M * G

feet_x = (RAIL["x0"] + 40, RAIL["x0"] + RAIL["len"] - 40)   # main feet lines (rail ends)
feet_y = RAIL["y"]
portal_feet_y = y_pp
print("Masses and centre of gravity (L configuration, axis at 1.6 m)")
for name, m, *_ in items:
    print(f"  {name:20s} {m:7.1f} kg")
print(f"  member list {sum(m for _, m, *_ in items):.0f} kg; CAD total {M:.0f} kg, weight {W:.0f} N; CG x {cg[0]:.0f}, y {cg[1]:.0f}, z {cg[2]:.0f} mm")
print(f"  ring: inner radius {r_i:.0f} mm, outer {r_o:.0f} mm, {ring_kg:.0f} kg")

# ── Load case 1: steady thrust (design 1.5 x 300 N) at the axis, either direction ─────────────
T = DESIGN_FACTOR * T_REQ
h = z_axis / 1e3
lever_rear = (cg[0] - feet_x[0]) / 1e3          # thrust pulls the head toward the posts (-x): tips about the rear feet
lever_front = (feet_x[1] - cg[0]) / 1e3         # reversed thrust (+x) tips about the front feet
print("\nLoad case 1: steady thrust", T, "N at", h, "m")
print(f"  overturning {T * h:.0f} N·m; restoring about the rear feet {W * lever_rear:.0f} N·m "
      f"(factor {W * lever_rear / (T * h):.1f}); about the front feet {W * lever_front:.0f} N·m "
      f"(factor {W * lever_front / (T * h):.1f})")
print(f"  sliding: friction {MU_FLOOR * W:.0f} N against {T:.0f} N (factor {MU_FLOOR * W / T:.1f}, mu = {MU_FLOOR})")
Q = DESIGN_FACTOR * Q_REQ
print(f"  torque reaction {Q:.0f} N·m about x; restoring about the side feet {W * feet_y / 1e3:.0f} N·m "
      f"(factor {W * feet_y / 1e3 / Q:.0f})")

# ── Load case 2: blade-off. A blade leaves in the rotor plane and strikes the ring ─────────────


def blade(p):
    """Energy, translational speed and momentum of one released blade (uniform rod from hub to tip, ASSUMED)."""
    omega = 2 * math.pi * p["n"]
    R = p["d"] / 2 / 1e3
    m = p["mass"] / p["blades"]
    i_hub = m * R ** 2 / 3                       # rod about its end
    e = 0.5 * i_hub * omega ** 2                 # its share of the rotor energy
    v_cg = omega * R / 2                         # centre of mass at mid-span
    return e, v_cg, m * v_cg


for label, p in (("FlyCart-like", PROP), ("MK30-like", PROP_MK30)):
    e, v, mom = blade(p)
    print(f"\nLoad case 2 ({label}): blade {p['mass'] / p['blades']:.3f} kg, energy {e:.0f} J, "
          f"centre-of-mass speed {v:.0f} m/s, momentum {mom:.1f} N·s")
    p_imp = 2 * mom                              # it rebounds: up to twice its momentum (conservative)
    # The ring takes the impulse first; its velocity, then the energy the portal posts must absorb elastically
    v_ring = p_imp / ring_kg
    print(f"  impulse <= {p_imp:.1f} N·s; ring velocity {v_ring:.2f} m/s; ring kinetic energy "
          f"{0.5 * ring_kg * v_ring ** 2:.1f} J (into the posts' bending, elastic)")
    # Whole stand: angular momentum about the side feet line from an impulse at the ring top, sideways
    z_hit = (z_axis + r_o) / 1e3
    b = portal_feet_y / 1e3                      # widest feet (portal feet) in y
    i_edge = M * ((cg[2] / 1e3) ** 2 + b ** 2)   # point-mass approximation about the edge (lower bound on inertia: conservative)
    omega0 = p_imp * z_hit / i_edge
    ke = 0.5 * i_edge * omega0 ** 2
    barrier = W * (math.hypot(b, cg[2] / 1e3) - cg[2] / 1e3)
    print(f"  stand tipping: kinetic {ke:.2f} J against a {barrier:.0f} J barrier "
          f"(factor {barrier / ke:.0f}); sliding {(p_imp / M) ** 2 / (2 * MU_FLOOR * G) * 1e3:.2f} mm")

# ── Containment ring: perforation by a shear plug (conservative for a hard fragment) ───────────
TAU = 0.6 * 410e6                            # S275 / IS 2062 E250: shear strength ~0.6 x UTS 410 MPa
for d_contact in (0.010, 0.020):
    for t in (0.006, 0.008, 0.010, 0.012):
        e_plug = math.pi * d_contact * t ** 2 * TAU / 2      # plug force pi d t tau, falling linearly over t
        print(f"  plug energy, contact {d_contact * 1e3:.0f} mm, plate {t * 1e3:.0f} mm: {e_plug:.0f} J") if t == RING["t"] / 1e3 or d_contact == 0.020 else None
e_blade = blade(PROP)[0]
e_plug_design = math.pi * 0.020 * (RING["t"] / 1e3) ** 2 * TAU / 2
print(f"  chosen {RING['t']} mm ring: {e_plug_design:.0f} J against {e_blade:.0f} J per blade "
      f"(factor {e_plug_design / e_blade:.2f}); qualify by test")
half_angle = math.degrees(math.atan(RING["w"] / 2 / r_i))
print(f"  axial coverage: fragments within ±{half_angle:.1f}° of the rotor plane strike the band")

# ── Members ───────────────────────────────────────────────────────────────────────────────────
i80, z80 = rhs_props(80, 4)
m_post = T * h * 1e3 / 2                      # N·mm per post, cantilever from the base, ignoring the diagonals (conservative)
print(f"\nMembers: twin posts as cantilevers without diagonals: {m_post / z80:.1f} MPa (yield 250 MPa); "
      f"tip deflection {T / 2 * (h * 1e3) ** 3 / (3 * 200e3 * i80):.2f} mm")
i100, z100 = rhs_props(100, 4)
m_boom = (HEAD_MASS + MOTOR_MASS) * G * 450 * 1e3 / 1e3
print(f"  boom: compression {T:.0f} N ({T / ((100 ** 2 - 92 ** 2)):.2f} MPa); bending from the head weight "
      f"{m_boom / z100:.1f} MPa")

# ── Bolted joints (ISO 898-1 class 8.8; preload 70 % of proof, ASSUMED torque-controlled) ───────
AS = {"M8": 36.6, "M10": 58.0, "M12": 84.3, "M16": 157.0}        # tensile stress area, mm^2 (ISO 898-1)
PROOF = 600.0                                                     # MPa, class 8.8 proof stress (M16 and below)
preload = {k: 0.7 * PROOF * a for k, a in AS.items()}
MU_JOINT = 0.2                                                    # steel on steel, as-rolled (ASSUMED)
sad_slip = MU_JOINT * 2 * 4 * preload["M12"]                      # 4 bolts, two clamped faces
sad_load = (SADDLE_MASS + rhs_kg_per_m(100, 4) * BOOM["len"] / 1e3 + HEAD_MASS + MOTOR_MASS) * G + T * 0.3
print(f"\nBolts (8.8, preload M12 {preload['M12'] / 1e3:.0f} kN): saddle friction {sad_slip / 1e3:.0f} kN against "
      f"{sad_load:.0f} N (factor {sad_slip / sad_load:.0f}); the index pin carries the load if it ever slips")
boom_slip = MU_JOINT * 2 * 4 * preload["M10"]
print(f"  boom clamp (2 straps x 2 M10): {boom_slip / 1e3:.0f} kN against the thrust {T:.0f} N "
      f"(factor {boom_slip / T:.0f})")
flange_t = T / 4 + Q / (4 * 0.065)
print(f"  head flange (4 x M10 on a 130 mm square): worst bolt {flange_t:.0f} N against "
      f"{preload['M10'] / 1e3:.0f} kN preload")

# ── Spoke (torque) flexure under the weight it now carries (reversed head: torque stage + thrust stage + motor + prop) ──
# Four blades in radial planes at 45°, 135°, 225°, 315°; each is w (axial) × t (tangential) × L (radial free length).
# Weight W at a distance e in front of the blades' mid-width: shear W shared as radial forces by the blades (two take
# compression, at most W/√2 each, conservative), and a moment W·e shared as in-plane bending of the four blades.
SPOKE = {"S": dict(w=10, t=0.15, L=25, mass=0.744 + 0.240 + 0.14, e=45),      # mm, kg (CAD masses + motor/prop ASSUMED)
         "L": dict(w=40, t=0.40, L=40, mass=4.776 + 1.290 + 2.1, e=90)}
print("\nSpoke flexure under the carried weight")
for head, b in SPOKE.items():
    Wn = b["mass"] * G
    i_thin = b["w"] * b["t"] ** 3 / 12                                   # mm^4, buckling about the thin axis
    p_cr = 4 * math.pi ** 2 * 200e3 * i_thin / b["L"] ** 2                # N, Euler, both ends clamped
    p_comp = Wn / math.sqrt(2)
    m_blade = Wn * b["e"] / 4                                            # N·mm per blade, in-plane bending
    sigma = m_blade / (b["t"] * b["w"] ** 2 / 6)
    print(f"  {head}: {b['mass']:.2f} kg carried; buckling {p_cr:.0f} N against {p_comp:.1f} N (factor {p_cr / p_comp:.1f}); "
          f"in-plane bending {sigma:.0f} MPa (fatigue limit 500 MPa ASSUMED)")
