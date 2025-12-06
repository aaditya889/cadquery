import cadquery as cq
from cadquery import exporters
from ocp_vscode import show_object
import os, sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)
from lib.injected_parts.hooks import *

male_hook_1 = create_male_u_hook()
male_hook_2 = create_male_u_hook()
assembled = cq.Assembly()
assembled.add(male_hook_1, loc=cq.Location(cq.Vector(0, 0, 0)), name="male_hook_1", color="red")
assembled.add(male_hook_1, loc=cq.Location(cq.Vector(0, 0, 5)), name="male_hook_2", color="blue")

show_object(assembled)