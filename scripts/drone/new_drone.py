import cadquery as cq
from cadquery import exporters
from ocp_vscode import show_object
import os, sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)
from lib.hollow import *

# LENGTHS ARE IN MM (remove mm from the variables now!)
multiplier = 1
drone_base_length_mm = 230 * multiplier
drone_base_thickness_mm = 10 * multiplier
drone_base_leg_width_mm = 15 * multiplier
drone_base_cut_offset = (drone_base_length_mm/4 + drone_base_leg_width_mm) * multiplier
drone_base_motor_cut_offset = (drone_base_length_mm/2) * multiplier

drone_base_battery_pillar_offset = drone_base_leg_width_mm * multiplier
drone_base_battery_pillar_radius_mm = 0 * multiplier
drone_base_battery_pillar_height_mm = 0 * multiplier

pcb_holder_plate_length_mm = 100 * multiplier
pcb_holder_plate_width_mm = 80 * multiplier
pcb_holder_height = 20
pcb_holder_thickness = 2

battery_holder_thickness_mm = 4 * multiplier
battery_holder_length_mm = (140) * multiplier
battery_holder_width_mm = (50) * multiplier
battery_holder_height_mm = (32) * multiplier

motor_base_thickness_mm = 4 * multiplier
motor_base_radius_mm = 29/2 * multiplier
motor_screw_radius_mm = 1.4 * multiplier
motor_shaft_radius_mm = 4 * multiplier
motor_holder_height_mm = (drone_base_thickness_mm - motor_base_thickness_mm) * multiplier
motor_holder_wire_pocket_length_mm = 15
motor_screw_distance_from_center_mm = 8 * multiplier
motor_screw_coordinates = [(0, motor_screw_distance_from_center_mm), 
                           (motor_screw_distance_from_center_mm + 1, 0), 
                           (-motor_screw_distance_from_center_mm - 1, 0), 
                           (0, -motor_screw_distance_from_center_mm)]

esc_length = 57
esc_width = 32
esc_height =13
esc_holder_thickness = 2 * multiplier
esc_connector_wire_hole_radius = 7

switch_length = 21
switch_width = 15
switch_height = 11
switch_holder_thickness = 1
switch_pin_1_distance = 2
switch_pin_2_distance = 9
switch_pin_thickness = 1
switch_pin_width = 5.5

drone_base = cq.Workplane("XY").box(drone_base_length_mm, drone_base_length_mm, drone_base_thickness_mm)
drone_base = drone_base.faces(">Z").pushPoints([(drone_base_cut_offset, drone_base_cut_offset), (-drone_base_cut_offset, drone_base_cut_offset), (drone_base_cut_offset, -drone_base_cut_offset), (-drone_base_cut_offset, -drone_base_cut_offset)]).rect(drone_base_length_mm/2, drone_base_length_mm/2).cutThruAll()
drone_base = drone_base.faces(">Z").pushPoints([(0, drone_base_motor_cut_offset), (-drone_base_motor_cut_offset, 0), (drone_base_motor_cut_offset, 0), (0, -drone_base_motor_cut_offset)]).circle(motor_base_radius_mm + motor_base_thickness_mm).cutThruAll()
drone_base = drone_base.faces(">Z").pushPoints([(0, 0, -drone_base_thickness_mm/2)]).rect(pcb_holder_plate_length_mm, pcb_holder_plate_width_mm).extrude(drone_base_thickness_mm)
# drone_base = drone_base.faces("<Z").pushPoints([(drone_base_battery_pillar_offset, drone_base_battery_pillar_offset, -drone_base_thickness_mm/2), (drone_base_battery_pillar_offset, -drone_base_battery_pillar_offset, -drone_base_thickness_mm/2), (-drone_base_battery_pillar_offset, drone_base_battery_pillar_offset, -drone_base_thickness_mm/2), (-drone_base_battery_pillar_offset, -drone_base_battery_pillar_offset, -drone_base_thickness_mm/2)]).circle(drone_base_battery_pillar_radius_mm).extrude(-drone_base_battery_pillar_height_mm)

motor_holder = cq.Workplane("XY").circle(motor_base_radius_mm + motor_base_thickness_mm).center(0, 0).extrude(motor_base_thickness_mm)
motor_holder = motor_holder.pushPoints([motor_screw_coordinates[0], motor_screw_coordinates[1], motor_screw_coordinates[2], motor_screw_coordinates[3]]).circle(motor_screw_radius_mm).cutThruAll()
motor_holder = motor_holder.pushPoints([(0, 0)]).circle(motor_shaft_radius_mm).cutThruAll()
motor_holder = motor_holder.faces(">Z").circle(motor_base_radius_mm + motor_base_thickness_mm).circle(motor_base_radius_mm).extrude(motor_holder_height_mm)
# wire_pocket = cq.Workplane("YZ", origin=cq.Vector(motor_base_radius_mm + motor_base_thickness_mm/2, 0, 0)).box(motor_holder_wire_pocket_length_mm, motor_holder_height_mm + motor_base_thickness_mm + drone_base_thickness_mm, motor_base_thickness_mm + 1.5)
wire_pocket = cq.Workplane("YZ", origin=cq.Vector(motor_base_radius_mm + motor_base_thickness_mm, 0,  motor_holder_height_mm + motor_base_thickness_mm/2)).box(motor_holder_wire_pocket_length_mm, motor_holder_height_mm + motor_base_thickness_mm, motor_base_thickness_mm + drone_base_thickness_mm)
wire_pocket = wire_pocket.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 135)
motor_holder = motor_holder.cut(wire_pocket)

battery_holder = create_hollow_box_with_two_open_faces(battery_holder_length_mm, battery_holder_width_mm, battery_holder_height_mm, battery_holder_thickness_mm)
battery_holder = battery_holder.faces(">Y").workplane(origin=cq.Vector(0, 0, battery_holder_height_mm/4)).circle(esc_connector_wire_hole_radius).cutBlind(-battery_holder_thickness_mm)
battery_holder = battery_holder.faces("<Y").workplane().circle(esc_connector_wire_hole_radius).cutBlind(-battery_holder_thickness_mm)
battery_holder.faces("<<Z").tag("batteryHolderBottom").end()
battery_holder.faces(">>Z").tag("batteryHolderRoof").end()
# battery_holder = battery_holder.translate(cq.Vector((0, 0, -(drone_base_thickness_mm/2 + drone_base_battery_pillar_height_mm + battery_holder_height_mm/2))))

esc_holder = create_hollow_box_with_two_open_faces(esc_length, esc_width, esc_height, esc_holder_thickness).rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 90)

switch_location = cq.Vector((pcb_holder_plate_length_mm + switch_length + switch_holder_thickness)/2, (drone_base_leg_width_mm*2 + switch_width + switch_holder_thickness)/2, (drone_base_thickness_mm/2 - battery_holder_thickness_mm - 2*switch_holder_thickness))
switch_holder = create_hollow_box_with_open_face(switch_length, switch_width, switch_height, switch_holder_thickness)
switch_pin_1_location = cq.Vector(-switch_length/2 + switch_pin_1_distance, 0, 0)
switch_pin_2_location = cq.Vector(-switch_length/2 + switch_pin_2_distance, 0, 0)
switch_holder = switch_holder.faces(">Z").workplane(origin=switch_pin_1_location).rect(switch_pin_thickness, switch_pin_width).cutThruAll()
switch_holder = switch_holder.faces(">Z").workplane(origin=switch_pin_2_location).rect(switch_pin_thickness, switch_pin_width).cutThruAll()
# switch_holder = switch_holder.translate(switch_location)
switch_holder.edges("<X and >Y").tag("switchHolderFrontEdge").end()
switch_holder.edges("<X and <Z").tag("switchHolderBottomEdge").end()
switch_holder.vertices("<X and >Z and >Y").tag("switchHolderTopRightVertex").end()

drone_base = drone_base.cut(switch_holder)
battery_holder = battery_holder.cut(switch_holder)
battery_holder = battery_holder.faces(">Z").workplane(origin=cq.Vector((pcb_holder_plate_length_mm + switch_length + switch_holder_thickness)/2, (drone_base_leg_width_mm*2 + switch_width + switch_holder_thickness)/2, (drone_base_thickness_mm/2))).rect(switch_length + switch_holder_thickness, switch_width + switch_holder_thickness).cutBlind(-battery_holder_thickness_mm)


_pcb_holder_cut = cq.Workplane("XY").box(pcb_holder_plate_length_mm, pcb_holder_plate_width_mm, pcb_holder_height).translate(cq.Vector(0, 0, -(pcb_holder_height - pcb_holder_thickness - drone_base_thickness_mm)/2))
pcb_holder = create_hollow_box_with_open_face(pcb_holder_plate_length_mm, pcb_holder_plate_width_mm, pcb_holder_height, pcb_holder_thickness).translate(cq.Vector(0, 0, -(pcb_holder_height - pcb_holder_thickness - drone_base_thickness_mm)/2))
drone_base = drone_base.cut(_pcb_holder_cut)
pcb_holder.edges(">X and >Y").tag("pcbHolderFrontEdge").end()
pcb_holder.edges(">X and <Z").tag("pcbHolderBottomEdge").end()
pcb_holder.vertices(">X and >Z and >Y").tag("pcbHolderTopRightVertex").end()
# battery_holder = battery_holder.cut(_pcb_holder_cut)
# esc_holder = esc_holder.cut(_pcb_holder_cut)

assembled_drone = cq.Assembly()
assembled_drone.add(drone_base, loc=(cq.Location(cq.Vector((0, 0, 0)))), color=cq.Color("blue"), name="drone_base")
assembled_drone.add(motor_holder.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), -90), loc=cq.Location(cq.Vector((drone_base_length_mm/2, 0, -drone_base_thickness_mm/2))), color=cq.Color("red"), name="motor_holder_1")
assembled_drone.add(motor_holder, loc=cq.Location(cq.Vector((0, drone_base_length_mm/2, -drone_base_thickness_mm/2))), color=cq.Color("red"), name="motor_holder_2")
assembled_drone.add(motor_holder.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 180), loc=cq.Location(cq.Vector((0, -drone_base_length_mm/2, -drone_base_thickness_mm/2))), color=cq.Color("red"), name="motor_holder_3")
assembled_drone.add(motor_holder.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 90), loc=cq.Location(cq.Vector((-drone_base_length_mm/2, 0, -drone_base_thickness_mm/2))), color=cq.Color("red"), name="motor_holder_4")
# assembled_drone.add(battery_holder, color=cq.Color("green"), name="battery_holder")

# assembled_drone.add(esc_holder, loc=cq.Location(cq.Vector((battery_holder_length_mm/2 - esc_length/2, -(battery_holder_width_mm + battery_holder_thickness_mm + esc_height + 2 * esc_holder_thickness)/2, -(drone_base_thickness_mm/2 + drone_base_battery_pillar_height_mm + battery_holder_height_mm/2 + esc_holder_thickness)))), color=cq.Color("yellow"), name="esc_holder_1")
# assembled_drone.add(esc_holder, loc=cq.Location(cq.Vector((-(battery_holder_length_mm/2 - esc_length/2), -(battery_holder_width_mm + battery_holder_thickness_mm + esc_height + 2 * esc_holder_thickness)/2, -(drone_base_thickness_mm/2 + drone_base_battery_pillar_height_mm + battery_holder_height_mm/2 + esc_holder_thickness)))), color=cq.Color("yellow"), name="esc_holder_2")
# assembled_drone.add(esc_holder, loc=cq.Location(cq.Vector((-(battery_holder_length_mm/2 - esc_length/2), (battery_holder_width_mm + battery_holder_thickness_mm + esc_height + 2 * esc_holder_thickness)/2, -(drone_base_thickness_mm/2 + drone_base_battery_pillar_height_mm + battery_holder_height_mm/2 + esc_holder_thickness)))), color=cq.Color("yellow"), name="esc_holder_3")
# assembled_drone.add(esc_holder, loc=cq.Location(cq.Vector(((battery_holder_length_mm/2 - esc_length/2), (battery_holder_width_mm + battery_holder_thickness_mm + esc_height + 2 * esc_holder_thickness)/2, -(drone_base_thickness_mm/2 + drone_base_battery_pillar_height_mm + battery_holder_height_mm/2 + esc_holder_thickness)))), color=cq.Color("yellow"), name="esc_holder_4")

assembled_drone.add(switch_holder, color=cq.Color("red"), name="switchHolder")

assembled_drone.add(pcb_holder, color="grey", name="pcbHolder")

# assembled_drone.constrain("switchHolder@faces@<X", "pcbHolder@faces@>X", "Plane")
assembled_drone.constrain("pcbHolder?pcbHolderFrontEdge", "switchHolder?switchHolderFrontEdge", "Axis", param=0)
assembled_drone.constrain("pcbHolder?pcbHolderBottomEdge", "switchHolder?switchHolderBottomEdge", "Axis", param=0)
assembled_drone.constrain("pcbHolder?pcbHolderTopRightVertex", "switchHolder?switchHolderTopRightVertex", "Point")
assembled_drone.solve()

debug_edges_switch = switch_holder.vertices(tag="switchHolderTopRightVertex")
debug_edges_pcb = pcb_holder.vertices(tag="pcbHolderTopRightVertex")
# debug_edges_switch = switch_holder.faces("<X")
# debug_edges_pcb = pcb_holder.faces(">X")

assembled_drone.add(debug_edges_switch, name="switchDebug")
assembled_drone.add(debug_edges_pcb, name="pcbDebug")

show_object(assembled_drone)
# show_object(switch_holder)

# exporters.export(motor_holder, "export/new_drone.stl")
assembled_drone.export("export/new_drone.stl", "STL")