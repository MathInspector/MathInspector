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
import textwrap
from pprint import pformat
from util import get_font_color
from settings import Color, Font, Widget
from widget.text import TextEditor

# TODO - add this to settings.json
TEXTWRAP_WIDTH = 32
LABEL_OFFSET = 32

class Entry(TextEditor):
	def __init__(self, item, *args, **kwargs):
		TextEditor.__init__(self, item.canvas, 
			syntax=None, 
			auto_indent=False,
			background=Color.DARK_BLACK,
			padx=0,
			pady=0,
			on_change_callback=self._on_edit_change, 
			*args, **kwargs)

		self.item = item		
		self.app = item.canvas.app
		self.window = None
		self.edit_id = None
		self.bind("<Key>", self._on_key)	

	def hide(self):
		self.item.canvas.delete(self.window)
		self.window = None    	

	def edit(self, canvas_id, color=Color.VERY_LIGHT_GREY, font=Font.ALT + " 12"):
		if canvas_id == self.item.value_label:
			font = Font.ALT + " " + str(int(Widget.VALUE_LABEL_SIZE * self.item.canvas.zoomlevel) or 1)
			if isinstance(self.item.value, dict):
				value = pformat(self.item.value, width=4)[1:-1]
			else:
				value = str(self.item.value or "")
		else:
			arg = self.item.getarg("value_label", canvas_id)
			if arg:
				font = Font.ALT + " " + str(int(Widget.ARG_VALUE_SIZE * self.item.canvas.zoomlevel) or 1)
				value = str(arg["value"] or "")
				canvas_id = arg["value_label"]
			else:
				return
		
		self.edit_id = canvas_id
		self.item.canvas.itemconfig(canvas_id, text="")

		self.delete("1.0", "end")
		self.insert("1.0", value or "")
		self.delete("end-1c", "end") # NOTE - this is because tkinter text widget always adds a newline on insert, so annoying!
		
		# REFACTOR - make this a fn in canvas item .getwidth()
		# its not getting the correct width/height i dont think... 
		x,y = self.item.canvas.coords(canvas_id)
		if isinstance(self.item.value, dict):
			height = len(self.item.value)
			width =  len(max(value.split("\n"), key=len)) - 3
		elif callable(self.item.value):
			width =  max(8, min(int(len(value)*2/3), 22))
			height = 1 + textwrap.fill(value, TEXTWRAP_WIDTH, replace_whitespace=False).count("\n")
			x += 4*width*self.item.canvas.zoomlevel
		elif isinstance(self.item.value, str):
			width =  min(int(len(value)), TEXTWRAP_WIDTH)
			height = int(len(value)/TEXTWRAP_WIDTH)			
		else:
			width =  min(int(len(value)), 10)
			height = int(len(value)/10)
			if len(value) % 10 != 0:
				height += 1

		self.config(
			foreground=color,
			font=font,
			width=8 if not value else width,
			height=height,
		)		

		self.window = self.item.canvas.create_window(
			x,
			y,
			window=self
		)

		self.focus()
	
	def finish(self, cancel=False):
		self.hide()
		if cancel:
			value = None
			if self.edit_id == self.item.value_label:
				value = self.item.value
			else:
				arg = self.item.getarg("value_label", self.edit_id)
				if arg:
					self.item.canvas.itemconfig(self.edit_id, text=str(arg["value"] or "None"))
					value = arg["value"]
			
			self.item.canvas.itemconfig(self.edit_id, text=str(value), fill=get_font_color(value))
			return

		if self.edit_id == self.item.value_label and isinstance(self.item.value, str):
			value = self.get()
		else:
			cmd = self.get()
			try:
				if isinstance(self.item.value, dict):
					value = None if not cmd else self.app.execute("{" + cmd + "}", __SHOW_RESULT__=False, __EVAL_ONLY__=True)
				else:
					value = None if not cmd else self.app.execute(cmd, __SHOW_RESULT__=False, __EVAL_ONLY__=True)
			except Exception as err:
				if self.edit_id == self.item.value_label:
					self.item.canvas.itemconfig(self.item.value_label, text=str(self.item.value))
				else:
					for j in self.item.args:
						if "value_label" in self.item.args[j] and self.item.args[j]["value_label"] == self.edit_id:
							self.item.canvas.itemconfig(self.edit_id, text=str(self.item.args[j]["value"] or "None"))

				self.app.workspace.log.show(err)
				return
	
		if self.edit_id == self.item.value_label:
			self.app.objects.__setitem__(self.item.name, value)
		else:
			name = self.item.getarg("value_label", self.edit_id, name=True)
			if name:
				self.item.setarg(name, value)
		
		self.edit_id = None
		self.item.canvas.event = None

	def _on_key(self, event):
		if event.keysym == 'Escape':
			self.finish(cancel=True)
		elif event.keysym == 'Return':
			self.finish()
	
	def _on_edit_change(self):
		if self.edit_id != self.item.value_label: return

		x,y = self.item.get_position()
		content = self.get().strip()

		if isinstance(self.item.value, str):
			# @TODO - fix up style of typing strings into widget, there are a few quirks
			width =  min(int(len(content)), 20)
			height = 1 + textwrap.fill(content, TEXTWRAP_WIDTH, replace_whitespace=False).count("\n")
		else:
			width =  min(len(content), 10)
			height = int(len(content)/10)
			if len(content) % 10 != 0:
				height += 1

		self.config(width=width, height=height)
		
		node_size = Widget.NODE_SIZE * self.item.canvas.zoomlevel
		
		if isinstance(self.item.value, str):
			value_text = textwrap.fill(content, TEXTWRAP_WIDTH, replace_whitespace=False)
			widget_width =  self.item.canvas.zoomlevel * max(Widget.ITEM_SIZE, 16 + 8 * min(len(value_text), TEXTWRAP_WIDTH))
			widget_height = self.item.canvas.zoomlevel * max(Widget.ITEM_SIZE, 16 + 20 * (1 + value_text.count("\n")))
			# widget_width =  self.item.canvas.zoomlevel * (20 + max(60, len(value_text) * 12))
			# widget_height = self.item.canvas.zoomlevel * Widget.ITEM_SIZE # @TODO: change this to adjust height and pretty print various things like list/dict/long strings
		else:
			value_text = str(content) if len(str(content) or "") <= 10 else str(content)[:10] + "..."
			widget_width =  self.item.canvas.zoomlevel * (20 + max(60, len(value_text) * 12))
			widget_height = self.item.canvas.zoomlevel * Widget.ITEM_SIZE # @TODO: change this to adjust height and pretty print various things like list/dict/long strings

		self.item.canvas.coords(self.item.canvas_id, x - widget_width/2, y - widget_height/2, x + widget_width/2, y + widget_height/2)
		self.item.canvas.coords(self.item.output, x + widget_width/2 - node_size, y - node_size, x + widget_width/2 + node_size, y + node_size)
		self.item.canvas.coords(self.item.value_label, x, y)        
		self.item.canvas.coords(self.item.class_label, x, y + widget_height/2 + self.item.canvas.zoomlevel * LABEL_OFFSET)

		if "default" in self.item.args:
			self.item.canvas.coords(self.item.args["default"]["input"], x - widget_width/2 - node_size, y - node_size, x - widget_width/2 + node_size, y + node_size)


		# width =   self.item.canvas.zoomlevel * min(len(content), 24)
		# height =  self.item.canvas.zoomlevel * (1 + textwrap.fill(content).count("\n")) # @TODO: change this to adjust height and pretty print various things like list/dict/long strings

		# print ("WIDTH", width)
		# width =  max(2, min(len(content), 22))
		# height = 1 + int(textwrap.fill(content, TEXTWRAP_WIDTH, replace_whitespace=False).count("\n"))
		# height = self.item.canvas.zoomlevel * Widget.ITEM_SIZE # @TODO: change this to adjust height and pretty print various things like list/dict/long strings
		# width =  self.item.canvas.zoomlevel * max(Widget.ITEM_SIZE, 8 * min(len(content), TEXTWRAP_WIDTH))
		# width *= self.item.canvas.zoomlevel * Widget.VALUE_LABEL_SIZE
		# width =  1#self.item.canvas.zoomlevel * max(Widget.ITEM_SIZE, 16 + 8 * min(len(content), TEXTWRAP_WIDTH))
		# height = 1#self.item.canvas.zoomlevel * max(Widget.ITEM_SIZE, 16 + 20 * (1 + int(self.index("end").split(".")[0])	)) # @TODO: change this to adjust height and pretty print various things like list/dict/long strings
		# height += 20 * self.item.canvas.zoomlevel
		# if self.edit_id == self.item.value_label:
			# node_size = Widget.NODE_SIZE * self.item.canvas.zoomlevel
			# self.item.canvas.coords(self.item.canvas_id, x - width/2, y - height/2, x + width/2, y + height/2)
			# self.item.canvas.coords(self.item.output, x + width/2 - node_size, y - node_size, x + width/2 + node_size, y + node_size)
			# self.item.canvas.coords(self.item.value_label, x, y)        
			# self.item.canvas.coords(self.item.class_label, x, y + height*3/4)
			# if "default" in self.item.args:
			# 	self.item.canvas.coords(self.item.args["default"]["input"], x - width/2 - node_size, y - node_size, x - width/2 + node_size, y + node_size)
			# if self.item.output_connection:
			# 	arg = self.item.output_connection.getarg("connection", self.item)
			# 	if arg:
			# 		x1,y1,x2,y2 = self.item.canvas.coords(arg["input"])
			# 		self.item.move_wire(x1 + (x2 - x1)/2, y1 + (y2 - y1)/2)
			# for j in self.item.args:
			# 	if self.item.args[j]["connection"]:
			# 		x1,y1,x2,y2 = self.item.canvas.coords(self.item.args[j]["input"])
			# 		self.item.args[j]["connection"].move_wire(x1 + (x2 - x1)/2, y1 + (y2 - y1)/2)


