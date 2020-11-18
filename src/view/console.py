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
from widget import Text

class Console(Text):
	def __init__(self, app):	
		Text.__init__(self, app, background=Color.DARK_BLACK, font="Menlo 16")
		self.app = app
		self.history = { "items": [], "index": 1, "current": None }
		
		self.tag_configure("console_prompt", foreground=Color.PROMPT, font="Menlo 16 bold")
		self.tag_configure("result", foreground=Color.BLUE)
		self.tag_configure("error", foreground=Color.RED)
		
		self.bind("<Key>", self._on_key)
		self.bind("<<Selection>>", self._on_text_selection)
		self.bind("<<Modify>>", lambda event: self.syntax_highlight("end-1c linestart+5c", "end-1c"))

		self.prompt()
		
	def prompt(self, text=None):
		self.insert("end", ">>>  ", "console_prompt")
		if text:
			self.insert("end", text)
		self.see("end")
		self.edit_reset()
			
	def command(self, command=None, history=None):
		if command == None and history == None:
			return self.get("end-1c linestart+5c", "end-1c")

		if command == "clear":
			self.delete("1.0", "end")
			self.prompt()
			return

		if history == "up" and len(self.history["items"]) > 0:
			if self.history["index"] == len(self.history["items"]):
				self.history["current"] = self.command()
			if self.history["index"] > 0:
				self.history["index"] -= 1
			command = self.history["items"][self.history["index"]]
		elif history == "down":
			if self.history["index"] < len(self.history["items"]) - 1:
				self.history["index"] += 1
				command = self.history["items"][self.history["index"]]
			elif self.history["index"] >= len(self.history["items"]) - 1:
				self.history["index"] = len(self.history["items"])
				command = self.history["current"]

		self.delete("end-1c linestart+5c", "end")
		self.insert("end", command)

		if not history:
			self.history["items"].append(command)
			self.history["index"] = len(self.history["items"])
			result = self.app.execute(command)
			self.insert("end", "\n" + str(result) + "\n\n", "error" if isinstance(result, Exception) else None)			
			self.prompt()

	def autocomplete(self):
		command = self.command()
		if command.count("."):
			choices = self.app.eval("dir(" + command.rsplit(".", 1)[0] + ")")
		else:
			local_objects = [i for i in self.app.eval("locals()") if i[:2] != "__"]
			global_objects = [i for i in self.app.eval("globals()") if i[:2] != "__"]
			choices = local_objects + global_objects

		result = []
		query = command.rsplit(".", 1)
		for j in choices:
			if len(query) == 1:
				if j[:len(query[0])] == query[0]:
					result.append(j)
			else:
				if j[:len(query[1])] == query[1]:
					result.append(j)

		if len(result) == 0:
			print ("\a")
			return
	
		keyword = query[0] if len(query) == 1 else query[1]
		common = findcommonstart(result)
	
		if len(result) == 1:
			self.insert("end", result[0][len(keyword):])
		elif keyword[:len(common)] != common:
			self.insert("end", common[len(keyword):])
		else:
			self.insert("end", "\n" + "        ".join(result) + "\n\n")
			self.prompt(command)

	def state(self, history=None):
		if not history:
			return self.history

		self.history = history
		self.history["index"] = len(self.history["items"])

	def clear(self):
		self.history = { "items": [], "index": 1, "current": None }
		self.delete("1.0", "end")
		self.prompt()

	def _on_key(self, event):
		index = [int(i) for i in self.index("insert").split(".")]
		start = [int(i) for i in self.index("end-1c linestart").split(".")]
		end = [int(i) for i in self.index("end").split(".")]

		if (end[0] - index[0] > 1
				or (index[1] - start[1] < 5 and event.keysym != "Right")):
			self.mark_set("insert", "end-1c linestart+5c")

		if event.keysym in ("BackSpace", "Left"):
			col = index[1] - start[1]
			selected_range = self.tag_ranges("sel")
			if col == 5 and selected_range:
				self.delete(*selected_range)
				return "break"
			elif col < 6:
				print ("\a")
				return "break"

		if event.keysym == "Up":
			self.command(history="up")	
			return "break"
		
		if event.keysym == "Down":
			self.command(history="down")	
			return "break"		

		if event.keysym == "Tab":
			self.autocomplete()
			return "break"

		if event.keysym == "Return":
			self.command(self.command())
			return "break"

	def _on_text_selection(self, event):
		selected = self.tag_ranges("sel")
		if len(selected) == 0: return
		
		line, col = str(selected[0]).split(".")
		endline = self.index("end-1c").split(".")[0]

		if line == endline and int(col) < 5:
			self.tag_remove("sel", selected[0], str(line) + ".5")
			self.mark_set("insert", str(line) + ".5")
