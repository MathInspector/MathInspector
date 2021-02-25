import inspect, pkg_resources, builtins, keyword
from sys import builtin_module_names
from pkgutil import iter_modules

INSTALLED_PKGS = sorted([str(i).split(" ")[0] for i in pkg_resources.working_set], key=str.casefold)
BUILTIN_PKGS = sorted([j.name for j in iter_modules()], key=str.casefold)

BUILTIN_CLASS = [i for i in dir(builtins) if inspect.isclass(getattr(builtins, i))]
BUILTIN_FUNCTION = [i for i in dir(builtins) if callable(getattr(builtins, i)) and i not in BUILTIN_CLASS]
BUILTIN_CONSTANT = [i for i in dir(builtins) if i not in BUILTIN_FUNCTION and i not in BUILTIN_CLASS]
BUILTIN_MODULES = builtin_module_names
KEYWORD_LIST = keyword.kwlist
