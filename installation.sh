pip3 install cadquery
curl -LO https://github.com/CadQuery/CQ-editor/releases/download/nightly/CQ-editor-master-Linux-x86_64.sh
sh CQ-editor-master-Linux-x86_64.sh
rm CQ-editor-master-Linux-x86_64.sh

# Add this to your .bashrc or .bash_profile
echo "export PATH=${PATH}:/home/aaditya/cq-editor/bin/" >> ~/.bashrc

# Install ocp-cad-viewer vs code extension
code --install-extension opencaesar.ocp-cad-viewer
# Open the extension from the sidebar and initialise all the installtions from there
