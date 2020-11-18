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
		self.edit_key = None
		self.bind("<Key>", self._on_key)
		self.config(
			borderwidth=0,
			highlightthickness=0,
			background=Color.ALT_BACKGROUND,
			insertbackground=Color.WHITE,
			selectbackground=Color.HIGHLIGHT,
			foreground=Color.WHITE
		)


	def edit(self, key, event):
		name = re.sub(r"(<{1,2}[a-zA-Z0-9_' ]*>{1,2})", "", key)
		# if name in self.parent.app.objects:
		# 	obj = self.parent.app.objects[name]
		# 	item = self.parent.app.workspace.get_item(name)
		# 	if "default" in item.args and item.args["default"]["connection"]: 
		# 		return
		# 	if "<arg>" in key and items.args:
		# 		argname = re.findall(r"<<([a-zA-Z0-9_' ]*)>>", key)[0]
		# 		if item.args[argname]["connection"]:
		# 			return


		self.edit_key = key
		self.parent.selection_remove(self.parent.selection())
		self.parent.remove_tag(key, "hover")
		self.parent.selected = None
		x,y,width,height = self.parent.bbox(self.parent.identify_row(event.y), self.parent.identify_column(event.x))
		self.delete(0, "end")
		
		val = self.parent.item(key)["text"]
		if "<value>" in key:
			val = str(self.parent.app.objects[name])

		if "<arg>" in key:
			item = self.parent.app.workspace.get_item(name)
			argname = re.findall(r"<<([a-zA-Z0-9_' ]*)>>", key)[0]
			val = str(item.args[argname]["value"]) if item.args[argname]["value"] is not None else ""

		self.insert(0, val)
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
		item = self.parent.app.workspace.get_item(key)

		if cancel: return
		
		if "<arg>" in self.edit_key or "<kwarg>" in self.edit_key:
			argname = re.findall(r"<<([a-zA-Z0-9_' ]*)>>", self.edit_key)[0]
			val = None
			try:
				val = self.parent.app.eval(self.get("1.0", "end"))
			except Exception as err:
				print (err)

			item.setarg(argname, val)

		if "<value>" in self.edit_key:
			try:
				val = self.parent.app.eval(self.get("1.0", "end"))
				self.parent.app.objects.__setitem__(key, val, preserve_class=True, raise_error=True)
			except Exception as err:
				print ("\a")
				print (err)
	
		self.edit_key = None
            
