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

d_slot_thickness = 2

def get_pcb_arms():
  d_slot = cq.Workplane("XY").workplane().radiusArc((20.6, 0, 0), 20.6/2).close().extrude(d_slot_thickness).faces(">Z").cboreHole(3, 4, d_slot_thickness/1.5)
  mate_face = d_slot.faces("<Y").tag("mateFace")
  mate_edge = d_slot.faces("<Y").edges("<Z").tag("mateFace")

  pcb_arm = (cq.Workplane("XY").workplane().box(5, 10, 50)
             .faces(">Y").tag("mateFace").end()
             .edges("<Z").tag("mateEdge").end()
             )
  
  assembled = (cq.Assembly()
               .add(d_slot, color="blue", name="d_slot")
               .add(pcb_arm, color="red", name="pcb_arm")
               .constrain
               )



  return {"part": assembled, "mateFace": mate_face, "mateEdge": mate_edge}


show_object([get_pcb_arms()])

