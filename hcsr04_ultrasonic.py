import cadquery as cq
from cq_server.ui import ui, show_object, debug

chip_length = 45.2
chip_width = 20.2
chip_thickness = 1.6
mic_diameter = 16.0
mic_separation = 10.1
mic_pov_diameter = 12.5
mic_height = 12.4
overall_thickness = 2.0

chip_case = cq.Workplane("XY").box(chip_length, chip_width, chip_thickness)
mic_case = cq.Workplane("XY").workplane().pushPoints([((mic_separation + mic_diameter)/2, 0), (-((mic_separation + mic_diameter)/2), 0)]).circle((mic_diameter / 2) + overall_thickness).circle(mic_diameter / 2).extrude(mic_height).faces(">Z").workplane().pushPoints([((mic_separation + mic_diameter)/2, 0), (-((mic_separation + mic_diameter)/2), 0)]).circle((mic_pov_diameter / 2)).circle((mic_diameter / 2) + overall_thickness).extrude(overall_thickness)
# chip_case = chip_case.faces(">Z").add(mic_case)

result = (
  cq.Workplane("XY")
    .box(chip_length, chip_width, chip_thickness)
    .faces(">Z").workplane().pushPoints([((mic_separation + mic_diameter)/2, 0), (-((mic_separation + mic_diameter)/2), 0)]).circle((mic_diameter / 2) + overall_thickness).circle(mic_diameter / 2).extrude(mic_height).faces(">Z").workplane().pushPoints([((mic_separation + mic_diameter)/2, 0), (-((mic_separation + mic_diameter)/2), 0)]).circle((mic_pov_diameter / 2)).circle((mic_diameter / 2) + overall_thickness).extrude(overall_thickness)
    # .vertices().end().vertices().end().vertices().end().vertices().end().vertices().end().vertices().end().circle(0.1).extrude(20)
    
    
)
# result = cq.Workplane("XY").box(1, 2, 3).faces(">Z").vertices().circle(0.5).cutThruAll()


# show_object(result)
# debug(chip_case.add(mic_case))
show_object(chip_case)

