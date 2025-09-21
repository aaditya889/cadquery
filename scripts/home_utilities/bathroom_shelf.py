import cadquery as cq
from ocp_vscode import show_object

length = 45.2
width = 20.2
thickness = 1.6
overall_thickness = 2.0

body = cq.Workplane("XY").box(length, width, thickness)

# chip_case = chip_case.faces(">Z").add(mic_case)
assembled = cq.Assembly()

assembled.add(body, color=cq.Color(1, 0, 0), name="chip_case")
# result = cq.Workplane("XY").box(1, 2, 3).faces(">Z").vertices().circle(0.5).cutThruAll()


# show_object(result)
# debug(chip_case.add(mic_case))
# show_object(result)
show_object(assembled)
