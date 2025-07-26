import sys
import os
from cadquery import exporters

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)

from lib.airfoil import *
from ocp_vscode import show_object

# Points we will use to create spline and polyline paths to sweep over
pts = [(0, 1), (1, 2), (2, 4)]

# Spline path generated from our list of points (tuples)
path = cq.Workplane("XZ").spline(pts)

# Sweep a circle with a diameter of 1.0 units along the spline path we just created
defaultSweep = cq.Workplane("XY").circle(1.0).sweep(path)

# Create the airfoil with parameters optimized for vacuum application
# propeller_airfoil = create_airfoil(
#   chord_length=100.0,
#   max_camber=0.06,     
#   max_camber_pos=0.3,  
#   thickness=0.14       
# )

propeller_model = create_propeller(
    prop_radius=55,
    hub_radius=7.2,
    hub_height=10,
    rotor_hole_radius=3,
    num_blades=4,
    num_sections=6,
    twist_at_hub=40,
    twist_at_tip=12,
    chord_at_hub=15,
    chord_at_tip=10,
    fillet_radius=0.5
)

show_object(propeller_model)
exporters.export(propeller_model, "export/propeller_model.stl")

