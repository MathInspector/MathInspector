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
from settings import Color, Font, Widget
from widget.text import TextEditor

# TODO - add this to settings.json
TEXTWRAP_WIDTH = 32

class Entry(TextEditor):
	def __init__(self, item, *args, **kwargs):
		TextEditor.__init__(self, item.canvas, 
			syntax=None, 
			auto_indent=False,
			# on_change_callback=self._on_edit_change, 
			*args, **kwargs)

		self.item = item		
		self.app = item.canvas.app
		self.window = None
		self.edit_id = None
		self.bind("<Key>", self._on_key)	

		# sv = tk.StringVar()
		# sv.trace("w", lambda name, index, mode, sv=sv:self._on_edit_change())		
		# use <<Change>> event instead of sv
		# @REFACTOR - add this to __init__ call
		self.config(
			anchor="w",
			borderwidth=0, 
			background=Color.GREEN, #Color.VERY_LIGHT_PURPLE,
			insertbackground=Color.WHITE,
			selectbackground=Color.VERY_DARK_GREY,
			width=80,
			height=40,
			wrap="word"
		)

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
		if isinstance(self.item.value, dict):
			height = len(self.item.value)
			width =  len(max(value.split("\n"), key=len)) - 3
		else:
			width =  max(8, min(int(len(value)*2/3), 22))
			height = 1 + textwrap.fill(value, TEXTWRAP_WIDTH, replace_whitespace=False).count("\n")

		parent_width = int( self.item.canvas.zoomlevel * Widget.ITEM_SIZE / 12)
		self.config(
			foreground=color,
			font=font,
			width=0 if not value else width,
			height=height,
		)		

		x,y = self.item.canvas.coords(canvas_id)
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
			
			self.item.canvas.itemconfig(self.edit_id, text=str(value or "None"))
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

				# self.app.workspace.log.show(err)
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
		x,y = self.item.get_position()
		content = self.get()
		# width =   self.item.canvas.zoomlevel * min(len(content), 24)
		# height =  self.item.canvas.zoomlevel * (1 + textwrap.fill(content).count("\n")) # @TODO: change this to adjust height and pretty print various things like list/dict/long strings

		# print ("WIDTH", width)
		width =  max(2, min(len(content), 22))
		height = 1 + int(textwrap.fill(content, TEXTWRAP_WIDTH, replace_whitespace=False).count("\n"))
		print ("h", height)		
		# height = self.item.canvas.zoomlevel * Widget.ITEM_SIZE # @TODO: change this to adjust height and pretty print various things like list/dict/long strings
		# width =  self.item.canvas.zoomlevel * max(Widget.ITEM_SIZE, 8 * min(len(content), TEXTWRAP_WIDTH))
		self.config(width=width, height=height)
		# width *= self.item.canvas.zoomlevel * Widget.VALUE_LABEL_SIZE
		width =  1#self.item.canvas.zoomlevel * max(Widget.ITEM_SIZE, 16 + 8 * min(len(content), TEXTWRAP_WIDTH))
		height = 1#self.item.canvas.zoomlevel * max(Widget.ITEM_SIZE, 16 + 20 * (1 + int(self.index("end").split(".")[0])	)) # @TODO: change this to adjust height and pretty print various things like list/dict/long strings
		# height += 20 * self.item.canvas.zoomlevel
		if self.edit_id == self.item.value_label:
			node_size = Widget.NODE_SIZE * self.item.canvas.zoomlevel
			self.item.canvas.coords(self.item.canvas_id, x - width/2, y - height/2, x + width/2, y + height/2)
			self.item.canvas.coords(self.item.output, x + width/2 - node_size, y - node_size, x + width/2 + node_size, y + node_size)
			self.item.canvas.coords(self.item.value_label, x, y)        
			self.item.canvas.coords(self.item.class_label, x, y + height*3/4)
			if "default" in self.item.args:
				self.item.canvas.coords(self.item.args["default"]["input"], x - width/2 - node_size, y - node_size, x - width/2 + node_size, y + node_size)
			if self.item.output_connection:
				arg = self.item.output_connection.getarg("connection", self.item)
				if arg:
					x1,y1,x2,y2 = self.item.canvas.coords(arg["input"])
					self.item.move_wire(x1 + (x2 - x1)/2, y1 + (y2 - y1)/2)
			for j in self.item.args:
				if self.item.args[j]["connection"]:
					x1,y1,x2,y2 = self.item.canvas.coords(self.item.args[j]["input"])
					self.item.args[j]["connection"].move_wire(x1 + (x2 - x1)/2, y1 + (y2 - y1)/2)


