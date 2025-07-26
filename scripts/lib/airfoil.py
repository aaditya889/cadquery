import cadquery as cq
import numpy as np
import math

def create_airfoil(chord_length=100.0, max_camber=0.04, max_camber_pos=0.4, thickness=0.12):
  """
  Create an airfoil for vacuum cleaner rotor using NACA 4-digit approach with smoother leading edge
  """
  # Number of points to generate - increase for smoother curve
  num_points = 200
  
  # Generate x-coordinates with better distribution
  # Using cosine spacing for improved point distribution especially at leading edge
  beta = np.linspace(0, math.pi, num_points)
  x = 0.5 * (1 - np.cos(beta))
  
  # Arrays for coordinates
  y_camber = np.zeros(num_points)
  dyc_dx = np.zeros(num_points)
  yt = np.zeros(num_points)
  x_upper = np.zeros(num_points)
  y_upper = np.zeros(num_points)
  x_lower = np.zeros(num_points)
  y_lower = np.zeros(num_points)
  
  # Calculate camber line and its slope
  for i in range(num_points):
    xx = x[i]
    
    # Calculate mean camber line
    if xx <= max_camber_pos and max_camber_pos > 0:
      y_camber[i] = (max_camber / (max_camber_pos**2)) * (2 * max_camber_pos * xx - xx**2)
      dyc_dx[i] = (2 * max_camber / (max_camber_pos**2)) * (max_camber_pos - xx)
    else:
      y_camber[i] = (max_camber / ((1 - max_camber_pos)**2)) * ((1 - 2 * max_camber_pos) + 2 * max_camber_pos * xx - xx**2)
      dyc_dx[i] = (2 * max_camber / ((1 - max_camber_pos)**2)) * (max_camber_pos - xx)
  
    # Calculate thickness distribution - modified NACA thickness formula
    # Using a slightly modified formula for better leading edge
    # yt[i] = 5 * thickness * (0.2969 * np.sqrt(xx) - 0.1260 * xx - 0.3516 * xx**2 + 0.2843 * xx**3 - 0.1015 * xx**4)
    yt[i] = 4.5 * thickness * (0.33 * np.sqrt(xx) - 0.1260 * xx - 0.3516 * xx**2 + 0.2843 * xx**3 - 0.1015 * xx**4)
    
    # Calculate surface coordinates
    theta = np.arctan(dyc_dx[i])
    
    x_upper[i] = xx - yt[i] * np.sin(theta)
    y_upper[i] = y_camber[i] + yt[i] * np.cos(theta)
    
    x_lower[i] = xx + yt[i] * np.sin(theta)
    y_lower[i] = y_camber[i] - yt[i] * np.cos(theta)

  # Scale all coordinates by chord length
  x_upper = x_upper * chord_length
  y_upper = y_upper * chord_length
  x_lower = x_lower * chord_length
  y_lower = y_lower * chord_length
  
  # Create points for the upper surface
  upper_points = [(x_upper[i], y_upper[i]) for i in range(num_points)]
  
  # Create points for the lower surface in reverse order to connect properly
  lower_points = [(x_lower[num_points-1-i], y_lower[num_points-1-i]) for i in range(num_points)]
  
  # Combine points to form a closed loop
  all_points = upper_points + lower_points
  
  # Create a CadQuery workplane and sketch the airfoil profile
  result = (cq.Workplane("XY")
            .polyline(all_points)
            .close()
            )  # Extrude to create a 3D airfoil with 50 units depth
  
  return result


def create_propeller(
    prop_radius=60.0,
    hub_radius=8.0,
    hub_height=10.0,
    rotor_hole_radius=5,
    num_blades=3,
    num_sections=3,
    twist_at_hub=40.0,
    twist_at_tip=15.0,
    chord_at_hub=18.0,
    chord_at_tip=10.0,
    fillet_radius=1.0
):
    """
    Creates a 3D drone propeller model with smooth blade-to-hub transitions.

    Args:
        prop_radius (float): The total radius of the propeller.
        hub_radius (float): The radius of the central hub.
        hub_height (float): The height of the central hub.
        num_blades (int): The number of propeller blades.
        num_sections (int): The number of airfoil sections to loft for each blade.
        twist_at_hub (float): The blade's twist angle (pitch) in degrees at the hub.
        twist_at_tip (float): The blade's twist angle (pitch) in degrees at the tip.
        chord_at_hub (float): The airfoil chord length at the hub.
        chord_at_tip (float): The airfoil chord length at the tip.
        fillet_radius (float): The radius of the fillet on the hub edges.

    Returns:
        cadquery.Workplane: A workplane containing the final 3D propeller model.
    """
    blade_length = prop_radius - hub_radius
    blade_thickness_ratio = 0.20 # Matches the thickness used in create_airfoil
    
    # A list to hold the 2D airfoil cross-sections (as Wires)
    airfoil_sections = []
    hub = (cq.Workplane("XY")
          .circle(hub_radius)
          .extrude(hub_height)
          .translate((0, 0, -hub_height / 1.3)) # Center hub vertically
          )
    hub = hub.faces(">Z").circle(rotor_hole_radius).cutThruAll()

    # --- 1. Generate the cross-sections for a single blade ---
    for i in range(num_sections):
        print(f"section: {i}")
        # Determine position along the blade (0.0 at hub, 1.0 at tip)
        fraction = i / (num_sections - 1)
        
        # Interpolate geometric properties based on the fraction along the blade
        current_twist = twist_at_hub + fraction * (twist_at_tip - twist_at_hub)
        current_chord = chord_at_hub + fraction * (chord_at_tip - chord_at_hub)
        
        # Calculate the intended radial position for this section
        radial_pos = hub_radius*0.1 + fraction * blade_length
        
        # For the root section (i=0), we pull it slightly inside the hub.
        # This creates a deliberate overlap, making the final boolean union
        # operation much more robust and less likely to fail or hang.
        if i == 0:
            translation_radius = hub_radius * 0.98 # Place it just inside the hub
        else:
            translation_radius = radial_pos
        print(f"D1")
        # --- 2. Create the wire for the current section ---
        # Special handling for the root section to create a smooth blend
        if i == 0:
            # Create an elliptical base on the XZ plane for a smooth transition
            x_radius = current_chord / 4.0
            z_radius = (current_chord * blade_thickness_ratio) / 4.0
            
            print(f"D2")
            chord_length = hub_height / 1.2
            blend_shape = create_airfoil(
                            chord_length=chord_length,
                            max_camber=0.1,
                            max_camber_pos=0.3,
                            thickness=blade_thickness_ratio
                        ).wire().val()
            
            # The blend shape is already on the XZ plane, so we just twist and translate
            transformed_wire = (
                blend_shape
                .rotate((0, 0, 0), (1, 0, 0), 90) # Apply twist
                .rotate((0, 0, 0), (0, 1, 0), current_twist) # Apply twist
                # .translate((chord_length * math.cos(current_twist * math.pi/180), 0, -chord_length * math.sin(current_twist * math.pi/180)))
                )
            print(f"D3")
        else:
            # Create the standard airfoil shape for the rest of the blade
            airfoil_profile = create_airfoil(
                chord_length=current_chord,
                max_camber=0.06,
                max_camber_pos=0.3,
                thickness=blade_thickness_ratio
            )
            print(f"D4")
        
            airfoil_wire = airfoil_profile.wire().val()
        
            # Transform the airfoil wire to its 3D position and orientation
            transformed_wire = (
                airfoil_wire
                .rotate((0, 0, 0), (1, 0, 0), 90)      # Orient to XZ plane
                .rotate((0, 0, 0), (0, 1, 0), current_twist) # Apply twist
                .translate((0, translation_radius, 0))      # Move to its radial position
            )
            print(f"D5")
                
        airfoil_sections.append(transformed_wire)

    # --- 3. Create the 3D blade by lofting through the sections ---
    print(f"D6")
    # print(airfoil_sections)
    # return airfoil_sections
    single_blade = cq.Solid.makeLoft(airfoil_sections)
    print(f"D7")
    
    # --- 4. Create the central hub with filleted edges ---

    # Add fillets to the top and bottom edges of the hub for a smoother look
    if fillet_radius > 0:
        hub = hub.edges(">Z or <Z").fillet(fillet_radius)
    
    # --- 5. Pattern the blades around the hub ---
    all_blades = cq.Workplane("XY")
    angle_step = 360.0 / num_blades
    for i in range(num_blades):
        angle = i * angle_step
        # The blade was built along the Y-axis. We rotate it around the Z-axis for the pattern.
        rotated_blade = single_blade.rotate((0, 0, 0), (0, 0, 1), angle)
        all_blades.add(rotated_blade)
        
    # --- 6. Combine the hub and all blades into a single object ---
    # all_blades = all_blades.combine().clean()
    print("Combining...")
    all_blades = all_blades.combine(glue=True)
    print("Taking the union...")
    propeller = hub.union(all_blades.val(), glue=True)
    print(f"Creating the rotor slot...")
    rotor_hole = cq.Workplane("XY").circle(rotor_hole_radius).extrude(hub_height).translate((0, 0, -hub_height / 1.3))
    # propeller = propeller.cut(rotor_hole)
    print(f"Done!")
    # propeller = propeller.clean()
    # propeller = all_blades.combine(glue=True)
    
    return propeller