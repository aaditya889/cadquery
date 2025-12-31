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
pcb_plate_width = 60
pcb_plate_height = 10
pcb_plate_thickness = 2

battery_holder_length = 90
battery_holder_width = 30
battery_holder_height = 20
battery_holder_thickness = 2

arm_length = (220 - pcb_plate_length)/2
arm_width = 30
arm_thickness = 5

motor_holder_thickness = 5

esc_holder_length = 40
esc_holder_width = 15
esc_holder_height = 10
esc_holder_thickness = 2

dampener_support_thickness = 3


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


def get_pcb_and_battery_holder(length=battery_holder_length, width=battery_holder_width, height=battery_holder_height, 
															 thickness=battery_holder_thickness):
	# pcb_plate = cq.Workplane("XY").box(pcb_plate_length, pcb_plate_width, pcb_plate_height)
	# pcb_plate2 = cq.Workplane("XY").box(pcb_plate_width, pcb_plate_length, pcb_plate_height)
	# pcb_plate = pcb_plate.faces(">Z").shell(pcb_plate_thickness)
	# pcb_plate.edges(">Y").tag("mateEdge")
	# pcb_plate.faces("<Z").tag("mate")

	# pcb_plate = pcb_plate.edges(">Z").rect(2, 4).extrude(10)
	
	battery_holder = cq.Workplane("XY").box(length, width, height)
	battery_holder.faces(">Z").tag("mate")
	battery_holder = battery_holder.faces("<Z or <X or >X").shell(thickness)
	# battery_holder = battery_holder.faces("<X").shell(thickness)
	# battery_holder = battery_holder.faces(">X").shell(thickness)
	battery_holder.edges(">Y").tag("mateEdge")

	assembled = cq.Assembly()
	# assembled.add(pcb_plate, name="pcbPlate")
	# show_object(pcb_plate)
	# assembled.add(pcb_plate2, name="pcbPlate2")
	assembled.add(battery_holder, name="batteryHolder")
	# assembled.constrain("pcbPlate?mate", "batteryHolder?mate", "Plane")
	# assembled.constrain("pcbPlate?mateEdge", "batteryHolder?mateEdge", "Axis", param=0)
	# assembled.solve()

	return assembled


def get_X_frame_base(length=pcb_plate_length, width=pcb_plate_width, height=pcb_plate_height):
	cross_sketch = (
    cq.Sketch()
    .rect(length, width)
    .rect(width, length, mode='a')
    .clean()                                    # Cleans up unnecessary internal lines
		.vertices(">X or <X or >Y or <Y")
		.fillet(10)
	)
	assembled = (
    cq.Workplane("XY")
    # .faces(">Z")
    # .workplane()
    .placeSketch(cross_sketch)
		.extrude(height)
    # .cutBlind(-x_washer_thickness - 0.1)
		# .rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 45)
	)

	# fused = cq.Workplane("XY").newObject([assembled.toCompound()])
	fused = assembled

	# Arm mating tags
	_a1 = fused.faces(">X").workplane(centerOption="CenterOfBoundBox").pushPoints([(0, height/2 - 0.5)]).rect(1, 1).extrude(0.01)
	_a2 = fused.faces("<X").workplane(centerOption="CenterOfBoundBox").pushPoints([(0, height/2 - 0.5)]).rect(1, 1).extrude(0.01)
	_a3 = fused.faces(">Y").workplane(centerOption="CenterOfBoundBox").pushPoints([(0, height/2 - 0.5)]).rect(1, 1).extrude(0.01)
	_a4 = fused.faces("<Y").workplane(centerOption="CenterOfBoundBox").pushPoints([(0, height/2 - 0.5)]).rect(1, 1).extrude(0.01)

	# ESC mating tags
	_a5 = fused.faces(">X").workplane(centerOption="CenterOfBoundBox").pushPoints([(0, -height/2 - 0.5)]).rect(1, 1).extrude(0.01)
	_a6 = fused.faces("<X").workplane(centerOption="CenterOfBoundBox").pushPoints([(0, -height/2 - 0.5)]).rect(1, 1).extrude(0.01)
	_a7 = fused.faces(">Y").workplane(centerOption="CenterOfBoundBox").pushPoints([(0, -height/2 - 0.5)]).rect(1, 1).extrude(0.01)
	_a8 = fused.faces("<Y").workplane(centerOption="CenterOfBoundBox").pushPoints([(0, -height/2 - 0.5)]).rect(1, 1).extrude(0.01)
	
	_a1.faces(">X").tag("armMatePlane1").edges(">Z").tag("armMateEdge1")
	_a2.faces("<X").tag("armMatePlane2").edges(">Z").tag("armMateEdge2")
	_a3.faces(">Y").tag("armMatePlane3").edges(">Z").tag("armMateEdge3")
	_a4.faces("<Y").tag("armMatePlane4").edges(">Z").tag("armMateEdge4")

	_a5.faces(">X").tag("escMatePlane1").edges(">Z").tag("escMateEdge1")
	_a6.faces("<X").tag("escMatePlane2").edges(">Z").tag("escMateEdge2")
	_a7.faces(">Y").tag("escMatePlane3").edges(">Z").tag("escMateEdge3")
	_a8.faces("<Y").tag("escMatePlane4").edges(">Z").tag("escMateEdge4")

	fused = fused.edges("|Z").fillet(length*4)
	
	fusedXYVs = fused.faces(">Z").vertices(">XY")
	fusedXYV1 = fusedXYVs.item(0)
	fusedXYV2 = fusedXYVs.item(1)
	fusedXY1_vector1 = cq.Vector(fusedXYV1.objects[0].Center())
	fusedXY1_vector2 = cq.Vector(fusedXYV2.objects[0].Center())
	r1 = (fusedXY1_vector1 - fusedXY1_vector2).Length

	fusedYXVs = fused.faces(">Z").vertices("<XY")
	fusedYXV1 = fusedYXVs.item(0)
	fusedYXV2 = fusedYXVs.item(1)
	fusedYX1_vector1 = cq.Vector(fusedYXV1.objects[0].Center())
	fusedYX1_vector2 = cq.Vector(fusedYXV2.objects[0].Center())
	r2 = (fusedYX1_vector1 - fusedYX1_vector2).Length

	fusedLYXVs = fused.faces(">Z").vertices("not (<XY or >XY or >X or <X or >Y or <Y)")

	currLX = 0
	currGY = 0
	currGX = 0
	currLY = 0
	least_x_point = None
	greatest_y_point = None
	greatest_x_point = None
	least_y_point = None
	for i in range(fusedLYXVs.size()):
		if fusedLYXVs.item(i).objects[0].X < currLX:
			least_x_point = fusedLYXVs.item(i)
			currLX = fusedLYXVs.item(i).objects[0].X
		if fusedLYXVs.item(i).objects[0].Y > currGY:
			greatest_y_point = fusedLYXVs.item(i)
			currGY = fusedLYXVs.item(i).objects[0].Y

		if fusedLYXVs.item(i).objects[0].X > currGX:
			greatest_x_point = fusedLYXVs.item(i)
			currGX = fusedLYXVs.item(i).objects[0].X
		if fusedLYXVs.item(i).objects[0].Y < currLY:
			least_y_point = fusedLYXVs.item(i)
			currLY = fusedLYXVs.item(i).objects[0].Y

	fusedLYXV1 = least_x_point
	fusedLYXV2 = greatest_y_point
	fusedLYXV12 = least_y_point 
	fusedLYXV22 = greatest_x_point

	fusedLYX1_vector1 = cq.Vector(fusedLYXV1.objects[0].Center())
	fusedLYX1_vector2 = cq.Vector(fusedLYXV2.objects[0].Center())
	fusedLYX12_vector1 = cq.Vector(fusedLYXV12.objects[0].Center())
	fusedLYX22_vector2 = cq.Vector(fusedLYXV22.objects[0].Center())
	r3 = (fusedLYX1_vector1 - fusedLYX1_vector2).Length
	r4 = (fusedLYX12_vector1 - fusedLYX22_vector2).Length

	fused = (fused.faces(">Z")
					.pushPoints([fusedXY1_vector1]).radiusArc(fusedXY1_vector2, -r1/2).close()
					.cutBlind(-(height - dampener_support_thickness))
					.pushPoints([(fusedXY1_vector1 + fusedXY1_vector2)/2 - cq.Vector(1, 1, 0)*r1/6.0])
					.cboreHole(3, 4, height/1.5)

					.pushPoints([fusedYX1_vector1]).radiusArc(fusedYX1_vector2, r2/2).close()
					.cutBlind(-(height - dampener_support_thickness))
					.pushPoints([(fusedYX1_vector1 + fusedYX1_vector2)/2 + cq.Vector(1, 1, 0)*r2/6.0])
					.cboreHole(3, 4, height/1.5)

					.pushPoints([fusedLYX1_vector1]).radiusArc(fusedLYX1_vector2, -r3/2).close()
					.cutBlind(-(height - dampener_support_thickness))
					.pushPoints([(fusedLYX1_vector1 + fusedLYX1_vector2)/2 + cq.Vector(1, -1, 0)*r3/6.0])
					.cboreHole(3, 4, height/1.5)
					
					.pushPoints([fusedLYX12_vector1]).radiusArc(fusedLYX22_vector2, r4/2).close()
					.cutBlind(-(height - dampener_support_thickness))
					.pushPoints([(fusedLYX12_vector1 + fusedLYX22_vector2)/2 + cq.Vector(-1, 1, 0)*r4/6.0])
					.cboreHole(3, 4, height/1.5)
					)


	# fusedV2 = fused.faces(">Z").workplane().transformed(rotate=cq.Vector(0, 0, -45)).rect(length, width/2).vertices()
	
	# fused = fused.faces(">Z").workplane().vertices(tag="v1").extrude(-10)
	# fused = fused.faces(">Z").workplane().vertices(fusedV2).circle(2).extrude(10)
	# sketch1R = cq.Sketch().rect(length, width/2, angle=-45)

	# exporters.export(fusedXYV1, "export/fusedV1.stl")
	# show_object([fusedV1])
	# loc1 = fused.faces(">Z").vertices(">X").vertices("<Y").val().location()
	# show_object(fused.faces(">Z").vertices(">X").vertices("<Y"))
	# print(loc1.toTuple())
	# fused = fused.faces(">Z").workplane(origin=cq.Location(loc1)).rect(2, 3).cutBlind(-2)

	# _e1 = curved_faces.edges("|Z and <Y").vals()
	# _e2 = curved_faces.edges("|Z and <X").vals()
	# _e3 = curved_faces.edges("|Z and >Y").vals()
	# _e4 = curved_faces.edges("|Z and >X").vals()
	# positive_edge_list = []
	# [show_object(cq.Workplane("XY").newObject(e).tag("hookCut1")) for e in _e1 if e.Center().x > 0]
	# [e.tag("hookCut2") for e in _e2 if e.Center().y < 0]
	# [e.tag("hookCut3") for e in _e3 if e.Center().x < 0]
	# [e.tag("hookCut4") for e in _e4 if e.Center().y > 0]


	# large_curves = [f for f in curved_faces if f.Geom().Radius() > 2.0]
	# fused = (fused
  #        .faces("not (|X or |Y or |Z)") # Select all curved faces
  #        .faces(">X and >Y")            # Filter for just the Top-Right one
  #        .workplane(offset=5) 
  #        .center(0, 0)
  #        .rect(5, 5)
  #        .cutBlind(-5)
  #        )


	return fused


def get_esc_holder(length=esc_holder_length, width=esc_holder_width, height=esc_holder_height, thickness=esc_holder_thickness):
	esc_holder = cq.Workplane("XY").box(length, width, height)
	esc_holder = esc_holder.faces(">Z or >X or <X").shell(thickness)
	_b = esc_holder.faces("<Z").tag("matePlane")
	_a = esc_holder.edges("<Z and >X").tag("mateEdge")

	# all_edges = esc_holder.edges("<Z and |X").vals()
	# positive_edge_list = [e for e in all_edges if e.Center().y < 0]

	# if positive_edge_list:
	# 		_c = positive_edge_list[0]
	return esc_holder


def get_vertical_cross_section_arms():
	arm_len = arm_length
	total_h = pcb_plate_height   # Total height of the T
	flange_w = arm_width  # Width of the top bar
	flange_t = arm_thickness   # Thickness of the top bar
	web_t = arm_thickness      # Thickness of the vertical bar
	web_h = total_h - flange_t
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


def _attach_esc_with_constraints(drone: cq.Assembly, length=esc_holder_length, width=esc_holder_width, 
																 height=esc_holder_height, thickness=esc_holder_thickness):
	drone.add(get_esc_holder(length, width, height, thickness), color=cq.Color("green"), name="esc1")
	drone.add(get_esc_holder(length, width, height, thickness), color=cq.Color("green"), name="esc2")
	drone.add(get_esc_holder(length, width, height, thickness), color=cq.Color("green"), name="esc3")
	drone.add(get_esc_holder(length, width, height, thickness), color=cq.Color("green"), name="esc4")

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


if __name__ == "__main__":
	# show_object(get_arm_with_motor_holder(get_motor_holder_with_X_base()))
	drone = cq.Assembly()

	body = get_X_frame_base()
	drone.add(body, color=cq.Color("yellow"), name="body")

	_attach_arms_with_constraints(drone)
	# _attach_esc_with_constraints(drone)
	# show_object([get_arm_with_motor_holder(get_motor_holder_with_X_base())])
	show_object([drone.toCompound(), get_pcb_and_battery_holder()])
	# show_object([get_vertical_cross_section_arms()])
	print(drone.toCompound().matrixOfInertia(drone.toCompound()))
	exporters.export(drone.toCompound(), "export/drone_x.stl")
	# drone.export("export/drone_x.stl", "STL")