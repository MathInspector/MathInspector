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
from util import Color, unique_name, get_class_name, get_font_color
from settings import ButtonRight
import re, inspect

RE_METHOD = re.compile(r"([a-zA-Z0-9_' ]*)<{1,2}([a-zA-Z0-9_' ]*)>{1,2}")

class ObjectTree(Treeview):
	def __init__(self, app, *args, **kwargs):
		Treeview.__init__(self, app, *args, **kwargs)

		self.app = app
		self.entry = TreeEntry(self)
		
		self.drag = {
			"selected": None,
			"position": (0,0),
			"in_workspace": False,
			"new_object": None
		}

		self.tag_configure("class", foreground=Color.RED, font="Nunito 10")
		self.tag_configure("argname", foreground=Color.DARK_ORANGE, font="Nunito 10")
		self.tag_configure("kwargname", foreground=Color.ORANGE, font="Nunito 10")
		self.tag_configure("connected", foreground=Color.BLUE)
		
		self.bind("<<TreeviewSelect>>", self._on_treeview_select)
		self.bind("<Button-1>", self._on_button_1)
		self.bind('<B1-Motion>', self.b1_motion)
		self.bind('<ButtonRelease-1>', self._on_button_release_1)

	def set_state(self, openobjects):
		self.setexpanded(openobjects)

		for i in self.get_children():
			self.update_object(i)

	def select(self, key):
		selection = self.selection()
		if selection and key == selection[0]: return

		if key is None and len(selection) > 0:
			self.selection_remove(selection[0])
			return

		if key in self.app.objects:
			self.selection_set(key)

	def _on_treeview_select(self, event):
		selection = self.selection()
		if not selection: return

		if selection[0] in self.app.objects:
			self.app.select(selection[0])

	def _on_button_1(self, event):
		key = self.identify_row(event.y)

		if not key: return
		if self.entry.edit_key:
			self.entry.set_edit_value(cancel=True)
		
		if self.has_tag(key, "editable"):			
			self.entry.edit(key, event)
			return "break"

	def get_selected_obj(self, key=False):
		if not self.selection(): return
		
		obj_key = re.sub(r"(<{1,2}[a-zA-Z0-9_' ]*>{1,2})", "", self.selection()[0])
		if key: return obj_key
		
		return self.app.objects[obj_key]
	
	def update_object(self, key, prev_item=None):
		if key is None: return

		obj = self.app.objects[key]
		item = self.app.workspace.get_item(key)
		is_open = False

		if prev_item is not None:
			is_open = self.item(key)["open"]
			self.delete_object(key)

		if key in self.get_children():
			self.item(key + "<class>", text=get_class_name(obj))						
			if self.exists(key + "<value>"):
				self.item(key + "<value>", text=str(obj))
				if "default" in item.args and item.args["default"]["connection"]:
					self.add_tag(key + "<value>", "connected")
					self.add_tag(key + "<value>", "no_hover")
					self.remove_tag(key + "<value>", "editable")
				elif self.has_tag(key + "<value>", "connected"):
					self.remove_tag(key + "<value>", "connected")
					self.remove_tag(key + "<value>", "no_hover")
					self.add_tag(key + "<value>", "editable")

		else:
			self.insert("", "end", key, text=key, tags=("object", "doc"), open=is_open)			
			self.insert(key, "end", key + "<class>", text=get_class_name(obj), tags=("class", "no_hover"))
			if not callable(obj):
				self.insert(key, "end", key + "<value>", text=str(obj), tags="editable")

		if "default" not in item.args:
			for name in item.args:
				if self.exists(key + "<argname><<" + name + ">>"):
					self.item(key + "<arg><<" + name + ">>", text=str(item.args[name]["value"]))
					if item.args[name]["connection"]:
						self.add_tag(key + "<arg><<" + name + ">>", "connected")
						self.add_tag(key + "<arg><<" + name + ">>", "no_hover")
						self.remove_tag(key + "<arg><<" + name + ">>", "editable")
					elif self.has_tag(key + "<arg><<" + name + ">>", "connected"):
						self.remove_tag(key + "<arg><<" + name + ">>", "connected")
						self.remove_tag(key + "<arg><<" + name + ">>", "no_hover")
						self.add_tag(key + "<arg><<" + name + ">>", "editable")
				else:
					self.insert(key, "end", key + "<argname><<" + name + ">>", text=name, 
						tags=("argname", "no_hover"))
					self.insert(key, "end", key + "<arg><<" + name + ">>", 
						text=str(item.args[name]["value"]), 
						tags="editable")
			
			if len(item.kwargs) > 0:
				if not self.exists(key + "<kwargs>"):
					kwargs = self.insert(key, "end", key + "<kwargs>", text="kwargs")
				for name in item.kwargs:
					if self.exists(key + "<kwargname><<" + name + ">>"):
						self.item(key + "<kwarg><<" + name + ">>", text=str(item.kwargs[name]["value"]))
					else:
						self.insert(kwargs, "end", key + "<kwargname><<" + name + ">>", text=name, 
							tags=("kwargname", "no_hover"))
						self.insert(kwargs, "end", key + "<kwarg><<" + name + ">>", 
							text=str(item.kwargs[name]["value"]), 
							tags="editable")


		if not self.exists(key + "<methods>"):
			methods = constants = None
			for j in dir(obj):
				if j[:1] != "_":
					attr = getattr(obj, j)
					if callable(attr):
						if not methods:
							methods = self.insert(key, "end", key + "<methods>", text="methods")
						self.insert(methods, "end", key + "<" + j + ">", text=j, tags="doc")
					else:
						if not constants:
							constants = self.insert(key, "end", key + "<constants>", text="constants")
						self.insert(constants, "end", key + "<" + j + ">", text=j + ": " + str(attr))
		
	def delete_object(self, key):
		if key is None: return
		self.delete(key)

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
		elif self.drag["selected"] and self.app.workspace == self.winfo_containing(event.x_root, event.y_root):
			self.drag["in_workspace"] = True
			self.drag["new_object"] = self.create_new_object(self.drag["selected"][0])
			
		self.drag["position"] = (event.x, event.y)

	def _on_button_release_1(self, event):
		self.drag["selected"] = None
		self.drag["in_workspace"] = False				

