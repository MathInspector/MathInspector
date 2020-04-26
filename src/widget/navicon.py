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
from util import loadimage, assetpath
from settings import Color, ButtonRight
from PIL import ImageTk, Image

image = {
	"editor": {
		"default": ["fa-edit"],
		"selected": ["fa-edit-selected"],
		"selected-alt": ["fa-edit-selected-alt"],
		"hover": ["fa-edit-hover"]
	},
	"console": {
		"default": ["console"],
		"selected": ["console-selected"],
		"selected-alt": ["console-selected-alt"],
		"hover": ["console-hover"]
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
	"workspace": {
		"default": ["workspace"],
		"selected": ["workspace-selected"],
		"selected-alt": ["workspace-selected-alt"],
		"hover": ["workspace-hover"]
	},
}

class NavIcon(tk.Label):
	def __init__(self, parent, name, app):
		if len(image[name]["default"]) == 1:
			image[name]["default"].append(loadimage(image[name]["default"][0]))
			image[name]["hover"].append(loadimage(image[name]["hover"][0]))
			image[name]["selected"].append(loadimage(image[name]["selected"][0]))
			image[name]["selected-alt"].append(loadimage(image[name]["selected-alt"][0]))

		tk.Label.__init__(self, parent, image=image[name]["default"][1], background=Color.BLACK)

		self.name = name
		self.app = app
		self.parent = parent
		self.is_selected = False
		self.style = None
		self.bind("<Button-1>", self._on_button_1)
		self.bind(ButtonRight, self._on_button_2)
		self.bind("<Enter>", self._on_enter)
		self.bind("<Leave>", self._on_leave)

	def select(self, style=None):
		if style:
			self.style = style
			
		for j in self.parent.icons:
			item = self.parent.icons[j]
			if item.is_selected and item.style == self.style:
				item.unselect()

		self.is_selected = True
		if self.style == "alt":
			self.config(image=image[self.name]["selected"][1])
		else:
			self.config(image=image[self.name]["selected-alt"][1])

		if self.name == "editor":
			self.app.editor.focus()
		elif self.name == "console":
			self.app.console.focus()


	def unselect(self):
		self.is_selected = False
		self.config(image=image[self.name]["default"][1])

	def _on_button_2(self, event):
		self.style = None
		self.app.setview(self.name)

	def _on_button_1(self, event):
		self.style = "alt"
		self.app.setview(self.name, True)


	def _on_enter(self, event):
		self.config(image=image[self.name]["hover"][1])

	def _on_leave(self, event):
		if self.is_selected:
			self.select()
		else:
			self.config(image=image[self.name]["default"][1])




