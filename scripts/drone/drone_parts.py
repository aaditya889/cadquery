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


pcb_plate_length = 90
pcb_plate_width = 30
pcb_plate_height = 15
pcb_plate_thickness = 5

arm_length = (220 - pcb_plate_length)/2
arm_width = 30
arm_thickness = 5

motor_holder_thickness = 5

esc_holder_length = 40
esc_holder_width = 30
esc_holder_height = 10
esc_holder_thickness = 2


def get_arm_with_motor_holder(motor_holder_part, length=arm_length, width=arm_width, height=arm_thickness):
	# arm = cq.Workplane("XY").box(length, width, height)
	arm = get_vertical_cross_section_arms()
	
	assembled = cq.Assembly()
	assembled.add(arm, color=cq.Color("red"), name="arm")
	assembled.add(motor_holder_part["part"], color=cq.Color("blue"), name="motorHolder")

	arm.faces("<X").edges(">Z").tag("armLeftTopEdge")


	# return [arm, _t]
	assembled.constrain("arm?armLeftTopEdge", "motorHolder?motorHolderCurvedEdge", "Point", param=20)
	assembled.constrain("arm@faces@<X", "motorHolder?motorHolderCurvedFace", "Plane", param=0)
	assembled.constrain("arm?armLeftTopEdge", "motorHolder?motorHolderCurvedEdge", "Axis", param=90)
	# assembled.constrain("arm@faces@<X@edges@>Z", "motorHolder?motorHolderCurvedEdge", "Axis", param=0)
	# assembled.constrain("arm@edges@<X and <Y", "motorHolder?motorHolderCurvedEdge", "Axis", param=0)
	
	assembled.solve()
	
	new_motor_object = assembled.objects["motorHolder"]
	new_motor_object_solid: cq.Workplane = motor_holder_part["cutter"].val().moved(new_motor_object.loc)
	r = cq.Workplane("XY").newObject([new_motor_object_solid]).faces("<Z").edges().val().radius()

	wp_solid = cq.Workplane("XY").newObject([new_motor_object_solid])

	# 2. Get the specific face context
	face_context = wp_solid.faces("<Z")

	# 3. Extract the wires (The shape of the face)
	#    We use .vals() to get a LIST of wires (e.g., Outer Circle + Inner Hole)
	face_wires = face_context.wires().vals()

	# 4. Extrude
	extended_cutter = (
			face_context         # Start from the face selection
			.workplane()         # Create the grid
			.add(face_wires)     # <--- Add the wires we extracted earlier
			.toPending()         # Tell CadQuery: "These are the wires I want to extrude"
			.extrude(-20, taper=0)
	)

	new_motor_object = new_motor_object.obj.val().moved(new_motor_object.loc)
	fused = arm.cut(extended_cutter).union(new_motor_object)
	_a = fused.faces(">X").tag("matePlane")
	_e = fused.faces(">X").edges(">Z").tag("mateEdge")
	# show_object([fused, _e])
	return {"part": fused, "matePlane": _a, "mateEdge": _e}


def get_motor_holder(thickness=motor_holder_thickness):
	motor_holder_radius =  29
	radius = motor_holder_radius
	motor_holder_solid = cq.Workplane("XY").circle(radius + thickness).center(0, 0).extrude(thickness)
	motor_holder_solid.faces("%Cylinder").edges()[0].tag("motorHolderCurvedEdge")
	motor_holder_solid.faces("%Cylinder").faces(">X").tag("motorHolderCurvedFace")
	motor_screw_distance_from_center = 8
	motor_shaft_radius = 9.5/2
	motor_screw_radius = 3.5/2
	motor_screw_coordinates = [(0, motor_screw_distance_from_center + 1), 
														(motor_screw_distance_from_center - 0.5, 0), 
														(-motor_screw_distance_from_center + 0.5, 0), 
														(0, -motor_screw_distance_from_center - 1)]
	motor_holder = motor_holder_solid.pushPoints([motor_screw_coordinates[0], motor_screw_coordinates[1], motor_screw_coordinates[2], motor_screw_coordinates[3]]).circle(motor_screw_radius).cutThruAll()
	motor_holder = motor_holder.pushPoints([(0, 0)]).circle(motor_shaft_radius).cutThruAll()
	return {"part": motor_holder, "cutter": motor_holder_solid}



def get_motor_holder_with_X_base(thickness=motor_holder_thickness):
	motor_holder_x_radius =  42/2
	radius = motor_holder_x_radius
	motor_holder_x_width =  8.2
	motor_screw_radius = 3.5/2
	motor_shaft_radius = 9.5/2
	motor_x_screw_radius = 3.0/2
	motor_screw_distance_from_center = 8
	motor_screw_x_distance_from_center = 16.2
	motor_screw_coordinates = [(0, motor_screw_distance_from_center + 1.2), 
														(motor_screw_distance_from_center - 0.5, 0), 
														(-motor_screw_distance_from_center + 0.5, 0), 
														(0, -motor_screw_distance_from_center - 1.2)]

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
		.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 45)
	)
	motor_holder = motor_holder.edges("|Z").fillet(motor_holder_x_width)
	return {"part": motor_holder, "cutter": motor_holder_solid}


def get_pcb_and_battery_holder():
	# pcb_plate1 = cq.Workplane("XY").box(pcb_plate_length, pcb_plate_width, pcb_plate_height)
	# pcb_plate2 = cq.Workplane("XY").box(pcb_plate_width, pcb_plate_length, pcb_plate_height)
	# # pcb_plate = pcb_plate.faces(">Z").shell(pcb_plate_thickness)
	# # pcb_plate.edges(">Y").tag("mateEdge")
	
	# # battery_holder = cq.Workplane("XY").box(pcb_plate_length, pcb_plate_width, pcb_plate_height).faces(">Z").tag("mate").end()
	# # battery_holder = battery_holder.faces("<Z").shell(pcb_plate_thickness)
	# # battery_holder.edges(">Y").tag("mateEdge")

	# assembled = cq.Assembly()
	# assembled.add(pcb_plate1, name="pcbPlate1")
	# assembled.add(pcb_plate2, name="pcbPlate2")
	# # assembled.add(battery_holder, name="batteryHolder")
	# # assembled.constrain("pcbPlate?mate", "batteryHolder?mate", "Plane")
	# # assembled.constrain("pcbPlate?mateEdge", "batteryHolder?mateEdge", "Axis", param=0)
	# # assembled.solve()

	cross_sketch = (
    cq.Sketch()
    .rect(pcb_plate_length, pcb_plate_width)
    .rect(pcb_plate_width, pcb_plate_length, mode='a')
    .clean()                                    # Cleans up unnecessary internal lines
		.vertices(">X or <X or >Y or <Y")
		.fillet(0.5)
	)
	assembled = (
    cq.Workplane("XY")
    # .faces(">Z")
    # .workplane()
    .placeSketch(cross_sketch)
		.extrude(pcb_plate_height)
    # .cutBlind(-x_washer_thickness - 0.1)
		# .rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 45)
	)

	# fused = cq.Workplane("XY").newObject([assembled.toCompound()])
	fused = assembled

	# Arm mating tags
	_a1 = fused.faces(">X").workplane(centerOption="CenterOfBoundBox").pushPoints([(0, pcb_plate_height/2 - 0.5)]).rect(1, 1).extrude(0.01)
	_a2 = fused.faces("<X").workplane(centerOption="CenterOfBoundBox").pushPoints([(0, pcb_plate_height/2 - 0.5)]).rect(1, 1).extrude(0.01)
	_a3 = fused.faces(">Y").workplane(centerOption="CenterOfBoundBox").pushPoints([(0, pcb_plate_height/2 - 0.5)]).rect(1, 1).extrude(0.01)
	_a4 = fused.faces("<Y").workplane(centerOption="CenterOfBoundBox").pushPoints([(0, pcb_plate_height/2 - 0.5)]).rect(1, 1).extrude(0.01)

	# ESC mating tags
	_a5 = fused.faces(">X").workplane(centerOption="CenterOfBoundBox").pushPoints([(0, -pcb_plate_height/2 - 0.5)]).rect(1, 1).extrude(0.01)
	_a6 = fused.faces("<X").workplane(centerOption="CenterOfBoundBox").pushPoints([(0, -pcb_plate_height/2 - 0.5)]).rect(1, 1).extrude(0.01)
	_a7 = fused.faces(">Y").workplane(centerOption="CenterOfBoundBox").pushPoints([(0, -pcb_plate_height/2 - 0.5)]).rect(1, 1).extrude(0.01)
	_a8 = fused.faces("<Y").workplane(centerOption="CenterOfBoundBox").pushPoints([(0, -pcb_plate_height/2 - 0.5)]).rect(1, 1).extrude(0.01)
	
	_a1.faces(">X").tag("armMatePlane1").edges(">Z").tag("armMateEdge1")
	_a2.faces("<X").tag("armMatePlane2").edges(">Z").tag("armMateEdge2")
	_a3.faces(">Y").tag("armMatePlane3").edges(">Z").tag("armMateEdge3")
	_a4.faces("<Y").tag("armMatePlane4").edges(">Z").tag("armMateEdge4")

	_a5.faces(">X").tag("escMatePlane1").edges(">Z").tag("escMateEdge1")
	_a6.faces("<X").tag("escMatePlane2").edges(">Z").tag("escMateEdge2")
	_a7.faces(">Y").tag("escMatePlane3").edges(">Z").tag("escMateEdge3")
	_a8.faces("<Y").tag("escMatePlane4").edges(">Z").tag("escMateEdge4")

	fused = fused.edges("|Z").fillet(pcb_plate_length)
	# show_object([_a1.faces(">X").edges(">Z"), _a1])

	return fused


def get_esc_holder():
	esc_holder = cq.Workplane("XY").box(esc_holder_length, esc_holder_width, esc_holder_height)
	esc_holder = esc_holder.faces(">Z or >X or <X").shell(pcb_plate_thickness)
	_b = esc_holder.faces("<Z").tag("matePlane")
	_a = esc_holder.edges("<Z and >X").tag("mateEdge")

	# all_edges = esc_holder.edges("<Z and |X").vals()
	# positive_edge_list = [e for e in all_edges if e.Center().y < 0]

	# if positive_edge_list:
	# 		_c = positive_edge_list[0]
	
	return esc_holder


def get_vertical_cross_section_arms():
	# cross_section = cq.Sketch().spline([[0, 0], [-2, 2], [2, 2], [0, 0]]).close()
	# beam = cq.Workplane("YZ").bezier([[0, 0], [-0.4, 0], [-4, 5], [4, 5], [0.4, 0], [0, 0]]).close().extrude(20)

	# --- Dimensions ---
	# arm_length = 100
	# height = 30   # Y-axis (Vertical)
	# width = 15    # X-axis (Thickness)

	# --- Extrude ---
	# beam = cq.Workplane("YZ").placeSketch(oval_sketch).extrude(arm_length)
	# Alternative for organic shapes
	# beam = cq.Workplane("YZ").spline(points).close().extrude(10)

	# Calculate the height of the vertical web part
	arm_len = arm_length
	total_h = pcb_plate_height   # Total height of the T
	flange_w = arm_width  # Width of the top bar
	flange_t = arm_thickness   # Thickness of the top bar
	web_t = arm_thickness      # Thickness of the vertical bar
	web_h = total_h - flange_t
		# --- 2. Define the Sketch ---
	# We center the Web at (0,0) for symmetry, then place the Flange on top.
	t_sketch = (
			cq.Sketch()
			# Draw the vertical Web first (centered at 0,0)
			.rect(web_t, web_h)
			
			# Move 'pen' up to where the flange center should be
			# (Half the web height + Half the flange thickness)
			.push([(0, (web_h / 2) + (flange_t / 2))])
			
			# Draw the Flange and UNION it ('u') with the existing web
			.rect(flange_w, flange_t)
			
			# Clean up internal lines so it becomes one single profile
			.clean()
			
			# OPTIONAL: Add fillets to reduce stress at the sharp inner corners
			# We select vertices that are "inside" (not at the extreme boundaries)
			# .vertices("not (>Y or <Y or >X or <X)")
			# .fillet(2)
	)

	# --- 3. Extrude the Arm ---
	arm = cq.Workplane("YZ").placeSketch(t_sketch).extrude(arm_len).edges("not >X").fillet(2)
	# _a = arm.faces("<X").tag("matePlane")
	# _b = arm.faces("<X").edges(">Z").tag("mateEdge")
	return arm


def _attach_arms_with_constraints(drone: cq.Assembly):
	motor_object = get_motor_holder_with_X_base()
	drone.add(get_arm_with_motor_holder(motor_object)["part"], color=cq.Color("yellow"), name="arm1")
	drone.add(get_arm_with_motor_holder(motor_object)["part"], color=cq.Color("yellow"), name="arm2")
	drone.add(get_arm_with_motor_holder(motor_object)["part"], color=cq.Color("yellow"), name="arm3")
	drone.add(get_arm_with_motor_holder(motor_object)["part"], color=cq.Color("yellow"), name="arm4")

	# drone.constrain("body?armMatePlane1", "arm1?matePlane", "Plane")
	drone.constrain("body?armMatePlane1", "arm1?matePlane", "Axis")
	drone.constrain("body?armMateEdge1", "arm1?mateEdge", "Axis", param=0)
	drone.constrain("body?armMateEdge1", "arm1?mateEdge", "Point", param=0)

	# drone.constrain("body?armMatePlane2", "arm2?matePlane", "Plane")
	drone.constrain("body?armMatePlane2", "arm2?matePlane", "Axis")
	drone.constrain("body?armMateEdge2", "arm2?mateEdge", "Axis", param=0)
	drone.constrain("body?armMateEdge2", "arm2?mateEdge", "Point", param=0)

	# drone.constrain("body?armMatePlane3", "arm3?matePlane", "Plane")
	drone.constrain("body?armMatePlane3", "arm3?matePlane", "Axis")
	drone.constrain("body?armMateEdge3", "arm3?mateEdge", "Axis", param=0)
	drone.constrain("body?armMateEdge3", "arm3?mateEdge", "Point", param=0)

	# drone.constrain("body?armMatePlane4", "arm4?matePlane", "Plane")
	drone.constrain("body?armMatePlane4", "arm4?matePlane", "Axis")
	drone.constrain("body?armMateEdge4", "arm4?mateEdge", "Axis", param=0)
	drone.constrain("body?armMateEdge4", "arm4?mateEdge", "Point", param=0)

	drone.solve()
	# return drone


def _attach_esc_with_constraints(drone: cq.Assembly):
	drone.add(get_esc_holder(), color=cq.Color("green"), name="esc1")
	drone.add(get_esc_holder(), color=cq.Color("green"), name="esc2")
	drone.add(get_esc_holder(), color=cq.Color("green"), name="esc3")
	drone.add(get_esc_holder(), color=cq.Color("green"), name="esc4")

	drone.constrain("body?escMatePlane1", "esc1?matePlane", "Plane")
	drone.constrain("body?escMatePlane1", "esc1?matePlane", "Axis")
	drone.constrain("body?escMateEdge1", "esc1?mateEdge", "Axis", param=90)

	drone.constrain("body?escMatePlane2", "esc2?matePlane", "Plane")
	drone.constrain("body?escMatePlane2", "esc2?matePlane", "Axis")
	drone.constrain("body?escMateEdge2", "esc2?mateEdge", "Axis", param=90)

	drone.constrain("body?escMatePlane3", "esc3?matePlane", "Plane")
	drone.constrain("body?escMatePlane3", "esc3?matePlane", "Axis")
	drone.constrain("body?escMateEdge3", "esc3?mateEdge", "Axis", param=90)

	drone.constrain("body?escMatePlane4", "esc4?matePlane", "Plane")
	drone.constrain("body?escMatePlane4", "esc4?matePlane", "Axis")
	drone.constrain("body?escMateEdge4", "esc4?mateEdge", "Axis", param=90)

	drone.solve()

# show_object(get_arm_with_motor_holder(get_motor_holder_with_X_base()))
drone = cq.Assembly()

body = get_pcb_and_battery_holder()
drone.add(body, color=cq.Color("yellow"), name="body")

_attach_arms_with_constraints(drone)
# _attach_esc_with_constraints(drone)
# show_object([get_arm_with_motor_holder(get_motor_holder_with_X_base())])
show_object([drone])
# show_object([get_vertical_cross_section_arms()])

# exporters.export(motor_object["part"], "export/motor_holder.stl")
# part.export("export/motor_holder.stl", "STL")