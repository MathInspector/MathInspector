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
import numpy as np
import inspect, os, platform
from ..style import Color

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
    if inspect.isclass(obj):
        return obj.__name__
    elif inspect.isfunction(obj) and obj.__module__:
        return obj.__module__ + "." + obj.__name__
    elif obj.__class__.__module__ and hasattr(obj, "__name__"):
        return obj.__class__.__module__ + "." + obj.__name__
    return obj.__class__.__name__

def name_ext(file):
    return os.path.splitext(os.path.basename(file))

def open_editor(file):
    if platform.system() in ("Windows", "Linux"):
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
