import sys
import os
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
    prop_radius=75,
    hub_radius=10,
    hub_height=20,
    num_blades=3,
    twist_at_hub=35,
    twist_at_tip=12,
    chord_at_hub=20,
    chord_at_tip=12
)

# propeller_airfoil = propeller_airfoil.twistExtrude(100, 20)
show_object(propeller_model)

# You can visualize or export the model using:
# vacuum_airfoil.toSvg()
# vacuum_airfoil.exportStep("vacuum_rotor_airfoil.step")
