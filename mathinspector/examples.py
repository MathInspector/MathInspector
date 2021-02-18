"""
The functions in this module should provide an excellent starting place for learning about how
math inspector works, and what makes it different from other programming environments
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

import numpy as np
from skimage import measure as _measure
from skimage.color import hsv2rgb as _hsv2rgb

NEG_Z = -1e-12
POS_Z = 1e-12

def complex_grid(x_min=-10, x_max=10, y_min=-10, y_max=10, num=25):
	"""
creates a grid of intersecting lines made of complex numbers

Parameters
----------
x_min : float
    the minimum x-coordinate
x_max : float
    the maximum x-coordinate
y_min : float
	the minimum y-coordinate
y_max : float
    the maximum y-coordinate
num : int
	the number of grid lines per axis


Notes
-----
If the grid passes through either the x or y axis, then this function returns a grid for each quadrant of the plane occupied by the grid.  This is important when using complex_grid as input to a ufunc to avoid visual artificats that result from points which are very close together but have a different sign.

Examples
--------

To create a complex grid, we will use the numpy ``meshgrid`` method, the first step is to create two arrays of evenly spaced numbers

>>> from numpy import linspace, meshgrid, transpose
>>> x = linspace(0,10)
>>> y = linspace(0,10)

We can then create a set of lines `Z` in the following way

>>> Y,X = meshgrid(y,x)
>>> Z = X + 1j*Y

To plot the grid, we transponse `Z` to get the lines to go in the other direction as well

>>> plot(Z,transpose(Z))
    """
	if (x_min < 0 and x_max > 0) or (y_min < 0 and y_max > 0):
		return (*complex_grid(x_min, NEG_Z, y_min, NEG_Z, int(num/2)),
			*complex_grid(POS_Z, x_max, y_min, NEG_Z, int(num/2)),
			*complex_grid(x_min, NEG_Z, POS_Z, y_max, int(num/2)),
			*complex_grid(POS_Z, x_max, POS_Z, y_max, int(num/2)))

	x = np.linspace(x_min, x_max, num+1)
	y = np.linspace(y_min, y_max, num+1)
	X, Y = np.meshgrid(x,y)
	Z = X + 1j*Y

	return Z, np.transpose(Z)

def power(points, exponent):
	"""
draws the result of taking the power of a set of points to an arbitrary exponent

Parameters
----------
points : array
    a numpy array

exponent: float
	the exponent


Examples
--------

>>> from mathinspector.examples import complex_grid
>>> from numpy import power
>>> t=1
>>> plot(power(complex_grid(), 2))

Animation:

>>> app.animate("power", argname="x2", start=2, stop=-2, step=-0.005, delay=0.01)

    """
	return points**exponent

def times_table(factor, start=0, end=199):
	"""
creates a visual representation of the remainders of a number modulo a factor f,
by representing these numbers as points along a circle

Parameters
----------
factor : float
    the minimum x-coordinate
start : int
    the maximum x-coordinate
end : int
	the minimum y-coordinate

Notes
-----
If the grid passes through either the x or y axis, then this function returns a grid for each quadrant of the plane occupied by the grid.  This is important when using complex_grid as input to a ufunc to avoid visual artificats that result from points which are very close together but have a different sign.

References
----------
Mathologer, Times Tables, Mandelbrot and the Heart of Mathematics,
https://www.youtube.com/watch?v=qhbuKbxJsk8

Examples
--------
>>> from mathinspector.examples import times_table
>>> t=2
>>> plot(times_table(t))

Animation

>>> app.animate("t", start=2, stop=50)
    """

	result = []

	for value in range(start, end):
		new_value = (value * factor) % end
		result.append([
			(np.cos(value * 2 * np.pi / end), np.sin(value * 2 * np.pi / end)),
			(np.cos(new_value * 2 * np.pi / end), np.sin(new_value * 2 * np.pi / end))
		])

	return tuple(result);

def elliptic_curve(q,p):
	"""
draws an elliptic curve with parameters q,p

:math: y^3 = x^3 + p*x + q

Parameters
----------
p : float
    coefficient of x

q : float
    constant term

Notes
-----
This function is implemented by using the library skimage to find the set of points (x,y) which satisfy the equation y^2 = x^3 + p*x + q


The polynomial form of an elliptic curve is related to the differential equation satisfied by the Weierstrass elliptic function[1], by making the substitution

ro(z)′ = y

ro(z)  = x

References
----------
[0] https://en.wikipedia.org/wiki/Elliptic_curve


[1] https://en.wikipedia.org/wiki/Weierstrass%27s_elliptic_functions#Differential_equation

Examples
--------

>>> from mathinspector.examples import elliptic_curve
>>> plot(elliptic_curve(0,0))
    """
	x, y = np.ogrid[-12:12:100j, -12:12:100j]
	r = y**2 - x**3 - x*p - q

	return _measure.find_contours(r, 0)

def four_leaf_rose(q=4):
	"""
draws the algebraic variety known as the "four leaf rose"

:math: (x^2 + y^2)^3 - q*(x^2)*(y^2) = 0

Parameters
----------
q : float
    the coefficient of the cross term

Notes
-----
This function is implemented by using the library skimage to find the set of points (x,y) which satisfy the equation (x^2 + y^2)^3 - q*(x^2)*(y^2) = 0

Examples
--------

>>> from mathinspector.examples import four_leaf_rose
>>> plot(four_leaf_rose())
    """
	x, y = np.ogrid[-12:12:100j, -12:12:100j]
	r = (x**2 + y**2)**3 - q*(x**2)*(y**2)
	return _measure.find_contours(r, 0)


def transform(f, g, X, t):
	"""
animate the transition between two functions

:math: w(f,g,X,t) = f(X)*(t-1) + g(X)*t

Parameters
----------
f : array
    the first function to blend
g : array
    the second function to blend
X : array
	the range where the functions f and g are evaluated
t : float
    A number between 0 and 1 which determines the amount of blending between f and g


Examples
--------
>>> from mathinspector.examples import transform
>>> from numpy import exp, sqrt, linspace
>>> transform(exp, sqrt, linspace(-3,3), 0.5)
[ 0.5        -0.69980788  0.62129323 -0.29568233 -0.14752521]

Graphical illustration:

>>> from mathinspector.examples import complex_grid
>>> t = 0.5
>>> plot(transform(exp, sqrt, complex_grid(), t))

Animated Transition:

>>> app.animate("t", start=1, stop=0, step=-0.001)
    """
	return f(X)*(t-1) + g(X)*t

def complex_points(position, size, step):
	"""
creates a matrix of complex points using numpy methods

:math: (x^2 + y^2)^3 - q*(x^2)*(y^2) = 0

Parameters
----------
position : tuple
    the (x,y) position of the center of the points

size : tuple
    the (width,height) of the square which contains the point set

step : float
    the spacing between points

Notes
-----
This function uses the numpy `arange` and `meshgrid` functions to create a set of complex points.  View the source code for this example to see the implementation details.

Examples
--------

>>> from mathinspector.examples import complex_points
>>> complex_points((0,0),(2,2),0.5)
[[-1. +1.j  -1. +0.5j -1. +0.j  -1. -0.5j]
 [-0.5+1.j  -0.5+0.5j -0.5+0.j  -0.5-0.5j]
 [ 0. +1.j   0. +0.5j  0. +0.j   0. -0.5j]
 [ 0.5+1.j   0.5+0.5j  0.5+0.j   0.5-0.5j]]
    """
	x0, y0 = position
	w, h = size
	y = np.arange(y0 + h/2, y0 - h/2, -step)
	x = np.arange(x0 - w/2, x0 + w/2, step)
	Y, X = np.meshgrid(y,x)
	return X + 1j*Y

def domain_coloring(position, size, step, transform=None):
	"""
Domain coloring is a popular technique for visualizing the output of complex valued functions of a
complex variable.

Parameters
----------
position : tuple
    the (x,y) position of the center of the pixels

size : tuple
    the (width,height) of the square which contains the pixel set

step : float
    the distance between adjacent pixels

Examples
--------
>>> from mathinspector.examples import domain_coloring
>>> plot(pixelmap=domain_coloring)

References
----------
3blue1brown, Winding numbers and domain coloring, https://www.youtube.com/watch?v=b7FxPsqfkOY


https://en.wikipedia.org/wiki/Domain_coloring


	"""
	Z = complex_points(position, size, step)
	if transform:
		Z = transform(Z)
	H = np.angle(Z) % (2*np.pi)
	r = np.log2(1. + np.abs(Z))
	S = (1. + np.abs(np.sin(2. * np.pi * r))) / 2.
	V = (1. + np.abs(np.cos(2. * np.pi * r))) / 2.

	color_wheel = np.empty((Z.shape[0], Z.shape[1], 3), dtype=np.uint8)
	color_wheel[:, :, 0] = 255 * (H / H.max())
	color_wheel[:, :, 1] = 255 * S
	color_wheel[:, :, 2] = 255 * V

	return 255 * _hsv2rgb(color_wheel)

def mandelbrot_set(position, size, step, iterations=80):
	"""
The Mandlebrot set is one of the most famous fractals, this function computes it's defining equation up to a given number of iterations.

:math: $M = lim_{n \\to iterations} z_n < 2$ where $z_{n+1}=z_n^2 + z_0$

Parameters
----------
position : tuple
    the (x,y) position of the center of the pixels

size : tuple
    the (width,height) of the square which contains the pixel set

step : float
    the distance between adjacent pixels

iterations : int
	the number of iterations before bailing out of the calculation

References
----------
https://en.wikipedia.org/wiki/Mandelbrot_set


https://tomroelandts.com/articles/how-to-compute-the-mandelbrot-set-using-numpy-array-operations

Examples
--------
>>> from mathinspector.examples import mandelbrot_set
>>> plot(pixelmap=mandelbrot_set)

	"""
	C = complex_points(position, size, step)
	C_size = C.shape[0], C.shape[1]
	Z = np.zeros(C_size, dtype=complex)
	M = np.full(C_size, True, dtype=bool)

	for i in range(iterations):
		Z[M] = Z[M] * Z[M] + C[M]
		M[np.abs(Z) > 2] = False

	M = np.uint8(M)
	R = np.empty((C_size[0], C_size[1], 3), dtype=np.uint8)
	R[:,:,0] = 255 * M
	R[:,:,1] = 255 * M
	R[:,:,2] = 255 * M
	return R

def helix(t, as_points=False):
	"""
draws a three dimensional helix

:math: helix(t) = (np.cos(t), t, np.sin(t))

Parameters
----------
t : float
    parameter of the curve

Examples
--------
>>> from mathinspector.examples import helix
>>> from numpy import linspace
>>> T = 10
>>> plot(helix(linspace(0,T)))

Animated:

>>> app.animate("T", start=10, stop=25)
    """
	result = np.cos(t), t, np.sin(t)
	return result if as_points else list(result)

def wireframe(x,y,fn):
	"""
draws the wireframe line for a surface given by a function of two real variables f(x,y)

:math: wireframe(t) = (x, y, fn(x,y))

Parameters
----------
x  : array
	the x values of the range

y  : array
	the y values of the range

fn : callable
    a real valued function of two real variables

Examples
--------
>>> from numpy import linspace
>>> from mathinspector.examples import wireframe
>>> X = linspace(0,10)
>>> Y = linspace(0,10)
>>> plot(wireframe(X,Y, lambda x,y: (x,y,x**2 + y**2)))
    """

	x_lines, y_lines = [], []
	for xval in x:
		temp = []
		for yval in y:
			temp.append(fn(xval,yval))
		x_lines.append(temp)

	for yval in y:
		temp = []
		for xval in x:
			temp.append(fn(xval,yval))
		y_lines.append(temp)

	return x_lines, y_lines

def surface(x,y,fn):
	"""
draws quads for a surface given by a function of two real variables f(x,y)

:math: surface(t) = (x, y, fn(x,y))

Parameters
----------
x  : array
	the x values of the range

y  : array
	the y values of the range

fn : callable
    a real valued function of two real variables

Examples
--------
>>> from mathinspector.examples import surface
>>> X = linspace(0,10)
>>> Y = linspace(0,10)
>>> plot(surface(X,Y, lambda x,y: (x,y,x**2 + y**2)))
	"""

	return wireframe(x,y,fn)[1]

def cylinder(pos=(0,0,0),radius=1,num=25, as_wireframe=False):
	"""
draws a cylinder at a given position with a given radius and number of subdivisions

:math: f(t) = (cos(t), sin(t), r)

Parameters
----------
pos  : tuple
	position of the center of the cylinder

radius : float
	radius of the cylinder

num : int
    number of subdivisions

Examples
--------
>>> from mathinspector.examples import cylinder
>>> plot(cylinder())
    """
	result = wireframe(
		np.linspace(-radius,radius, num=num),
		np.linspace(0, 2*np.pi, num=num),
		lambda r,t: (pos[0] + np.cos(t), pos[1] + np.sin(t), pos[2] + r)
	)

	return result if as_wireframe else result[1]

def sphere(pos=(0,0,0),radius=1,num=12, as_wireframe=False):
	"""
draws a sphere at a given position with a given radius and number of subdivisions

:math: f(t) = (cos(t), sin(t), r)

Parameters
----------
pos  : tuple
	position of the center of the cylinder

radius : float
	radius of the cylinder

num : int
    number of subdivisions

Notes
-----
There are some known issues with the way this function has been implemented related to how the normals are calculated by the OpenGLWindow of the `plot` module.

Examples
--------
>>> from mathinspector.examples import sphere
>>> plot(sphere())
    """
	result = wireframe(
		np.linspace(-np.pi,np.pi, num=num),
		np.linspace(-np.pi,np.pi, num=num),
		lambda p,t: (pos[0] + radius*np.cos(t)*np.cos(p), pos[1] + radius*np.cos(t)*np.sin(p), pos[2] + radius*np.sin(t))
	)
	return result if as_wireframe else result[1]

