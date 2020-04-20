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

class ContextMenu():
	def __init__(self, app, callbacks={}, items=[]):
		self.app = app
		self.key = None
		self.menus = []
		self.set_menu(items)

	def set_menu(self, items):
		self.menu = tk.Menu(self.app, tearoff=0)
		for j in items:
			if "menu" in j and len(j["menu"]) > 0:
				menu = tk.Menu(self.app)
				self.menus.append(menu)
				for k in j["menu"]:
					if "separator" in k:
						menu.add_separator(k["separator"])
					if "label" in k and "command" in k:
						menu.add_command(label=k["label"], command=k["command"])
				self.menu.add_cascade(label=j["label"], menu=menu)

			if "separator" in j:
				self.menu.add_separator(j["separator"])
			if "label" in j and "command" in j:
				self.menu.add_command(label=j["label"], command=j["command"])

	def delete(self):
		del self.app.objects[self.key]

	def show(self, event, key):
		self.key = key
		self.menu.post(event.x_root, event.y_root)
