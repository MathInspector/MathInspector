"""
Usage:
    MathInspector/pkg$ python -m pip install ../ PyInstaller
    MathInspector/pkg$ python build.py
"""
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
