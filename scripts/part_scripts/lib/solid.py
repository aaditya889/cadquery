import cadquery as cq


def create_solid_box(length, width, height, workplane="XY", origin=(0, 0, 0), centered=True):
  origin = cq.Vector(origin)
  main_box = cq.Workplane(workplane).box(length, width, height, centered=centered).translate(origin)
  return main_box


def create_solid_cylinder(radius, height, workplane="XY"):
  main_cylinder = cq.Workplane(workplane).cylinder(height, radius)
  return main_cylinder


def create_solid_triangle(side1, side2, angle, workplane="XY"):
  triangle = cq.Workplane(workplane)


# assy = AssembledPart(y_assembled)
# x_assembled = assy.clone_and_rotate(axis="Z", angle=90)
# y_assembled.add(x_assembled, name="x_assembled")
# for i in test_ass.objects.values():
#   if (not i.name.startswith("y")):
#     continue
#   print(i.name)
#   i.loc *= rotation_vector
# x_assembled = y_assembled.toCompound().rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 90).translate(cq.Vector(0, 0, -(drone_width + error_margin/2)))
# y_assembled = y_assembled.add(x_assembled, name="x_assembled", color="red")