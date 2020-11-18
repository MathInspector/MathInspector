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
from util import loadimage
from settings import Color, ButtonRight
from PIL import ImageTk, Image

image = {
	"console": {
		"default": ["console"],
		"selected": ["console-selected"],
		"selected-alt": ["console-selected-alt"],
		"hover": ["console-hover"]
	},
	"workspace": {
		"default": ["workspace"],
		"selected": ["workspace-selected"],
		"selected-alt": ["workspace-selected-alt"],
		"hover": ["workspace-hover"]
	},
	"docviewer": {
		"default": ["docviewer"],
		"selected": ["docviewer-selected"],
		"selected-alt": ["docviewer-selected-alt"],
		"hover": ["docviewer-hover"]
	},
	"output": {
		"default": ["output"],
		"selected": ["output-selected"],
		"selected-alt": ["output-selected-alt"],
		"hover": ["output-hover"]
	},
}

class Nav(tk.Frame):
	def __init__(self, app):
		tk.Frame.__init__(self, app, background=Color.BLACK, pady=12)		
		self.app = app
		self.selected = { "top": None, "bottom": None }

		for i in image:
			for j in image[i]:
				image[i][j].append(loadimage(image[i][j][0]))

		self.icons = {
			i: tk.Label(self, image=image[i]["default"][1], background=Color.BLACK) for i in image
		}
		
		self.pack(side="top", fill="both")
		for j in self.icons:
			self.icons[j].bind("<Enter>", lambda event, key=j: self._on_enter(key))
			self.icons[j].bind("<Leave>", lambda event, key=j: self._on_leave(key))
			self.icons[j].bind("<Button-1>", lambda event, key=j: self.select("bottom", key))
			self.icons[j].bind(ButtonRight, lambda event, key=j: self.select("top", key))
			self.icons[j].pack()


	def select(self, panel, key, flip_panels=True):
		if self.selected[panel] == key: return

		if self.selected[panel]:
			self.icons[self.selected[panel]].config(image=image[self.selected[panel]]["default"][1])

		if panel == "top":
			if flip_panels and self.selected["top"] and self.selected["bottom"] == key:
				self.select("bottom", self.selected["top"], False)
			widget = self.app.top_view
			self.icons[key].config(image=image[key]["selected"][1])
		elif panel == "bottom":
			if flip_panels and self.selected["bottom"] and self.selected["top"] == key:
				self.select("top", self.selected["bottom"], False)
			widget = self.app.bottom_view
			self.icons[key].config(image=image[key]["selected-alt"][1])	
		else:
			return

		iid = ".!" + key
		if iid in widget.tabs and iid in widget.notebook.tabs():
			widget.tabs[iid].select()
		else:
			widget.add(key, getattr(self.app, key))

		widget.notebook.select(iid)
		self.selected[panel] = key
		if key == "console":
			self.app.console.focus()
		

	def _on_enter(self, key):
		self.icons[key].config(image=image[key]["hover"][1])

	def _on_leave(self, key):	
		self.icons[key].config(image=image[key]["selected-alt" if key == self.selected["bottom"] else "selected" if key == self.selected["top"] else "default"][1])

