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
from util import Color
import re

class TreeEntry(tk.Entry):
	def __init__(self, parent, *args, **kwargs):
		tk.Entry.__init__(self, parent, *args, **kwargs)
		self.parent = parent
		# @REFACTOR: can actually just get rid of is_editing and use edit_key instead
		self.is_editing = False
		self.edit_key = None
		self.bind("<Key>", self._on_key)
		self.config(
			borderwidth=0,
			highlightthickness=0,
			background=Color.VERY_LIGHT_GREY,
			font="Nunito 12",
			foreground=Color.VERY_DARK_GREY
		)

	def edit(self, key, event):
		self.is_editing = True
		self.edit_key = key
		self.parent.selection_remove(key)
		self.parent.add_tag(key, "no_hover")
		self.parent.remove_tag(key, "hover")
		self.parent.selected = None
		x,y,width,height = self.parent.bbox(self.parent.identify_row(event.y), self.parent.identify_column(event.x))
		self.delete(0, "end")
		self.insert(0, self.parent.item(key)["text"])
		self.place(x=x + 23, y=y + height/2, anchor="w", relwidth=1)
		self.focus()
		return

	def _on_key(self, event):
		if event.keysym == "Escape":
			self.set_edit_value(cancel=True)		
		elif event.keysym == "Return":
			self.set_edit_value()

	def set_edit_value(self, cancel=False):
		self.place_forget()
		key = re.sub(r"(<{1,2}[a-zA-Z0-9_' ]*>{1,2})", "", self.edit_key)
		obj = self.parent.app.objects[key]
		self.parent.remove_tag(self.edit_key, "no_hover")
		self.parent.selection_set(self.edit_key)
		self.parent.selected = self.edit_key
		self.is_editing = False
		self.edit_key = None

		if cancel: return
		if isinstance(obj, str):
			val = self.get()
		else:
			try:
				val = self.parent.app.execute(self.get(), __SHOW_RESULT__=False, __EVAL_ONLY__=True)
			except Exception as err:
				# TODO - find a better way to display this error in the tree itself (msg window on bottom?)
				self.parent.app.console.result(err)
				return
	
		self.parent.app.objects.__setitem__(key, val, preserve_class=True)

