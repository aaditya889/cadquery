import cadquery as cq
from cadquery import exporters
from ocp_vscode import show_object
import os, sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)
from lib.hollow import *

multiplier = 1
drone_base_length_mm = 150 * multiplier
drone_base_thickness_mm = 10 * multiplier
drone_base_leg_width_mm = 15 * multiplier
drone_base_cut_offset = (drone_base_length_mm/4 + drone_base_leg_width_mm) * multiplier
drone_base_motor_cut_offset = (drone_base_length_mm/2) * multiplier

drone_base_battery_pillar_offset = drone_base_leg_width_mm * multiplier
drone_base_battery_pillar_radius_mm = 0 * multiplier
drone_base_battery_pillar_height_mm = 0 * multiplier

pcb_holder_plate_length_mm = 95 * multiplier
pcb_holder_plate_width_mm = 80 * multiplier

battery_holder_thickness_mm = 4 * multiplier
battery_holder_length_mm = (118 + battery_holder_thickness_mm) * multiplier
battery_holder_width_mm = (50 + battery_holder_thickness_mm) * multiplier
battery_holder_height_mm = (30 + battery_holder_thickness_mm) * multiplier

motor_base_thickness_mm = 3.5 * multiplier
motor_base_radius_mm = 28/2 * multiplier
motor_screw_radius_mm = 1.4 * multiplier
motor_shaft_radius_mm = 4 * multiplier
motor_holder_height_mm = (drone_base_thickness_mm - motor_base_thickness_mm) * multiplier
motor_holder_wire_pocket_length_mm = 6.5
motor_screw_distance_from_center_mm = 8 * multiplier
motor_screw_coordinates = [(0, motor_screw_distance_from_center_mm), 
                           (motor_screw_distance_from_center_mm + 1, 0), 
                           (-motor_screw_distance_from_center_mm - 1, 0), 
                           (0, -motor_screw_distance_from_center_mm)]

drone_base = cq.Workplane("XY").box(drone_base_length_mm, drone_base_length_mm, drone_base_thickness_mm)
drone_base = drone_base.faces(">Z").pushPoints([(drone_base_cut_offset, drone_base_cut_offset), (-drone_base_cut_offset, drone_base_cut_offset), (drone_base_cut_offset, -drone_base_cut_offset), (-drone_base_cut_offset, -drone_base_cut_offset)]).rect(drone_base_length_mm/2, drone_base_length_mm/2).cutThruAll()
drone_base = drone_base.faces(">Z").pushPoints([(0, drone_base_motor_cut_offset), (-drone_base_motor_cut_offset, 0), (drone_base_motor_cut_offset, 0), (0, -drone_base_motor_cut_offset)]).circle(motor_base_radius_mm + motor_base_thickness_mm).cutThruAll()
drone_base = drone_base.faces(">Z").pushPoints([(0, 0, -drone_base_thickness_mm/2)]).rect(pcb_holder_plate_length_mm, pcb_holder_plate_width_mm).extrude(drone_base_thickness_mm)
# drone_base = drone_base.faces("<Z").pushPoints([(drone_base_battery_pillar_offset, drone_base_battery_pillar_offset, -drone_base_thickness_mm/2), (drone_base_battery_pillar_offset, -drone_base_battery_pillar_offset, -drone_base_thickness_mm/2), (-drone_base_battery_pillar_offset, drone_base_battery_pillar_offset, -drone_base_thickness_mm/2), (-drone_base_battery_pillar_offset, -drone_base_battery_pillar_offset, -drone_base_thickness_mm/2)]).circle(drone_base_battery_pillar_radius_mm).extrude(-drone_base_battery_pillar_height_mm)

motor_holder = cq.Workplane("XY").circle(motor_base_radius_mm + motor_base_thickness_mm).center(0, 0).extrude(motor_base_thickness_mm)
motor_holder = motor_holder.pushPoints([motor_screw_coordinates[0], motor_screw_coordinates[1], motor_screw_coordinates[2], motor_screw_coordinates[3]]).circle(motor_screw_radius_mm).cutThruAll()
motor_holder = motor_holder.pushPoints([(0, 0)]).circle(motor_shaft_radius_mm).cutThruAll()
motor_holder = motor_holder.faces(">Z").circle(motor_base_radius_mm + motor_base_thickness_mm).circle(motor_base_radius_mm).extrude(motor_holder_height_mm)
wire_pocket = cq.Workplane("YZ", origin=cq.Vector(motor_base_radius_mm + motor_base_thickness_mm/2, 0, 0)).box(motor_holder_wire_pocket_length_mm, motor_holder_height_mm + motor_base_thickness_mm + drone_base_thickness_mm, motor_base_thickness_mm + 1.5)
motor_holder = motor_holder.cut(wire_pocket)


battery_holder = create_hollow_box_with_two_open_faces(battery_holder_length_mm, battery_holder_width_mm, battery_holder_height_mm, battery_holder_thickness_mm)

assembled_drone = cq.Assembly()
assembled_drone.add(drone_base, loc=(cq.Location(cq.Vector((0, 0, 0)))), color=cq.Color("blue"), name="drone_base")
assembled_drone.add(motor_holder.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), -90), loc=cq.Location(cq.Vector((drone_base_length_mm/2, 0, -drone_base_thickness_mm/2))), color=cq.Color("red"), name="motor_holder_1")
assembled_drone.add(motor_holder, loc=cq.Location(cq.Vector((0, drone_base_length_mm/2, -drone_base_thickness_mm/2))), color=cq.Color("red"), name="motor_holder_2")
assembled_drone.add(motor_holder.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 180), loc=cq.Location(cq.Vector((0, -drone_base_length_mm/2, -drone_base_thickness_mm/2))), color=cq.Color("red"), name="motor_holder_3")
assembled_drone.add(motor_holder.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 90), loc=cq.Location(cq.Vector((-drone_base_length_mm/2, 0, -drone_base_thickness_mm/2))), color=cq.Color("red"), name="motor_holder_4")
assembled_drone.add(battery_holder, loc=cq.Location(cq.Vector((0, 0, -(drone_base_thickness_mm/2 + drone_base_battery_pillar_height_mm + battery_holder_height_mm/2)))), color=cq.Color("green"), name="battery_holder")

show_object(assembled_drone)

# exporters.export(motor_holder, "export/new_drone.stl")
# assembled_drone.export("export/new_drone.stl", "STL")