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
import pygame
import numpy as np

def instanceof(value, classes):
    if not isinstance(classes, tuple):
        classes = classes,

    if isinstance(value, tuple):
        return tuple in classes

    if value.__class__ in (np.array, np.ndarray) and list in classes:
        return True

    if np.dtype(value.__class__) == np.int64 and int in classes:
        return True

    if np.dtype(value.__class__) == np.float64 and float in classes:
        return True

    if np.dtype(value.__class__) == np.complex128 and complex in classes:
        return True

    return isinstance(value, classes)

def color(h):
	return pygame.Color(*hex_to_rgb(h))

def hex_to_rgb(h, as_dec=False):
    result = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    if as_dec:
        return result[0]/255, result[1]/255, result[2]/255
    return result

def is_iterable(obj):
    try:
        iter(obj)
        return True
    except:
        return False