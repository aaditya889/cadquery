import cadquery as cq
from cq_server.ui import ui, show_object, debug

chip_length = 46.2
chip_width = 21.5
chip_thickness = 3.0
mic_diameter = 16.5
mic_separation = 10.1
mic_pov_diameter = 13.0
mic_height = 12.4
overall_thickness = 1.8
crystal_length = 10.3
crystal_width = 4.0
crystal_height = 4.0
crystal_y_placement = 15.6 - chip_width/2 + crystal_width/2

chip_case = (cq.Workplane("XY")
              .box(chip_length + overall_thickness, chip_width + overall_thickness, chip_thickness + overall_thickness)
              .faces("<Z").workplane()
              .rect(chip_length, chip_width)
              .cutBlind(until=-chip_thickness, both=False)
              .faces("<Z[-2]").workplane()
              .pushPoints([((mic_separation + mic_diameter)/2, 0), (-((mic_separation + mic_diameter)/2), 0)])
              .circle((mic_diameter / 2))
              .cutBlind(-overall_thickness, both=False)
              .faces("<Z[-2]").workplane(origin=(0, crystal_y_placement))
              .rect(crystal_length, crystal_width)
              .cutBlind(-overall_thickness, both=False)
            )
mic_case = (cq.Workplane("XY").workplane()
            .pushPoints([((mic_separation + mic_diameter)/2, 0), (-((mic_separation + mic_diameter)/2), 0)])
            .circle((mic_diameter / 2) + overall_thickness)
            .circle(mic_diameter / 2)
            .extrude(mic_height - overall_thickness)
            .faces(">Z").workplane()
            .pushPoints([((mic_separation + mic_diameter)/2, 0), (-((mic_separation + mic_diameter)/2), 0)])
            .circle((mic_pov_diameter / 2))
            .circle((mic_diameter / 2) + overall_thickness)
            .extrude(overall_thickness)
          )

crystal_case = (cq.Workplane("XY")
                .box(crystal_length + overall_thickness, crystal_width + overall_thickness, crystal_height)
                .faces("<Z").workplane()
                .rect(crystal_length, crystal_width)
                .cutBlind(-crystal_height + overall_thickness, both=False)
              )


hcrs204_case = (cq.Assembly(name="hcrs204")
                .add(mic_case, loc=cq.Location((0, 0, (chip_thickness + overall_thickness)/2)), name="mic_case")
                .add(crystal_case, loc=cq.Location((0, crystal_y_placement, ((crystal_height)/2 + (chip_thickness + overall_thickness)/2))), name="crystal_case")
                .add(chip_case, name="chip_case")
              )

show_object(hcrs204_case, name='hcrs204_2', options={'color': 'pink'})
hcrs204_case.save("hcrs204_case.stl")
# show_object(chip_case, name='hcrs204', options={'color': 'pink'})

