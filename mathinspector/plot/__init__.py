"""
The math inspector console comes with a built-in function `plot` which is
not available in a standard python environment.  As a simple example, let's
plot the point (1,1) in a two-dimensional plane.

>>> plot((1,1))

You can hold down the right mouse button and move the cursor to pan around, and use the mouse
scroll wheel to zoom in and out.  Various options are available in the Plot section of the main
menu.

To draw a line in three dimensional space from the origin to the point (10,10,10), use the command

>>> plot([(0,0,0), (10,10,10)])

Holding down the left mouse button and moving the mouse will rotate the camera,
and the WASD or arrow keys can be used for movement.  The mouse wheel is used for
scaling the entire scene.

Parameter data structure
---
`plot` accepts an arbitrary number of arguments, and each argument will be plotted at the
same time, as long as all of the arguments are either two or three dimensional.

Arguments which are integers, floats, complex numbers, or 2-tuples will be plotted
as two dimensional points, lists of these types of objects will be plotted as lines
connecting each of the specified points.  A list of a list of these types of objects
will be plotted as distinct lines.

An example of a function which draws multiple lines is complex grid

>>> from mathinspector.examples import complex_grid
>>> plot(complex_grid())

Lists of lists of 3-tuples are plotted as solid surfaces, but
you have to be careful how these lists are ordered to ensure all normal
vectors are computed properly for the lighting.  To plot multiple distinct lines
in three dimensions, pass each list of 3-tuples to `plot` as its own argument.

It's also possible to pass a function to plot which returns an array of pixels,
by using the pixelmap key word argument.

An example of a pixelmap function is the Domain Coloring function

>>> from mathinspector.examples import domain_coloring
>>> plot(pixelmap=domain_coloring)

Animating pixelmaps is very computationally expensive, and the
`multiprocess` module is used to try and do as much of the computation in the background
as possible.  The plot window creates an offscreen surface for the purpose
of panning and zooming, and after movement stops for 1 second, it recalculates
the pixels for the current position, while also recomputing the pixels for the
offscreen surface in the background.  This system currently suffers from some flashing and
resolution artifacts which are hard to miss when moving very quickly.

Look for video rendering functionality in an upcoming release to address the
performance issues associated with the most computationally expensive animations.
"""
"""
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

from os import environ
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame

from .plot2d import SDLWindow, OPTIONS as OPTIONS_2D
from .plot3d import OpenGLWindow, OPTIONS as OPTIONS_3D
from .util import instanceof

active_window = None
opengl_window = OpenGLWindow()
sdl_window = SDLWindow()

def plot(*args, **kwargs):
	global active_window

	window = get_window(*args, **kwargs)

	if not window:
		raise Exception("Invalid Parameters")
	elif is_active() and window != active_window:
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
		if callable(arg):
			return False
		if instanceof(arg, (tuple,list)) and len(arg) == 3 and instanceof(arg[0], list) and instanceof(arg[0][0], (int,float)):
			return opengl_window
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
		if active_window and pygame.get_init():
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
	if pygame.display.get_init():
		active_window.close()
