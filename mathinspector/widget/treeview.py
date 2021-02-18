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

from tkinter import ttk
from ..style import Color
from os.path import basename
from .menu import Menu
from .text import Text

class Treeview(ttk.Treeview):
	def __init__(self, app, *args, drag=True, **kwargs):
		if not args:
			args = [app]

		ttk.Treeview.__init__(self, *args, **kwargs)

		self.app = app
		self.menu = Menu(app)
		self.hover_item = None

		self.bind('<Motion>', self._on_motion)
		self.bind('<Leave>', self._on_leave)
		self.tag_configure("hover", background=Color.HIGHLIGHT_INACTIVE)

		if drag:
			self.drag = None
			self.bind('<B1-Motion>', self._on_b1_motion)
			self.bind('<ButtonRelease-1>', self._on_button_release_1)


	def has_tag(self, item, tag):
		if not self.exists(item): return

		tags = self.item(item)["tags"]
		return tags and tag in tags

	def add_tag(self, item, tag):
		if not self.exists(item): return

		if not isinstance(tag, tuple):
			tag = (tag,)

		tags = self.item(item)["tags"]
		if isinstance(tags, list):
			for t in tag:
				if t not in tags:
					tags.append(t)
		elif not tags:
			tags = tag
		self.item(item, tags=tags)

	def remove_tag(self, item, tag):
		if not self.exists(item): return

		if not isinstance(tag, tuple):
			tag = (tag,)

		tags = self.item(item)["tags"]
		for t in tag:
			if t in tags:
				del tags[tags.index(t)]
		self.item(item, tags=tags)

	def order(self, items=None):
		if not items: return [{
			"key": i,
			"index": self.index(i),
			"filename": basename(i)
		} for i in self.get_children()]

		items.sort(key=lambda i: i["index"])

		for i in items:
			if self.exists(i["key"]):
				self.move(i["key"], "", i["index"])
			else:
				for j in items:
					if self.exists(j["key"]) and j["filename"] == basename(i["key"]):
						self.move(j["key"], "", i["index"])

	def expanded(self, names=None, children=None):
		if children == None:
			children = self.get_children()

		if not names:
			result = []
			for j in children:
				item = self.item(j)
				if item["open"]:
					result.append({
						"name": item["text"],
						"children": self.expanded(children=self.get_children(j))
					})

			return result

		for i in names:
			for j in children:
				item = self.item(j)
				if item["text"] == i["name"]:
					self.item(j, open=True)
					self.expanded(i["children"], self.get_children(j))

	def _on_motion(self, event):
		item = self.identify_row(event.y)
		if not item or self.has_tag(item, "no_hover"): return

		if self.hover_item and item != self.hover_item:
			self.remove_tag(self.hover_item, "hover")

		self.add_tag(item, "hover")
		self.hover_item = item

	def _on_leave(self, event):
		if self.hover_item:
			self.remove_tag(self.hover_item, "hover")

		self.hover_item = None

	def _on_b1_motion(self, event):
		item, x, y = self.drag if self.drag else (None,0,0)
		selection = self.selection()
		if not selection: return

		row = self.item(selection[0])
		if not selection:
			return
		elif "." in selection[0]:
			obj_path = selection[0]
		elif self.item(selection[0])["values"]:
			obj_path = self.item(selection[0])["values"][0]
		else:
			obj_path = None

		if item:
			item.move(event.x - x, event.y - y)
		elif obj_path and selection and self.winfo_containing(event.x_root, event.y_root) == self.app.node:
			try:
				name, attr = obj_path.rsplit(".", 1)
				obj = getattr(self[name], attr)
				key = self.app.objects.setobj(attr, obj, create_new=True, coord=self.app.node.get_pointer())
				item = self.app.node[key]
			except Exception as err:
				pass

		self.drag = item, event.x, event.y

		if not item:
			row = self.identify_row(event.y)
			if row not in self.get_children(): return

			moveto = self.index(row)
			for i in self.selection():
				self.move(i, "", moveto)


	def _on_button_release_1(self, event):
		self.drag = None


class TreeEntry(Text):
	def __init__(self, parent):
		Text.__init__(self, parent, background=Color.ALT_BACKGROUND, padx=0, pady=0)
		self.parent = parent
		self.app = parent.app
		self.editing = None
		self.bind("<Key>", self._on_key)

	def edit(self, key, event):
		name = key[:key.index("<")]
		item = self.app.node[name]
		if key == name + "<value>":
			argname = None
			in_args = False
		else:
			argname = key[key.index("<arg=") + 5:key.index(">") + 1]
			in_args = argname in item.args
		self.editing = item, argname, in_args

		value = item.obj if not argname else item.args[argname] if in_args else item.kwargs[argname]
		self.parent.selection_remove(self.parent.selection())
		self.parent.remove_tag(key, "hover")

		x,y,width,height = self.parent.bbox(key)
		y_off = self.parent.winfo_y() + height/2
		x_off = 48 if in_args or not argname else 66

		if isinstance(item.obj, str):
			self.bind("<<Modify>>", lambda event: self.highlight(r"((.*))", "yellow"))
			self.insert("end", str(value if value is not None else ""))
		else:
			self.bind("<<Modify>>", lambda event: self.syntax_highlight())
			self.insert("end", str(value if value is not None else ""))

		# self.insert("end", str(value if value is not None else ""))
		self.place(x=x + x_off, y=y + y_off, anchor="w", width=width - x_off, height=height)
		self.focus()
		self.lift()

	def finish(self, cancel=False):
		item, argname, in_args = self.editing
		content = self.get("1.0", "end-1c")
		arg = None if not argname else item.args[argname] if in_args else item.kwargs[argname]

		if isinstance(arg, str):
			value = content
		elif content in self.app.node:
			value = self.app.node[content]
		elif arg:
			try:
				value = self.app.console.eval(content)
			except:
				self.app.console.showtraceback()
				self.hide()
				return

		if not argname:
			try:
				result = self.app.console.eval(content)
			except:
				result = content

			try:
				self.app.objects[item.name] = item.obj.__class__(result)
			except Exception as err:
				self.app.console.prompt.push("")
				self.app.console.showtraceback()
				self.hide()
				return
		elif argname in item.args:
			item.args[argname] = value
		else:
			item.kwargs[argname] = value

		item.resize()
		self.hide()

	def hide(self):
		self.lower()
		self.delete("1.0", "end")
		self.editing = None

	def _on_key(self, event):
		if event.keysym == "Escape":
			self.hide()
			return "break"
		elif event.keysym == "Return":
			self.finish()
			return "break"
