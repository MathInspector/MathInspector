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
import tkinter as tk
from ..util import vdict
from ..console.builtin_print import builtin_print


class Menu(tk.Menu):
	def __init__(self, parent, items=[], **kwargs):
		tk.Menu.__init__(self, parent, tearoff=False)
		self._ = {}
		self.parent = parent
		self.set_menu(items)

	def set_menu(self, items, prev=None):
		if not prev:
			self.delete(0, 100)
			prev = self

		for j in items:
			# builtin_print(j)
			if "menu" in j:
				if len(j["menu"]) > 0:
					menu = Menu(self.parent)
					self._[j["label"]] = menu
					self.set_menu(j["menu"], menu)
					kwargs = j.copy()
					kwargs["menu"] = menu
					prev.add_cascade(**kwargs)
			elif "separator" in j:
				prev.add_separator(j["separator"])
			elif "label" in j:
				prev.add_command(**j)

				if "accelerator" in j:
					self.parent.bind("<" + j["accelerator"].replace("+", "-") + ">", j["command"])

	def show(self, event, items=None):
		if items:
			self.set_menu(items)
		self.post(event.x_root, event.y_root)
