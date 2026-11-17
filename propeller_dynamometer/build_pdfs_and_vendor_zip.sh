#!/bin/sh
# Makes the PDFs of the dynamometer's documents and the zip to send to vendors, in generated_pdfs_and_vendor_zip/.
# That folder is build output: recreated on every run, ignored by git. The markdown files here are the only copy of each
# document; edit them, then run this.
#   PDFs: theory, design, manufacturing package (full, for us), its vendor edition, battery cell rig theory, part drawings.
#   Vendor zip: the vendor edition, the part drawings, and for each head configuration one STEP per part, the assembly
#   STEP, parts.csv, fasteners.csv, holes.csv. No scripts, no markdown.
# The CAD exports come from ../scripts/sketch_scripts/projects/prop_dyno.py (both heads) and prop_dyno_drawings.py: run
# those first if the CAD changed.
# Run from anywhere:  sh /home/aaditya/atelier/synchronous/aaditya/cadquery/propeller_dynamometer/build_pdfs_and_vendor_zip.sh
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=$HERE/generated_pdfs_and_vendor_zip
CAD=$HERE/../scripts/sketch_scripts/export/prop_dyno
rm -rf "$OUT" && mkdir -p "$OUT"
for d in propeller_dynamometer_theory propeller_dynamometer_design propeller_dynamometer_manufacturing_package battery_cell_rig_theory; do
    node "$HERE/markdown_to_pdf.js" "$HERE/$d.md" "$OUT/$d.pdf"
done
node "$HERE/markdown_to_pdf.js" "$HERE/propeller_dynamometer_manufacturing_package.md" \
    "$OUT/propeller_dynamometer_manufacturing_package_for_vendors.pdf" --vendor-edition
cp "$CAD/prop_dyno_drawings.pdf" "$OUT/propeller_dynamometer_part_drawings.pdf"

NAME=propeller_dynamometer_vendor_package_$(date +%Y-%m-%d)
T=$(mktemp -d)
mkdir -p "$T/$NAME/large_head_configuration" "$T/$NAME/small_head_configuration"
cp "$OUT/propeller_dynamometer_manufacturing_package_for_vendors.pdf" "$T/$NAME/propeller_dynamometer_manufacturing_package.pdf"
cp "$OUT/propeller_dynamometer_part_drawings.pdf" "$T/$NAME/"
cp "$CAD"/L/*.step "$CAD"/L/*.csv "$T/$NAME/large_head_configuration/"
cp "$CAD"/S/*.step "$CAD"/S/*.csv "$T/$NAME/small_head_configuration/"
(cd "$T" && zip -qr "$OUT/$NAME.zip" "$NAME")
rm -r "$T"
echo "$OUT/$NAME.zip  $(du -h "$OUT/$NAME.zip" | cut -f1)"
