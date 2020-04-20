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
from widget import Treeview, ContextMenu, TreeEntry
from util import Color, unique_name
import re, inspect

RE_METHOD = re.compile(r"([a-zA-Z0-9_' ]*)<{1,2}([a-zA-Z0-9_' ]*)>{1,2}")

class ObjectTree(Treeview):
	def __init__(self, app, *args, **kwargs):
		Treeview.__init__(self, app, *args, **kwargs)

		self.app = app
		self.items = {}
		self.selected_key = None
		self.entry = TreeEntry(self)
		self.contextmenu = ContextMenu(app)

		self.contextmenu.set_menu(items=[{
			"label": "Delete",
			"command": self.contextmenu.delete
		}])		

		self.drag = {
			"selected": None,
			"position": (0,0),
			"in_workspace": False,
			"new_object": None
		}

		self.tag_configure("class", foreground=Color.RED, font="Nunito 10")
		
		self.bind("<<TreeviewSelect>>", self._on_treeview_select)
		self.bind("<Button-1>", self._on_button_1)
		self.bind("<Button-2>", self._on_button_2)
		self.bind('<B1-Motion>', self.b1_motion)
		self.bind('<ButtonRelease-1>', self._on_button_release_1)


	def select(self, key):
		selection = self.selection()
		if selection and key == selection[0]: return

		if key is None and len(selection) > 0:
			self.selected_key = None
			self.selection_remove(selection[0])
			return

		if key in self.items:
			self.selected_key = self.items[key]["tree_id"]
			self.selection_set( self.items[key]["tree_id"] )

	def _on_treeview_select(self, event):
		selection = self.selection()
		if not selection or self.entry.is_editing: return
		match = RE_METHOD.search(selection[0])
		if match and hasattr(self.app.objects[match.group(1)], match.group(2)):
			self.app.docviewer.showdoc( getattr(self.app.objects[match.group(1)], match.group(2)) )
		elif selection[0] in self.app.objects:
			self.app.docviewer.show(selection[0])
		# this is causing a problem with the treeview select, should not go thru app.select
		# self.app.select( re.sub(r"(<{1,2}[a-zA-Z0-9_' ]*>{1,2})", "", selection[0]) )

	def _on_button_1(self, event):
		if not self.selection(): return

		key = self.identify_row(event.y)
		if not self.entry.is_editing and key and key == self.selection()[0] and self.has_tag(key, "editable"):
			self.entry.edit(key, event)
			return "break"
		elif self.entry.is_editing:
			self.entry.set_edit_value()

	def _on_button_2(self, event):
		key = self.identify_row(event.y)
		if key:
			self.contextmenu.show(event, key)

	def get_selected_obj(self, key=False):
		if not self.selection(): return
		
		obj_key = re.sub(r"(<{1,2}[a-zA-Z0-9_' ]*>{1,2})", "", self.selection()[0])
		if key: return obj_key
		
		return self.app.objects[obj_key]
	
	def update_object(self, key):
		if key is None: return

		obj = self.app.objects[key]
		
		if key in self.items:
			if not callable(obj):
				self.item(self.items[key]["class"], text=obj.__class__.__module__ + "." + obj.__class__.__name__)
			
			if "value" in self.items[key] and self.items[key]["value"]:
				self.item(self.items[key]["value"], text=str(obj), tags="editable")
			
			if self.exists(key + "<" + "methods" + ">"):
				self.delete(key + "<" + "methods" + ">")
			if self.exists(key + "<" + "constants" + ">"):
				self.delete(key + "<" + "constants" + ">")
			if self.exists(key + "<" + "args" + ">"):
				self.delete(key + "<" + "args" + ">")
			if self.exists(key + "<" + "kwargs" + ">"):
				self.delete(key + "<" + "kwargs" + ">")
		else:
			tree_id = self.insert("", "end", key, text=key, tags=("object", "doc"))			
			self.items[key] = {
				"tree_id": tree_id,
				"class": None if callable(obj) else self.insert(key, "end", key + "<type>", text=obj.__class__.__module__ + "." + obj.__class__.__name__, tags=("class", "no_hover")),
				"value": None if callable(obj) else self.insert(key, "end", key + "<" + "value" + ">", text=str(obj), tags="editable")
			}

		args = kwargs = methods = constants = None
		if callable(obj):
			fn = obj
		else:
			fn = obj.__class__
		
		argspec = None
		try:
			argspec = inspect.getfullargspec(fn)
		except:
			pass
		
		if argspec:
			i = 0
			d = len(argspec[0] or []) - len(argspec[3] or [])
			if not args:
				args = self.insert(key, "end", key + "<" + "args" + ">", text="args")
			for j in argspec[0]:
				text = j
				if i < d:
					self.insert(args, "end", key + "<" + "args " + j + ">", text=j)
				else:
					if not kwargs:
						kwargs = self.insert(key, "end", key + "<" + "kwargs" + ">", text="kwargs")
					text = j + " = " + str(argspec[3][d - i])
					self.insert(kwargs, "end", key + "<" + "args " + j + ">", text=j + " = " + str(argspec[3][d - i]))
				i += 1

		for j in dir(obj):
			if j[:1] != "_":
				attr = getattr(obj, j)
				if callable(attr):
					if not methods:
						methods = self.insert(key, "end", key + "<" + "methods" + ">", text="methods")
					self.insert(methods, "end", key + "<" + j + ">", text=j, tags="doc")
				else:
					if not constants:
						constants = self.insert(key, "end", key + "<" + "constants" + ">", text="constants")
					self.insert(constants, "end", key + "<" + j + ">", text=j + ": " + str(attr))
		
	def delete_object(self, key):
		if key is None: return
		self.delete(self.items[key]["tree_id"])
		del self.items[key]

	def create_new_object(self, key):
		match = RE_METHOD.search(key)
		if match and hasattr(self.app.objects[match.group(1)].__class__, match.group(2)):
			obj_class = self.app.objects[match.group(1)].__class__
			obj = getattr(obj_class, match.group(2))
			if not callable(obj):
				obj = getattr(self.app.objects[match.group(1)], match.group(2))
				name = unique_name(self.app, match.group(1) + "_" + match.group(2))
			else:
				name = unique_name(self.app, obj_class.__name__ + "_" + obj.__name__)

			self.app.objects[name] = obj

			return name	


	def b1_motion(self, event):
		self.drag["selected"] = self.selection()
		
		if self.drag["in_workspace"] and self.drag["new_object"]:
			item = self.app.workspace.get_item(self.drag["new_object"])
			if item:
				item.move(event.x - self.drag["position"][0], event.y - self.drag["position"][1])
			else:
				print ('no item!')
		elif self.drag["selected"] and self.app.workspace == self.winfo_containing(event.x_root, event.y_root):
			self.drag["in_workspace"] = True
			self.drag["new_object"] = self.create_new_object(self.drag["selected"][0])
			
		self.drag["position"] = (event.x, event.y)

	def _on_button_release_1(self, event):
		self.drag["selected"] = None
		self.drag["in_workspace"] = False				

