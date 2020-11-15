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
from widget.canvas.item import Item
from settings import Color, Zoom, Widget, ButtonRight, ButtonReleaseRight, ButtonRightMotion

class PanZoomDragCanvas(tk.Canvas):
	def __init__(self, app, draggable=True, *args, **kwargs):
		tk.Canvas.__init__(self, app, *args, **kwargs)
		self.app = app
		self.config(
			background=Color.BACKGROUND,
			width=400,
			height=400,
			bd=0
		)

		self.event = None		
		self.items = {}
		self.hover_item = None
		self.canvas_ids = []
		self.input_nodes = []
		self.output_nodes = []

		self.selected = None

		self.zoomlevel = 1
		self.bind("<MouseWheel>", self._on_mouse_wheel)
		
		self.pan_position = None
		self.bind(ButtonRight, self._on_button_2)
		self.bind(ButtonReleaseRight, self._on_button_release_2)
		self.bind(ButtonRightMotion, self._on_b2_motion)

		if draggable:
			self.drag = {
				"item": None,
				"position": (0,0)
			}		
			self.tag_bind("draggable", "<Enter>", self._on_enter_item)
			self.tag_bind("draggable", "<Leave>", self._on_leave_item)
			self.tag_bind("draggable", "<Button-1>", self._on_drag_start)
			self.tag_bind("draggable", "<ButtonRelease-1>", self._on_drag_stop)
			self.tag_bind("draggable", "<B1-Motion>", self._on_drag)

			self.multiselect = {
				"position": None,
				"items": []
			}
			self.bind("<Button-1>", self._on_button_1)
			self.bind("<B1-Motion>", self._on_multiselect)
			self.bind("<ButtonRelease-1>", self._on_button_release_1)
			self.multiselect_box = self.create_rectangle(0,0,0,0, outline=Color.DARK_GREY, dash=(3,3), state="hidden")

	def create_item(self, value, name=None, coord=None):
		coord = coord or self.get_pointer(in_canvas=True)

		item = Item(self, value, name, coord, self.zoomlevel)
 
		self.items[item.canvas_id] = item

		self.canvas_ids.append({
			"canvas_id": item.canvas_id,
			"parent_id": None
		})

		for c in item.children:
			self.canvas_ids.append({
				"canvas_id": c,
				"parent_id": item.canvas_id    
			})
		
		for j in item.args:
			self.input_nodes.append(item.args[j]["input"])
		
		for j in item.kwargs:
			self.input_nodes.append(item.kwargs[j]["input"])

		self.output_nodes.append(item.output)
		self.output_nodes.append(item.output_wire)

		# self.app.select(item.name)

		return item

	def clear(self):
		self.canvas_ids.clear()
		self.delete("all")

	def get_pointer(self, in_canvas=False):
		x = self.canvasx(self.winfo_pointerx() - self.winfo_rootx()) 
		y = self.canvasy(self.winfo_pointery() - self.winfo_rooty())
		if in_canvas:
			return x % self.winfo_width(), y % self.winfo_height()
		else:		
			return x,y

	def get_parent(self, canvas_id):
		if canvas_id in self.items:
			return self.items[canvas_id] 
		else:
			for i in self.canvas_ids:
				if i["canvas_id"] == canvas_id:
					return self.items[i["parent_id"]]

	def get_closest(self, x,y, objects={}, parent=True):
		if not objects: objects = self.items

		x, y = self.get_pointer()

		overlapping = self.find_overlapping(
			x - Widget.HITBOX, y - Widget.HITBOX, 
			x + Widget.HITBOX, y + Widget.HITBOX
		) 
		
		for j in overlapping:
			for canvas_id in objects:
				if j == canvas_id:
					return self.get_parent(canvas_id) if parent else canvas_id
	
	def has_tag(self, canvas_id, tag):
		tags = self.gettags(canvas_id)
		return tags and tag in tags

	def add_tag(self, canvas_id, tag):
		tags = list(self.gettags(canvas_id))
		tags.append(tag)
		self.itemconfig(canvas_id, tags=tuple(tags))

	def remove_tag(self, canvas_id, tag):
		tags = self.gettags(canvas_id)
		new_tags = []
		for i in tags:
			if i != tag:
				new_tags.append(i)
		self.itemconfig(canvas_id, tags=tuple(new_tags))

	def _on_enter_item(self, event):
		if self.event not in ("drag", "connect"):
			self.hover_item = self.get_parent( self.find_closest(event.x, event.y)[0] )
			if self.hover_item.canvas_id in self.multiselect["items"]:
				for k in self.multiselect["items"]:
					self.itemconfig(self.items[k].canvas_id, fill=Color.LIGHT_PURPLE)
					if hasattr(self.items[k], "variable_label"):
						self.itemconfig(self.items[k].variable_label, fill=Color.VERY_DARK_GREY)
			else:
				self.itemconfig(self.hover_item.canvas_id, fill=Color.LIGHT_PURPLE)
				self.hover_item.canvasentry.config(background=Color.LIGHT_PURPLE)
				if hasattr(self.hover_item, "variable_label"):
					self.itemconfig(self.hover_item.variable_label, fill=Color.VERY_DARK_GREY)

	def _on_leave_item(self, event):
		if self.hover_item and self.event not in ("drag", "connect"):
			if self.hover_item.canvas_id in self.multiselect["items"]:
				for k in self.multiselect["items"]:
					self.itemconfig(self.items[k].canvas_id, fill=Color.VERY_LIGHT_PURPLE)
					if hasattr(self.items[k], "variable_label"):
						self.itemconfig(self.items[k].variable_label, fill=Color.WHITE)
			elif self.hover_item == self.selected:
				self.itemconfig(self.hover_item.canvas_id, fill=Color.VERY_LIGHT_PURPLE)
				self.hover_item.canvasentry.config(background=Color.VERY_LIGHT_PURPLE)
				if hasattr(self.hover_item, "variable_label"):
					self.itemconfig(self.hover_item.variable_label, fill=Color.WHITE)
			else:
				self.itemconfig(self.hover_item.canvas_id, fill=Color.BLACK)
				if hasattr(self.hover_item, "variable_label"):
					self.itemconfig(self.hover_item.variable_label, fill=Color.WHITE)
	
	def _on_mouse_wheel(self, event):
		x, y = self.get_pointer()

		if event.delta > 0:
			self.scale("all", x,y, Zoom.IN, Zoom.IN)
			self.zoomlevel *= Zoom.IN
		else:
			self.scale("all", x,y, Zoom.OUT, Zoom.OUT)
			self.zoomlevel *= Zoom.OUT

		for x in self.items: 
			if isinstance(self.items[x], Item):
				self.items[x].zoom()

	def _on_button_1(self, event):
		if self.event in ("drag", "connect"): return
		if self.event == "edit" and self.selected:			
			closest = self.find_closest(event.x,event.y)
			if not closest or (self.get_parent(closest[0]) != self.selected and self.selected.canvasentry.window != closest[0]):
				self.event = None
				self.selected.canvasentry.finish()
			return

		self.event = "multiselect"
		self.multiselect["position"] = (event.x, event.y)

		for j in self.multiselect["items"]:
			self.itemconfig(j, fill=Color.BLACK)

		del self.multiselect["items"][:]

		self.select(None)
		self.tag_raise(self.multiselect_box)
		self.itemconfig(self.multiselect_box, state="hidden")

	def select(self, key=None):
		pass

	def _on_button_release_1(self, event):		
		if self.event == "edit": return
		self.event = None		
		self.multiselect["position"] = None
		self.itemconfig(self.multiselect_box, state="hidden")
		for k in self.multiselect["items"]:
			self.itemconfig(k, fill=Color.VERY_LIGHT_PURPLE)

	def _on_multiselect(self, event):
		if self.event in ("drag", "connect", "edit") or not self.multiselect["position"]:
			return
		
		x,y = self.multiselect["position"]
		overlapping = self.find_overlapping(x,y,event.x,event.y)		
		self.coords(self.multiselect_box, x, y, event.x, event.y)
		self.itemconfig(self.multiselect_box, state="normal")

		for k in self.multiselect["items"]:
			if k not in overlapping:
				self.itemconfig(self.items[k].canvas_id, fill=Color.BLACK)

		del self.multiselect["items"][:]

		for node in self.items:
			for j in overlapping:			
				if j == node and j not in self.multiselect["items"]:
					self.multiselect["items"].append(node)
		
		for k in self.multiselect["items"]:
			self.itemconfig(self.items[k].canvas_id, fill=Color.LIGHT_PURPLE)
		
	def _on_button_2(self, event):
		self.pan_position = (event.x, event.y)
		if self.event == "edit":			
			self.event = None
			self.selected.canvasentry.finish()
		return

	def _on_button_release_2(self, event):
		self.pan_position = None

	def _on_b2_motion(self, event):
		if self.pan_position == None:
			self.pan_position = (event.x, event.y)

		self.pan((event.x - self.pan_position[0], event.y - self.pan_position[1]))
		self.pan_position = (event.x, event.y)

	def pan(self, delta):
		for c in self.canvas_ids:
			self.move(c["canvas_id"], delta[0], delta[1])		
	
	def zoom(self, zoomlevel, position=None):
		if position == None:
			position = (self.winfo_width() / 2, self.winfo_height() /2)

		scale = zoomlevel / self.zoomlevel
		self.zoomlevel = zoomlevel
		self.scale("all", *position, scale, scale)


	def _on_drag_start(self, event):
		if self.event in ("connect", "edit"): return
		self.event = "drag"
		self.drag["item"] = self.get_parent( self.find_closest(event.x, event.y)[0] )
		self.drag["position"] = (event.x, event.y)
		self.drag["item"].tag_raise()
		self.drag["item"].config(hover_editable=("leave", None))
		if self.drag["item"].canvas_id not in self.multiselect["items"]:
			self.app.select(self.drag["item"].name)

	def _on_drag_stop(self, event):
		if self.event == "edit": return
		self.event = None
		self.drag["item"] = None
		self.drag["position"] = (0,0)

	def _on_drag(self, event): 
		if self.event in ("connect", "edit"): return   
		
		delta_x = event.x - self.drag["position"][0]
		delta_y = event.y - self.drag["position"][1]
		if self.multiselect["items"]:
			for j in self.multiselect["items"]:
				self.items[j].move(delta_x , delta_y)
		elif self.drag["item"]:
			self.drag["item"].move(delta_x, delta_y)
		self.drag["position"] = (event.x, event.y)	
