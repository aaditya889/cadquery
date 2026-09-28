import cadquery as cq

def create_semicircular_ring(ring_radius_int, ring_radius_ext, ring_thickness):
  semi_ring = cq.Workplane("XY").workplane().pushPoints([(-ring_radius_ext, 0)]).radiusArc(cq.Vector(ring_radius_ext, 0), ring_radius_ext).pushPoints([(-ring_radius_int, 0)]).radiusArc(cq.Vector(ring_radius_int, 0), ring_radius_int).lineTo(ring_radius_ext, 0).pushPoints([(-ring_radius_int, 0)]).lineTo(-ring_radius_ext, 0).close().extrude(ring_thickness)

  return semi_ring