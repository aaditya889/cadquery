from ocp_vscode import show_object
import cadquery as cq
import math

motor_shaft_radius_mm = 2.39
motor_shaft_length_mm = 16.2
impeller_shaft_radius_mm = 10.05
impeller_shaft_length_mm = 20
impeller_attachment_disk_radius_mm = 29.5/2
impeller_attachment_disk_screw_position_radius_mm = 21.2
overall_thickness_mm = 2
screw_hole_radius_mm = 1


# sucker = cq.Workplane("XY", (0, 0, 9)).circle(5).extrude(20).faces(">Z").circle(4).cutThruAll()
impeller_attachment_disk = cq.Workplane("XY").circle(impeller_attachment_disk_radius_mm).extrude(overall_thickness_mm)
impeller_attachment_disk = impeller_attachment_disk.faces(">Z").polygon(6, impeller_attachment_disk_screw_position_radius_mm).vertices().cboreHole(screw_hole_radius_mm, screw_hole_radius_mm*1.7, screw_hole_radius_mm*0.5)
impeller_shaft = cq.Workplane("YX").circle(impeller_shaft_radius_mm).extrude(impeller_shaft_length_mm)
motor_shaft = cq.Workplane("XY").circle(motor_shaft_radius_mm + overall_thickness_mm*3).extrude(motor_shaft_length_mm).circle(motor_shaft_radius_mm).cutThruAll()

assembled_coupler = cq.Assembly()

assembled_coupler.add(impeller_attachment_disk, color=cq.Color(1, 0, 0), name="assembled_coupler")
assembled_coupler.add(impeller_shaft, color=cq.Color(0, 1, 0), name="impeller_shaft")
assembled_coupler.add(motor_shaft, loc=cq.Location(0, 0, overall_thickness_mm), color=cq.Color(0, 0, 1), name="motor_shaft")
# assembled_casing.add(main_casing, color=cq.Color(1, 0, 0), name="main_casing")
# assembled_casing.add(main_casing_cover, color=cq.Color(0, 1, 0), name="main_casing_cover")
# assembled_casing.add(main_casing_l_cover, color=cq.Color(1, 0.5, 0), name="main_casing_l_cover")
# assembled_casing.add(sucker_tube, color=cq.Color(0, 0, 1), name="sucker_tube")
# assembled_casing.add(outhole_tube, color=cq.Color(0, 1, 1), name="outhole_tube")

assembled_coupler.export('./export/impeller_motor_coupler.stl')
# main_casing = main_casing.add(sucker)
show_object(assembled_coupler)