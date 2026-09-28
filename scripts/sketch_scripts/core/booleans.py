"""
core/booleans.py — Robust solid manipulation, fusing, and junction edge selection.

Provides seamless fusion of mixed types (Workplane, Assembly, Compound), deep copying,
and automated seam/junction edge detection for filleting assembly interfaces.
"""

from __future__ import annotations
import cadquery as cq


def to_shape(obj) -> cq.Shape:
    """Extract raw CadQuery Shape from Workplane, Assembly, Compound, or Solid."""
    if hasattr(obj, "build"):       # Component instance
        obj = obj.build()
    if hasattr(obj, "toCompound"):  # Assembly
        return obj.toCompound()
    if hasattr(obj, "val"):         # Workplane
        return obj.val()
    return obj


def to_workplane(obj, workplane="XY") -> cq.Workplane:
    """Safely convert any CadQuery object/shape into an editable cq.Workplane."""
    if isinstance(obj, cq.Workplane):
        return obj
    shape = to_shape(obj)
    return cq.Workplane(workplane).newObject([shape])


def duplicate(obj) -> cq.Workplane:
    """
    Creates an independent deep-copy of any CadQuery object (Workplane, Compound, Solid, Assembly)
    and returns an editable Workplane.
    """
    shape = to_shape(obj)
    return cq.Workplane(obj=shape.copy())


def fuse_all(*parts) -> cq.Workplane:
    """
    Fuses multiple parts (Workplanes, Compounds, Assemblies, or Shapes) into a single 
    continuous, watertight solid Workplane.
    
    Usage:
        fused = fuse_all(stand_base, pillar_1, pillar_2, wing_1)
    """
    if len(parts) == 1 and isinstance(parts[0], (list, tuple)):
        parts = parts[0]
    
    all_solids = []
    for p in parts:
        shape = to_shape(p)
        if isinstance(shape, cq.Compound):
            all_solids.extend(shape.Solids())
        elif isinstance(shape, cq.Solid):
            all_solids.append(shape)
        else:
            all_solids.extend(shape.Solids())
            
    if not all_solids:
        raise ValueError("fuse_all received no valid solids to fuse.")
        
    return cq.Workplane().add(all_solids).combine()


def find_junction_edges(fused_model, part_a, part_b, tolerance: float = 0.5) -> cq.Workplane:
    """
    Selects only the seam edges formed where part_a and part_b touch/intersect in fused_model.
    Accepts any combination of Workplane, Compound, Solid, or Assembly objects.
    
    Usage:
        fused = fuse_all(base, pillar)
        fused = find_junction_edges(fused, base, pillar).fillet(2.0)
    """
    bb_a = to_shape(part_a).BoundingBox()
    bb_b = to_shape(part_b).BoundingBox()
    
    xmin = max(bb_a.xmin, bb_b.xmin) - tolerance
    xmax = min(bb_a.xmax, bb_b.xmax) + tolerance
    ymin = max(bb_a.ymin, bb_b.ymin) - tolerance
    ymax = min(bb_a.ymax, bb_b.ymax) + tolerance
    zmin = max(bb_a.zmin, bb_b.zmin) - tolerance
    zmax = min(bb_a.zmax, bb_b.zmax) + tolerance
    
    box_sel = cq.selectors.BoxSelector((xmin, ymin, zmin), (xmax, ymax, zmax))
    wp = to_workplane(fused_model)
    return wp.edges(box_sel)


class CustomSelector(cq.Selector):
    """Filter edges, faces, or vertices using an arbitrary Python predicate function."""
    def __init__(self, predicate):
        self.predicate = predicate
        
    def filter(self, object_list):
        return [obj for obj in object_list if self.predicate(obj)]
