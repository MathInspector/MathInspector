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
import numpy as np
import inspect, platform
from .. import plot
from ..util import fontcolor, instanceof, classname, argspec, numargs, open_editor, vdict, instanceof
from ..util.config import BUTTON_RIGHT, BUTTON_RELEASE_RIGHT, BUTTON_RIGHT_MOTION, HITBOX, ZOOM_IN, ZOOM_OUT, FONTSIZE, FONT_SIZE
from ..style import Color, getimage
from .output import Output
from .item import Item
from ..widget import Popup, Menu, Text

class NodeEditor(vdict, tk.Canvas):
	def __init__(self, app):
		self.app = app
		vdict.__init__(self)
		self.frame = tk.Frame(app, background=Color.BLACK)
		tk.Canvas.__init__(self, self.frame,
			highlightthickness=4,
			highlightbackground=Color.BACKGROUND,
			background=Color.BACKGROUND,
			bd=0)
		self.zoom = 1
		self.pan_position = None
		self.dragitem = None
		self.dragposition = (0,0)
		self.multiselect = {
			"position": None,
			"items": [],
			"box": self.create_rectangle(0,0,0,0, outline=Color.DARK_GREY, dash=(3,3), state="hidden")
		}

		self.pack(side="left", fill="both", expand=True)
		self.output = Output(self)
		self.output.pack(side="right")

		self.selected = None
		self.connect = None
		self.hover = None
		self.hover_input = None
		self.hover_edit = None
		self.edit_item = None
		self.dragstart = (0,0)
		self.has_menu = False
		self.menu = Menu(self.app)

		self.bind("<Button-1>", self._on_button_1)
		self.bind("<B1-Motion>", self._on_multiselect)
		self.bind("<ButtonRelease-1>", self._on_button_release_1)

		self.bind("<MouseWheel>", self._on_mouse_wheel)
		if platform.system() == "Linux":
			self.bind("<Button-4>", lambda event: self._on_mouse_wheel(event, 1))
			self.bind("<Button-5>", lambda event: self._on_mouse_wheel(event, -1))
		self.bind(BUTTON_RELEASE_RIGHT, self._on_button_release_2)
		self.bind(BUTTON_RIGHT_MOTION, self._on_b2_motion)

		self.tag_bind("draggable", "<Button-1>", self._on_drag_start)
		self.tag_bind("draggable", "<ButtonRelease-1>", self._on_drag_stop)
		self.tag_bind("draggable", "<B1-Motion>", self._on_drag)
		self.tag_bind("draggable", BUTTON_RIGHT, self._on_item_menu)
		self.tag_bind("editable", "<Enter>", self._on_enter_editable)
		self.tag_bind("editable", "<Motion>", self._on_motion_editable)
		self.tag_bind("editable", "<ButtonRelease-1>", self._on_click_editable)
		self.tag_bind("editable", "<Leave>", self._on_leave_editable)
		self.tag_bind("editable", "<Button-1>", self._on_drag_start)
		self.tag_bind("editable", "<B1-Motion>", self._on_drag)

		self.tag_bind("input", "<Motion>", self._on_motion_input)
		self.tag_bind("input", "<Enter>", self._on_enter_input)
		self.tag_bind("input", "<Leave>", self._on_leave_input)

		for i in ("draggable", "output", "wire"):
			self.tag_bind(i, "<Enter>", lambda event, tag=i:self._on_item_enter(event, tag))
			self.tag_bind(i, "<Leave>", lambda event, tag=i:self._on_item_leave(event, tag))

		for j in ("output", "wire", "input"):
			self.tag_bind(j, "<Button-1>", lambda event, tag=j:self._on_item_button_1(event, tag))
			self.tag_bind(j, "<B1-Motion>", lambda event, tag=j:self._on_item_b1_motion(event, tag))
			self.tag_bind(j, "<ButtonRelease-1>", lambda event, tag=j:self._on_item_button_release_1(event, tag))

		self.output.node.bind("<Button-1>", self._on_output_button_1)
		self.output.node.bind("<B1-Motion>", self._on_output_b1_motion)
		self.output.node.bind("<ButtonRelease-1>", self._on_output_button_release_1)


	def setitem(self, name, update_value=False, coord=None, is_output_item=False):
		if name not in self:
			self[name] = Item(self, name, coord=coord or self.get_pointer(random=True))
			self.scale_font()
			if len(self.store) == 1:
				self.app.menu.setview("node_editor", True)
			return

		item = self[name]
		if update_value:
			item.value(self.app.objects[name])
			return

		coord = item.position()
		connection = item.connection
		self[name].destroy()
		if not coord:
			coord = self.get_pointer(random=True)
		self[name] = Item(self, name,
			coord=coord,
			args=item.args,
			kwargs=item.kwargs,
			connection=connection,
			opts=item.opts,
			is_output_item=is_output_item
		)
		self.scale_font()

	def select(self, name):
		if name is None:
			self.selected = None
			return
		if self.selected == name: return
		if self.selected:
			self[self.selected].config("parent", fill=Color.BLACK)
		self[name].config("parent", fill=Color.VERY_LIGHT_PURPLE)
		self.selected = name

	def _on_item_enter(self, event, tag):
		if self.is_busy(): return
		closest = self.get_closest(event.x, event.y, tag) or self.find_closest(event.x, event.y)
		item = self[self.getname(closest)]
		self.hover = closest, item

		if tag == "draggable":
			if item.name != self.selected:
				item.config("parent", fill=Color.LIGHT_PURPLE)
		elif tag in ("output", "wire"):
			item.config("output", fill=Color.HOVER if item.connection else Color.LIGHT_BLACK)
			if item.connection:
				name, argname = item.connection
				self[name].config("arg="+argname, fill=Color.HOVER)
			elif item in self.output.items:
				self.output.hover()
			item.config("wire", "output", fill=Color.HOVER)

	def _on_item_leave(self, event, tag):
		if self.is_busy() or not self.hover: return
		closest, item = self.hover
		self.hover = None

		if tag == "draggable":
			item.config("parent", fill=Color.BLACK if self.getname(closest) != self.selected else Color.VERY_LIGHT_PURPLE)
		elif tag in ("output", "wire"):
			if item.connection:
				name, argname = item.connection
				self[name].config("arg="+argname, fill=Color.PURPLE)
				item.config("output", fill=Color.PURPLE)
				item.config("wire", fill=Color.PURPLE)
			elif item in self.output.items:
				self.output.hover(False)
				item.config("output", fill=Color.PURPLE)
				item.config("wire", fill=Color.PURPLE)
			else:
				item.config("output", fill=Color.EMPTY_NODE)

	def _on_mouse_wheel(self, event, delta=None):
		event_delta = delta or event.delta
		x, y = self.get_pointer()
		if event_delta > 0:
			self.scale("all", x,y, ZOOM_IN, ZOOM_IN)
			self.zoom *= ZOOM_IN
		else:
			self.scale("all", x,y, ZOOM_OUT, ZOOM_OUT)
			self.zoom *= ZOOM_OUT
		self.scale_font()
		self.scale_width()

		if self.output.items:
			for i in self.output.items:
				i.move_wire()

		if self.edit_item:
			self.edit_item.entry.zoom()

	def _on_motion_input(self, event):
		closest = self.find_closest(event.x, event.y)[0]
		if self.hover_input or "input" not in self.gettags(closest): return
		self._on_enter_input(event)

	def _on_enter_input(self, event):
		closest = self.find_closest(event.x, event.y)[0]
		input_item = self[self.getname(closest)]
		argname = self.getname(closest, "arg")
		if argname in input_item.args["connection"]:
			item = input_item.args["connection"][argname]
		elif argname in input_item.kwargs["connection"]:
			item = input_item.kwargs["connection"][argname]
		else:
			return
		self.itemconfig(closest, fill=Color.HOVER)
		item.config("wire", "output", fill=Color.HOVER)
		self.hover_input = closest, item

	def _on_leave_input(self, event):
		if not self.hover_input: return

		closest, item = self.hover_input
		self.itemconfig(closest, fill=Color.PURPLE)
		item.config("wire", "output", fill=Color.PURPLE)
		self.hover_input = None

	def _on_b2_motion(self, event):
		if self.pan_position is None:
			self.pan_position = (event.x, event.y)

		x, y = event.x - self.pan_position[0], event.y - self.pan_position[1]
		self.move("all", x, y)
		self.pan_position = (event.x, event.y)

		if self.output.items:
			for i in self.output.items:
				i.move_wire()

	def _on_item_button_1(self, event, tag):
		closest = self.find_closest(event.x, event.y)[0]
		item = self[self.getname(closest)]

		if tag == "input":
			argname = self.getname(closest, "arg")
			if argname in item.args["connection"]:
				item = item.args["connection"][argname]
			elif argname in item.kwargs["connection"]:
				item = item.kwargs["connection"][argname]
			else:
				return

		if item.connection:
			name, argname = item.connection
			self[name].config("arg="+argname, fill=Color.EMPTY_NODE)

		item.config("wire", "output", fill=Color.PURPLE)
		item.move_wire(event.x, event.y)
		self.connect = (item, None, None, None)

	def _on_output_button_1(self, event):
		if not self.output.items: return
		self.connect = (self.output.items[0], None, None, True)
		self.output.disconnect(self.output.items[0])

	def _on_output_b1_motion(self, event):
		if not self.connect: return
		item, output, argname, was_in_output = self.connect
		item.move_wire(
			self.winfo_pointerx() - self.winfo_rootx(),
			self.winfo_pointery() - self.winfo_rooty()
		)

	def _on_output_button_release_1(self, event):
		if not self.connect: return
		item, output, argname, was_in_output = self.connect
		item.hide_wire()

	def _on_item_b1_motion(self, event, tag):
		if not self.connect: return

		item, output, argname, was_in_output = self.connect

		input_id = self.get_closest(event.x, event.y, "input")
		in_output = self.winfo_containing(event.x_root, event.y_root) in (self.frame, self.output.node)
		in_items = (self.winfo_containing(event.x_root, event.y_root) == self)

		if was_in_output and not in_items:
			self.output.hover(True)
			item.move_wire(event.x, event.y)
			return
		elif item in self.output.items and in_items:
			self.output.disconnect(item)

		if input_id:
			x1,y1,x2,y2 = self.coords(input_id[0])
			item.move_wire((x1 + x2)/2, (y1 + y2)/2)
			output = self[self.getname(input_id)]
			argname = self.getname(input_id, "arg")
			output.config("arg="+argname, fill=Color.HOVER)
			self.connect = item, output, argname, in_output
			return
		else:
			if item.connection:
				item.disconnect()

			item.move_wire(event.x, event.y)
			if output and argname:
				if argname in output.args["connection"] or argname in output.kwargs["connection"]:
					output.config("arg="+argname, fill=Color.PURPLE)
				else:
					output.config("arg="+argname, fill=Color.EMPTY_NODE)
				output = argname = None

		self.connect = item, output, argname, in_output

	def _on_item_button_release_1(self, event, tag):
		if self.connect:
			item, output, argname, in_output = self.connect

			if in_output:
				self.output.connect(item)

			if not output:
				item.disconnect()
			elif argname in output.args:
				output.args[argname] = item
			elif argname in output.kwargs:
				output.kwargs[argname] = item

			self.connect = None

	def is_busy(self):
		return bool(self.dragitem
			or self.connect
			or self.multiselect["items"])

	def _on_delete(self, key=None):
		if self.multiselect["items"]:
			for i in self.multiselect["items"]:
				del self.app.objects[i]
			self.multiselect["items"].clear()
		elif key:
			del self.app.objects[key]

	def _on_multiselect(self, event):
		if self.connect: return

		for name in self.multiselect["items"]:
			self[name].config("parent", fill=Color.BLACK)

		if self.dragitem or not self.multiselect["position"]: return

		x,y = self.multiselect["position"]
		overlapping = self.find_overlapping(x,y,event.x,event.y)
		self.itemconfig(self.multiselect["box"], state="normal")
		self.coords(self.multiselect["box"], x, y, event.x, event.y)

		self.multiselect["items"].clear()

		for i in overlapping:
			name = self.getname(i)
			if name and name not in self.multiselect["items"]:
				self.multiselect["items"].append(name)

		for name in self.multiselect["items"]:
			self[name].config("parent", fill=Color.VERY_LIGHT_PURPLE)


	def _on_motion_editable(self, event):
		closest = self.get_closest(event.x, event.y, "editable")
		if self.hover_edit or "editable" not in self.gettags(closest): return
		self._on_enter_editable(event)

	def _on_enter_editable(self, event, closest=None):
		closest = closest or self.find_closest(event.x, event.y)[0]
		if "editable" not in self.gettags(closest): return

		item = self[self.getname(closest)]
		color = self.itemconfig(closest)["fill"][4]
		self.itemconfig(closest, fill=Color.WHITE)
		self.hover_edit = closest, item, color

	def _on_leave_editable(self, event):
		if self.hover_edit:
			closest, item, color = self.hover_edit
			self.itemconfig(closest, fill=color)
			self.hover_edit = None

	def _on_click_editable(self, event):
		if self.hover_edit and self.dragstart == (event.x, event.y):
			closest, item, color = self.hover_edit
			self.edit_item = item
			item.entry.edit(closest)

	def _on_drag_start(self, event):
		self.dragitem = self.find_closest(event.x, event.y)[0]
		self.dragposition = (event.x, event.y)
		items = self.find_siblings(self.dragitem) #REFACTOR - use item.ids
		for i in items:
			self.tag_raise(i)

		self.dragstart = (event.x, event.y)
		if "editable" in self.gettags(self.dragitem):
			self._on_enter_editable(event, self.dragstart)

	def _on_drag(self, event):
		name = self.getname(self.dragitem)
		if name not in self: return

		item = self[name]
		if "editable" in self.gettags(self.dragitem):
			delta_x = event.x - self.dragposition[0]
			delta_y = event.y - self.dragposition[1]
			self.dragposition = (event.x, event.y)
			key = self.getname(self.dragitem, "argvalue")
			if key == "<value>":
				if isinstance(item.obj, int):
					self.app.objects[item.name] += int(np.sign(delta_x) - np.sign(delta_y))
				elif isinstance(item.obj, float):
					num_decimals = 1 + len(str(item).split(".")[1])
					self.app.objects[item.name] = round(self.app.objects[item.name] + (delta_x - delta_y) / 100, num_decimals)
			else:
				args = item.args if key in item.args else item.kwargs
				if isinstance(args[key], int):
					args[key] = args[key] + int(np.sign(delta_x) - np.sign(delta_y))
				elif isinstance(args[key], float):
					num_decimals = 1 + len(str(item).split(".")[1])
					args[key] = round(args[key] + (delta_x - delta_y) / 100, num_decimals)
			if "<value>" in item.args["connection"]:
				item.args["connection"]["<value>"].disconnect()
			item.resize()
			return

		x, y = self.dragposition
		if self.multiselect["items"]:
			for i in self.multiselect["items"]:
				self[i].move(event.x - x, event.y - y)
		else:
			item.move(event.x - x, event.y - y)

		self.dragposition = (event.x, event.y)


	def _on_drag_stop(self, event):
		if self.dragstart == self.dragposition:
			self.select(self.getname(self.dragitem))
		self.dragitem = None
		self.dragposition = (0,0)

	def _on_button_1(self, event):
		if self.edit_item:
			self.edit_item.entry.finish()

		if self.dragitem or self.connect: return
		if self.hover_edit:
			self[self.getname(self.hover_edit)].entry.finish()
			self.hover_edit = None
			return
		for name in self.multiselect["items"]:
			self[name].config("parent", fill=Color.BLACK)
		self.select(None)

		# if self.dragitem: return

		self.multiselect["items"].clear()
		self.multiselect["position"] = (event.x, event.y)
		self.tag_raise(self.multiselect["box"])

	def _on_button_release_1(self, event):
		self.multiselect["position"] = None
		self.itemconfig(self.multiselect["box"], state="hidden")

	def _on_button_release_2(self, event):
		if not self.pan_position and not self.has_menu:
			self.menu.show(event, [{
				"label": "Add Object",
				"font": "Nunito " + FONT_SIZE["extra-small"] + " bold",
				"foreground": Color.DARK_ORANGE,
				"state": "disabled"
			}] + self.app.menu.object_menu)
		self.has_menu = False
		self.pan_position = None

	# REFACTOR: move the bulk of this into its own class with a __call__ attr so its super simple to call in here
	def _on_item_menu(self, event):
		self.has_menu = True
		item = self[self.getname(self.find_closest(event.x, event.y))]
		if self.multiselect["items"]:
			self.menu.show(event, [{
				"label": "Delete selected items...",
				"command": self._on_delete
			}])
			return

		methods = []
		graph = []
		extras = []
		obj = self.app.objects[item.name]
		value = item.value()
		item_methods = [i for i in dir(obj) if i[:1] != "_" and callable(getattr(obj, i)) and isinstance(i, str)]
		if item_methods:
			methods.append({ "separator": None })
			for fn in item_methods:
				attr = getattr(item.obj, fn)
				methods.append({
					"label": fn,
					"command": lambda fn=fn, attr=attr, item=item: self.run_method(fn, attr, item)
				})

		window = plot.get_window(value)
		if item in self.output.items:
			extras.append({
				"label": "Disconnect Output",
				"command": lambda: self.output.disconnect(item)
			})
		elif not window:
			extras.append({
				"label": "Show Output",
				"command": lambda: self.output.connect(item)
			})
		else:
			extras.append({
				"label": "Plot",
				"command": lambda: self.output.connect(item),
				"state": "normal" if (plot.active_window == window or not plot.is_active()) else "disabled"
			})

		extras.append({
			"separator": None
		})

		if self.app.animate.can_animate(item):
			extras.append({
				"label": "Animate",
				"command": lambda: self.app.animate(item.name)
			})

		if len(item.kwargs) > 0 and len(item.kwargs["connection"]) == 0:
			extras.append({
				"label": "Hide kwargs" if item.opts["show_kwargs"] else "Show kwargs",
				"command": lambda: item.option("show_kwargs")
			})

		if help.getobj(item.obj) is not None:
			extras.append({
				"label": "View Doc",
				"command": lambda: help(item.obj)
			})

		try:
			file = inspect.getsourcefile(item.obj)
		except:
			file = None

		if file:
			extras.append({
				"label": "View Source Code",
				"command": lambda: open_editor(file)
			})

		# graph.append({
		# 	"label": "Set color     " + item.opts["line_color"] if item.opts["line_color"] != Color.BLUE else "Set color",
		# 	"command": lambda: Popup(self.app, item.name + ".set_color", obj=lambda color: item.option("line_color", color), canvas_item=item)
		# })

		self.menu.show(event, extras + methods + [{
			"separator": None
		},{
			"label": "Delete " + item.name,
			"command": lambda: self._on_delete(item.name)
		}])

	def run_method(self, name, attr, item):
		args, kwargs = argspec(attr)
		args = [i for i in args if i not in ("self")]
		if len(args) + len(kwargs) > 0:
			Popup(self.app, [{
				"label": i
			} for i in args] + [{
				"label": k,
				"value": kwargs[k]
			} for k in kwargs],
			lambda params: self._method_result(name, attr, item, params),
			title="Run Item Method",
			header=name)
		else:
			self._method_result(name, attr, item)

	def _method_result(self, name, attr, item, params={}):
		if params:
			try:
				argcount = numargs(attr)
			except:
				argcount = len(params) - 1
			keys = list(params.keys())[1 + argcount:]
			args = [params[i] for i in params][:argcount]
			kwargs = { i:params[i] for i in keys }
			if kwargs:
				result = attr(*args, **kwargs)
			else:
				result = attr(*[i for i in list(params.values()) if i != ""])
		else:
			result = attr()

		item.value(self.app.objects[item.name])
		if instanceof(result, (int, float, complex, bool)):
			self.output.show(result)
		elif result:
			self.app.objects.setobj(name, result, create_new=True)

	def get_pointer(self, random=False):
		if random:
			x = np.random.rand() * self.winfo_width()
			y = np.random.rand() * self.winfo_height()
		else:
			x = self.canvasx(self.winfo_pointerx() - self.winfo_rootx())
			y = self.canvasy(self.winfo_pointery() - self.winfo_rooty())
		return x,y

	def scale_font(self):
		font_items = []
		for i in self:
			font_items.extend([self[i].ids["name"], self[i].ids["class"]])
			if "value" in self[i].ids:
				 font_items.append(self[i].ids["value"])
			for j in self[i].ids:
				if j[:7] == "argname" or j[:9] == "kwargname" or j[:8] == "argvalue" or j[:10] == "kwargvalue":
					font_items.append(self[i].ids[j])

		for i in font_items:
			font = self.itemconfig(i)["font"][3].split(" ")
			tags = self.gettags(i)
			fontsize = FONTSIZE
			for t in tags:
				if t[:9] == "fontsize=":
					if "stop_scaling" in tags and self.zoom < 1:
						fontsize = t[9:]
					else:
						fontsize = str(int(int(t[9:]) * self.zoom) or 1)
			self.itemconfig(i, font=font[0] + " " + fontsize + ("" if len(font) < 3 else " " + font[2]))

	def scale_width(self):
		width_items = [self[i].ids["wire"] for i in self]
		for i in width_items:
			self.itemconfig(i, width=1 + int(self.zoom))

	def find_siblings(self, item):
		name = self.getname(item)
		return self.find_withtag("name=" + name) if name else [item]

	def getname(self, item, key="name"):
		for t in self.gettags(item):
			if t[:len(key) + 1] == key + "=":
				return t[len(key) + 1:]
		return None

	def find_withtag(self, *args):
		if len(args) <= 1:
			return super(NodeEditor, self).find_withtag(args[0])

		result = self.find_withtag(args[0])
		for i in range(1, len(args)):
			result = [j for j in self.find_withtag(args[i]) if j in result]

		if len(result) == 1:
			return result[0]

		return result

	def get_closest(self, x,y, tag=None):
		overlapping = self.find_overlapping(
			x - HITBOX * self.zoom, y - HITBOX * self.zoom,
			x + HITBOX * self.zoom, y + HITBOX * self.zoom
		)

		if tag == None:
			return overlapping

		return tuple([i for i in self.find_closest(x,y) if i in self.find_withtag(tag)])
