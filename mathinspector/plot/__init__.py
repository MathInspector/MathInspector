from os import environ
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame

from .plot2d import SDLWindow, OPTIONS as OPTIONS_2D
from .plot3d import OpenGLWindow, OPTIONS as OPTIONS_3D
from .util import instanceof
from .example import *

active_window = None
opengl_window = OpenGLWindow()
sdl_window = SDLWindow()

def plot(*args, **kwargs):
	global active_window
	
	window = get_window(*args, **kwargs)
	for i in args:
		if instanceof(i, PixelMap):
			kwargs["pixelmap"] = i
			args = tuple([j for j in args if j != i])

	if not window:
		raise Exception("Invalid Parameters")
	elif active_window and window != active_window:
		print(Exception("Can't plot 2D and 3D at the same time."))
		return
	active_window = window
	active_window.plot(*args, **kwargs)

def is_active():
	return pygame.display.get_init()

def get_window(*args, **kwargs):
	if "pixelmap" in kwargs:
		return sdl_window

	for arg in args:
		if instanceof(arg, PixelMap):
			return sdl_window
		if callable(arg):
			return False
		if instanceof(arg, (int,float,complex)):
			return sdl_window if len(args) > 1 else False
		if instanceof(arg, tuple):
			if len(arg) == 1 and instanceof(arg[0], complex):
				return sdl_window
			if len(arg) == 2 and instanceof(arg[0], (int,float)):
				return sdl_window
			if len(arg) == 3 and instanceof(arg[0], (int,float)):
				return opengl_window
			else:
				return get_window(*arg)
		if instanceof(arg, list):
			if len(arg) == 3 and instanceof(arg[0], list) and len(arg[0]) == len(arg[1]) == len(arg[2]):
				return opengl_window
			return get_window(*arg)
	return False

def config(**kwargs):
	if kwargs:
		OPTIONS_2D.update(kwargs)
		OPTIONS_3D.update(kwargs)
		if active_window:
			active_window.config(**kwargs)
		return
	
	if not active_window: 
		return OPTIONS_2D
	return OPTIONS_2D if active_window == sdl_window else OPTIONS_3D

def animate(delay, callback):
	active_window.animate(delay, callback)

def update(*args, **kwargs):
	if active_window:
		active_window.update(*args, **kwargs)
		return

def close():
	active_window.close()
