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


arm_length = 230/2
arm_width = 15
arm_thickness = 5
motor_holder_thickness = 5


def get_arm_with_motor_holder(motor_holder_part, length=arm_length, width=arm_width, height=arm_thickness):
	arm = cq.Workplane("XY").box(length, width, height)
	assembled = cq.Assembly()
	assembled.add(arm, color=cq.Color("red"), name="arm")
	assembled.add(motor_holder_part["part"], color=cq.Color("blue"), name="motorHolder")
	arm.edges("<X and <Z").tag("armLeftBottomEdge").end()
	assembled.constrain("arm?armLeftBottomEdge", "motorHolder?motorHolderCurvedEdge", "Axis", param=90)
	assembled.constrain("arm@edges@<X and >Y", "motorHolder?motorHolderCurvedEdge", "Axis", param=0)
	assembled.constrain("arm@edges@<X and <Y", "motorHolder?motorHolderCurvedEdge", "Axis", param=0)
	assembled.constrain("arm@faces@<X", "motorHolder?motorHolderCurvedFace", "Plane", param=0)
	assembled.solve()
	new_motor_object = assembled.objects["motorHolder"]
	new_motor_object_solid = motor_holder_part["cutter"].val().moved(new_motor_object.loc)
	new_motor_object = new_motor_object.obj.val().moved(new_motor_object.loc)
	fused = arm.cut(new_motor_object_solid).union(new_motor_object)
	_a = fused.faces(">X").tag("mate")
	return {"part": fused, "mate": _a}


def get_motor_holder(thickness=motor_holder_thickness):
	motor_holder_radius =  29
	radius = motor_holder_radius
	motor_holder_solid = cq.Workplane("XY").circle(radius + thickness).center(0, 0).extrude(thickness)
	motor_holder_solid.faces("%Cylinder").edges()[0].tag("motorHolderCurvedEdge")
	motor_holder_solid.faces("%Cylinder").faces(">X").tag("motorHolderCurvedFace")
	motor_screw_distance_from_center = 8
	motor_shaft_radius = 9.5/2
	motor_screw_radius = 3.5/2
	motor_holder_wire_pocket_length = 15
	motor_screw_coordinates = [(0, motor_screw_distance_from_center + 0.8), 
														(motor_screw_distance_from_center - 0.5, 0), 
														(-motor_screw_distance_from_center + 0.5, 0), 
														(0, -motor_screw_distance_from_center - 0.8)]
	motor_holder = motor_holder_solid.pushPoints([motor_screw_coordinates[0], motor_screw_coordinates[1], motor_screw_coordinates[2], motor_screw_coordinates[3]]).circle(motor_screw_radius).cutThruAll()
	motor_holder = motor_holder.pushPoints([(0, 0)]).circle(motor_shaft_radius).cutThruAll()
	return {"part": motor_holder, "cutter": motor_holder_solid}



def get_motor_holder_with_X_base(thickness=motor_holder_thickness):
	motor_holder_x_radius =  42.5/2
	radius = motor_holder_x_radius
	motor_holder_x_width =  8.5
	motor_screw_radius = 3.5/2
	motor_shaft_radius = 9.5/2
	motor_x_screw_radius = 3.0/2
	motor_screw_distance_from_center = 8
	motor_screw_x_distance_from_center = 16.2
	motor_screw_coordinates = [(0, motor_screw_distance_from_center + 0.8), 
														(motor_screw_distance_from_center - 0.5, 0), 
														(-motor_screw_distance_from_center + 0.5, 0), 
														(0, -motor_screw_distance_from_center - 0.8)]

	motor_x_screw_coordinates = [(0, motor_screw_x_distance_from_center), 
														(motor_screw_x_distance_from_center, 0), 
														(-motor_screw_x_distance_from_center, 0), 
														(0, -motor_screw_x_distance_from_center)]
	x_washer_thickness = 2.0


	motor_holder_solid = cq.Workplane("XY").circle(radius + 1).center(0, 0).extrude(thickness)
	motor_holder_solid.faces("%Cylinder and >X").edges(">Y")[0].tag("motorHolderCurvedEdge")
	motor_holder_solid.faces("%Cylinder").faces(">X").tag("motorHolderCurvedFace")
	motor_holder = motor_holder_solid.pushPoints([motor_screw_coordinates[0], motor_screw_coordinates[1], motor_screw_coordinates[2], motor_screw_coordinates[3]]).circle(motor_screw_radius).cutThruAll()
	motor_holder = motor_holder.pushPoints([motor_x_screw_coordinates[0], motor_x_screw_coordinates[1], motor_x_screw_coordinates[2], motor_x_screw_coordinates[3]]).circle(motor_x_screw_radius).cutThruAll()
	motor_holder = motor_holder.pushPoints([(0, 0)]).circle(motor_shaft_radius).cutThruAll()

	cross_sketch = (
    cq.Sketch()
    .rect(motor_holder_x_radius*2, motor_holder_x_width)
    .rect(motor_holder_x_width, motor_holder_x_radius*2, mode='a')
    .clean()                                    # Cleans up unnecessary internal lines
		.vertices(">X or <X or >Y or <Y")
		.fillet(motor_holder_x_width/2)
	)
	motor_holder = (
    motor_holder
    .faces(">Z")
    .workplane()
    .placeSketch(cross_sketch)
    .cutBlind(-x_washer_thickness - 0.1)
	)
	motor_holder = motor_holder.edges("|Z").fillet(motor_holder_x_width)
	return {"part": motor_holder, "cutter": motor_holder_solid}

def get_pcb_and_battery_holder():
	pass

# show_object(get_arm_with_motor_holder(get_motor_holder_with_X_base()))
motor_object = get_motor_holder_with_X_base()
arm = get_arm_with_motor_holder(motor_object)
x = cq.Workplane("XY").box(50, 20, 20)
_a = x.faces(">X").tag("mate")
ass = cq.Assembly()
ass.add(arm["part"], color=cq.Color("blue"), name="arm")
ass.add(x, color=cq.Color("red"), name="x")

ass.constrain("arm?mate", "x?mate", "Plane")
ass.solve()
show_object([ass])

# exporters.export(motor_object["part"], "export/motor_holder.stl")
# part.export("export/motor_holder.stl", "STL")