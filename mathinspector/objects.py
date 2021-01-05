"""
Math Inspector: a visual programming environment for scientific computing with python
Copyright (C) 2020 Matt Calhoun

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

import doc, inspect
from util import vdict
from widget import Treeview, TreeEntry
from util import Color, argspec, classname, fontcolor, open_editor, BUTTON_RIGHT, BUTTON_RELEASE_RIGHT
from style import TREE_TAGS
from inspect import getsourcefile

class ObjectTree(vdict, Treeview):
	def __init__(self, app, *args, **kwargs):
		vdict.__init__(self, *args, setitem=self.setobj, delitem=self.delete)
		Treeview.__init__(self, app, *args, **kwargs)

		self.drag = None
		self.entry = TreeEntry(self)

		for i in TREE_TAGS:
			self.tag_configure(i, **TREE_TAGS[i])		

		self.tag_configure("class", foreground=Color.BLUE, font="Nunito 10")
		self.tag_configure("editable")
		self.tag_configure("argname", foreground=Color.DARK_ORANGE, font="Nunito 10")
		self.tag_configure("kwargname", foreground=Color.ORANGE, font="Nunito 10")
		
		self.bind("<Button-1>", self._on_button_1)
		self.bind(BUTTON_RIGHT, self._on_button_right)
		self.bind(BUTTON_RELEASE_RIGHT, self._on_button_release_right)
		
	def setobj(self, name, value, create_new=False, coord=None):
		name = self.unique_name(name) if create_new else name
		prev = self.app.node[name] if name in self.app.node else None
		order = self.order()
		expanded = self.expanded()
		update_value = prev and prev.argspec == argspec(value) and prev.classname == classname(value)
		self.store[name] = value
		self.app.node.setitem(name, update_value=update_value, coord=coord) 
		
		if update_value and self.exists(name + "<arg=<value>>"):
			self.item(name + "<arg=<value>>", 
				text=str(value), 
				tags=("editable", fontcolor(value, as_string=True)))
			return
		
		if self.exists(name):
			super(Treeview, self).delete(name)

		item = self.app.node[name]

		self.insert("", "end", name, text=name, tags=("object", "doc"))			
		self.insert(name, "end", name + "<class>", text=item.classname, tags=("class", "no_hover"))
		if not item.is_callable:
			self.insert(name, "end", name + "<arg=<value>>", text=str(value), tags=("editable", fontcolor(value, as_string=True)))

		if item.is_callable:
			for j in item.args:
				self.insert(name, "end", name + "<argname=" + j + ">", text=j, 
					tags=("argname", "no_hover"))
				self.insert(name, "end", name + "<arg=" + j + ">", 
					text=str(item.args[j]), 
					tags=("editable", fontcolor(item.args[j], as_string=True)))
			
			if len(item.kwargs) > 0:
				kwargs = self.insert(name, "end", name + "<kwargs>", text="kwargs")
				for k in item.kwargs:
					self.insert(kwargs, "end", name + "<argname=" + k + ">", text=k, 
						tags=("kwargname", "no_hover"))
					self.insert(kwargs, "end", name + "<arg=" + k + ">", 
						text=str(item.kwargs[k]), 
						tags=("editable", fontcolor(item.kwargs[k], as_string=True)))

		for j in dir(value):
			if j[:1] != "_":
				attr = getattr(value, j)
				if callable(attr):
					if not self.exists(name + "<methods>"):
						self.insert(name, "end", name + "<methods>", text="methods")
					self.insert(name + "<methods>", "end", name + "." + j, text=j, tags="doc")
				else:
					if not self.exists(name + "<constants>"):
						self.insert(name, "end", name + "<constants>", text="constants")
					self.insert(name + "<constants>", "end", name + "." + j, text=j + ": " + str(attr))

		self.order(order)
		self.expanded(expanded)
		
		if create_new:
			return name
		return False

	def delete(self, key):
		super(Treeview, self).delete(key)
		self.app.node[key].destroy()
	
	def unique_name(self, name):
	    i = 2
	    temp = name
	    while True:
	        if temp not in self:
	            return temp
	        temp = name + "_" + str(i)
	        i += 1

	def _on_button_1(self, event):
		key = self.identify_row(event.y)
		if not key: return

		if self.entry.editing:
			self.entry.finish(cancel=True)
		
		if self.has_tag(key, "editable"):			
			self.entry.edit(key, event)
			return "break"

		if self.has_tag(key, "no_hover"):
			return "break"

	def _on_button_right(self, event):
		key = self.identify_row(event.y)
		self.selection_set(key)
	
	def _on_button_release_right(self, event):
		key = self.identify_row(event.y)
		obj = help.getobj(key)
		if obj is None: return

		items = []

		if help.getobj(key):
			items.append({
				"label": "View Doc",
				"command": lambda: help(key)
			})
		
		try:
			file = getsourcefile(obj)
			items.append({
				"label": "View Source Code",
				"command": lambda: open_editor(file)
			})
		except:
			pass		

		if key in self:
			items.extend([{
				"separator": None	
			},{
				"label": "Delete " + key,
				"command": lambda: self.delete(key)
			}])
		
		self.menu.set_menu(items)
		self.menu.show(event)
