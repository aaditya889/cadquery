import cadquery as cq

def create_hollow_box(length, width, height, thickness, workplane="XY"):
  main_box = cq.Workplane(workplane).box(length, width, height)
  cavity_box = cq.Workplane(workplane).box(length - thickness, width - thickness, height - thickness)
  hollow_box = main_box.cut(cavity_box)
  return hollow_box


def create_hollow_box_with_open_face(length, width, height, thickness, workplane="XY"):
  main_box = cq.Workplane(workplane).box(length + thickness*2, width + thickness*2, height + thickness*2)
  cavity_box = cq.Workplane(workplane).box(length, width, height)
  hollow_box = main_box.cut(cavity_box)
  hollow_box = hollow_box.faces(">Z").rect(length, width).cutBlind(-thickness)
  return hollow_box


def create_hollow_box_with_two_open_faces(length, width, height, thickness, workplane="XY"):
  main_box = cq.Workplane(workplane).box(length + thickness*2, width + thickness*2, height + thickness*2)
  cavity_box = cq.Workplane(workplane).box(length, width, height)
  hollow_box = main_box.cut(cavity_box)
  hollow_box = hollow_box.faces("<X").rect(2*thickness, width + thickness/2).cutThruAll()
  hollow_box = hollow_box.faces(">X").rect(2*thickness, width + thickness/2).cutThruAll()
  return hollow_box

def create_hollow_cylinder_with_two_open_faces(radius, height, thickness, workplane="XY"):
  main_cylinder = cq.Workplane(workplane).cylinder(height, radius + thickness)
  main_cylinder = main_cylinder.workplane().circle(radius).cutThruAll()
  # hollow_box = main_cylinder.cutThruAll()
  # hollow_box = hollow_box.faces("<X").rect(2*thickness, width + thickness/2).cutThruAll()
  # hollow_box = hollow_box.faces(">X").rect(2*thickness, width + thickness/2).cutThruAll()
  return main_cylinder