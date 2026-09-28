import math

def run_simulation(
    laptop_mass: float = 2.0,       # kg
    tray_mass: float = 0.3,         # kg
    arm1_length: float = 180.0,     # mm
    arm2_length: float = 150.0,     # mm
    arm_width: float = 24.0,        # mm (dimension perpendicular to bending)
    arm_thickness: float = 14.0,    # mm (dimension in the plane of bending)
    theta1_deg: float = 30.0,       # Angle of arm 1 relative to horizontal
    theta2_deg: float = 0.0,        # Angle of arm 2 relative to horizontal
    material: str = "PLA",
    hinge_radius: float = 20.0,     # mm
    hinge_hole_radius: float = 3.2, # mm (M6 bolt)
    hinge_num_teeth: int = 24,
    hinge_tooth_width: float = 2.5, # mm
):
    """
    Simulates the static forces, joint torques, bending stresses, Hirth joint teeth stresses,
    and factors of safety for the armrest laptop stand under load.
    """
    g = 9.81  # m/s^2
    
    # Material properties
    # PLA typical values for FDM 3D printing (assuming 40% infill, 4 perimeters)
    properties = {
        "PLA": {"yield_strength": 35.0e6, "shear_strength": 18.0e6, "elastic_modulus": 2.5e9},
        "PETG": {"yield_strength": 28.0e6, "shear_strength": 14.0e6, "elastic_modulus": 2.1e9},
        "ABS": {"yield_strength": 32.0e6, "shear_strength": 16.0e6, "elastic_modulus": 2.0e9}
    }
    
    prop = properties.get(material, properties["PLA"])
    yield_strength = prop["yield_strength"]
    shear_strength = prop["shear_strength"]
    
    # Convert dimensions to meters
    L1 = arm1_length / 1000.0
    L2 = arm2_length / 1000.0
    b = arm_width / 1000.0       # width
    h = arm_thickness / 1000.0   # thickness/height in bending plane
    
    # Angles to radians
    r1 = math.radians(theta1_deg)
    r2 = math.radians(theta2_deg)
    
    # Weights (N)
    F_laptop = laptop_mass * g
    F_tray = tray_mass * g
    
    # Estimate arm weights based on volume and density of PLA (~1.24 g/cm^3)
    # With 40% infill, effective density is ~ 0.8 g/cm^3 (800 kg/m^3)
    density = 800.0  # kg/m^3
    vol_arm1 = L1 * b * h
    vol_arm2 = L2 * b * h
    
    m_arm1 = vol_arm1 * density
    m_arm2 = vol_arm2 * density
    
    F_arm1 = m_arm1 * g
    F_arm2 = m_arm2 * g
    
    # Horizontal coordinates relative to base clamp pivot (0,0)
    x_joint2 = L1 * math.cos(r1)
    x_tray = x_joint2 + L2 * math.cos(r2)
    
    # Centers of gravity for the arms
    cg_arm1 = (L1 / 2.0) * math.cos(r1)
    cg_arm2 = x_joint2 + (L2 / 2.0) * math.cos(r2)
    
    # --------------------------------------------------------------------------
    # 1. Joint Torques (Moment statics)
    # --------------------------------------------------------------------------
    torque_joint2 = (F_laptop + F_tray) * (L2 * math.cos(r2)) + F_arm2 * ((L2 / 2.0) * math.cos(r2))
    torque_joint1 = (F_laptop + F_tray) * x_tray + F_arm1 * cg_arm1 + F_arm2 * cg_arm2
    
    # --------------------------------------------------------------------------
    # 2. Structural Bending Stresses in Arm Beams
    # --------------------------------------------------------------------------
    I = (b * (h ** 3)) / 12.0
    stress_arm1 = (6.0 * torque_joint1) / (b * (h ** 2))
    stress_arm2 = (6.0 * torque_joint2) / (b * (h ** 2))
    
    fo_safety_arm1 = yield_strength / stress_arm1
    fo_safety_arm2 = yield_strength / stress_arm2
    
    # --------------------------------------------------------------------------
    # 3. M6 Joint Bolt Shear Stress
    # --------------------------------------------------------------------------
    shear_force_bolt2 = F_laptop + F_tray + F_arm2
    shear_force_bolt1 = shear_force_bolt2 + F_arm1
    
    r_bolt = 0.0025  # meters (root radius of M6)
    area_bolt = math.pi * (r_bolt ** 2)
    
    shear_stress_bolt1 = shear_force_bolt1 / area_bolt
    shear_stress_bolt2 = shear_force_bolt2 / area_bolt
    
    bolt_shear_strength = 370.0e6  # Steel shear yield
    fo_safety_bolt1 = bolt_shear_strength / shear_stress_bolt1
    
    # --------------------------------------------------------------------------
    # 4. Hirth Locking Teeth Shear Stress
    # --------------------------------------------------------------------------
    # The torque is resisted by the radial teeth.
    # The average radius at which the teeth act is approx 75% of the outer joint radius.
    r_avg = (hinge_radius * 0.75) / 1000.0  # meters
    
    # Tangential forces acting on the joint teeth interface
    F_tangential1 = torque_joint1 / r_avg
    F_tangential2 = torque_joint2 / r_avg
    
    # Shear area of a single tooth base (tooth_width * radial length)
    radial_len = (hinge_radius - hinge_hole_radius) / 1000.0  # meters
    w_tooth = hinge_tooth_width / 1000.0  # meters
    area_single_tooth = w_tooth * radial_len  # m^2
    
    # Due to 3D printing tolerances, we assume only 50% of the teeth are active
    active_teeth = hinge_num_teeth / 2.0
    total_shear_area = active_teeth * area_single_tooth
    
    shear_stress_teeth1 = F_tangential1 / total_shear_area
    shear_stress_teeth2 = F_tangential2 / total_shear_area
    
    fo_safety_teeth1 = shear_strength / shear_stress_teeth1
    fo_safety_teeth2 = shear_strength / shear_stress_teeth2
    
    # --------------------------------------------------------------------------
    # Output Results
    # --------------------------------------------------------------------------
    print("=" * 60)
    print("           ARMREST STAND MECHANICAL STATICS SIMULATION        ")
    print("=" * 60)
    print(f"Simulation Parameters:")
    print(f"  - Laptop Mass:       {laptop_mass:.2f} kg  ({F_laptop:.1f} N)")
    print(f"  - Tray Mass:         {tray_mass:.2f} kg  ({F_tray:.1f} N)")
    print(f"  - Arm 1 Dimensions:  Length {arm1_length:.1f}mm, Section {arm_width:.1f}x{arm_thickness:.1f}mm")
    print(f"  - Arm 2 Dimensions:  Length {arm2_length:.1f}mm, Section {arm_width:.1f}x{arm_thickness:.1f}mm")
    print(f"  - Angles:            Arm 1 = {theta1_deg}° | Arm 2 = {theta2_deg}°")
    print(f"  - Reach:             Horizontal reach = {x_tray * 1000.0:.1f} mm")
    print(f"  - Material:          {material} (Yield = {yield_strength / 1e6:.1f} MPa | Shear Yield = {shear_strength / 1e6:.1f} MPa)")
    print("-" * 60)
    print("Calculated Torques and Beam Bending Stresses:")
    print(f"  - Joint 1 (Base) Torque: {torque_joint1:.2f} N-m")
    print(f"    * Max Bending Stress:  {stress_arm1 / 1e6:.2f} MPa")
    print(f"    * Factor of Safety:    {fo_safety_arm1:.2f}x ({'SAFE' if fo_safety_arm1 >= 1.5 else 'FAIL/WARNING'})")
    print(f"  - Joint 2 (Elbow) Torque:{torque_joint2:.2f} N-m")
    print(f"    * Max Bending Stress:  {stress_arm2 / 1e6:.2f} MPa")
    print(f"    * Factor of Safety:    {fo_safety_arm2:.2f}x ({'SAFE' if fo_safety_arm2 >= 1.5 else 'FAIL/WARNING'})")
    print("-" * 60)
    print("Hirth Interlocking Locking Teeth Analysis (PLA Shear Stress):")
    print(f"  - Joint 1 Hirth Teeth Tangential Force:  {F_tangential1:.1f} N")
    print(f"  - Joint 1 Hirth Teeth Shear Stress:      {shear_stress_teeth1 / 1e6:.2f} MPa")
    print(f"  - Factor of Safety (Teeth Strip):        {fo_safety_teeth1:.2f}x ({'SAFE' if fo_safety_teeth1 >= 1.5 else 'FAIL/WARNING'})")
    print(f"  - Joint 2 Hirth Teeth Shear Stress:      {shear_stress_teeth2 / 1e6:.2f} MPa")
    print(f"  - Factor of Safety (Teeth Strip):        {fo_safety_teeth2:.2f}x ({'SAFE' if fo_safety_teeth2 >= 1.5 else 'FAIL/WARNING'})")
    print("-" * 60)
    print("M6 Joint Bolt Analysis (Steel Bolt):")
    print(f"  - Joint 1 Bolt Shear Force:  {shear_force_bolt1:.1f} N")
    print(f"  - Joint 1 Bolt Shear Stress: {shear_stress_bolt1 / 1e6:.2f} MPa")
    print(f"  - Factor of Safety:          {fo_safety_bolt1:.1f}x (Extremely Safe)")
    print("=" * 60)
    
    return {
        "torque_joint1": torque_joint1,
        "stress_arm1_mpa": stress_arm1 / 1e6,
        "fo_safety_arm1": fo_safety_arm1,
        "torque_joint2": torque_joint2,
        "stress_arm2_mpa": stress_arm2 / 1e6,
        "fo_safety_arm2": fo_safety_arm2,
        "shear_stress_teeth1_mpa": shear_stress_teeth1 / 1e6,
        "fo_safety_teeth1": fo_safety_teeth1,
    }

if __name__ == "__main__":
    # Case A: Tilted / Articulated position (Arm 1 = 30 deg, Arm 2 = 0 deg)
    run_simulation(theta1_deg=30.0, theta2_deg=0.0)
    
    # Case B: Maximum horizontal reach (Worst-case stress)
    print("\nSimulating Worst-Case Scenario (Both arms fully extended horizontally):")
    run_simulation(theta1_deg=0.0, theta2_deg=0.0)
