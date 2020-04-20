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

from tkinter import ttk
from settings import Color

class Treeview(ttk.Treeview):
	def __init__(self, parent, header=None, *args, **kwargs):
		ttk.Treeview.__init__(self, parent, *args, **kwargs)

		if header:
			self.heading("#0", text=header, anchor="w")

		self.hover_item = None
		self.bind('<Motion>', self._on_motion)
		self.bind('<Leave>', self._on_leave)
		self.tag_configure("hover", background=Color.HIGHLIGHT_INACTIVE)			
		# self.tag_configure("no_hover", background=Color.VERY_LIGHT_GREY)			

	def _on_motion(self, event):
		item = self.identify_row(event.y)
		if not item or self.has_tag(item, "no_hover"): return

		if self.hover_item and item != self.hover_item:
			self.remove_tag(self.hover_item, "hover")
		
		self.add_tag(item, "hover")
		self.hover_item = item

	def has_tag(self, item, tag):
		tags = self.item(item)["tags"]
		return tags and tag in tags

	def add_tag(self, item, tag):
		tags = self.item(item)["tags"]
		if isinstance(tags, list):
			if tag not in tags: 
				tags.append(tag)
		elif not tags:
			tags = tag
		self.item(item, tags=tags)

	def remove_tag(self, item, tag):
		tags = self.item(item)["tags"]
		if tag in tags: del tags[tags.index(tag)]
		self.item(item, tags=tags)

	def _on_leave(self, event):
		if self.hover_item:
			self.item(self.hover_item, tags=[])

		self.hover_item = None

	def getexpanded(self, children=None):
		result = []
		
		if children == None:
			children = self.get_children()

		for j in children:
			item = self.item(j)
			if item["open"]:
				result.append({
					"name": item["text"],
					"children": self.getexpanded(self.get_children(j))
				})

		return result

	def setexpanded(self, names, children=None):
		if children == None:
			children = self.get_children()
		
		for i in names:
			for j in children:
				item = self.item(j)
				if item["text"] == i["name"]:
					self.item(j, open=True)
					self.setexpanded(i["children"], self.get_children(j))