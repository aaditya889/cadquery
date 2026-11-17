"""
projects/prop_dyno.py — In-house propeller dynamometer, detailed for manufacture.

Every part has its real joints: welded frame members, bolted clamps with their holes and threads, flexure blades in
clamp bars, load cells on threaded studs, levelling feet. Bought parts (load cells, feet, fasteners) are modelled to
their datasheet envelopes; the motor and prop are placeholders for clearance only.

Design, requirements and numbers: cadquery/propeller_dynamometer/propeller_dynamometer_design.md;
structure and stability: cadquery/propeller_dynamometer/dynamometer_structure.py; manufacturing package:
cadquery/propeller_dynamometer/propeller_dynamometer_manufacturing_package.md. Change them together.

World axes: +x along the thrust axis toward the prop (the wake blows +x), +z up, y left; origin on the floor midway
between the twin posts. Units: mm.

Run:  python3 projects/prop_dyno.py          (export/prop_dyno_<HEAD>.stl: the whole stand in one file;
                                             export/prop_dyno/<HEAD>/: one STEP per part, the assembly STEP,
                                             parts.csv, fasteners.csv, holes.csv)
      cq-server run projects/prop_dyno.py    (browser preview)
      DYNO_HEAD=S DYNO_H_AXIS=900 DYNO_PROP_D=381 python3 projects/prop_dyno.py   (small head)
      python3 projects/prop_dyno_drawings.py (one drawing sheet per manufactured part, PDF)
"""

from cq_server.ui import ui, show_object
import csv
import math
import os
import sys
from dataclasses import dataclass, field

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import cadquery as cq
from core import show
from hardware.standards import MACHINED

# ════════════════════════════════════════════════════════════════════
# PARAMETERS
# ════════════════════════════════════════════════════════════════════
HEAD = os.environ.get("DYNO_HEAD", "L")      # "S": props up to ~20" (15" delivery prototype); "L": props up to 1.5 m
H_AXIS = float(os.environ.get("DYNO_H_AXIS", 1600))   # thrust-axis height, 800-1600 in 50 mm steps (L head with a 1.37 m prop: >= 1400)
PROP_D = float(os.environ.get("DYNO_PROP_D", 1370))   # prop drawn (placeholder): 1370 FlyCart-like, 600 MK30-like (L); 381 = 15" delivery prototype (S)
PROP_BLADES = 2

FOOT_H = 100.0          # floor to the underside of the base, levelling feet at mid-range (adjust 80-120)
RAIL_Y, RAIL_X0, RAIL_X1 = 600.0, -1400.0, 1100.0
CROSS_X = (-1360.0, 0.0, 1060.0)
POST_Y, POST_TOP = 100.0, 1810.0
INDEX_PITCH = 50.0
BOOM_LEN = 950.0
BOOM_FLANGE_X = {"S": 265.0, "L": 465.0}        # flange front face: overhang from the posts (dyno doc §2)
PORTAL_FOOT = 900.0


@dataclass(frozen=True)
class HeadSpec:
    tp: float              # head-frame back wall (x)
    arm_h: float           # torque-stage top and bottom arms (z)
    stage_t: float         # torque-stage plate (x)
    carriage: tuple        # thrust carriage (x, y, z)
    thrust_blade: tuple    # (w, t, free L)
    torque_blade: tuple    # (w, t, free L)
    r_m: float             # spoke-blade mean radius
    rim_w: float           # collar (outer ring of the torque flexure) radial width
    arm_r: float           # torque-arm radius to the torque-cell axis
    arm_w: float           # torque arm height (z)
    wall: float            # carriage outer wall
    web: float             # carriage cross webs
    rib: float             # blade clamp rib (x)
    bar: float             # blade clamp bar (x)
    land: float            # clamped blade length at each end
    slot_d: float          # spoke-blade slot depth in collar and hub
    screw: str             # blade-clamp screws
    blade_screw_l: int
    adapter_screw: str     # motor adapter to the carriage
    adapter_screw_l: int
    adapter_pcd: float
    adapter_t: float
    motor_holes: tuple     # motor bolt pattern on the adapter ((y, z), ...)
    motor_screw: str
    motor_d: float         # placeholder envelope
    motor_l: float


HEADS = {   # blade sets from dynamometer_sizing.py. S: 15" delivery prototype (MN4006 + 1555); L: MK30- and FlyCart-like
    "S": HeadSpec(tp=15, arm_h=12, stage_t=10, carriage=(30, 50, 50), thrust_blade=(15, 0.15, 35),
                  torque_blade=(10, 0.15, 25), r_m=25, rim_w=10, arm_r=100, arm_w=16, wall=5, web=10, rib=6, bar=5,
                  land=10, slot_d=5, screw="M3", blade_screw_l=12, adapter_screw="M3", adapter_screw_l=8, adapter_pcd=36,
                  adapter_t=5, motor_holes=tuple((sy * 8.84, sz * 8.84) for sy in (-1, 1) for sz in (-1, 1)),
                  motor_screw="M3", motor_d=45, motor_l=26),
    "L": HeadSpec(tp=20, arm_h=25, stage_t=20, carriage=(40, 120, 120), thrust_blade=(50, 0.5, 50),
                  torque_blade=(40, 0.4, 40), r_m=60, rim_w=12, arm_r=150, arm_w=30, wall=6, web=12, rib=10, bar=8,
                  land=20, slot_d=10, screw="M5", blade_screw_l=20, adapter_screw="M6", adapter_screw_l=16, adapter_pcd=60,
                  adapter_t=10, motor_holes=tuple((sy * 10.6, sz * 10.6) for sy in (-1, 1) for sz in (-1, 1)),
                  motor_screw="M4", motor_d=110, motor_l=60),
}
CELL = dict(h=30.0, w=25.0, t=12.0, thread="M6", gap=6.0)   # micro S-type 1-50 kg (ATO DYLY-106 class): 30 along the load

STEEL, AL7075, SPRING, PC, BOUGHT = "S275 (IS 2062 E250)", "Al 7075-T6", "spring steel, EN42 / 301 full-hard", \
    "polycarbonate", "bought"
DENSITY = {STEEL: 7850, AL7075: 2810, SPRING: 7850, PC: 1200, BOUGHT: 7850}

# ════════════════════════════════════════════════════════════════════
# REGISTRY: parts, holes, fasteners
# ════════════════════════════════════════════════════════════════════


@dataclass
class Hole:
    label: str           # e.g. "M10 tap 20 deep", "Ø13 thru", "Ø8 H7 dowel"
    pos: tuple           # world, at the entry face
    axis: tuple          # into the material


@dataclass
class Part:
    pid: str
    name: str
    material: str
    process: str
    source: str          # make (our CNC) / outsource (welding, rolling, laser) / buy
    stock: str
    group: str           # weldment or sub-assembly it belongs to
    color: tuple
    notes: str = ""
    solids: list = field(default_factory=list)
    holes: list = field(default_factory=list)

    @property
    def mass(self) -> float:
        return self.solids[0].Volume() * 1e-9 * DENSITY[self.material]


PARTS: dict[str, Part] = {}
FASTENERS: dict[str, list] = {}          # spec -> [count, where]
HW_SOLIDS: list = []                     # fastener solids, display only
GREY, DARK, ALU, CELL_C, BLADE_C, RED, PC_C, MOTOR_C, PROP_C, FOOT_C, BOLT_C = (
    (0.55, 0.55, 0.58), (0.30, 0.32, 0.36), (0.78, 0.80, 0.84), (0.90, 0.49, 0.13), (0.20, 0.60, 0.86),
    (0.86, 0.26, 0.20), (0.75, 0.88, 0.95), (0.15, 0.15, 0.15), (0.18, 0.80, 0.44), (0.10, 0.10, 0.10), (0.85, 0.75, 0.30))


def add(pid, name, solid, material, process, source, stock, group, color, holes=(), notes=""):
    """Register one instance of a part; a repeated pid adds an instance (the first carries the drawing)."""
    if stock == "auto":                       # machined from solid: envelope + 5 mm
        b = solid.BoundingBox()
        stock = f"block {b.xlen + 5:.0f} × {b.ylen + 5:.0f} × {b.zlen + 5:.0f}"
    if pid not in PARTS:
        PARTS[pid] = Part(pid, name, material, process, source, stock, group, color, notes)
        PARTS[pid].holes = list(holes)
    PARTS[pid].solids.append(solid)
    return solid


def fastener(spec, where, start, axis, length, head=True):
    """Count a fastener and draw it: head at `start`, shank `length` along `axis`."""
    FASTENERS.setdefault(spec, [0, set()])
    FASTENERS[spec][0] += 1
    FASTENERS[spec][1].add(where)
    size = spec.split()[1].split("×")[0] if "×" in spec else None
    f = MACHINED.get(size) if size else None
    d = f.d if f else 10.0
    a = cq.Vector(axis).normalized()
    s = cq.Vector(start)
    shank = cq.Solid.makeCylinder(d / 2, length, s, a)
    if head and f:
        shank = shank.fuse(cq.Solid.makeCylinder(f.head_d / 2, f.head_h, s - a * f.head_h, a))
    HW_SOLIDS.append(shank)


# ════════════════════════════════════════════════════════════════════
# GEOMETRY HELPERS
# ════════════════════════════════════════════════════════════════════
def box(x0, x1, y0, y1, z0, z1) -> cq.Solid:
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))


def cyl(p0, p1, r) -> cq.Solid:
    v0, v1 = cq.Vector(p0), cq.Vector(p1)
    return cq.Solid.makeCylinder(r, (v1 - v0).Length, v0, (v1 - v0).normalized())


def ring(x0, x1, r_i, r_o, yc=0.0, zc=0.0) -> cq.Solid:
    return cyl((x0, yc, zc), (x1, yc, zc), r_o).cut(cyl((x0, yc, zc), (x1, yc, zc), r_i))


def rhs(p0, p1, a, t, side=(0, 0, 1)) -> cq.Shape:
    """Square hollow section from p0 to p1; one pair of walls faces `side` (projected normal to the axis)."""
    v0, v1 = cq.Vector(p0), cq.Vector(p1)
    d = (v1 - v0).normalized()
    s = cq.Vector(side)
    s = (s - d * s.dot(d)).normalized()
    plane = cq.Plane(origin=v0, xDir=s, normal=d)
    return cq.Workplane(plane).rect(a, a).rect(a - 2 * t, a - 2 * t).extrude((v1 - v0).Length).val()


def trim(shape, point, normal) -> cq.Shape:
    """Remove the material on the +normal side of the plane through `point`."""
    n = cq.Vector(normal).normalized()
    x = cq.Vector(0, 0, 1) if abs(n.z) < 0.9 else cq.Vector(1, 0, 0)
    x = (x - n * x.dot(n)).normalized()
    half = cq.Workplane(cq.Plane(origin=cq.Vector(point), xDir=x, normal=n)).rect(2e4, 2e4).extrude(1e4).val()
    return shape.cut(half)


def drill(shape, holes, label, points, axis, dia, depth=None, cbore=None):
    """Cut holes (through when depth is None) along `axis` from each entry point; record them for the hole table."""
    a = cq.Vector(axis).normalized()
    for p in points:
        s = cq.Vector(p) - a * 1.0
        length = (depth + 1.0) if depth else 5000.0
        shape = shape.cut(cq.Solid.makeCylinder(dia / 2, length, s, a))
        if cbore:
            shape = shape.cut(cq.Solid.makeCylinder(cbore[0] / 2, cbore[1] + 1.0, s, a))
        holes.append(Hole(label, tuple(round(c, 2) for c in p), tuple(axis)))
    return shape


def tap(size):
    f = MACHINED[size]
    return f.tap_drill


def clear(size):
    return MACHINED[size].clearance


# ════════════════════════════════════════════════════════════════════
# W1 BASE FRAME (weldment)
# ════════════════════════════════════════════════════════════════════
BASE_TOP = FOOT_H + 80.0
Z_RAIL = FOOT_H + 40.0
index_z = [H_AXIS_i - 200.0 for H_AXIS_i in [800 + INDEX_PITCH * k for k in range(17)]]   # pin 200 below the axis


def build_frame():
    g = "W1 base frame"
    for s in (-1, 1):
        h = []
        rail = rhs((RAIL_X0, s * RAIL_Y, Z_RAIL), (RAIL_X1, s * RAIL_Y, Z_RAIL), 80, 4)
        add("W1-01", "Side rail", rail, STEEL, "saw cut square, weld", "outsource", "RHS 80×80×4 × 2500", g, GREY, h)
    for x in CROSS_X:
        cm = rhs((x, -RAIL_Y + 40, Z_RAIL), (x, RAIL_Y - 40, Z_RAIL), 80, 4)
        add("W1-02", "Cross member", cm, STEEL, "saw cut square, weld", "outsource", "RHS 80×80×4 × 1120", g, GREY)
    for x in (CROSS_X[0], CROSS_X[2]):
        for s in (-1, 1):
            h = []
            fp = box(x - 60, x + 60, s * RAIL_Y - 60, s * RAIL_Y + 60, FOOT_H - 12, FOOT_H)
            fp = drill(fp, h, "M16 tap thru", [(x, s * RAIL_Y, FOOT_H - 12)], (0, 0, 1), tap("M16"))
            add("W1-03", "Foot plate", fp, STEEL, "laser cut, drill, tap M16, weld", "outsource",
                "plate 12 × 120 × 120", g, GREY, h)
    for s in (-1, 1):
        h = []
        post = rhs((0, s * POST_Y, BASE_TOP), (0, s * POST_Y, POST_TOP), 80, 4, side=(1, 0, 0))
        post = drill(post, h, "Ø13 thru (index)", [(40, s * POST_Y, z) for z in index_z], (-1, 0, 0), 13.0)
        add("W1-04", "Post", post, STEEL, "saw cut, drill index holes on a jig, weld", "outsource",
            "RHS 80×80×4 × 1630", g, GREY, h, "index holes on 50 mm pitch, ±0.2 mm cumulative")
        add("W1-05", "Post cap", box(-40, 40, s * POST_Y - 40, s * POST_Y + 40, POST_TOP, POST_TOP + 5), STEEL,
            "laser cut, weld", "outsource", "plate 5 × 80 × 80", g, GREY)
        tri = (cq.Workplane("YZ").polyline([(s * 140, BASE_TOP), (s * 290, BASE_TOP), (s * 140, BASE_TOP + 150)])
               .close().extrude(8).translate((-4, 0, 0)).val())
        add("W1-06", "Post gusset", tri, STEEL, "laser cut, weld", "outsource", "plate 8 × 150 × 150", g, GREY)
    add("W1-07", "Post top tie", rhs((0, -60, POST_TOP - 30), (0, 60, POST_TOP - 30), 60, 4), STEEL,
        "saw cut, weld", "outsource", "RHS 60×60×4 × 120", g, GREY)
    # Diagonals: post rear face (x = -40) at z 1760 to the rear cross member top, in the x-z plane of each post
    top, foot = (-40.0, 1760.0), (CROSS_X[0], BASE_TOP)
    d = cq.Vector(foot[0] - top[0], 0, foot[1] - top[1]).normalized()
    for s in (-1, 1):
        p0 = cq.Vector(top[0], s * POST_Y, top[1]) - d * 60
        p1 = cq.Vector(foot[0], s * POST_Y, foot[1]) + d * 60
        dg = rhs(p0.toTuple(), p1.toTuple(), 60, 4, side=(0, 1, 0))
        dg = trim(dg, (-40, 0, 0), (1, 0, 0))                 # cut to the post's rear face
        dg = trim(dg, (0, 0, BASE_TOP), (0, 0, -1))           # cut to the cross member's top
        dg = trim(dg, (0, 0, POST_TOP), (0, 0, 1))
        add("W1-08", "Diagonal", dg, STEEL, "saw cut both ends at 50.1° (on the CAD), weld", "outsource",
            "RHS 60×60×4 × 2090", g, GREY, notes="end cuts as modelled; fit-up gap ≤ 2 mm before welding")
    # levelling feet (bought) under the foot plates
    for x in (CROSS_X[0], CROSS_X[2]):
        for s in (-1, 1):
            levelling_foot(x, s * RAIL_Y, "W1 base frame")


def levelling_foot(x, y, where):
    foot = cyl((x, y, 0), (x, y, 25), 40).fuse(cyl((x, y, 25), (x, y, FOOT_H - 12), 8))
    foot = foot.fuse(cyl((x, y, FOOT_H - 12), (x, y, FOOT_H), MACHINED["M16"].tap_drill / 2))   # thread in the plate
    add("B-01", "Levelling foot M16 × 100, Ø80 swivel base, NBR pad, ≥ 5 kN", foot, BOUGHT, "—", "buy",
        "catalogue part", "feet", FOOT_C)
    FASTENERS.setdefault("Nut ISO 4032 M16 (foot lock nut)", [0, set()])
    FASTENERS["Nut ISO 4032 M16 (foot lock nut)"][0] += 1
    FASTENERS["Nut ISO 4032 M16 (foot lock nut)"][1].add(where)


# ════════════════════════════════════════════════════════════════════
# A1 SADDLE (clamps the twin posts; carries the boom) and B1 BOOM
# ════════════════════════════════════════════════════════════════════
def build_saddle(zb):
    """zb: boom underside = H_AXIS - 50. Front and rear plates pinch the posts; seat block and straps hold the boom."""
    g = "A1 saddle"
    zp = H_AXIS - 200.0                                       # index-pin height
    bolts = [(s * 165, z) for s in (-1, 1) for z in (zb - 40, zb - 260)]
    for pid, x0, x1, nm in (("A1-01", 40, 55, "Saddle front plate"), ("A1-02", -55, -40, "Saddle rear plate")):
        h = []
        pl = box(x0, x1, -190, 190, zb - 300, zb)
        pl = drill(pl, h, "Ø13.5 thru", [(x0, y, z) for y, z in bolts], (1, 0, 0), clear("M12"))
        pl = drill(pl, h, "Ø12.5 thru (index pin)", [(x0, s * POST_Y, zp) for s in (-1, 1)], (1, 0, 0), 12.5)
        add(pid, nm, pl, STEEL, "laser cut, drill" + (", weld seat block" if pid == "A1-01" else ""), "outsource",
            "plate 15 × 380 × 300", g, DARK, h)
    h = []
    seat = box(55, 205, -80, 80, zb - 25, zb)
    seat = drill(seat, h, "M10 tap thru", [(x, s * 60, zb) for x in (90, 170) for s in (-1, 1)], (0, 0, -1), tap("M10"))
    add("A1-03", "Seat block (welded to the front plate)", seat, STEEL, "saw cut, mill top flat, drill, tap, weld",
        "outsource", "flat 25 × 160 × 150", g, DARK, h, "top face flat 0.1 mm and flush with the front plate top")
    for x in (90, 170):
        h = []
        st = box(x - 20, x + 20, -80, 80, zb + 100, zb + 112)
        st = drill(st, h, "Ø11 thru", [(x, s * 60, zb + 112) for s in (-1, 1)], (0, 0, -1), clear("M10"))
        add("A1-04", "Boom strap", st, STEEL, "saw cut, drill", "make", "flat 12 × 40 × 160", g, DARK, h)
        for s in (-1, 1):
            fastener("ISO 4762 M10×130 8.8", "boom straps", (x, s * 60, zb + 112), (0, 0, -1), 130)
    for y, z in bolts:
        fastener("ISO 4017 M12×130 8.8 + 2 washers ISO 7089 + nut ISO 4032", "saddle clamp", (55, y, z), (-1, 0, 0), 130)
    for s in (-1, 1):
        fastener("Clevis pin Ø12 × 130 + R-clip (index pin)", "saddle index", (70, s * POST_Y, zp), (-1, 0, 0), 145,
                 head=False)


def build_boom(xf, z):
    g = "B1 boom"
    h = []
    tube = rhs((xf - 15 - BOOM_LEN, 0, z), (xf - 15, 0, z), 100, 4)
    add("B1-01", "Boom tube", tube, STEEL, "saw cut square, weld", "outsource", "RHS 100×100×4 × 950", g, DARK)
    fl = box(xf - 15, xf, -100, 100, z - 100, z + 100)
    fl = drill(fl, h, "Ø11 thru", [(xf - 15, y, z + zz) for y in (-65, 65) for zz in (-65, 65)], (1, 0, 0), clear("M10"))
    fl = drill(fl, h, "Ø8 H7 thru (dowel)", [(xf - 15, 0, z + zz) for zz in (-85, 85)], (1, 0, 0), 8.0)
    fl = drill(fl, h, "Ø30 thru (stud and nut access)", [(xf - 15, 0, z)], (1, 0, 0), 30.0)
    add("B1-02", "Boom flange", fl, STEEL, "laser cut, weld, then face-mill and drill after welding", "outsource",
        "plate 20 × 200 × 200", g, DARK, h, "front face flat 0.05 mm and square to the tube axis 0.1 mm after welding")
    add("B1-03", "Boom end cap", box(xf - 20 - BOOM_LEN, xf - 15 - BOOM_LEN, -50, 50, z - 50, z + 50), STEEL,
        "laser cut, weld", "outsource", "plate 5 × 100 × 100", g, DARK)
    for y in (-65, 65):
        for zz in (-65, 65):
            fastener("ISO 4762 M10×30 8.8", "head to boom flange", (xf - 15, y, z + zz), (1, 0, 0), 30)
    FASTENERS.setdefault("Dowel pin ISO 8734 Ø8 m6 × 30", [0, set()])
    FASTENERS["Dowel pin ISO 8734 Ø8 m6 × 30"][0] += 2
    FASTENERS["Dowel pin ISO 8734 Ø8 m6 × 30"][1].add("head to boom flange")


# ════════════════════════════════════════════════════════════════════
# HEAD (S or L): monolithic head frame, guided blades, carriage, thrust cell, torque stage
# ════════════════════════════════════════════════════════════════════
def spoke_slots(shape, holes, x0, zc, r_face, slot_d, tt, tw, outer_face, pinch):
    """Four radial slots at 45°, 135°, 225°, 315° for the spoke blades, cut from a cylindrical face at radius r_face
    (inward from the collar's bore, or outward... here: into the material away from the face); each pinched by an M3."""
    for a in (45, 135, 225, 315):
        u = cq.Vector(0, math.cos(math.radians(a)), math.sin(math.radians(a)))
        v = cq.Vector(0, -u.z, u.y)
        r_c = r_face - slot_d / 2 if outer_face else r_face + slot_d / 2
        slot = (cq.Workplane(cq.Plane(origin=cq.Vector(x0, 0, zc) + u * r_c, xDir=u, normal=cq.Vector(1, 0, 0)))
                .rect(slot_d + 2, tt + 0.02).extrude(tw).val())
        shape = shape.cut(slot)
        if pinch:
            c = cq.Vector(x0 + tw / 2, 0, zc) + u * r_c
            shape = drill(shape, holes, "M3 tap (pinch screw across the slot)", [(c - v * 8).toTuple()], v.toTuple(),
                          tap("M3"), 14)
    return shape


def build_head(x0, zc, s: HeadSpec):
    """Load path: boom flange -> head frame (fixed; carries the collar of the torque flexure and the torque-cell bracket)
    -> spoke blades -> torque stage (hub, plate, arms, torque arm) -> thrust cell + guided blades -> thrust carriage
    -> motor adapter -> motor. The thrust cell carries only the carriage, adapter, motor and prop.
    x0: back face of the head frame (= boom flange front face); zc: thrust axis height. Returns the motor face x."""
    g = f"H-{HEAD} measuring head"
    lc, wc, hc = s.carriage
    bw, bt, bl = s.thrust_blade
    tw, tt, tl = s.torque_blade
    sc = s.screw
    r_hub = s.r_m - tl / 2
    r_ri, r_ro = s.r_m + tl / 2, s.r_m + tl / 2 + s.rim_w
    xc0 = x0 + s.tp                              # collar from the back wall's front face
    xs0 = xc0 + tw + 2                           # torque-stage plate, 2 mm in front of the collar
    xs1 = xs0 + s.stage_t
    cell_x0 = xs1 + CELL["gap"]
    cx0 = cell_x0 + CELL["h"] + CELL["gap"]      # thrust carriage
    cx1 = cx0 + lc
    z_lo, z_hi = zc + hc / 2, zc + hc / 2 + s.land + bl + s.land
    top_arm = (z_hi, z_hi + s.arm_h)
    bot_arm = (zc - hc / 2 - 25 - s.arm_h, zc - hc / 2 - 25)
    sw = wc / 2 + 10                             # torque-stage half width
    stop_gap, tab = 0.3, 6.0
    xm = (cx0 + cx1) / 2
    ar = s.arm_r
    ax = (xs0 + xs1) / 2                         # torque-cell axis x (centre of the torque arm)
    c_top = zc - s.arm_w / 2 - CELL["gap"]
    c_bot = c_top - CELL["h"]
    br_top = c_bot - CELL["gap"]
    bt_t = 10.0 if HEAD == "L" else 8.0          # bracket thickness
    tz0, tz1 = zc - s.arm_w / 2, zc + s.arm_w / 2

    # ── H-01 head frame (fixed): back wall + collar (outer ring of the torque flexure) + torque-cell bracket + stop
    h = []
    wall_z = (min(zc - 100, br_top - bt_t - 10), zc + 100)
    fr = box(x0, xc0, -100, max(100, ar + 45), *wall_z)
    fr = fr.fuse(ring(xc0, xc0 + tw, r_ri, r_ro, 0, zc))
    fr = fr.fuse(box(xc0, ax + CELL["w"] / 2 + 6, ar - 20, ar + 45, br_top - bt_t, br_top))
    cblk = box(xs0 - 4, xs1 + 4, ar + 18, ar + 30, br_top, tz1 + 20)
    fr = fr.fuse(cblk).cut(box(xs0 - 5, xs1 + 5, ar + 17, ar + 31, tz0 - 8, tz1 + 8))
    fr = fr.fuse(box(xc0, xs1 + 4, ar + 30, ar + 45, br_top, tz1 + 20))          # web from the bracket up to the C-block
    fr = spoke_slots(fr, h, xc0, zc, r_ri, s.slot_d, tt, tw, outer_face=False, pinch=True)
    fr = drill(fr, h, "M10 tap 18 deep", [(x0, y, zc + zz) for y in (-65, 65) for zz in (-65, 65)], (1, 0, 0),
               tap("M10"), 18)
    fr = drill(fr, h, "Ø8 H7 × 12 deep (dowel)", [(x0, 0, zc + zz) for zz in (-85, 85)], (1, 0, 0), 8.0, 12)
    fr = drill(fr, h, f"{CELL['thread']} tap thru (torque-cell stud)", [(ax, ar, br_top - bt_t)], (0, 0, 1),
               tap(CELL["thread"]))
    fr = drill(fr, h, "M5 tap thru (torque stop screw)", [(ax, ar + 24, tz1 + 20)], (0, 0, -1), tap("M5"))
    fr = drill(fr, h, "M5 tap thru (torque stop screw)", [(ax, ar + 24, br_top)], (0, 0, 1), tap("M5"))
    add(f"H{HEAD}-01", "Head frame (fixed): back wall, torque-flexure collar, torque-cell bracket", fr, AL7075,
        "CNC mill from solid, 3 setups; wire-EDM the collar slots", "make", "auto", g, ALU, h,
        f"collar slots {tt + 0.02:.2f} +0.01/0 wide; collar bore concentric to the dowel holes 0.02 mm")

    # ── H-02 torque stage (rotates): hub inside the collar + plate + top/bottom arms with clamp ribs + torque arm
    h = []
    st = cyl((xc0 + 1, 0, zc), (xs0 + 0.5, 0, zc), r_hub)
    st = spoke_slots(st, h, xc0, zc, r_hub, s.slot_d, tt, tw, outer_face=True, pinch=True)
    st = st.fuse(box(xs0, xs1, -sw, sw, bot_arm[0], top_arm[1]))
    st = st.fuse(box(xs1, cx1, -sw, sw, *top_arm))
    for rx0, rx1 in ((cx0, cx0 + s.rib), (cx1 - s.rib, cx1)):
        st = st.fuse(box(rx0, rx1, -wc / 2, wc / 2, z_hi - s.land, z_hi))
    st = st.fuse(box(xs1, cx1, -sw, sw, *bot_arm))
    stop = (xm - tab / 2 - stop_gap - 12, xm + tab / 2 + stop_gap + 12)
    st = st.fuse(box(stop[0], stop[1], -14, 14, bot_arm[1], zc - hc / 2 - 2))
    st = st.cut(box(xm - tab / 2 - 4, xm + tab / 2 + 4, -15, 15, bot_arm[1], zc - hc / 2))
    st = st.fuse(box(xs0, xs1, 0, ar + 30, tz0, tz1))                            # torque arm with its stop tongue
    st = drill(st, h, f"{CELL['thread']} tap 12 deep (thrust-cell stud)", [(xs1, 0, zc)], (1, 0, 0),
               tap(CELL["thread"]), 12)
    st = drill(st, h, f"{CELL['thread']} tap thru (torque-cell stud)", [(ax, ar, tz0)], (0, 0, 1), tap(CELL["thread"]))
    ys = [sy * (wc / 2 - bw / 2 - 3) for sy in (-1, 1)]
    st = drill(st, h, f"{sc} tap thru rib", [(cx0, y, z_hi - s.land / 2) for y in ys], (1, 0, 0), tap(sc))
    st = drill(st, h, f"{sc} tap thru rib", [(cx1, y, z_hi - s.land / 2) for y in ys], (-1, 0, 0), tap(sc))
    st = drill(st, h, "M5 tap thru (thrust stop screw)", [(stop[0], 0, zc - hc / 2 - 12)], (1, 0, 0), tap("M5"))
    st = drill(st, h, "M5 tap thru (thrust stop screw)", [(stop[1], 0, zc - hc / 2 - 12)], (-1, 0, 0), tap("M5"))
    add(f"H{HEAD}-02", "Torque stage (one piece): hub, plate, arms, torque arm", st, AL7075,
        "CNC turn the hub, mill the rest from solid; wire-EDM the hub slots", "make", "auto", g, ALU, h,
        f"hub slots {tt + 0.02:.2f} +0.01/0; rib faces flat 0.01 and parallel 0.01 mm; torque-cell hole at r = {ar} ± 0.05 mm")

    # ── H-03 thrust carriage: open frame (outer wall + cross webs), clamp ribs, overload tab, adapter holes on the webs
    h = []
    ca = box(cx0, cx1, -wc / 2, wc / 2, zc - hc / 2, zc + hc / 2)
    for py in (-1, 1):
        for pz in (-1, 1):
            y_a, y_b = sorted((py * s.web / 2, py * (wc / 2 - s.wall)))
            z_a, z_b = sorted((zc + pz * s.web / 2, zc + pz * (hc / 2 - s.wall)))
            ca = ca.cut(box(cx0 - 1, cx1 + 1, y_a, y_b, z_a, z_b))
    for rx0, rx1 in ((cx0, cx0 + s.rib), (cx1 - s.rib, cx1)):
        ca = ca.fuse(box(rx0, rx1, -wc / 2, wc / 2, z_lo, z_lo + s.land))
    ca = ca.fuse(box(xm - tab / 2, xm + tab / 2, -10, 10, zc - hc / 2 - 18, zc - hc / 2))
    ca = drill(ca, h, f"{CELL['thread']} tap 12 deep (thrust-cell stud)", [(cx0, 0, zc)], (1, 0, 0), tap(CELL["thread"]), 12)
    ca = drill(ca, h, f"{sc} tap thru rib", [(cx0, y, z_lo + s.land / 2) for y in ys], (1, 0, 0), tap(sc))
    ca = drill(ca, h, f"{sc} tap thru rib", [(cx1, y, z_lo + s.land / 2) for y in ys], (-1, 0, 0), tap(sc))
    r_a = s.adapter_pcd / 2
    ad_pts = [(cx1, r_a * math.cos(math.radians(a)), zc + r_a * math.sin(math.radians(a))) for a in (0, 90, 180, 270)]
    ca = drill(ca, h, f"{s.adapter_screw} tap {2.5 * MACHINED[s.adapter_screw].d:.0f} deep (motor adapter, on the webs)",
               ad_pts, (-1, 0, 0), tap(s.adapter_screw), 2.5 * MACHINED[s.adapter_screw].d)
    add(f"H{HEAD}-03", "Thrust carriage", ca, AL7075, "CNC mill from solid, 2 setups", "make", "auto", g, ALU, h,
        "rib faces flat 0.01 mm, parallel to the torque-stage ribs 0.02 mm when assembled; lightest part of the head: "
        "no material may be added")

    # ── thrust cell (bought) between the torque stage and the carriage, on two studs
    cell = box(cell_x0, cell_x0 + CELL["h"], -CELL["w"] / 2, CELL["w"] / 2, zc - CELL["t"] / 2, zc + CELL["t"] / 2)
    add("B-02", f"Load cell, micro S-type, {'5' if HEAD == 'S' else '20/50'} kg, M6×1, 0.05 % FS (thrust)", cell, BOUGHT,
        "—", "buy", "catalogue part", "load cells", CELL_C,
        notes="ATO DYLY-106 class: 25 × 30 × 12 mm, 2 × M6×1 (datasheet drawing); measure on delivery")
    for xa in (xs1 - 12, cx0 - CELL["gap"] - 6):
        fastener("Stud: set screw ISO 4026 M6×25 45H + 1 jam nut ISO 4035 M6", "thrust cell", (xa, 0, zc), (1, 0, 0), 24,
                 head=False)

    # ── guided blades (4) and clamp bars (8)
    bar_x = {"rear": (cx0 + s.rib + bt, cx0 + s.rib + bt + s.bar), "front": (cx1 - s.rib - bt - s.bar, cx1 - s.rib - bt)}
    blade_x = {"rear": (cx0 + s.rib, cx0 + s.rib + bt), "front": (cx1 - s.rib - bt, cx1 - s.rib)}
    for row in ("rear", "front"):
        for y in ys:
            h = []
            bl_s = box(*blade_x[row], y - bw / 2, y + bw / 2, z_lo, z_hi)
            bl_s = drill(bl_s, h, f"Ø{clear(sc)} thru", [(blade_x[row][0], y, z) for z in
                                                          (z_lo + s.land / 2, z_hi - s.land / 2)], (1, 0, 0), clear(sc))
            add(f"H{HEAD}-04", "Thrust flexure blade", bl_s, SPRING, "wire-EDM or photo-etch from shim, deburr", "outsource",
                f"shim {bt} × {bw} × {z_hi - z_lo:.0f}", g, BLADE_C, h,
                f"free length {bl} mm between clamp edges; no scratches across the width; edges deburred")
            for zz in (z_lo, z_hi - s.land):
                h = []
                cb = box(*bar_x[row], y - bw / 2, y + bw / 2, zz, zz + s.land)
                cb = drill(cb, h, f"Ø{clear(sc)} thru", [(bar_x[row][0], y, zz + s.land / 2)], (1, 0, 0), clear(sc))
                add(f"H{HEAD}-05", "Blade clamp bar", cb, STEEL, "mill, surface-grind the clamp face", "make",
                    f"flat {s.bar} × {bw} × {s.land}", g, DARK, h, "clamp face ground flat 0.005 mm; clamp edge sharp")
                d_in = (1, 0, 0) if row == "front" else (-1, 0, 0)
                x_head = bar_x[row][0] if row == "front" else bar_x[row][1]
                fastener(f"ISO 4762 {sc}×{s.blade_screw_l} 12.9", "blade clamps", (x_head, y, zz + s.land / 2), d_in,
                         s.blade_screw_l)

    # ── spoke blades (4) between the collar and the hub
    for a in (45, 135, 225, 315):
        u = cq.Vector(0, math.cos(math.radians(a)), math.sin(math.radians(a)))
        r0, r1 = r_hub - s.slot_d, r_ri + s.slot_d
        bl_t = (cq.Workplane(cq.Plane(origin=cq.Vector(xc0, 0, zc) + u * ((r0 + r1) / 2), xDir=u, normal=cq.Vector(1, 0, 0)))
                .rect(r1 - r0, tt).extrude(tw).val())
        add(f"H{HEAD}-06", "Torque flexure blade", bl_t, SPRING, "wire-EDM or photo-etch from shim, deburr", "outsource",
            f"shim {tt} × {tw} × {r1 - r0:.0f}", g, BLADE_C, notes=f"free length {tl} mm between slot edges")
    for _ in range(8):
        FASTENERS.setdefault("ISO 4762 M3×12 12.9 (slot pinch screw)", [0, set()])
        FASTENERS["ISO 4762 M3×12 12.9 (slot pinch screw)"][0] += 1
        FASTENERS["ISO 4762 M3×12 12.9 (slot pinch screw)"][1].add("torque flexure slots")

    # ── torque cell (bought) between the arm and the bracket, on two studs
    tcell = box(ax - CELL["w"] / 2, ax + CELL["w"] / 2, ar - CELL["t"] / 2, ar + CELL["t"] / 2, c_bot, c_top)
    add("B-03", f"Load cell, micro S-type, {'2' if HEAD == 'S' else '10/30'} kg, M6×1, 0.05 % FS (torque)", tcell, BOUGHT,
        "—", "buy", "catalogue part", "load cells", CELL_C, notes="as B-02")
    for zs in (tz0 + 12, br_top + 1):
        fastener("Stud: set screw ISO 4026 M6×25 45H + 1 jam nut ISO 4035 M6", "torque cell", (ax, ar, zs), (0, 0, -1), 24,
                 head=False)
    for spec_pt, ax_dir in (((stop[0], 0, zc - hc / 2 - 12), (1, 0, 0)), ((stop[1], 0, zc - hc / 2 - 12), (-1, 0, 0)),
                            ((ax, ar + 24, tz1 + 20), (0, 0, -1)), ((ax, ar + 24, br_top), (0, 0, 1))):
        fastener("ISO 4026 M5×16 set screw + jam nut (overload stop)", "overload stops", spec_pt, ax_dir, 16, head=False)

    # ── H-07 motor adapter on the carriage's front face
    xm0, xm1 = cx1, cx1 + s.adapter_t
    h = []
    f_ad = MACHINED[s.adapter_screw]
    ad = cyl((xm0, 0, zc), (xm1, 0, zc), max(s.motor_d / 2, r_a + 2.2 * f_ad.d))
    cb_depth = min(f_ad.head_h, s.adapter_t - 2)
    ad = drill(ad, h, f"Ø{f_ad.clearance} thru, cbore Ø{f_ad.cbore_d} × {cb_depth:.0f}", [(xm1, p[1], p[2]) for p in ad_pts],
               (-1, 0, 0), f_ad.clearance, cbore=(f_ad.cbore_d, cb_depth))
    ad = drill(ad, h, f"Ø{clear(s.motor_screw)} thru (motor pattern; screws from the back)",
               [(xm0, y, zc + z) for y, z in s.motor_holes], (1, 0, 0), clear(s.motor_screw))
    ad = drill(ad, h, "Ø8 thru (shaft clearance)", [(xm0, 0, zc)], (1, 0, 0), 8.0)
    add(f"H{HEAD}-07", "Motor adapter (one per motor pattern)", ad, AL7075, "CNC turn, drill", "make", "auto", g, ALU, h,
        "motor pattern: placeholder until the motor drawing is in hand; faces parallel 0.02 mm")
    for p in ad_pts:
        fastener(f"ISO 4762 {s.adapter_screw}×{s.adapter_screw_l} 12.9", "motor adapter to carriage",
                 (xm1 - cb_depth, p[1], p[2]), (-1, 0, 0), s.adapter_screw_l)
    return xm1


# ════════════════════════════════════════════════════════════════════
# MOTOR AND PROP (placeholders), CALIBRATION PARTS
# ════════════════════════════════════════════════════════════════════
def build_motor_prop(xm, zc, s: HeadSpec):
    motor = cyl((xm, 0, zc), (xm + s.motor_l, 0, zc), s.motor_d / 2)
    add("P-01", "Motor (placeholder envelope)", motor, BOUGHT, "—", "buy", "test article", "test article", MOTOR_C)
    x_disc = xm + s.motor_l + 15
    chord = max(15.0, 0.08 * PROP_D)
    prop = cyl((xm + s.motor_l, 0, zc), (x_disc + 4, 0, zc), max(8.0, 0.05 * PROP_D))
    for k in range(PROP_BLADES):
        blade = box(x_disc - 4, x_disc + 4, 0, PROP_D / 2, zc - chord / 2, zc + chord / 2)
        prop = prop.fuse(blade.rotate(cq.Vector(0, 0, zc), cq.Vector(1, 0, zc), k * 360 / PROP_BLADES))
    add("P-02", f"Prop Ø{PROP_D:.0f} (placeholder envelope)", prop, BOUGHT, "—", "buy", "test article", "test article", PROP_C)
    return x_disc


def build_calibration(s: HeadSpec):
    """Not in the assembly: drawn and exported on their own. Both bolt to the thrust carriage in place of the adapter."""
    g = "C calibration kit"
    f_ad = MACHINED[s.adapter_screw]
    r_a = s.adapter_pcd / 2
    r_pl = r_a + 2.2 * f_ad.d
    pts = [(s.adapter_t + 5, r_a * math.cos(math.radians(a)), r_a * math.sin(math.radians(a))) for a in (0, 90, 180, 270)]
    h = []
    pl = cyl((0, 0, 0), (s.adapter_t + 5, 0, 0), r_pl)
    pl = drill(pl, h, f"Ø{f_ad.clearance} thru, cbore Ø{f_ad.cbore_d}", pts, (-1, 0, 0), f_ad.clearance,
               cbore=(f_ad.cbore_d, f_ad.head_h))
    pl = drill(pl, h, "M8 tap thru (eye bolt on the axis)", [(s.adapter_t + 5, 0, 0)], (-1, 0, 0), tap("M8"))
    add(f"C{HEAD}-01", "Thrust calibration plate (replaces the motor adapter)", pl, AL7075, "CNC turn, drill, tap", "make",
        "auto", g, ALU, h, "eye bolt DIN 580 M8; pull line on the thrust axis ±0.5 mm")
    radii = (50, 100, 150) if HEAD == "L" else (25, 50, 100)
    h = []
    bar = box(0, 12, -radii[-1] - 15, radii[-1] + 15, -12, 12)
    bar = drill(bar, h, f"Ø{f_ad.clearance} thru", [(12, p[1], p[2]) for p in pts], (-1, 0, 0), f_ad.clearance)
    bar = drill(bar, h, "Ø6 H7 thru (load pin at a known radius)", [(0, sy * r, 0) for r in radii for sy in (-1, 1)],
                (1, 0, 0), 6.0)
    add(f"C{HEAD}-02", "Torque calibration bar", bar, AL7075, "CNC mill, jig-bore the load-pin holes", "make", "auto", g,
        ALU, h, "load-pin holes at the radii ±0.02 mm from the pattern centre")


# ════════════════════════════════════════════════════════════════════
# W2 RING PORTAL (weldment, clamped to the rails) + R1 CONTAINMENT RING (L) or G1 GUARD (S)
# ════════════════════════════════════════════════════════════════════
def build_portal(xd, zc):
    g = "W2 ring portal"
    r_i = (PROP_D / 2 + 60) if HEAD == "L" else 0
    y_pp = 855.0 if HEAD == "L" else 855.0
    top = 2460.0
    for s in (-1, 1):
        h = []
        post = rhs((xd, s * y_pp, BASE_TOP), (xd, s * y_pp, top), 80, 4, side=(1, 0, 0))
        post = drill(post, h, "Ø17.5 thru (ring or guard bolts)", [(xd, s * (y_pp - 40), z)
                     for z in [750 + INDEX_PITCH * k for k in range(19)]], (0, s, 0), clear("M16"))
        add("W2-01", "Portal post", post, STEEL, "saw cut, drill on a jig, weld", "outsource", "RHS 80×80×4 × 2280", g, GREY, h,
            "holes on 50 mm pitch, ±0.2 mm cumulative, both posts drilled as a pair")
        add("W2-02", "Portal foot", rhs((xd - PORTAL_FOOT / 2, s * y_pp, Z_RAIL), (xd + PORTAL_FOOT / 2, s * y_pp, Z_RAIL), 80, 4),
            STEEL, "saw cut, weld", "outsource", "RHS 80×80×4 × 900", g, GREY)
        for xe in (-1, 1):
            h = []
            x = xd + xe * (PORTAL_FOOT / 2 - 40)
            fp = box(x - 60, x + 60, s * y_pp - 60, s * y_pp + 60, FOOT_H - 12, FOOT_H)
            fp = drill(fp, h, "M16 tap thru", [(x, s * y_pp, FOOT_H - 12)], (0, 0, 1), tap("M16"))
            add("W1-03", "Foot plate", fp, STEEL, "laser cut, drill, tap M16, weld", "outsource", "plate 12 × 120 × 120",
                g, GREY, h)
            levelling_foot(x, s * y_pp, "W2 ring portal")
            kb = rhs((xd + xe * 40, s * y_pp, 1000), (xd + xe * 380, s * y_pp, BASE_TOP), 60, 4, side=(0, 1, 0))
            kb = trim(kb, (xd + xe * 40, 0, 0), (-xe, 0, 0))
            kb = trim(kb, (0, 0, BASE_TOP), (0, 0, -1))
            add("W2-03", "Portal knee brace", kb, STEEL, "saw cut both ends (on the CAD), weld", "outsource",
                "RHS 60×60×4 × 1000", g, GREY)
    add("W2-04", "Portal top tie", rhs((xd, -y_pp + 40, top - 40), (xd, y_pp - 40, top - 40), 80, 4), STEEL,
        "saw cut, weld", "outsource", "RHS 80×80×4 × 1630", g, GREY)
    h = []
    beam = rhs((xd, -y_pp + 40, Z_RAIL + 80), (xd, y_pp - 40, Z_RAIL + 80), 80, 4)
    clamp_pts = [(xd, s * (RAIL_Y + o), BASE_TOP + 80) for s in (-1, 1) for o in (-52, 52)]
    beam = drill(beam, h, "Ø13.5 thru (rail clamp)", clamp_pts, (0, 0, -1), clear("M12"))
    add("W2-05", "Portal beam (on the rails)", beam, STEEL, "saw cut, drill, weld", "outsource", "RHS 80×80×4 × 1630", g, GREY, h)
    for s in (-1, 1):
        h = []
        cp = box(xd - 40, xd + 40, s * RAIL_Y - 75, s * RAIL_Y + 75, FOOT_H - 12, FOOT_H)
        cp = drill(cp, h, "Ø13.5 thru", [(xd, s * (RAIL_Y + o), FOOT_H) for o in (-52, 52)], (0, 0, -1), clear("M12"))
        add("W2-06", "Rail clamp plate", cp, STEEL, "laser cut, drill", "make", "plate 12 × 80 × 150", g, GREY, h)
        for o in (-52, 52):
            fastener("ISO 4014 M12×200 8.8 + 2 washers ISO 7089 + nut ISO 4032", "portal to rails", (xd, s * (RAIL_Y + o), BASE_TOP + 80),
                     (0, 0, -1), 200)
    if HEAD == "L":
        build_ring(xd, zc, y_pp, r_i)
    else:
        build_guard(xd, zc, y_pp)


def build_ring(xd, zc, y_pp, r_i):
    g = "R1 containment ring"
    t, w = 10.0, 300.0
    r_o = r_i + t
    add("R1-01", "Containment band (rolled, butt-welded)", ring(xd - w / 2, xd + w / 2, r_i, r_o, 0, zc), STEEL,
        "roll plate to Ø, full-penetration butt weld, grind flush, UT the seam", "outsource",
        f"plate 10 × 300 × {2 * math.pi * (r_i + r_o) / 2:.0f}", g, RED, notes="seam at the bottom; band plate qualified by a coupon impact test before first use")
    for s in (-1, 1):
        h = []
        yb = s * (y_pp - 40)
        lug = box(xd - 60, xd + 60, min(yb, yb - s * 20), max(yb, yb - s * 20), zc - 110, zc + 110)
        lug = drill(lug, h, "Ø17.5 thru", [(xd, yb - s * 20, zc + dz) for dz in (-50, 50)], (0, s, 0), clear("M16"))
        add("R1-02", "Ring lug plate", lug, STEEL, "laser cut, drill, weld", "outsource", "plate 20 × 120 × 220", g, RED, h)
        y_in = s * (r_o - 5)
        for dx in (-45, 45):
            rib = box(xd + dx - 6, xd + dx + 6, min(y_in, yb - s * 20), max(y_in, yb - s * 20), zc - 90, zc + 90)
            rib = rib.cut(cyl((xd - 200, 0, zc), (xd + 200, 0, zc), r_o))
            add("R1-03", "Ring lug rib", rib, STEEL, "laser cut, weld", "outsource", "plate 12 × 90 × 180", g, RED)
        for dz in (-50, 50):
            fastener("ISO 4017 M16×130 8.8 + 2 washers ISO 7089 + nut ISO 4032", "ring to portal", (xd, s * (y_pp + 40), zc + dz),
                     (0, -s, 0), 130)


def build_guard(xd, zc, y_pp):
    """S head: rolled 3 mm steel band between two aluminium flat rings, on two arms to the portal posts. (Polycarbonate
    was dropped: 6 mm sheet cannot be cold-bent below ~600-900 mm radius; this band's radius is ~230 mm.)"""
    g = "G1 small-prop guard"
    r_i = PROP_D / 2 + 40
    add("G1-01", "Guard band (rolled steel, butt-welded)", ring(xd - 75, xd + 75, r_i, r_i + 3, 0, zc), STEEL,
        "roll sheet to Ø, butt weld, grind flush", "outsource", "sheet 3 × 150 × " + f"{2 * math.pi * r_i:.0f}", g, RED,
        notes="contains a 20 J blade fragment (≈ 35 J to perforate); paint high-visibility")
    r_t = r_i + 18                                         # tie rods between the flat rings, outside the band
    rods = [(r_t * math.cos(math.radians(a)), zc + r_t * math.sin(math.radians(a))) for a in (45, 135, 225, 315)]
    tab_y = r_i + 51                                       # tab bolt radius (at +/- y)
    for xs in (xd - 81, xd + 75):
        h = []
        fr = ring(xs, xs + 6, r_i - 15, r_i + 31, 0, zc)
        for sy in (-1, 1):
            fr = fr.fuse(box(xs, xs + 6, min(sy * (r_i + 26), sy * (r_i + 71)), max(sy * (r_i + 26), sy * (r_i + 71)),
                             zc - 25, zc + 25))
        fr = drill(fr, h, "Ø9 thru (tie rod)", [(xs, y, z) for y, z in rods], (1, 0, 0), clear("M8"))
        fr = drill(fr, h, "Ø9 thru (arm fork)", [(xs, sy * tab_y, zc) for sy in (-1, 1)], (1, 0, 0), clear("M8"))
        add("G1-02", "Guard flat ring with tabs", fr, AL7075, "laser or waterjet cut, drill", "outsource", "plate 6", g, ALU, h)
    for y, z in rods:
        fastener("Threaded rod M8 × 180 + spacer tube + 2 nuts", "guard tie rods", (xd - 90, y, z), (1, 0, 0), 180, head=False)
    for sy in (-1, 1):
        y0 = sy * (r_i + 81)                                # arm's inner end (outer face of the cross plate)
        h = []
        cp = box(xd - 87, xd + 87, min(y0, y0 - sy * 10), max(y0, y0 - sy * 10), zc - 30, zc + 30)
        add("G1-05", "Guard arm cross plate", cp, STEEL, "laser cut, weld", "outsource", "plate 10 × 60 × 174", g, GREY)
        for xf0, xf1 in ((xd - 87, xd - 81), (xd + 81, xd + 87)):
            h = []
            fk = box(xf0, xf1, min(sy * (r_i + 31), y0 - sy * 10), max(sy * (r_i + 31), y0 - sy * 10), zc - 25, zc + 25)
            fk = drill(fk, h, "Ø9 thru", [(xf0, sy * tab_y, zc)], (1, 0, 0), clear("M8"))
            add("G1-06", "Guard fork plate", fk, STEEL, "laser cut, drill, weld", "outsource", "plate 6 × 50 × 40", g, GREY, h)
            fastener("ISO 4017 M8×25 8.8 + washers + nut", "guard fork", (xf0 if xf0 < xd else xf1, sy * tab_y, zc),
                     (1, 0, 0) if xf0 < xd else (-1, 0, 0), 25)
        h = []
        arm = rhs((xd, y0, zc), (xd, sy * (y_pp - 52), zc), 60, 4)
        add("G1-03", "Guard arm", arm, STEEL, "saw cut, weld", "outsource", "RHS 60×60×4", g, GREY)
        ep = box(xd - 60, xd + 60, min(sy * (y_pp - 40), sy * (y_pp - 52)), max(sy * (y_pp - 40), sy * (y_pp - 52)),
                 zc - 110, zc + 110)
        ep = drill(ep, h, "Ø17.5 thru", [(xd, sy * (y_pp - 52), zc + dz) for dz in (-50, 50)], (0, sy, 0), clear("M16"))
        add("G1-04", "Guard arm end plate", ep, STEEL, "laser cut, drill, weld", "outsource", "plate 12 × 120 × 220", g, GREY, h)
        for dz in (-50, 50):
            fastener("ISO 4017 M16×120 8.8 + 2 washers ISO 7089 + nut ISO 4032", "guard to portal", (xd, sy * (y_pp + 40), zc + dz),
                     (0, -sy, 0), 120)


# ════════════════════════════════════════════════════════════════════
# BUILD
# ════════════════════════════════════════════════════════════════════
spec = HEADS[HEAD]
assert 800 <= H_AXIS <= 1600 and (H_AXIS - 800) % INDEX_PITCH == 0, "H_AXIS: 800-1600 mm in 50 mm steps"
build_frame()
build_saddle(H_AXIS - 50)
build_boom(BOOM_FLANGE_X[HEAD], H_AXIS)
x_motor = build_head(BOOM_FLANGE_X[HEAD], H_AXIS, spec)
X_DISC = build_motor_prop(x_motor, H_AXIS, spec)
build_portal(X_DISC, H_AXIS)
build_calibration(spec)

if HEAD == "L":
    assert H_AXIS - PROP_D / 2 > 300, "prop tip too close to the floor: raise H_AXIS"

# ════════════════════════════════════════════════════════════════════
# CHECKS: no part overlaps another (fasteners excluded); every assembled part touches another
# ════════════════════════════════════════════════════════════════════
ASSEMBLED = [(pid, i, s) for pid, p in PARTS.items() if not pid.startswith("C") for i, s in enumerate(p.solids)]


def check_assembly(tol=1e-3):
    global HW_BOXES
    HW_BOXES = [(hw, hw.BoundingBox()) for hw in HW_SOLIDS]
    clashes, floating = [], []
    boxes = [s.BoundingBox() for _, _, s in ASSEMBLED]
    for a in range(len(ASSEMBLED)):
        touching = False
        for b in range(len(ASSEMBLED)):
            if a == b:
                continue
            ba, bb = boxes[a], boxes[b]
            if (ba.xmin > bb.xmax + 0.5 or bb.xmin > ba.xmax + 0.5 or ba.ymin > bb.ymax + 0.5 or bb.ymin > ba.ymax + 0.5
                    or ba.zmin > bb.zmax + 0.5 or bb.zmin > ba.zmax + 0.5):
                continue
            sa, sb = ASSEMBLED[a][2], ASSEMBLED[b][2]
            if b > a:
                v = sa.intersect(sb).Volume()
                if v > tol:
                    clashes.append((ASSEMBLED[a][0], ASSEMBLED[b][0], round(v, 1)))
            if not touching and sa.distance(sb) < 0.05:
                touching = True
        if not touching:                              # held by a fastener (load cells hang on their studs)
            touching = any(boxes[a].xmin - 1 <= hb.xmax and hb.xmin <= boxes[a].xmax + 1 and boxes[a].ymin - 1 <= hb.ymax
                           and hb.ymin <= boxes[a].ymax + 1 and boxes[a].zmin - 1 <= hb.zmax and hb.zmin <= boxes[a].zmax + 1
                           and ASSEMBLED[a][2].distance(hw) < 0.05 for hw, hb in HW_BOXES)
        if not touching and not ASSEMBLED[a][0].startswith("P-"):
            floating.append(ASSEMBLED[a][0])
    return clashes, floating


# ════════════════════════════════════════════════════════════════════
# PREVIEW & EXPORT
# ════════════════════════════════════════════════════════════════════
display, names, colors = [], [], []
for pid, p in PARTS.items():
    if pid.startswith("C"):
        continue
    for i, s in enumerate(p.solids):
        display.append(cq.Workplane(obj=s))
        names.append(f"{pid}_{i}")
        colors.append(p.color)
display.append(cq.Workplane(obj=cq.Compound.makeCompound(HW_SOLIDS)))
names.append("fasteners")
colors.append(BOLT_C)
show(*display, names=names, colors=colors)

if __name__ == "__main__" or os.environ.get("PROP_DYNO_EXPORT"):
    out = os.path.join("export", "prop_dyno", HEAD)
    import shutil
    shutil.rmtree(out, ignore_errors=True)                # generated files only: no stale part numbers survive
    os.makedirs(out, exist_ok=True)
    assembly = cq.Assembly(name=f"prop_dyno_{HEAD}")
    for pid, p in PARTS.items():
        s0 = p.solids[0]
        bb = s0.BoundingBox()
        cq.exporters.export(cq.Workplane(obj=s0.moved(cq.Location(cq.Vector(-bb.xmin, -bb.ymin, -bb.zmin)))),
                            os.path.join(out, f"{pid}.step"))
        if not pid.startswith("C"):
            for i, s in enumerate(p.solids):
                assembly.add(s, name=f"{pid}_{i}", color=cq.Color(*p.color))
    assembly.add(cq.Compound.makeCompound(HW_SOLIDS), name="fasteners", color=cq.Color(*BOLT_C))
    assembly.save(os.path.join(out, f"prop_dyno_{HEAD}_assembly.step"))
    stl = os.path.join("export", f"prop_dyno_{HEAD}.stl")
    cq.exporters.export(cq.Workplane(obj=assembly.toCompound()), stl, tolerance=0.2, angularTolerance=0.2)
    with open(os.path.join(out, "parts.csv"), "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["part", "name", "qty", "material", "process", "source", "stock", "group", "mass_kg_each", "notes"])
        for pid, p in PARTS.items():
            wr.writerow([pid, p.name, len(p.solids), p.material, p.process, p.source, p.stock, p.group,
                         round(p.mass, 3), p.notes])
    with open(os.path.join(out, "fasteners.csv"), "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["fastener", "qty", "used in"])
        for spec_s, (n, where) in sorted(FASTENERS.items()):
            wr.writerow([spec_s, n, "; ".join(sorted(where))])
    with open(os.path.join(out, "holes.csv"), "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["part", "feature", "x", "y", "z", "axis (into material)", "frame: part bounding-box minimum corner"])
        for pid, p in PARTS.items():
            bb = p.solids[0].BoundingBox()
            for hl in p.holes:
                wr.writerow([pid, hl.label, round(hl.pos[0] - bb.xmin, 2), round(hl.pos[1] - bb.ymin, 2),
                             round(hl.pos[2] - bb.zmin, 2), hl.axis])
    total = sum(p.mass * len(p.solids) for pid, p in PARTS.items() if not pid.startswith(("C", "P")))
    print(f"prop dyno ({HEAD} head, axis {H_AXIS:.0f} mm, prop Ø{PROP_D:.0f}): {len(PARTS)} part numbers, "
          f"{sum(len(p.solids) for p in PARTS.values())} parts, {sum(n for n, _ in FASTENERS.values())} fasteners, "
          f"{total:.0f} kg without fasteners")
    print(f"exported {stl} and {out}/")
    moving = (PARTS[f"H{HEAD}-03"].mass + PARTS[f"H{HEAD}-07"].mass + 0.5 * PARTS["B-02"].mass
              + 4 * PARTS[f"H{HEAD}-05"].mass + 0.5 * 4 * PARTS[f"H{HEAD}-04"].mass)   # carriage-side bars, half the blades
    print(f"torque stage (rotating, carries the thrust stage): {PARTS[f'H{HEAD}-02'].mass:.3f} kg")
    print(f"thrust-axis moving structure (CAD): {moving:.3f} kg")
    CLASSES = {"S": (("15-inch delivery prototype", 5, 0.12 + 0.02),),                 # cell kg, motor + prop kg (ASSUMED)
               "L": (("MK30-like", 20, 0.5 + 0.15), ("FlyCart-like", 50, 1.5 + 0.6))}
    for name, cap, mp in CLASSES[HEAD]:
        k = cap * 9.81 / 0.2e-3                                 # N/m: capacity over 0.2 mm full-scale deflection (ASSUMED)
        m = moving + mp
        print(f"  {name}: {cap} kg cell, moving {m:.2f} kg -> f_n = {math.sqrt(k / m) / (2 * math.pi):.0f} Hz (need >= 100)")
    if os.environ.get("PROP_DYNO_CHECK", "1") == "1":
        clashes, floating = check_assembly()
        print("overlaps:", clashes or "none")
        print("parts touching nothing:", floating or "none")
