import cadquery as cq
# from cadquery import show_object
from ocp_vscode import show_object, reset_show, set_defaults


height = 60.0
width = 80.0
thickness = 10.0
diameter = 22.0

# make the base
result = (
    cq.Workplane("XY")
    .box(height, width, thickness)
    .faces(">Z")
    .workplane()
    .hole(diameter)
)

# Render the solid
show_object(result)
