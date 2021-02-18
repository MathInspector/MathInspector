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
import tkinter as tk
import pygame
from ..widget import Text
from ..util import argspec, instanceof, MESSAGE_TIMEOUT
from ..console.builtin_print import builtin_print
from ..style import Color, getimage
from .. import plot

class Output(tk.Frame):
	def __init__(self, canvas):
		self.canvas = canvas
		self.app = canvas.app
		tk.Frame.__init__(self, canvas.frame, background=Color.BLACK)
		self.log = Text(canvas.frame,
			font="Nunito 24 bold",
			foreground=Color.ORANGE,
			background=Color.BLACK,
			readonly=True,
			bd=1
		)

		plot.config(on_update=self.app.update, on_close=self.disconnect)

		self.node = tk.Label(self, image=getimage("node"), foreground=Color.RED, padx=0, pady=0, bd=0)
		self.node.pack()
		self.node.bind("<Enter>", self._on_enter_node)
		self.node.bind("<Leave>", self._on_leave_node)
		self.node.bind("<Configure>", self._on_configure)
		self.log.tag_configure("center", justify="center")
		self.items = []
		self.values = {}
		self.log_item = None

	def show(self, obj, autohide=True):
		self.log.delete("1.0", "end")
		self.log.insert("end", str(obj), "center")
		self.log.place(x=0, y=0, width=self.canvas.winfo_width(), height=60)
		self.log.lift()

		if autohide:
			self.after(MESSAGE_TIMEOUT, self.log.lower)

	def _on_enter_node(self, event):
		if len(self.items) == 1:
			self.hover()
			self.items[0].config("output", "wire", fill=Color.HOVER)

	def _on_leave_node(self, event):
		if self.items:
			self.hover()
			if len(self.items) == 1:
				self.items[0].config("output", "wire", fill=Color.PURPLE)

	def hover(self, is_visible=True):
		if is_visible is False:
			img = "node-active" if self.items else "node"
		else:
			img = "node-connect"
		self.node.config(image=getimage(img))

	def connect(self, item, show_plot=True):
		self.items.append(item)
		value = item.value()
		window = plot.get_window(value)
		if not window and not show_plot:
			return

		if show_plot and window and plot.is_active() and window != plot.active_window:
			item.move_wire()
			print(Exception("Can't plot 2D and 3D at the same time."))
			return

		item.move_wire()		
		self.hover()
		if not show_plot: return

		name = " ".join([i.name for i in self.items])

		if self.is_pixelmap(item.obj):
			pixelmap_fn = lambda *args: item.obj(*args, **item.kwargs)
			if plot.is_active():
				plot.config(pixelmap=pixelmap_fn)
			else:
				plot.plot(pixelmap=pixelmap_fn, title=name)
		elif window:
			self.values[item.name] = value
			if plot.is_active():
				plot.update(*list(self.values.values()))
			else:
				plot.plot(value, title=name)
		else:
			if self.log_item:
				self.disconnect(self.log_item)
			self.show(item.content(truncate=False), autohide=False)
			self.log_item = item

	def disconnect(self, item=None):
		if item is None:
			for i in self.items:
				i.hide_wire()
				i.config("output", fill=Color.EMPTY_NODE)
			self.items.clear()
			self.values.clear()
		else:
			self.items = [i for i in self.items if i != item]
			if self.log_item == item:
				self.log_item = None
			elif item.name in self.values:
				del self.values[item.name]
			item.hide_wire()
			item.config("output", fill=Color.EMPTY_NODE)

		if not self.items:
			self.hover(False)
			self.log.lower()
			if plot.is_active() and item:
				plot.close()
		else:
			plot.update(*list(self.values.values()))

	def is_pixelmap(self, obj):
		if not callable(obj):
			return False
		return argspec(obj)[0] == ["position", "size", "step"]

	def update_value(self, item):
		if plot.is_active():
			if self.is_pixelmap(item.obj):
				plot.config(pixelmap=lambda *args: item.obj(*args, **item.kwargs))
			else:
				self.values[item.name] = item.value()
				plot.update(*list(self.values.values()))
		else:
			self.show(item.content(truncate=False), autohide=False)

	def _on_configure(self, event):
		for i in self.items:
			i.move_wire()

		if self.items and not plot.is_active():
			self.log.place(width=self.canvas.winfo_width())
