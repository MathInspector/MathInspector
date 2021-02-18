"""
The objects which are currently in the local namespace are displayed in the left hand sidebar
of the main window, in the "Objects" tab.  The Objects tab is a traditional object
debugger, which you might be familiar with from web inspector and related
development tools in modern web browsers.

From this tab, you can change the values of objects, or the value of arguments
and key word arguments to any function, simply by clicking on the relevant item
and typing in a new value.

A list of an object's methods are contained in the methods folder.  To run
a method, either double click on it, or right click and choose "Run Method"
from the options menu.  If the method doesn't have any arguments, it will
be run, otherwise the method dialog will appear. It's also possible to drag
methods directly into the node editor from the Objects tab.

To directly access the global object which stores the names and values
of all variables, use the command

>>> app.objects

See the class `ObjectTree` for a full list of available attributes.
"""
"""
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

import inspect
from . import doc
from .util import vdict, Color, argspec, classname, fontcolor, open_editor, BUTTON_RIGHT, BUTTON_RELEASE_RIGHT
from .style import TREE_TAGS
from .widget import Treeview, TreeEntry

class ObjectTree(vdict, Treeview):
	"""
	In order to synchronize the values of variables currently in memory across views,
	math inspector stores the names and values of all variables in a vdict called the Object Tree.
	A vdict is like a normal python dictionary, except it has callbacks for things like setting and
	deleting items.

	A vdict stores its values in an ordered dictionary attribute named "store".
	To display the current contents of the Object Tree, use the command

	>>> app.objects.store

	As an example, if you wanted to set the variable `x` to have a value of `1`, you
	could use the command

	>>> x=1

	which is equivilent to

	>>> app.objects["x"] = 1

	if you need fine grained control when assigning variables to the local namespace,
	use the function

	>>> app.objects.setobj("x", 1)

	See the documentation for `setobj` for more information
	about the available keyword arguments
	"""
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
		self.bind("<Double-Button-1>", self._on_double_button_1)
		self.bind(BUTTON_RIGHT, self._on_button_right)
		self.bind(BUTTON_RELEASE_RIGHT, self._on_button_release_right)

	def setobj(self, name, value, create_new=False, coord=None, is_binop=False):
		"""
		The callback of app.objects, called whenever new objects are created, or the value
		of an object is changed.  This method is responsible for updating the values
		displayed in the Objects tab of the sidebar, as well as notifying the other
		views that the value of a variable in the local namespace has changed.

		Parameters
		----------
		name : string
		    the name of the variable
		value : object
		    the value to assign
		create_new : bool
			when set to True, this will generate a unique variable name if there is already
			a key with the same name
		coord : tuple(float, float)
		    a tuple of floats which determines the coordinates of the newly created item in the
		    node editor


		Examples
		--------
		>>> app.objects.setitem("x", create_new=True)
		>>> app.objects.setitem("x", create_new=True)
		"""
		name = self.unique_name(name) if create_new else name
		prev = self.app.node[name] if name in self.app.node else None
		order = self.order()
		expanded = self.expanded()
		update_value = prev and prev.argspec == argspec(value) and prev.classname == classname(value)
		is_output_item = prev in self.app.node.output.items or prev == self.app.node.output.log_item
		self.store[name] = value
		if is_output_item and not update_value:
			self.app.node.output.disconnect(prev)
			is_output_item = False
		self.app.node.setitem(name, update_value=update_value, coord=coord, is_output_item=is_output_item)

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
					self.insert(name + "<constants>", "end", name + "." + j, text=j + ": " + str(attr), tags="no_hover")

		self.order(order)
		self.expanded(expanded)

		if create_new:
			return name
		return False

	def delete(self, key):
		if key in self.app.node:
			item = self.app.node[key]
			item.disconnect()
			for i in item.args["connection"]:
				item.args["connection"][i].disconnect()
			for k in item.kwargs["connection"]:
				item.kwargs["connection"][k].disconnect()
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

	def _on_double_button_1(self, event):
		key = self.identify_row(event.y)
		obj = help.getobj(key)
		if callable(obj) and "." in key:
			name, fn = key.rsplit(".", 1)
			self.app.node.run_method(fn, obj, self.app.node[name])

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
			file = inspect.getsourcefile(self.app.objects[key])
			items.append({
				"label": "View Source Code",
				"command": lambda: open_editor(file)
			})
		except:
			pass

		if key in self.app.node and self.app.animate.can_animate(self.app.node[key]):
			items.append({
				"label": "Animate",
				"command": lambda: self.app.animate(key)
			})

		if callable(obj) and "." in key:
			name, fn = key.rsplit(".", 1)
			items.append({
				"label": "Run Method",
				"command": lambda: self.app.node.run_method(fn, obj, self.app.node[name])
			})

		if key in self:
			items.extend([{
				"separator": None
			},{
				"label": "Delete " + key,
				"command": lambda: self.delete(key)
			}])

		self.menu.set_menu(items)
		self.menu.show(event)
