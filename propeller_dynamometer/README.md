# Propeller dynamometer

Our test stand for measuring a propeller's thrust and torque, from the 3D-printed drone's props up to 1.5 m delivery-class
rotors, with its battery cell and pack rig. Each document exists once, as markdown; the PDFs and the vendor zip are
generated from it.

| File | What it is |
|---|---|
| `propeller_dynamometer_theory.md` | Theory: flexures, sensor dynamics, torque arm, calibration, uncertainty |
| `propeller_dynamometer_design.md` | Our design with every number, and the battery cell rig (§12) |
| `propeller_dynamometer_manufacturing_package.md` | Everything vendors need, plus our questions, answer log and open decisions (the vendor edition leaves those out) |
| `battery_cell_rig_theory.md` | Theory of the battery cell rig |
| `dynamometer_sizing.py` | Loads, load cells, frequencies, uncertainty |
| `dynamometer_structure.py` | Stability, blade-off, containment, members, bolts |
| `battery_cell_rig_sizing.py` | The battery cell rig's numbers |
| `build_pdfs_and_vendor_zip.sh` | Makes every PDF and a dated vendor zip in `generated_pdfs_and_vendor_zip/` (build output, ignored by git) |
| `markdown_to_pdf.js` | The converter the build uses; also makes the vendor edition |
| `../scripts/sketch_scripts/projects/prop_dyno.py` | The CAD, both heads: STEP per part, assembly, part lists; `prop_dyno_drawings.py` next to it makes the drawing set |
