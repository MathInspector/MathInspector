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
import builtins
from tkinter import ttk
from settings import Color
from util import makereadonly, findcommonstart
from widget.text import TextEditor
from widget import HighlightedText

class Console(TextEditor):
	def __init__(self, app, *args, **kwargs):	
		TextEditor.__init__(self, app, *args, **kwargs, background=Color.DARK_BLACK)
		self.app = app
		self.history = []
		self.history_index = 0
		self.current_entry = None
		self.tabcount = 0
		self.newprompt()
		self.tag_configure("console_prompt", foreground=Color.PROMPT, font="Menlo 15 bold")
		self.tag_configure("result", foreground=Color.BLUE)
		self.tag_configure("error", foreground=Color.RED)
		self.bind("<Key>", self._on_key)
		self.bind("<KeyRelease>", self._on_key_release)
		self.bind("<Configure>", self._on_configure)
		self.bind("<<MarkSet>>", self._on_mark_set)
		
	def clear(self):
		self.delete()
		self.newprompt()
		
	def _on_key(self, event):
		index = [int(i) for i in self.index("insert").split(".")]
		start = [int(i) for i in self.index("end-1c linestart").split(".")]
		end = [int(i) for i in self.index("end").split(".")]

		# @TODO allow copy/paste when ready for that
		if (end[0] - index[0] > 1
				or (index[1] - start[1] < 5 and event.keysym != "Right")):
			self.mark_set("insert", "end")

		if event.keysym in ("Left", "BackSpace") and index[1] - start[1] < 6:
			return "break"

		if event.keysym == "Up":
			if self.history_index == len(self.history):
				self.current_entry = self.getcmd()
			if self.history_index > 0:
				self.history_index -= 1
				self.replace(self.history[self.history_index])	
			return "break"
		
		if event.keysym == "Down":
			if self.history_index < len(self.history) - 1:
				self.history_index += 1
				self.replace(self.history[self.history_index])
			elif self.history_index == len(self.history) - 1:
				self.history_index += 1
				self.replace(self.current_entry or "")			
			return "break"		

		if event.keysym == "Tab" and self.autocomplete():
			return "break"

		if event.keysym == "Return":
			cmd = self.getcmd()

			if cmd == "clear":
				self.delete("1.0", "end")
				self.newprompt()
			else:
				self.app.execute(cmd)
				self.tabcount = 0
				if cmd:
					self.history.append(cmd)
					self.history_index = len(self.history)
			return "break"

		self.tabcount = 0
		return super(Console, self)._on_key(event)
	
	def _on_key_release(self, event):
		if event.keysym == "Return":
			return "break"
		return super(Console, self)._on_key_release(event)

	def _on_mark_set(self, event):
		pass
		# line, col = self.index("insert").split(".")
		# endline = self.index("end-1c").split(".")[0]
		# if line == endline and int(col) < 5:
		# 	self.after(100, lambda: self.mark_set("index", "end"))

	def _on_configure(self, event):
		self.see("insert")
		super(Console, self)._on_configure(event)


	def getcmd(self):
		return str(self.get("end-1c linestart", "end")[5:]).strip()

	def run(self, cmd):
		self.history.append(cmd)	
		self.insert("end", cmd)
		self.app.execute(cmd)
		self.app.setview("console")
		
	def newprompt(self):
		self.insert("end", ">>>  ")
		self.highlight(">>>", "console_prompt")
		self.see("end")
		self.focus()
		self.mark_set("insert", "end")
		self.syntax_highlight()
		self.edit_reset()

	def result(self, res):
		self.insert("end", "\n")
		if res is None:
			self.newprompt()
			return

		self.insert("end", "\n" + str(res) + "\n\n", "error" if isinstance(res, Exception) else None)
		self.newprompt()

	def replace(self, cmd):
		# @TODO find better way to do these index manipulations
		index = self.index("end")
		row = str( int(index.rsplit('.')[0]) - 1 )

		self.delete(row + ".5", "end")
		self.insert("end", cmd)
		return "break"

	# REFACTOR - may actually need to move this into math inspector so it gets all the globals like app
	def autocomplete(self):
		cmd = self.getcmd()
		result = (
			[i for i in self.app.objects if cmd == i[:len(cmd)] and i != cmd] + 
			[i for i in self.app.modules if cmd == i[:len(cmd)] and i != cmd] + 
			[i for i in dir(builtins) if cmd == i[:len(cmd)] and i != cmd] + 
			[i for i in locals() if cmd == i[:len(cmd)] and i != cmd]
		)

		if len(result) == 0:
			return False
		
		if len(result) == 1:
			self.replace(result[0])
		elif self.tabcount < 1:
			common = findcommonstart(result)
			if common == cmd:
				print ("\a")
				self.tabcount += 1
			else:
				self.replace(common)
				self.tabcount = 0
		else:
			self.result("        ".join(result))
			self.replace(cmd)

		return True
