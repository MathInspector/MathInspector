"""
There are two ways to animate objects, either clicking on an item
in the node editor and seleting the "Animate" option, or from the
console using the `app.animate` function.

As a simple example, the following code creates a variable `x`
and animates it's value from 0 to 1 with a delay of 0.1 seconds and a
step of 0.05

>>> x=0
>>> app.animate("x", start=0, stop=1, delay=0.1, step=0.05)

The usefulness of the app.animate function is that it is fully integrated
with the plotting features, and has been designed to optimize the
performance of plots by offloading as much of the animation to the
plot window as possible.

Another reason the app.animate function is so useful is it makes possible
to include animations in code samples that you can provide in
the documentation for your own projects.

One of the most interesting animations is the power function applied
to a set of gridlines in the complex plane.  Check it out!

>>> from mathinspector.examples import complex_grid
>>> from numpy import power
>>> t=1
>>> plot(power(complex_grid(), t))

Once the plot window is up, run the animation with the command

>>> app.animate("t", start=1, stop=4, step=0.005, delay=0.01)

You can pan and zoom while an animation is playing and the performance
should be typically be over 60 fps, as long as the mouse cursor
is inside the plot window.  If during an animation the mouse cursor is not
hovering over the plot window, the frame rate can drop.  This
happens because the plot window needs to share resources with the rest
of the app when it's not in focus.

It's also possible to animate the arguments of functions

>>> from numpy import linspace
>>> app.animate("linspace", argname="start", start=0, stop=5)

When the plot window is closed, all animations are automatically
paused. To pause or unpause all currently running animations,
use the command

>>> app.animate.pause()

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
from . import plot
from .widget.popup import Popup

DELAY = 0.01
STEP = 0.005

def hexstring(num):
    return '#' + str(hex(num))[2:].zfill(6)

class Animation:
	def __init__(self, app):
		self.app = app
		self.is_running = False
		self.stack = []
		self.cache = {}

	def __call__(self, name, **kwargs):
		item = self.app.node[name]

		val = 0 if item.is_callable else item.obj
		opts = {
			"start": val,
			"stop": val + 10,
			"delay": DELAY,
			"step": STEP,
		}

		if kwargs:
			opts.update(kwargs)
			self.start(name, opts)
		else:
			if item.is_callable:
				opts.update({
					"argname": ""
				})

			Popup(self.app, [{
				"label": i,
				"value": opts[i]
			} for i in opts],
			lambda params: self.start(name, params),
			"Animate Item", name)

	def start(self, name, params):
		item = self.app.node[name]
		if params["stop"] is None:
			print (Exception("AnimationError: Missing required parameters"))
			return

		if "argname" in params and params["argname"] is None:
			print (Exception("AnimationError: Missing required parameters"))
			return

		self.is_running = True
		if params["start"] is None:
			pass
		elif "argname" in params:
			if params["argname"] in item.args:
				item.args[params["argname"]] = params["start"]
			elif params["argname"] in item.kwargs:
				item.kwargs[params["argname"]] = params["start"]
			else:
				print (Exception("AnimationError: argname not found"))
				return
		else:
			self.app.objects[item.name] = params["start"]

		if self.app.node.output.items:
			plot.animate(params["delay"], lambda: self._plot_update(name, params))
		else:
			self.run(item.name, params)

	def run(self, name, params):
		item = self.app.node[name]
		if "argname" in params:
			if params["argname"] in item.args:
				obj = self.app.node[name].args[params["argname"]]
			else:
				obj = self.app.node[name].kwargs[params["argname"]]
				return
		else:
			obj = self.app.objects[name]

		if self.is_running and (
			(params["step"] > 0 and obj < params["stop"])
			or (params["step"] < 0 and obj > params["stop"])
		):
			if "argname" in params:
				if params["argname"] in item.args:
					item.args[params["argname"]] += params["step"]
				else:
					item.kwargs[params["argname"]] += params["step"]
			else:
				self.app.objects[name] += params["step"]
			self.app.after(int(params["delay"]*1000), lambda: self.run(name, params))
			return

		if not self.is_running:
			self.stack.append((name, params))
			return

		self.is_running = False
		if "argname" in params:
			if params["argname"] in item.args:
				item.args[params["argname"]] = params["stop"]
			else:
				item.kwargs[params["argname"]] = params["stop"]
		else:
			self.app.objects[name] = params["stop"]

	def _plot_update(self, name, params):
		item = self.app.node[name]
		if "argname" in params:
			if params["argname"] in item.args:
				obj = item.args[params["argname"]]
			else:
				obj = item.kwargs[params["argname"]]
				return
		else:
			obj = self.app.objects[name]

		if self.is_running and (
			(params["step"] > 0 and obj < params["stop"])
			or (params["step"] < 0 and obj > params["stop"])
		):
			if "argname" in params:
				if params["argname"] in item.args:
					item.args[params["argname"]] += params["step"]
				else:
					item.kwargs[params["argname"]] += params["step"]
			else:
				self.app.objects[name] += params["step"]

			self.app.update()
			return list(self.app.node.output.values.values())

		if "argname" in params:
			if params["argname"] in item.args:
				item.args[params["argname"]] = params["stop"]
			else:
				item.kwargs[params["argname"]] = params["stop"]
		else:
			self.app.objects[name] = params["stop"]
		self.app.update()
		return False

	def can_animate(self, item):
		return item.is_callable or isinstance(item.obj, (int,float))

	def pause(self):
		if self.is_running:
			self.is_running = False
		else:
			for i in self.stack:
				i[1]["start"] = None
				self.start(i[0], i[1])
			self.stack.clear()
