"""
Math Inspector: a visual programming environment for scientific computing
Copyright (C) 2021 Matt Calhoun

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from pkg_resources import resource_filename
import inspect, os, platform, sys, pkg_resources, builtins, keyword, math
from sys import builtin_module_names
from pkgutil import iter_modules

SYSTEM = platform.system()
BUTTON_RIGHT = '<Button-3>' if SYSTEM in ("Windows", "Linux") else '<Button-2>'
BUTTON_RELEASE_RIGHT = '<ButtonRelease-3>' if SYSTEM in ("Windows", "Linux") else '<ButtonRelease-2>'
BUTTON_RIGHT_MOTION = '<B3-Motion>' if SYSTEM in ("Windows", "Linux") else '<B2-Motion>'
CONTROL_KEY = 'Control' if SYSTEM in ("Windows", "Linux") else 'Command'
if hasattr(sys, "_MEIPASS"):
    BASEPATH = os.path.join(
        sys._MEIPASS,
        "assets" if SYSTEM in ("Windows", "Linux") else "../Resources/assets")
    if SYSTEM == "Windows":
        AUTOSAVE_PATH = os.path.join(os.path.join(os.getenv('LOCALAPPDATA'), "MathInspector"), "autosave.math")
    else:
        AUTOSAVE_PATH = os.path.join(BASEPATH, "autosave.math")
else:
    BASEPATH = resource_filename("mathinspector", "assets")
    AUTOSAVE_PATH = os.path.join(BASEPATH, "autosave.math")

MESSAGE_TIMEOUT = 4000

INSTALLED_PKGS = sorted([str(i).split(" ")[0] for i in pkg_resources.working_set], key=str.casefold)
BUILTIN_PKGS = sorted([j.name for j in iter_modules()], key=str.casefold)

BUILTIN_CLASS = [i for i in dir(builtins) if inspect.isclass(getattr(builtins, i))]
BUILTIN_FUNCTION = [i for i in dir(builtins) if callable(getattr(builtins, i)) and i not in BUILTIN_CLASS]
BUILTIN_CONSTANT = [i for i in dir(builtins) if i not in BUILTIN_FUNCTION and i not in BUILTIN_CLASS]
BUILTIN_MODULES = builtin_module_names
KEYWORD_LIST = keyword.kwlist

ZOOM_IN = 1.1
ZOOM_OUT = 0.9
HITBOX = 32
FONTSIZE = "12" # TODO - refactor this into the rest of the FONTSIZE stuff
PROMPT_FONTSIZE = 18.5

if SYSTEM in ("Windows", "Linux"):
    FONT = "LucidaConsole 12"
    DOC_FONT = "Nunito-ExtraLight 12"
    FONT_SIZE = {
        "extra-small": "8",
        "small": "10",
        "default": "12",
        "medium": "16",
        "large": "18",
        "extra-large": "22",
    }
    ITEM_FONTSIZE = {
        "name": "14",
        "class": "8",
        "value": "12",
        "argname": "8",
        "argvalue": "10",
    }
else:
    FONT = "Menlo 15"
    DOC_FONT = "Nunito-ExtraLight 16"
    FONT_SIZE = {
        "extra-small": "12",
        "small": "14",
        "default": "15",
        "medium": "18",
        "large": "22",
        "extra-large": "24",
    }
    ITEM_FONTSIZE = {
        "name": "18",
        "class": "12",
        "value": "16",
        "argname": "8",
        "argvalue": "12",
    }

EXCLUDED_MODULES = [
    "absolute_import",
    "division",
    "print_function",
    "testing",
    "version",
    "add_newdoc",
    "add_newdocs",
    "add_docstring",
    "add_newdoc_ufunc"
]

# EXCLUDED_SUBMODULES = INSTALLED_PKGS + BUILTIN_PKGS

EXCLUDED_DIR = [
    "__pycache__",
    ".git"
]

EXCLUDED_FILES = [
    ".DS_Store",
    "__pycache__",
]

EXCLUDED_EXT = [
    ".pyc",
    ".DS_Store",
    ".math"
]
