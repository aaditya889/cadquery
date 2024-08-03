import cadquery as cq
# from cadquery import show_object
from ocp_vscode import show_object, reset_show, set_defaults

height = 60.0
width = 80.0
thickness = 10.0
diameter = 22.0
padding = 12.0

# make the base
# result = (
#     cq.Workplane("XY")
#     .box(height, width, thickness)
#     .faces(">Z")
#     .workplane()
#     .hole(diameter)
#     .faces(">Z")
#     .workplane()
#     .rect(height - padding, width - padding, forConstruction=True)
#     .vertices()
#     .cboreHole(2.4, 4.4, 2.1)
#     .edges("|Z")
#     .fillet(2.0)
# )
result = cq.importers.importStep('./Pelvis.STEP')
# Render the solid
show_object(result)

# Export
# cq.exporters.export(result, "result.stl")
# cq.exporters.export(result.section(), "result.dxf")
# cq.exporters.export(result, "result.step")