#!/bin/bash
echo -e "\n--- PROVISIONING SERVER ---\n"
sudo apt update >/dev/null 2>&1
sudo apt install -y software-properties-common >/dev/null 2>&1
sudo apt install -y python3-pip >/dev/null 2>&1

echo -e "\n--- INSTALLING TKINTER ---\n"
sudo apt install -y python3-tk >/dev/null 2>&1

echo -e "\n--- INSTALLING PYTHON MODULES ---\n"
pip3 install -U pip >/dev/null 2>&1
sudo apt install -y mesa-common-dev libgl1-mesa-dev libglu1-mesa-dev
sudo apt install -y mesa-utils libgl1-mesa-glx
sudo apt install -y mesa-libGLw-dev.x86_64
# sudo apt-get install -y libglu1-mesa-dev freeglut3-dev mesa-common-dev >/dev/null 2>&1
python3 -m pip install -y /MathInspector >/dev/null 2>&1

echo -e "\n--- COPYING STYLE FILES ---\n"
sudo cp /MathInspector/mathinspector/style/arc.tcl /usr/local/lib/python3.6/dist-packages/ttkthemes/png/arc/
sudo cp -r /MathInspector/mathinspector/style/arc/ /usr/local/lib/python3.6/dist-packages/ttkthemes/png/arc/
