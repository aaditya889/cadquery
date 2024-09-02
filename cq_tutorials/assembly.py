from cq_server.ui import ui, show_object, debug
import cadquery as cq


# Use the Point constraint to position boxes relative to an arc
line = cq.Edge.makeCircle(radius=10, angle1=0, angle2=180)
box = cq.Workplane().box(1, 1, 1)

assy = cq.Assembly()
assy.add(line, name="line")

# position the red box on the center of the arc
assy.add(box, name="box0", color=cq.Color("red"))
assy.constrain("line", "box0", "Point")

# position the green box at a normalized distance of 0.8 along the arc
# position0 = line.positionAt(0.8)
# assy.add(box, name="box1", color=cq.Color("green"))
# assy.constrain(
#     "line",
#     cq.Vertex.makeVertex(*position0.toTuple()),
#     "box1",
#     box.val(),
#     "Point",
# )

# # position the orange box 2 units in any direction from the green box
# assy.add(box, name="box2", color=cq.Color("orange"))
# assy.constrain(
#     "line",
#     cq.Vertex.makeVertex(*position0.toTuple()),
#     "box2",
#     box.val(),
#     "Point",
#     param=2,
# )

# # position the blue box offset 2 units in the x direction from the green box
# position1 = position0 + cq.Vector(2, 0, 0)
# assy.add(box, name="box3", color=cq.Color("blue"))
# assy.constrain(
#     "line",
#     cq.Vertex.makeVertex(*position1.toTuple()),
#     "box3",
#     box.val(),
#     "Point",
# )

assy.solve()
show_object(assy)