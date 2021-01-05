import numpy as np
import inspect, os, platform
from style import Color

def getrandom(min, max):
    N = 10
    max_val, min_val = 1, -1
    range_size = (max_val - min_val)  # 2
    np.random.rand(N) * range_size + min_val

def fontcolor(value, as_string=False):
    result = "blue"
    if isinstance(value, str):
        result = "yellow"
    elif isinstance(value, dict):
        result = "grey"
    elif isinstance(value, int) or isinstance(value, float) or isinstance(value, complex):
        result = "purple"
    elif callable(value) or value is None:
        result = "red"
    return result if as_string else getattr(Color, result.upper())

def classname(obj):
    if inspect.isfunction(obj) and obj.__module__:
        return obj.__module__ + "." + obj.__name__
    elif obj.__class__.__module__ and hasattr(obj, "__name__"):
        return obj.__class__.__module__ + "." + obj.__name__
    return obj.__class__.__name__

def name_ext(file):
    return os.path.splitext(os.path.basename(file))

def open_editor(file):
    if platform.system() == "Windows":
        command = "start " + file
    elif platform.system() == "Darwin":
        command = "open " + file
    os.system(command)

def instanceof(value, classes):
    if not isinstance(classes, tuple):
        classes = classes, 

    if isinstance(value, tuple) and tuple in classes:
        return True

    if np.dtype(value.__class__) == np.object_ and list in classes:
        return True

    if np.dtype(value.__class__) == np.int64 and int in classes:
        return True

    if np.dtype(value.__class__) == np.float64 and float in classes:
        return True

    if np.dtype(value.__class__) == np.complex128 and complex in classes:
        return True 

    return isinstance(value, classes)        