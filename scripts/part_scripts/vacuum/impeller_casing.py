from ocp_vscode import show_object
import cadquery as cq
import math

overall_thickness = 2
main_casing_radius_mm = 10
main_casing_width_mm = 10
sucker_tube_radius_mm = 5
sucker_hole_radius_mm = 4
sucker_tube_length_mm = 20
outhole_tube_radius_mm = 5
outhole_tube_length_mm = 20
outhole_hole_radius_mm = 4
motor_hole_radius_mm = 3

# main_casing_hole = cq.Workplane("XY").circle(5, forConstruction=True)
main_casing = cq.Workplane("XY").circle(main_casing_radius_mm).circle(main_casing_radius_mm-overall_thickness).extrude(main_casing_width_mm)
main_casing_cover = cq.Workplane("XY", (0, 0, main_casing_width_mm)).circle(main_casing_radius_mm).extrude(overall_thickness).faces(">Z").circle(sucker_tube_radius_mm).cutThruAll()
main_casing_l_cover = cq.Workplane("XY", (0, 0, -overall_thickness)).circle(main_casing_radius_mm).extrude(overall_thickness).faces(">Z").circle(motor_hole_radius_mm).cutThruAll()
sucker_tube = cq.Workplane("XY", (0, 0, main_casing_width_mm + overall_thickness)).circle(sucker_tube_radius_mm).circle(sucker_hole_radius_mm).extrude(sucker_tube_length_mm)
outhole_tube = cq.Workplane("YZ", (main_casing_radius_mm - overall_thickness - 1, 0, main_casing_width_mm/2)).circle(outhole_tube_radius_mm).extrude(outhole_tube_length_mm)
main_casing = main_casing.cut(outhole_tube)
outhole_tube = outhole_tube.circle(outhole_hole_radius_mm).cutThruAll()
# sucker = cq.Workplane("XY", (0, 0, 9)).circle(5).extrude(20).faces(">Z").circle(4).cutThruAll()


assembled_casing = cq.Assembly()
assembled_casing.add(main_casing, color=cq.Color(1, 0, 0), name="main_casing")
assembled_casing.add(main_casing_cover, color=cq.Color(0, 1, 0), name="main_casing_cover")
assembled_casing.add(main_casing_l_cover, color=cq.Color(1, 0.5, 0), name="main_casing_l_cover")
assembled_casing.add(sucker_tube, color=cq.Color(0, 0, 1), name="sucker_tube")
assembled_casing.add(outhole_tube, color=cq.Color(0, 1, 1), name="outhole_tube")

assembled_casing.export('./export/impeller_casing.stl')
# main_casing = main_casing.add(sucker)
show_object(assembled_casing)