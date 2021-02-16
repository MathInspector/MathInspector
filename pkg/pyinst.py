import shutil
from PyInstaller.__main__ import run as pyinstaller
from platform import system

SYSTEM = system()
SPEC = {
   "Linux": "mathinspector.linux.spec",
   "Darwin": "mathinspector.macos.spec",
   "Windows": "mathinspector.win.spec",
}

shutil.rmtree("build/", ignore_errors=True)
shutil.rmtree("dist/", ignore_errors=True)
pyinstaller([SPEC[SYSTEM], "--noconfirm"])

if SYSTEM == "Darwin":
    shutil.copytree("assets", "dist/mathinspector.app/Contents/assets")
    shutil.copytree("/Library/Frameworks/Python.framework/Versions/3.7/lib/tcl8", "dist/mathinspector.app/Contents/MacOS")
