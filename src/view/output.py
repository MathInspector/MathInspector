"""
Math Inspector: a visual programing environment for scientific computing with python
Copyright (C) 2018 Matt Calhoun

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

import tkinter as tk
from settings import Color
from util import classname, makereadonly
from numpy import ndarray
from PIL import Image,ImageTk
from widget import SciPlot, InfoBox
from widget import Text
from pprint import pformat
import traceback

REPR_TYPES = (str, int, float, complex, dict)
photos = []
SCALE = 10

class Output(tk.Frame):
	def __init__(self, app, *args, **kwargs):
		tk.Frame.__init__(self, app, *args, **kwargs, background=Color.BACKGROUND)
		self.app = app
		self.selected = None
		self.is_panning = False
		self.prev_value = None
		infobox = tk.Frame(self, background=Color.ALT_BACKGROUND)
		self.name_label = tk.Label(infobox, font="CONSOLA 16 bold", foreground=Color.WHITE, background=Color.BACKGROUND)
		self.class_label = tk.Label(infobox, font="Nunito 12 bold", foreground=Color.RED, background=Color.BACKGROUND)
		divider = tk.Frame(self, background=Color.BLACK, height=8)
		self.canvas = SciPlot(self)
		self.text = Text(self, syntax=None)
		makereadonly(self.text)
		self.log = InfoBox(self, hide_callback=lambda: self.text.lift())
		
		infobox.pack(side="top", fill="both")
		self.name_label.pack(side="top", anchor="nw")
		self.class_label.pack(side="top", anchor="nw")
		divider.pack(side="top", fill="both")
		self.canvas.frame.pack(side="top", fill="both", expand=True)		

	def update(self, key):
		if key == self.selected:
			self.select(key)

	def save(self):
		return self.canvas.key, self.canvas.cache, self.canvas.overlay_items

	def load(self, key, cache, overlay_items):
		self.canvas.key = key
		self.canvas.cache = cache
		self.canvas.overlay_items = overlay_items

	def clear(self):
		self.select(None)
		self.canvas.key = None
		self.canvas.cache = {}
		self.canvas.overlay_items = {}		

	def select(self, key=None):
		item = self.app.workspace.get_item(key)
		if key is None or not item: 
			self.name_label.config(text="")
			self.class_label.config(text="")
			self.canvas.frame.pack_forget()
			self.text.pack_forget()
			self.selected = None
			return 

		# commented out bc this breaks animations
		# if key == self.selected and isinstance(item.value, (str, int, float, complex, dict)):
		# 	return
		
		self.selected = key
		self.name_label.config(text=key)
		self.class_label.config(text=classname(item.value))

		show_repr = False
		if callable(item.value):
			try:
				item.get_output(raise_err=True)
			except Exception as err:
				show_repr = True

		if show_repr or isinstance(item.value, REPR_TYPES):
			self.canvas.frame.pack_forget()
			self.text.delete("1.0", "end")

			if isinstance(item.value, dict):
				self.prev_value = pformat(item.value, width=4)[1:-1]
			else:
				self.prev_value = str(item.value)

			self.text.insert("end", self.prev_value)
			self.text.pack(side="top", fill="both", expand=True)
			return

		args = None
		output = item.get_output()

		self.text.pack_forget()
		self.canvas.frame.pack(side="top", fill="both", expand=True)

		if isinstance(output, ndarray):
			for j in item.args:
				if "value" in item.args[j] and isinstance(item.args[j]["value"], ndarray):
					args = item.args[j]["value"]

		if args is not None:
			output = [(args[i], output[i]) for i in range(0, len(args))]

		if isinstance(output, (list, ndarray)):
			try:
				self.canvas.plot(output, key, item.line_color)
			except Exception as e:
				print (traceback.format_exc())
				pass		
			return

		self.canvas.frame.pack_forget()
		self.text.delete("1.0", "end")
		self.text.insert("end", str(output))
		self.text.pack(side="top", fill="both", expand=True)		

	def overlay(self, item, remove=False):
		if remove:
			self.canvas.overlay(item.name)
			return

		args = None
		output = item.get_output()
		if isinstance(output, ndarray):
			for j in item.args:
				if "value" in item.args[j] and isinstance(item.args[j]["value"], ndarray):
					args = item.args[j]["value"]

		if args is not None:
			output = [(args[i], output[i]) for i in range(0, len(args))]

		if isinstance(output, (list, ndarray)):
			try:
				self.canvas.overlay(item.name, output, item.line_color)
				return
			except Exception as e:
				print (traceback.format_exc())
				pass				
		
		# self.canvas.overlay_items.append(item.get_output())
		# if remove and item.name in self.overlay_items:
		# 	del self.canvas.overlay_items[item.name]
		# else:
		# 	print ("HITHERE", self.canvas.overlay_items)


	def delete_object(self, key):
		if key == self.selected:
			self.select(None)

	def toggle(self, *args):
		if "smooth" in args:
			self.canvas.smooth = "true" if not self.canvas.smooth else None
			result = self.canvas.smooth == "true"
		if "random_color" in args:
			self.canvas.has_random_color = not self.canvas.has_random_color
			result = self.canvas.has_random_color
		if "show_grid_lines" in args:
			self.canvas.show_grid_lines = not self.canvas.show_grid_lines
			result = self.canvas.show_grid_lines
		self.app.select(self.app.selected)
		return result

