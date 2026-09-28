from ocp_vscode import show_object

import cadquery as cq
import math

def create_vacuum_rotor(
        outer_diameter=180.0,       # Outer diameter of the rotor in mm
        inner_diameter=40.0,        # Hub diameter in mm
        height=50.0,                # Rotor height/thickness in mm
        num_blades=9,               # Number of blades
        blade_thickness=3.0,        # Thickness of blades
        blade_curve=30.0,           # Curvature angle of blades in degrees
        hub_height=60.0,            # Height of the central hub
        motor_shaft_diameter=12.0,  # Motor shaft diameter for mounting
        shroud_thickness=3.0,       # Thickness of outer shroud
        include_shroud=True         # Whether to include an outer shroud
    ):
    """
    Create a complete vacuum rotor with curved blades and mounting hub
    """
    # Create hub
    hub_radius = inner_diameter / 2
    hub = (cq.Workplane("XY")
           .circle(hub_radius)
           .extrude(hub_height)
           .faces(">Z")
           .chamfer(2.0))  # Add chamfer for aesthetics
    
    # Create motor shaft hole
    shaft_hole = (cq.Workplane("XY")
                 .circle(motor_shaft_diameter / 2)
                 .extrude(hub_height + 2))  # Make it slightly longer for clean boolean
    
    # Subtract shaft hole from hub
    hub = hub.cut(shaft_hole)
    
    # Create a flat key for the motor shaft (to prevent rotation)
    key_width = motor_shaft_diameter * 0.2
    key_depth = motor_shaft_diameter * 0.15
    key_slot = (cq.Workplane("XY")
                .rect(key_width, motor_shaft_diameter + 2)
                .extrude(hub_height + 2)
                .translate((hub_radius - key_depth, 0, 0)))
    
    # Cut key slot from hub
    hub = hub.cut(key_slot)
    
    # Calculate blade parameters
    radius = outer_diameter / 2
    blade_length = radius - hub_radius
    
    # Create blades using a sweep approach for curved blades
    all_blades = cq.Workplane("XY")
    
    for i in range(num_blades):
        angle_deg = i * (360.0 / num_blades)
        
        # Create a curved path for the blade
        path_points = []
        steps = 10  # Number of points on the path
        
        for step in range(steps + 1):
            t = step / steps  # Parameter from 0 to 1
            
            # Calculate angle along the curve
            current_angle = math.radians(angle_deg - blade_curve * t)
            
            # Calculate radius at this point
            current_radius = hub_radius + blade_length * t
            
            # Calculate position
            x = current_radius * math.cos(current_angle)
            y = current_radius * math.sin(current_angle)
            z = 0
            
            path_points.append((x, y, z))
        
        # Create a rectangular cross-section for the blade
        blade_width = blade_length * 0.25  # Blade gets wider toward tip
        
        # Create blade as a solid sweep along the path
        for j in range(len(path_points) - 1):
            # Create a segment connecting two points on the path
            p1 = path_points[j]
            p2 = path_points[j+1]
            
            # Calculate vector from p1 to p2
            vec_x = p2[0] - p1[0]
            vec_y = p2[1] - p1[1]
            length = math.sqrt(vec_x**2 + vec_y**2)
            
            # Calculate perpendicular vector for width
            perp_x = -vec_y / length
            perp_y = vec_x / length
            
            # Calculate width at this point (wider at tip)
            width_factor = (j + 0.5) / len(path_points)
            local_width = blade_width * (0.5 + width_factor)
            
            # Create points for a rectangular segment
            rect_points = [
                (p1[0] + perp_x * local_width/2, p1[1] + perp_y * local_width/2),
                (p1[0] - perp_x * local_width/2, p1[1] - perp_y * local_width/2),
                (p2[0] - perp_x * local_width/2, p2[1] - perp_y * local_width/2),
                (p2[0] + perp_x * local_width/2, p2[1] + perp_y * local_width/2)
            ]
            
            # Create a polygon and extrude it
            segment = (cq.Workplane("XY")
                      .polyline(rect_points)
                      .close()
                      .extrude(height))
            
            # Union with all blades
            all_blades = all_blades.union(segment)
    
    # Combine hub and blades
    rotor = hub.union(all_blades)
    
    # Add optional shroud
    if include_shroud:
        outer_shroud = (cq.Workplane("XY")
                       .circle(radius + shroud_thickness)
                       .circle(radius)  # Inner circle
                       .extrude(height))
        
        # Combine with rotor
        rotor = rotor.union(outer_shroud)
    
    return rotor

# Create a vacuum rotor with optimized parameters
vacuum_rotor = create_vacuum_rotor(
    outer_diameter=180.0,   # Size appropriate for medium vacuum cleaner
    inner_diameter=40.0,
    height=50.0,
    num_blades=9,           # Changed to 9 for better coverage
    blade_thickness=3.0,
    blade_curve=35.0,       # More curve for better airflow
    hub_height=60.0,
    motor_shaft_diameter=12.0,
    shroud_thickness=3.0,
    include_shroud=True     # Shroud improves efficiency
)

# Export the model
# vacuum_rotor.exportStep("vacuum_rotor_complete.step")

# To visualize in a GUI if available (useful for debugging)
# show_object(vacuum_rotor)

# For headless operation, you might want to export to STL for 3D printing
# vacuum_rotor.exportStl("vacuum_rotor.stl")

show_object(vacuum_rotor)