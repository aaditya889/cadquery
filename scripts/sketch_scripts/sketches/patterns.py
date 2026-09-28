"""
sketches/patterns.py — 2D Grid, Circular, and Hexagonal cut patterns.
"""

from __future__ import annotations
import math
import cadquery as cq


def bolt_circle_pattern(radius: float, count: int, hole_dia: float, start_angle: float = 0) -> cq.Sketch:
    """Creates a circular pitch pattern of drill holes (bolt circle / PCD)."""
    pts = []
    angle_step = 360.0 / count
    for i in range(count):
        ang_rad = math.radians(start_angle + i * angle_step)
        pts.append((radius * math.cos(ang_rad), radius * math.sin(ang_rad)))
        
    return (
        cq.Sketch()
        .push(pts)
        .circle(hole_dia / 2.0)
    )


def slotted_grille(width: float, height: float, slot_w: float, slot_h: float, spacing_x: float, spacing_y: float) -> cq.Sketch:
    """Creates a 2D ventilation grille made of rounded stadium slots."""
    pts = []
    nx = int(width / (slot_w + spacing_x))
    ny = int(height / (slot_h + spacing_y))
    
    start_x = -((nx - 1) * (slot_w + spacing_x)) / 2.0
    start_y = -((ny - 1) * (slot_h + spacing_y)) / 2.0
    
    sketch = cq.Sketch()
    for ix in range(nx):
        for iy in range(ny):
            cx = start_x + ix * (slot_w + spacing_x)
            cy = start_y + iy * (slot_h + spacing_y)
            r = min(slot_w, slot_h) / 2.0
            dx = (slot_w - 2 * r) / 2.0
            dy = (slot_h - 2 * r) / 2.0
            slot = (
                cq.Sketch()
                .push([(cx - dx, cy - dy), (cx + dx, cy + dy)])
                .circle(r)
                .clean()
                # .hull()
            )
            sketch = sketch.face(slot, mode="a")
            
    return sketch


def hex_grid_pattern(width: float, height: float, hex_radius: float, wall_t: float) -> cq.Sketch:
    """Creates a 2D honeycomb hex ventilation pattern."""
    dx = math.sqrt(3) * hex_radius + wall_t
    dy = 1.5 * hex_radius + (wall_t * math.sqrt(3) / 2)
    
    nx = int(width / dx)
    ny = int(height / dy)
    
    start_x = -((nx - 1) * dx) / 2.0
    start_y = -((ny - 1) * dy) / 2.0
    
    pts = []
    for iy in range(ny):
        offset_x = (dx / 4.0) if ( iy % 4 == 1 or iy % 4 == 3 ) else 0.0
        for ix in range(nx):
            cx = start_x + ix * dx + ((offset_x)*(-1)**(iy % 3))
            cy = start_y + iy * dy
            pts.append((cx, cy))
            
    sketch = cq.Sketch()
    hex_pts = [
        (hex_radius * math.cos(math.radians(a)), hex_radius * math.sin(math.radians(a)))
        for a in range(0, 360, 60)
    ]
    
    for p in pts:
        single_hex = cq.Sketch().push([p]).polygon(hex_pts)
        sketch = sketch.face(single_hex, mode="a")
        
    return sketch
