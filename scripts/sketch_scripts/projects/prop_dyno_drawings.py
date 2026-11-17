"""
projects/prop_dyno_drawings.py — Drawing set for every made or outsourced dyno part, both head configurations.

One A3 sheet per part: front, top and side projections plus an isometric (hidden lines dashed), the title block
(material, process, stock, mass, quantity per configuration, general tolerance) and the hole table (every hole and
thread, its position from the part's bounding-box corner, and its direction). Views are not to scale: the STEP file
of the part (export/prop_dyno/<HEAD>/<part>.step) is the master geometry; this sheet states what the STEP cannot.

Run:  python3 projects/prop_dyno_drawings.py   ->  export/prop_dyno/prop_dyno_drawings.pdf
"""

import io
import contextlib
import os
import runpy
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import cadquery as cq
import cairosvg
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIGS = (("L", "1600", "1370"), ("S", "900", "381"))
GENERAL = ("General tolerances ISO 2768-mK. Break sharp edges 0.3 × 45° unless marked sharp. Dimensions in mm. "
           "Machined surfaces Ra 3.2 unless noted. Welded parts: ISO 13920-BF, fillet welds a = 0.7 × thinner wall, "
           "all round, per ISO 5817 level C.")


def load(head, h_axis, prop_d):
    os.environ.update(DYNO_HEAD=head, DYNO_H_AXIS=h_axis, DYNO_PROP_D=prop_d)
    from cq_server.ui import ui
    ui.get_assembly()                          # clear the viewer's assembly between configurations
    with contextlib.redirect_stdout(io.StringIO()):
        return runpy.run_path(os.path.join(HERE, "prop_dyno.py"), run_name="drawings")


def view_png(shape, rotations, size=900):
    """Rotate `shape` by exact axis rotations [(axis, degrees), ...], then project along z (x right, y up)."""
    o = cq.Vector(0, 0, 0)
    for axis, deg in rotations:
        shape = shape.rotate(o, cq.Vector(*axis), deg)
    svg = cq.occ_impl.exporters.svg.getSVG(shape, opts={
        "width": size, "height": size, "marginLeft": 20, "marginTop": 20, "showAxes": False,
        "projectionDir": (0, 0, 1), "strokeWidth": -1.0, "strokeColor": (20, 20, 20),
        "hiddenColor": (150, 150, 150), "showHidden": True})
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), background_color="white")))


def sheet(pdf, part, qty):
    s0 = part.solids[0]
    bb = s0.BoundingBox()
    s0 = s0.moved(cq.Location(cq.Vector(-bb.xmin, -bb.ymin, -bb.zmin)))
    fig = plt.figure(figsize=(16.54, 11.69))                       # A3 landscape
    views = (("Front: x right, z up (from −y)", [((1, 0, 0), -90)]),
             ("Top: x right, y up (from +z)", []),
             ("Side: y right, z up (from +x)", [((0, 0, 1), -90), ((1, 0, 0), -90)]),
             ("Isometric (from +x, −y, +z)", [((0, 0, 1), -45), ((1, 0, 0), -54.7356)]))
    for k, (title, rot) in enumerate(views):
        ax = fig.add_axes([0.02 + (k % 2) * 0.31, 0.50 - (k // 2) * 0.42, 0.30, 0.40])
        ax.imshow(view_png(s0, rot)); ax.set_title(title, fontsize=9); ax.axis("off")
    tb = fig.add_axes([0.64, 0.50, 0.35, 0.47]); tb.axis("off")
    lines = [(f"{part.pid}  {part.name}", 13, "bold"),
             (f"Quantity: {qty}", 10, "normal"),
             (f"Material: {part.material}", 10, "normal"),
             (f"Stock: {part.stock}", 10, "normal"),
             (f"Process: {part.process}", 10, "normal"),
             (f"Made by: {part.source}", 10, "normal"),
             (f"Group: {part.group}", 10, "normal"),
             (f"Envelope: {bb.xlen:.1f} (x) × {bb.ylen:.1f} (y) × {bb.zlen:.1f} (z) mm   Mass ≈ {part.mass:.3f} kg", 10, "normal"),
             ("Axes: x along the thrust axis toward the prop, y left, z up (as installed).", 9, "normal"),
             (f"Master geometry: {part.pid}.step (STEP file of the same name)", 9, "normal"),
             ("Special requirements: " + (part.notes or "none beyond the general note"), 10, "normal"),
             (GENERAL, 8, "normal")]
    y = 1.0
    import textwrap
    for text, size, weight in lines:
        for ln in textwrap.wrap(text, 78 if size <= 9 else 66):
            tb.text(0, y, ln, fontsize=size, fontweight=weight, va="top", family="DejaVu Sans")
            y -= 0.032 if size <= 9 else 0.042
        y -= 0.01
    ht = fig.add_axes([0.64, 0.04, 0.35, 0.44]); ht.axis("off")
    rows = [[h.label, f"{h.pos[0] - bb.xmin:.2f}", f"{h.pos[1] - bb.ymin:.2f}", f"{h.pos[2] - bb.zmin:.2f}",
             "".join(f"{'+' if c > 0 else '−'}{n}" for c, n in zip(h.axis, "xyz") if abs(c) > 1e-6) or "—"]
            for h in part.holes]
    if rows:
        shown = rows[:28]
        t = ht.table(cellText=shown, colLabels=["Hole / thread", "x", "y", "z", "into"], loc="upper left",
                     colWidths=[0.52, 0.12, 0.12, 0.12, 0.12], cellLoc="left")
        t.auto_set_font_size(False); t.set_fontsize(7.5); t.scale(1, 1.15)
        ht.set_title(f"Hole table ({len(rows)} holes; positions from the envelope's minimum corner, mm)"
                     + ("; first 28 shown, all in holes.csv" if len(rows) > 28 else ""), fontsize=9, loc="left")
    else:
        ht.text(0, 1, "No holes.", fontsize=10, va="top")
    pdf.savefig(fig); plt.close(fig)


def main():
    parts, qty = {}, {}
    for head, h, d in CONFIGS:
        g = load(head, h, d)
        for pid, p in g["PARTS"].items():
            if p.source == "buy":
                continue
            parts.setdefault(pid, p)
            qty.setdefault(pid, []).append(f"{len(p.solids)} ({head} head)")
    out = os.path.join("export", "prop_dyno", "prop_dyno_drawings.pdf")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with PdfPages(out) as pdf:
        for pid in sorted(parts):
            sheet(pdf, parts[pid], ", ".join(qty[pid]))
    print(f"{len(parts)} drawing sheets -> {out}")


if __name__ == "__main__":
    main()
