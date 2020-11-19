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
from .infobox import InfoBox
from .button import Button
from util import argspec, unique_name
from view.docviewer import DocViewer

BTN_HEIGHT = 32

class Popup(tk.Toplevel):
	def __init__(self, root, title, app, obj=None, canvas_item=None, width=720, height=480, callback=None, eval_args=True):
		tk.Toplevel.__init__(self, root, background=Color.BLACK)
		self.app = app
		self.obj = obj
		self.eval_args = eval_args
		self.callback = callback
		self.item = canvas_item
		self.args = []
		self.kwargs = {}
		self.log = InfoBox(self)

		self.bind("<Return>", self._on_ok)
		self.bind("<Escape>", self._on_cancel)
		if obj:
			self.title(obj.__name__)
			tk.Label(self, 
				text=obj.__name__, 
				font="Montserrat 24 bold", 
				foreground=Color.WHITE, 
				background=Color.PURPLE, 
				anchor="w",
				padx=8
			).pack(fill="x", expand=True, padx=8)	

			inputs = argspec(obj, withself=False)
			input_area = tk.Frame(self, background=Color.BLACK)

			i = 0
			did_focus = False
			for i, argname in enumerate(inputs["args"]):
				tk.Label(input_area, text=argname, font="Menlo 14", background=Color.BLACK, foreground=Color.WHITE).grid(column=0, row=i)
				temp = tk.Entry(input_area, font="Monospace 14", highlightbackground=Color.BLACK)
				temp.grid(column=1, row=i)
				self.args.append(temp)
				if not did_focus:
					temp.focus_set()
					did_focus = True	

			for j, kwargname in enumerate(inputs["kwargs"]):
				tk.Label(input_area, text=kwargname, font="Menlo 14", background=Color.BLACK, foreground=Color.WHITE).grid(column=0, row=i + j + 1)
				temp = tk.Entry(input_area, font="Monospace 14", highlightbackground=Color.BLACK)
				temp.insert("end", str(inputs["kwargs"][kwargname]))
				temp.grid(column=1, row=i + j + 1)
				self.kwargs[kwargname] = temp
				if not did_focus:
					temp.focus_set()
					did_focus = True	

			
			input_area.pack(fill="x", expand=True)

			btn_area = tk.Frame(self, background=Color.BLACK)
			Button(btn_area, text="Help", command=self._on_help, height=2, width=6).pack(side="left", fill="x", expand=True, anchor="center", padx=4, pady=4)
			Button(btn_area, text="Cancel", command=self._on_cancel, height=2, width=6).pack(side="left", fill="x", expand=True, anchor="center", padx=4, pady=4)
			Button(btn_area, text="OK", command=self._on_ok, height=2, width=6).pack(side="left", fill="x", expand=True, anchor="center", padx=4, pady=4)
			btn_area.pack(side="left", fill="both", expand=True)
			width_alt = max(input_area.winfo_width(), btn_area.winfo_width())
			height_alt = input_area.winfo_width() + btn_area.winfo_width()

			height = 40 + 64 + 29 * (len(self.args) + len(self.kwargs))
			width = 280
			
			x = str(int(app.winfo_x() + app.winfo_width()/2))
			y = str(int(app.winfo_y() + app.winfo_height()/4))

			self.geometry(str(width) + "x" + str(height) + "+" + x + "+" + y)	
		else:
			# lol w/e
			label = tk.Label(self, text=="uhh ... ?", anchor="w", justify="left")
			label.pack(fill="both")
			x = str(int(app.winfo_x() + app.winfo_width()/2))
			y = str(int(app.winfo_y() + app.winfo_height()/2))
			self.geometry(str(width) + "x" + str(height) + "+" + x + "+" + y)

		root.wait_window(self)

	def _on_help(self):
		self.app.docviewer.select(self.obj)
		self.app.nav.select("top", "docviewer")

	def _on_ok(self, event=None):
		args = []
		kwargs = {}
		if self.eval_args:
			for i in self.args:
				try:
					value = self.app.eval(i.get("1.0", "end"))
				except:
					value = str(i.get("1.0", "end")) or None
					print ("uhhh", i.get("1.0", "end"))
				args.append(value)

			for j in self.kwargs:
				try:
					value = self.app.eval(self.kwargs[j].get("1.0", "end"))
				except:
					print ("uhhh", value)
					value = str(self.kwargs[j].get("1.0", "end"))			

				kwargs[j] = value
		else:
			args = [i.get("1.0", "end") for i in self.args]
			kwargs = { j:self.kwargs[j].get("1.0", "end") for j in self.kwargs}

		if not self.callback:
			self.obj(*args, **kwargs)
			self.destroy()			
			return

		if self.callback:
			try:
				result = self.callback(*args, **kwargs)
			except Exception as err:
				self.app.workspace.log.show(err)
				self.destroy()
				return

		if self.item:
			if isinstance(result, bool):
				self.log.show(result)
				return
			elif result != None:
				name = unique_name(self.app, self.item.name + "_" + self.obj.__name__)
				self.app.objects[name] = result
		
			self.item.set_value(self.app.objects[self.item.name])
		
		self.destroy()
	
	def _on_cancel(self, event=None):
		self.destroy();

