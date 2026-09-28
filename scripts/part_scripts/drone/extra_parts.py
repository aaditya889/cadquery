import cadquery as cq
from cadquery import exporters
from ocp_vscode import show_object
import os, sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)
from lib.solid import *
from lib.hollow import *
from lib.parts import *
from drone_parts import get_X_frame_base, get_esc_holder, _attach_esc_with_constraints, get_pcb_and_battery_holder


d_slot_thickness = 3
pcb_arm_height = 60
pcb_arm_thickness = 3
d_slot_arc_radius = 20.6
screw_distance_from_edge = 3.5
# extra_length = 10
# pcb_plate_


def _get_pcb_arms(extra_length):
  d_slot = cq.Workplane("XY").workplane().radiusArc((d_slot_arc_radius, 0, 0), d_slot_arc_radius/2).close().extrude(d_slot_thickness).rotate((0, 0, 0), (0, 0, 1), -90)
  d_slot = d_slot.faces(">Z").workplane(origin=(d_slot_arc_radius/2 - screw_distance_from_edge, -d_slot_arc_radius/2, d_slot_thickness/2)).cboreHole(3, 4, d_slot_thickness/1.5)
  d_slot = d_slot.faces("<X").workplane(centerOption="CenterOfBoundBox").rect(d_slot_arc_radius, d_slot_thickness).extrude(extra_length)
  pcb_arm = cq.Workplane("XY").workplane().box(pcb_arm_thickness, d_slot_arc_radius, pcb_arm_height)
  d_slot = d_slot.translate((pcb_arm_thickness/2 + extra_length, d_slot_arc_radius/2, -pcb_arm_height/2))

  fused = pcb_arm.union(d_slot)
  # fused = fused.union(fused.mirror("XY"))
  fused = fused.edges("not (<Z or >Z or %Circle or <Y or >Y or <X or >X or |Z)").fillet(2)
  fused = fused.edges("<X").fillet(2)

  return fused


def get_pcb_arms():
  arm1 = _get_pcb_arms(extra_length=10)
  arm2 = _get_pcb_arms(extra_length=0.1)
  arm2 = arm2.rotate((0, 0, 0), (1, 0, 0), 180)
  arm = arm1.union(arm2)
  return arm


def get_pcb_and_battery_holders():
  pcb_holder_height = 5
  pcb_holder_length = 110
  pcb_holder_width = 80
  esc_holder_length = 57
  esc_holder_width = 32
  esc_holder_height =13
  esc_holder_thickness = 2
  battery_holder_length = 140
  battery_holder_width = 48
  battery_holder_height = 45
  battery_holder_thickness = 2
  switch_pin_1_distance = 2
  switch_pin_2_distance = 9
  switch_pin_thickness = 1
  switch_pin_width = 5.5
  switch_width = 17

  pcb_plate = get_X_frame_base(length=pcb_holder_length, width=pcb_holder_width, height=pcb_holder_height)
  # show_object([pcb_plate.faces("<Z").workplane().rect(80, 60).vertices(), pcb_plate])
  _pcb_plate = pcb_plate.faces("<Z").workplane().rect(55, 75, forConstruction=True).vertices().tag("pcbHoles").end()
  pcb_plate.faces(">Z").tag("plateMate")

  switch_pin_1_location = cq.Vector(pcb_holder_width/2 + switch_width/2, switch_pin_1_distance, 0)
  switch_pin_2_location = cq.Vector(pcb_holder_width/2 + switch_width/2, switch_pin_2_distance, 0)


  pcb_plate = pcb_plate.faces("<Z").workplane(origin=switch_pin_1_location).rect(switch_pin_width, switch_pin_thickness).cutThruAll()
  pcb_plate = pcb_plate.faces("<Z").workplane(origin=switch_pin_2_location).rect(switch_pin_width, switch_pin_thickness).cutThruAll()
  # pcb_plate = pcb_plate.faces("<Z").workplane(origin=switch_pin_2_location).rect(switch_pin_thickness, switch_pin_width).cutThruAll()
  pcb_plate = pcb_plate.vertices(tag="pcbHoles").cboreHole(3, 4, 5/1.5)
  fused = cq.Workplane("XY").newObject(get_pcb_and_battery_holder(battery_holder_length, battery_holder_width, 
                                                                  battery_holder_height, battery_holder_thickness).toCompound())

	# ESC mating tags
  ratio = 1/6
  esc_holder_placement = pcb_holder_length/2 - 40/4 - 40/4
  _a5 = fused.faces(">Y").workplane(centerOption="CenterOfBoundBox").pushPoints([(esc_holder_placement, -esc_holder_width/7)]).rect(1, 1).extrude(0.01)
  _a6 = fused.faces(">Y").workplane(centerOption="CenterOfBoundBox").pushPoints([(-esc_holder_placement, -esc_holder_width/7)]).rect(1, 1).extrude(0.01)
  _a7 = fused.faces("<Y").workplane(centerOption="CenterOfBoundBox").pushPoints([(esc_holder_placement, -esc_holder_width/7)]).rect(1, 1).extrude(0.01)
  _a8 = fused.faces("<Y").workplane(centerOption="CenterOfBoundBox").pushPoints([(-esc_holder_placement, -esc_holder_width/7)]).rect(1, 1).extrude(0.01)

  _a5.faces(">Y").tag("escMatePlane1").edges(">Z").tag("escMateEdge1")
  _a6.faces(">Y").tag("escMatePlane2").edges(">Z").tag("escMateEdge2")
  _a7.faces("<Y").tag("escMatePlane3").edges(">Z").tag("escMateEdge3")
  _a8.faces("<Y").tag("escMatePlane4").edges(">Z").tag("escMateEdge4")
  fused.faces(">Z").tag("plateMate")
  # _attach_esc_with_constraints(esc_battery_holder)
  drone = cq.Assembly()
  drone.add(fused, color=cq.Color("yellow"), name="body")
  drone.add(pcb_plate, color=cq.Color("red"), name="pcbPlate")

  _attach_esc_with_constraints(drone, esc_holder_length, esc_holder_width, esc_holder_height, esc_holder_thickness)
  drone.constrain("pcbPlate?plateMate", "body?plateMate", "Plane")
  # drone.constrain("pcbPlate?plateMate", "body?plateMate", "Axis", param=180)
  drone.solve()
  return drone

arm = get_pcb_arms()
# arm.export("export/new_support_arm.stl", "STL")
# body = get_pcb_and_battery_holders()
exporters.export(arm, "export/new_support_arm.stl")
# body.export("export/new_body.stl", "STL")
# show_object([arm])
show_object([
    # body, 
    arm
  ])


