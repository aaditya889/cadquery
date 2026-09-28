import cadquery as cq
from ocp_vscode import show_object

base_radius_mm = 100
base_thickness_mm = 10
wheel_cut_radius_mm = 10
roomba_shell_height_mm = 70
wheel_origin = (0, 10)
front_wheel_coordinates = (wheel_origin[0], wheel_origin[1] + 0.6 * base_radius_mm)
rear_wheel_displacement_from_center = d = 0.3 * base_radius_mm
rear_wheel_1_coordinates = (wheel_origin[0]-0.5*((base_radius_mm**2 - d**2)**(1/2)) , wheel_origin[1] - d)
rear_wheel_2_coordinates = (wheel_origin[0] + 0.5*((base_radius_mm**2 - d**2)**(1/2)) , wheel_origin[1] - d)


roomba_base = cq.Workplane("XY").circle(base_radius_mm).center(0, 0).extrude(base_thickness_mm)
roomba_base = roomba_base.pushPoints([front_wheel_coordinates, rear_wheel_1_coordinates, rear_wheel_2_coordinates]).circle(wheel_cut_radius_mm).cutThruAll()
roomba_base = roomba_base.faces(">Z").circle(base_radius_mm).circle(base_radius_mm - base_thickness_mm).extrude(roomba_shell_height_mm)
# mic_case = cq.Workplane("XY", (0, 0, (chip_thickness)/2)).workplane().pushPoints([((mic_separation + mic_diameter)/2, 0), (-((mic_separation + mic_diameter)/2), 0)]).circle((mic_diameter / 2) + overall_thickness).circle(mic_diameter / 2).extrude(mic_height).faces(">Z").workplane().pushPoints([((mic_separation + mic_diameter)/2, 0), (-((mic_separation + mic_diameter)/2), 0)]).circle((mic_pov_diameter / 2)).circle((mic_diameter / 2) + overall_thickness).extrude(overall_thickness)

# chip_case = chip_case.faces(">Z").add(mic_case)
# assembled_chip = cq.Assembly()

# result = (
#   cq.Workplane("XY")
#     .box(chip_length, chip_width, chip_thickness)
#     .faces(">Z").workplane().pushPoints([((mic_separation + mic_diameter)/2, 0), (-((mic_separation + mic_diameter)/2), 0)]).circle((mic_diameter / 2) + overall_thickness).circle(mic_diameter / 2).extrude(mic_height).faces(">Z").workplane().pushPoints([((mic_separation + mic_diameter)/2, 0), (-((mic_separation + mic_diameter)/2), 0)]).circle((mic_pov_diameter / 2)).circle((mic_diameter / 2) + overall_thickness).extrude(overall_thickness)
#     # .vertices().end().vertices().end().vertices().end().vertices().end().vertices().end().vertices().end().circle(0.1).extrude(20)   
# )

# assembled_chip.add(chip_case, color=cq.Color(1, 0, 0), name="chip_case")
# assembled_chip.add(mic_case, color=cq.Color(0, 1, 0), name="mic_case")
# result = cq.Workplane("XY").box(1, 2, 3).faces(">Z").vertices().circle(0.5).cutThruAll()


# show_object(result)
# debug(chip_case.add(mic_case))
# show_object(result)
show_object(roomba_base)
