import inspect, pkg_resources, builtins, keyword, math
from sys import builtin_module_names
from pkgutil import iter_modules

INSTALLED_PKGS = sorted([str(i).split(" ")[0] for i in pkg_resources.working_set], key=str.casefold)
BUILTIN_PKGS = sorted([j.name for j in iter_modules()], key=str.casefold)

BUILTIN_CLASS = [i for i in dir(builtins) if inspect.isclass(getattr(builtins, i))]
BUILTIN_FUNCTION = [i for i in dir(builtins) if callable(getattr(builtins, i)) and i not in BUILTIN_CLASS]
BUILTIN_CONSTANT = [i for i in dir(builtins) if i not in BUILTIN_FUNCTION and i not in BUILTIN_CLASS]
BUILTIN_MODULES = builtin_module_names
KEYWORD_LIST = keyword.kwlist

TRIG_FUNCTIONS = [i for i in ("acos", "acosh", "asin", "asinh", "atan", "atan2", "atanh", "cos", "cosh", "degrees", "sin", "sinh", "tan", "tanh")]
MATH_FUNCTIONS = [i for i in dir(math) if callable(getattr(math, i)) and i not in TRIG_FUNCTIONS + ["pow"] and i[:1] != "_"]
MATH_FUNCTIONS.append("power")
MATH_FUNCTIONS.sort()
MATH_CONSTANTS = [i for i in dir(math) if i not in MATH_FUNCTIONS + TRIG_FUNCTIONS and i[:1] != "_"]
