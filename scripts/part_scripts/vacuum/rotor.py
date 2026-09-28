from lib.airfoil import *
from ocp_vscode import show_object

# Create the airfoil with parameters optimized for vacuum application
vacuum_airfoil = create_airfoil(
  chord_length=100.0,
  max_camber=0.06,     
  max_camber_pos=0.3,  
  thickness=0.14       
)

show_object(vacuum_airfoil)

# You can visualize or export the model using:
# vacuum_airfoil.toSvg()
# vacuum_airfoil.exportStep("vacuum_rotor_airfoil.step")
