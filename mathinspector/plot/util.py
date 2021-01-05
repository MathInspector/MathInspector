import pygame
import numpy as np

def instanceof(value, classes):
    if not isinstance(classes, tuple):
        classes = classes, 

    if isinstance(value, tuple):
        return tuple in classes

    if np.dtype(value.__class__) == np.object_ and list in classes:
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