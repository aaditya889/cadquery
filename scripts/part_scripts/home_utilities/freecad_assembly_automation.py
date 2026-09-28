import FreeCAD as App
import FreeCADGui as Gui
import ImportGui
import math
import os

try:
    from PySide import QtGui, QtCore
except ImportError:
    from PySide2 import QtWidgets as QtGui
    from PySide2 import QtCore

# ==============================================================================
# FREECAD INTERACTIVE SIMULATION MACRO
# ==============================================================================
# INSTRUCTIONS:
# 1. Open FreeCAD.
# 2. Go to Macro -> Macros... -> Create.
# 3. Name it "ArmrestAssemblyComplete.py" and paste this code.
# 4. Click Run! A dialog window will appear.
# 5. Drag the sliders to interactively move the arms and tray!
# ==============================================================================

# Path to exported STEP files
EXPORT_DIR = "/home/aaditya/atelier/synchronous/aaditya/cadquery/scripts/export/armrest_stand"

# Assembly dimensions (must match the cadquery script)
ARM1_LENGTH = 180.0
ARM2_LENGTH = 150.0
ARMREST_THICKNESS = 40.0
CLAMP_LENGTH = 120.0
CLAMP_THICKNESS = 10.0
HINGE_RADIUS = 20.0
HINGE_THICKNESS = 8.0
JOINT_OFFSET_X = CLAMP_LENGTH / 2.0 - HINGE_RADIUS
ARM1_PIVOT_Z = CLAMP_THICKNESS + HINGE_RADIUS

class AssemblySimulator(QtGui.QWidget):
    def __init__(self):
        super(AssemblySimulator, self).__init__()
        self.doc_name = "Armrest_Stand_Assembly"
        self.imported_objects = {}
        self.init_document()
        self.init_ui()
        self.update_assembly()
        
    def init_document(self):
        try:
            if self.doc_name in App.listDocuments():
                App.closeDocument(self.doc_name)
        except Exception:
            pass
            
        self.doc = App.newDocument(self.doc_name)
        App.setActiveDocument(self.doc_name)
        
        parts_to_import = [
            ("1_clamp_top.step", "Clamp_Top", (0.3, 0.5, 0.7)),
            ("2_clamp_bottom.step", "Clamp_Bottom", (0.25, 0.25, 0.25)),
            ("3_articulation_arm_1.step", "Articulation_Arm_1", (0.9, 0.5, 0.2)),
            ("4_articulation_arm_2.step", "Articulation_Arm_2", (0.8, 0.4, 0.1)),
            ("5_tray_mount_bracket.step", "Tray_Mount_Bracket", (0.4, 0.4, 0.4)),
            ("6_laptop_tray.step", "Laptop_Tray", (0.9, 0.8, 0.2)),
            ("7_joint_locking_knob.step", "Joint_Knob_1", (0.8, 0.1, 0.1)),
            ("7_joint_locking_knob.step", "Joint_Knob_2", (0.8, 0.1, 0.1)),
            ("7_joint_locking_knob.step", "Joint_Knob_3", (0.8, 0.1, 0.1))
        ]
        
        print("Importing models...")
        for file_name, label, color in parts_to_import:
            file_path = os.path.join(EXPORT_DIR, file_name)
            if os.path.exists(file_path):
                ImportGui.insert(file_path, self.doc.Name)
                obj = self.doc.Objects[-1]
                obj.Label = label
                gui_obj = Gui.activeDocument().getObject(obj.Name)
                if gui_obj:
                    gui_obj.ShapeColor = color
                self.imported_objects[label] = obj
            else:
                print(f"Warning: {file_path} not found.")
        Gui.SendMsgToActiveView("ViewFit")
                
    def init_ui(self):
        self.setWindowTitle("Interactive Armrest Simulation")
        layout = QtGui.QVBoxLayout()
        
        # Joint 1
        self.slider1 = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider1.setRange(-90, 90)
        self.slider1.setValue(30)
        self.slider1.valueChanged.connect(self.update_assembly)
        layout.addWidget(QtGui.QLabel("Base Pivot (Angle 1)"))
        layout.addWidget(self.slider1)
        
        # Joint 2
        self.slider2 = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider2.setRange(-150, 150)
        self.slider2.setValue(-30)
        self.slider2.valueChanged.connect(self.update_assembly)
        layout.addWidget(QtGui.QLabel("Elbow Pivot (Angle 2)"))
        layout.addWidget(self.slider2)
        
        # Tray Angle
        self.slider3 = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider3.setRange(-90, 90)
        self.slider3.setValue(10)
        self.slider3.valueChanged.connect(self.update_assembly)
        layout.addWidget(QtGui.QLabel("Tray Angle"))
        layout.addWidget(self.slider3)
        
        self.setLayout(layout)
        self.resize(350, 200)
        # Ensure it stays on top of FreeCAD main window
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.show()
        
    def get_vec_from_placement(self, placement, vec):
        # FreeCAD Placement doesn't have multVec, so we apply Rotation then Base
        return placement.Base + placement.Rotation.multVec(vec)

    def update_assembly(self):
        angle1 = self.slider1.value()
        angle2 = self.slider2.value()
        angle3 = self.slider3.value()
        
        if "Clamp_Top" in self.imported_objects:
            self.imported_objects["Clamp_Top"].Placement = App.Placement(App.Vector(0,0,0), App.Rotation(0,0,0))
            
        if "Clamp_Bottom" in self.imported_objects:
            self.imported_objects["Clamp_Bottom"].Placement = App.Placement(
                App.Vector(0, 0, -ARMREST_THICKNESS - CLAMP_THICKNESS),
                App.Rotation(0, 0, 0)
            )
            
        arm1_placement = App.Placement()
        p_joint2 = App.Vector()
        
        if "Articulation_Arm_1" in self.imported_objects:
            arm1 = self.imported_objects["Articulation_Arm_1"]
            p_local = App.Placement(App.Vector(ARM1_LENGTH / 2.0, 0, 0), App.Rotation(0, 0, 0))
            p_rot = App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(0, 1, 0), angle1))
            # Shifted -HINGE_THICKNESS in Y to perfectly mesh with Clamp Top
            p_global = App.Placement(App.Vector(JOINT_OFFSET_X, -HINGE_THICKNESS, ARM1_PIVOT_Z), App.Rotation(0, 0, 0))
            
            arm1_placement = p_global.multiply(p_rot).multiply(p_local)
            arm1.Placement = arm1_placement
            p_joint2 = self.get_vec_from_placement(arm1_placement, App.Vector(ARM1_LENGTH / 2.0, 0, 0))
            
        arm2_placement = App.Placement()
        p_joint3 = App.Vector()
            
        if "Articulation_Arm_2" in self.imported_objects:
            arm2 = self.imported_objects["Articulation_Arm_2"]
            p_local2 = App.Placement(App.Vector(ARM2_LENGTH / 2.0, 0, 0), App.Rotation(0, 0, 0))
            p_rot2 = App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(0, 1, 0), angle1 + angle2))
            # Shifted -HINGE_THICKNESS * 2 in Y to perfectly mesh with Arm 1
            p_global2 = App.Placement(App.Vector(p_joint2.x, -HINGE_THICKNESS * 2, p_joint2.z), App.Rotation(0, 0, 0))
            
            arm2_placement = p_global2.multiply(p_rot2).multiply(p_local2)
            arm2.Placement = arm2_placement
            p_joint3 = self.get_vec_from_placement(arm2_placement, App.Vector(ARM2_LENGTH / 2.0, 0, 0))
            
        bracket_placement = App.Placement()
            
        if "Tray_Mount_Bracket" in self.imported_objects:
            bracket = self.imported_objects["Tray_Mount_Bracket"]
            p_local_b = App.Placement(App.Vector(0, 0, HINGE_RADIUS), App.Rotation(0, 0, 0))
            p_rot_b = App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(0, 1, 0), angle3))
            # Wait, Tray Bracket teeth face -Y (like clamp). We'll place it at -HINGE_THICKNESS * 3 but flipped so it meshes.
            p_global_b = App.Placement(App.Vector(p_joint3.x, -HINGE_THICKNESS * 3, p_joint3.z), App.Rotation(App.Vector(0, 0, 1), 180))
            
            bracket_placement = p_global_b.multiply(p_rot_b).multiply(p_local_b)
            bracket.Placement = bracket_placement
            
        if "Laptop_Tray" in self.imported_objects:
            tray = self.imported_objects["Laptop_Tray"]
            p_local_t = App.Placement(App.Vector(0, 0, HINGE_RADIUS + 6.0), App.Rotation(0, 0, 0))
            tray.Placement = bracket_placement.multiply(p_local_t)
            
        # Place Knobs flushed against the outside flat faces!
        # Knob center is 6mm from its face (12mm thick total).
        if "Joint_Knob_1" in self.imported_objects:
            self.imported_objects["Joint_Knob_1"].Placement = App.Placement(
                App.Vector(JOINT_OFFSET_X, HINGE_THICKNESS / 2.0 + 6.0, ARM1_PIVOT_Z),
                App.Rotation(App.Vector(1, 0, 0), 90)
            )
            
        if "Joint_Knob_2" in self.imported_objects:
            self.imported_objects["Joint_Knob_2"].Placement = App.Placement(
                App.Vector(p_joint2.x, -HINGE_THICKNESS / 2.0 + 6.0, p_joint2.z),
                App.Rotation(App.Vector(1, 0, 0), 90)
            )
            
        if "Joint_Knob_3" in self.imported_objects:
            self.imported_objects["Joint_Knob_3"].Placement = App.Placement(
                App.Vector(p_joint3.x, -HINGE_THICKNESS * 1.5 + 6.0, p_joint3.z),
                App.Rotation(App.Vector(1, 0, 0), 90)
            )
            
        App.ActiveDocument.recompute()

# Ensure we keep a reference to the window so it doesn't get garbage collected
if not hasattr(App, "stand_simulator_gui"):
    App.stand_simulator_gui = None

if App.stand_simulator_gui is not None:
    try:
        App.stand_simulator_gui.close()
    except Exception:
        pass

App.stand_simulator_gui = AssemblySimulator()
