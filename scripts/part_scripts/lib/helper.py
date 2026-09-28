import cadquery as cq

def _get_shape(obj):
  """Safely extract the CAD shape from Workplane, Assembly, Compound, or Solid."""
  if hasattr(obj, "toCompound"):
    return obj.toCompound()
  if hasattr(obj, "val"):
    return obj.val()
  return obj


def find_junction_edges(fused_model, part_a, part_b, tolerance=0.5):
  """
  Selects only the seam edges formed where part_a and part_b touch/intersect.
  """
  bb_a = _get_shape(part_a).BoundingBox()
  bb_b = _get_shape(part_b).BoundingBox()  
  # Calculate the overlapping 3D contact region
  xmin = max(bb_a.xmin, bb_b.xmin) - tolerance
  xmax = min(bb_a.xmax, bb_b.xmax) + tolerance
  ymin = max(bb_a.ymin, bb_b.ymin) - tolerance
  ymax = min(bb_a.ymax, bb_b.ymax) + tolerance
  zmin = max(bb_a.zmin, bb_b.zmin) - tolerance
  zmax = min(bb_a.zmax, bb_b.zmax) + tolerance
  
  # Select edges located inside that contact zone
  box_sel = cq.selectors.BoxSelector((xmin, ymin, zmin), (xmax, ymax, zmax))
  return fused_model.edges(box_sel)

def duplicate(obj):
  """
  Creates a deep copy of any CadQuery object (Workplane, Compound, Solid, Assembly)
  and returns an editable Workplane.
  """
  if isinstance(obj, cq.Workplane):
    return cq.Workplane(obj=obj.val().copy())
  if hasattr(obj, "toCompound"):   # Assembly
    return cq.Workplane(obj=obj.toCompound().copy())
  if hasattr(obj, "copy"):         # Compound or Solid
    return cq.Workplane(obj=obj.copy())
  return obj
