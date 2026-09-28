import cadquery as cq

hinge_radius = 20.0
hinge_thickness = 8.0
thickness = hinge_thickness
radius = hinge_radius

# Base cylinder
disc = cq.Workplane("XY").cylinder(thickness, radius)

rotated_disc = (
    disc
    .rotate((0, 0, 0), (1, 0, 0), 90)
    .translate((0, 0, hinge_radius))
)

# Support 1 (My current broken one)
support1 = (
    cq.Workplane("XY")
    .box(hinge_radius, hinge_thickness / 2.0, hinge_radius, centered=(True, False, False))
    .translate((0, -hinge_thickness / 2.0, 0))
)

# Support 2 (The fixed one)
support2 = (
    cq.Workplane("XY")
    .box(hinge_radius, hinge_thickness / 2.0, hinge_radius, centered=(True, False, False))
    .translate((0, 0, 0))
)

print(f"Disc Y bounds: {rotated_disc.val().BoundingBox().ymin} to {rotated_disc.val().BoundingBox().ymax}")
print(f"Support1 Y bounds: {support1.val().BoundingBox().ymin} to {support1.val().BoundingBox().ymax}")
print(f"Support2 Y bounds: {support2.val().BoundingBox().ymin} to {support2.val().BoundingBox().ymax}")

