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
from .highlightedtext import HighlightedText
from .blinkingcursor import BlinkingCursor
from .linenumbers import LineNumbers
from settings import Color, Font
from util import ObjectContainer
import style.syntax

class TextEditor(HighlightedText):
	def __init__(self, parent, content=None, on_change_callback=None, auto_indent=True, *args, **kwargs):
		HighlightedText.__init__(self, parent, *args, **kwargs, font="Menlo-Regular 15")
				
		self.linenumbers = LineNumbers(parent, width=56)
		self.linenumbers.attach(self)			
		self.keypress = ObjectContainer(getitem=lambda key: self.keypress.store[key] if key in self.keypress.store else False)
		self._orig = self._w + "_orig"
		self.tk.call("rename", self._w, self._orig)
		self.tk.createcommand(self._w, self._proxy)
		self.bind("<Configure>", self._on_configure)
		
		if auto_indent:
			self.bind("<Key>", self._on_key)		
			self.bind("<KeyRelease>", self._on_key_release)
		
		self.bind("<<Update>>", self._on_change)
		self.bind("<<Modify>>", self._on_modify)
		self.on_change_callback = on_change_callback

	def _on_key(self, event):
		self.keypress[event.keysym] = True		
		if event.keysym == "Return":
			return "break"
		
	def _on_key_release(self, event):
		self.keypress[event.keysym] = False
		index = self.index("insert")
		if not index: return
		line = int(index.split(".")[0])
		start = str(line) + ".0"
		end = str(line + 1) + ".0-1c"
		num_tabs = self.get(start, end).count("\t")
		if event.keysym == "Return":
			self.insert(index, "\n" + "\t" * num_tabs)
			self.see("insert")
		# self.syntax_highlight()	
		
	def _on_configure(self, event):
		self.linenumbers.redraw()

	def _on_change(self, event):
		self.linenumbers.redraw()
		if self.on_change_callback:
			self.on_change_callback()

	def _on_modify(self, event):
		self.syntax_highlight()
	
	def _proxy(self, *args):
		try:
			cmd = (self._orig,) + args
			result = self.tk.call(cmd)
		except:
			return

		did_change = args[0] in ("insert", "replace", "delete") or args[0:3] == ("mark", "set", "insert")

		if args[0] in ("insert", "replace", "delete") and self.syntax == ".py":
			self.event_generate("<<Modify>>")

		if args[0:3] == ("mark", "set", "insert"):
			self.event_generate("<<MarkSet>>")

		if args[0] in ("insert", "replace", "delete"):
			self.event_generate("<<Change>>", when="tail")
		
		if (did_change
			 or
			args[0:2] == ("xview", "moveto") or
			args[0:2] == ("xview", "scroll") or
			args[0:2] == ("yview", "moveto") or
			args[0:2] == ("yview", "scroll")
		):
			self.event_generate("<<Update>>", when="tail")

		return result             
