import inspect, os, platform, sys, pkg_resources, builtins, keyword, math
from sys import builtin_module_names
from pkgutil import iter_modules

BUTTON_RIGHT = '<Button-3>' if platform.system() == 'Windows' else '<Button-2>'
BUTTON_RELEASE_RIGHT = '<ButtonRelease-3>' if platform.system() == 'Windows' else '<ButtonRelease-2>'
BUTTON_RIGHT_MOTION = '<B3-Motion>' if platform.system() == 'Windows' else '<B2-Motion>'
CONTROL_KEY = 'Control' if platform.system() == 'Windows' else 'Command'
BASEPATH = sys._MEIPASS if hasattr(sys, "_MEIPASS") else os.path.abspath(os.path.join(__file__, "../../"))
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
FONTSIZE = "12"

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
