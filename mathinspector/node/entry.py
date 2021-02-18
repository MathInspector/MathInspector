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
import textwrap, traceback
from pprint import pformat
from ..util import fontcolor
from ..style import Color
from ..widget.text import Text

class Entry(Text):
	def __init__(self, item):
		Text.__init__(self, item.canvas,
			foreground=Color.VERY_LIGHT_GREY,
			# background=Color.GREEN,
			background=Color.VERY_LIGHT_PURPLE,
			padx=0,
			pady=0)

		self.item = item
		self.canvas = item.canvas
		self.app = item.canvas.app
		self.argname = None
		self.window = None
		self.edit_id = None
		self.font = None
		self.tag_configure("center", justify="center")
		self.bind("<Key>", self._on_key)
		self.bind("<<Modify>>", self._on_edit_change)

	def edit(self, canvas_id, color=Color.VERY_LIGHT_GREY):
		self.edit_id = canvas_id
		self.argname = self.canvas.getname(canvas_id, "argvalue")
		self.canvas.itemconfig(canvas_id, text="")
		self.delete("1.0", "end")
		# REFACTOR - way too busy with these nested if's
		arg = None if self.argname == "<value>" else self.item.args[self.argname] if self.argname in self.item.args else self.item.kwargs[self.argname]
		self.insert("end", self.item.content(truncate=False) if self.argname == "<value>" else "" if arg is None else self.item.content(arg, truncate=False))

		font = self.canvas.itemconfig(canvas_id)["font"][4]
		params = font.split(" ")
		fontsize = 12 if len(params) < 2 else int(int(params[1]) / self.canvas.zoom)

		self.font = params[0] + " " + str(int(fontsize)) + ("" if len(params) < 3 else (" " + " ".join(params[2:])))
		if self.argname == "<value>":
			self.config(font=font, **self.item.text_dimensions(self.item.obj))
		else:
			self.config(font=font, **self.item.text_dimensions(arg))

		if isinstance(self.item.obj, str):
			self.config(foreground=Color.YELLOW)

		opts = { "window": self }

		self.window = self.canvas.create_window(*self.canvas.coords(canvas_id), **opts)
		self.focus()

	def _on_edit_change(self, event=None):
		if self.item.is_callable: return
		try:
			content = self.item.obj.__class__(self.get("1.0", "end"))
		except:
			content = self.get("1.0", "end")

		self.config(**self.item.text_dimensions(content, truncate=False))
		self.item.resize(content)

		if not isinstance(self.item.obj, str):
			self.syntax_highlight()

	def zoom(self):
		params = self.font.split(" ")
		fontsize = int(12 if len(params) < 2 else int(params[1]))
		self.config(font=params[0] + " " + str(int(fontsize * self.canvas.zoom)) + ("" if len(params) < 3 else (" " + params[2])))

	def finish(self, cancel=False):
		if cancel:
			if self.argname == "<value>":
				content = self.item.content()
			else:
				arg = self.item.args[self.argname] if self.argname in self.item.args else self.item.kwargs[self.argname]
				content = self.item.content(arg)

			self.canvas.itemconfig(self.edit_id, text=content)
			self.item.resize()
			self.hide()
			return

		content = self.get("1.0", "end-1c")
		if content == "":
			content = "None"

		if self.argname == "<value>":
			try:
				result = self.app.console.eval(content)
			except:
				result = content

			try:
				self.app.objects[self.item.name] = self.item.obj.__class__(result)
			except:
				self.app.console.prompt.push("")
				self.app.console.showtraceback()
				self.finish(cancel=True)
				return
		elif self.argname in self.item.args:
			self.item.args[self.argname] = self.app.console.eval(content)
		else:
			self.item.kwargs[self.argname] = self.app.console.eval(content)

		self.hide()

	def hide(self):
		self.canvas.delete(self.window)
		self.window = None
		self.edit_id = None
		self.font = None
		self.canvas.edit_item = False

	def _on_key(self, event):
		if event.keysym == 'Escape':
			self.finish(cancel=True)
			return "break"
		elif event.keysym == 'Return':
			self.finish()
			return "break"
