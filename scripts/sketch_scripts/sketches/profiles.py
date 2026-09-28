"""
sketches/profiles.py — Reusable 2D geometric sketches and profiles.

Using CadQuery's 2D Sketch API guarantees that 2D fillets and complex
profiles never fail, producing mathematically clean 3D extrusions.
"""

from __future__ import annotations
import math
import cadquery as cq


def rounded_rect(length: float, width: float, radius: float) -> cq.Sketch:
    """Creates a 2D rectangle with smoothly filleted corners."""
    max_r = min(length, width) / 2.0 - 0.01
    radius = min(radius, max_r)
    
    sketch = cq.Sketch().rect(length, width)
    if radius > 0:
        sketch = sketch.vertices().fillet(radius)
    return sketch


def chamfered_rect(length: float, width: float, chamfer: float) -> cq.Sketch:
    """Creates a 2D rectangle with chamfered corners."""
    max_c = min(length, width) / 2.0 - 0.01
    chamfer = min(chamfer, max_c)
    
    sketch = cq.Sketch().rect(length, width)
    if chamfer > 0:
        sketch = sketch.vertices().chamfer(chamfer)
    return sketch


def slotted_hole(length: float, diameter: float, angle: float = 0) -> cq.Sketch:
    """Creates a 2D elongated slot / stadium shape."""
    return cq.Sketch().slot(length, diameter, angle)


def regular_polygon(sides: int, radius: float, fillet_r: float = 0) -> cq.Sketch:
    """Creates an n-sided regular polygon with optional rounded vertices."""
    pts = []
    angle_step = 2 * math.pi / sides
    for i in range(sides):
        angle = i * angle_step
        pts.append((radius * math.cos(angle), radius * math.sin(angle)))
        
    sketch = cq.Sketch().polygon(pts)
    if fillet_r > 0:
        sketch = sketch.vertices().fillet(fillet_r)
    return sketch


def trapezoid(base_w: float, top_w: float, height: float, fillet_r: float = 0) -> cq.Sketch:
    """Creates a symmetrical trapezoid sketch centered along the X axis."""
    pts = [
        (-base_w / 2.0, -height / 2.0),
        ( base_w / 2.0, -height / 2.0),
        ( top_w / 2.0,   height / 2.0),
        (-top_w / 2.0,   height / 2.0),
    ]
    sketch = cq.Sketch().polygon(pts)
    if fillet_r > 0:
        sketch = sketch.vertices().fillet(fillet_r)
    return sketch


def u_channel(width: float, height: float, thickness: float, inner_r: float = 0) -> cq.Sketch:
    """Creates a 2D U-channel profile."""
    outer_pts = [
        (-width / 2.0, height / 2.0),
        (-width / 2.0, -height / 2.0),
        ( width / 2.0, -height / 2.0),
        ( width / 2.0, height / 2.0),
        ( width / 2.0 - thickness, height / 2.0),
        ( width / 2.0 - thickness, -height / 2.0 + thickness),
        (-width / 2.0 + thickness, -height / 2.0 + thickness),
        (-width / 2.0 + thickness, height / 2.0),
    ]
    sketch = cq.Sketch().polygon(outer_pts)
    if inner_r > 0:
        # exc --> AND NOT operator
        sketch = sketch.vertices("<Y exc >Y").fillet(inner_r)
    return sketch


def l_profile(width: float, height: float, thickness: float, inner_r: float = 0) -> cq.Sketch:
    """Creates a 2D L-bracket profile."""
    pts = [
        (0, 0),
        (width, 0),
        (width, thickness),
        (thickness, thickness),
        (thickness, height),
        (0, height),
    ]
    sketch = cq.Sketch().polygon(pts)
    if inner_r > 0:
        sketch = sketch.vertices("(>X and >Y)").fillet(inner_r)
    return sketch


def i_beam(height: float, flange_w: float, web_t: float, flange_t: float, fillet_r: float = 0) -> cq.Sketch:
    """Creates a standard 2D I-beam cross section."""
    hw = flange_w / 2.0
    hh = height / 2.0
    wt = web_t / 2.0
    ft = hh - flange_t
    
    pts = [
        (-hw,  hh), ( hw,  hh), ( hw,  ft), ( wt,  ft),
        ( wt, -ft), ( hw, -ft), ( hw, -hh), (-hw, -hh),
        (-hw, -ft), (-wt, -ft), (-wt,  ft), (-hw,  ft),
    ]
    sketch = cq.Sketch().polygon(pts)
    if fillet_r > 0:
        sketch = sketch.vertices().fillet(fillet_r)
    return sketch
