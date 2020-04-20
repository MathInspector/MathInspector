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
from .text import TextEditor
from .notebooktab import NotebookTab
from util import getnamefrompath
from settings import Color
import os, re

class EditorTab(tk.Frame):
	def __init__(self, parent, content=None, filepath=None, name="Untitled", wrap="none", is_preview=False, syntax=None, *args, **kwargs):
		tk.Frame.__init__(self, parent, background=Color.BACKGROUND, *args, **kwargs)
		
		self.text = TextEditor(self, 
			wrap=wrap, 
			syntax=syntax or os.path.splitext(filepath)[1] if filepath else None
		)
		
		self.name = name
		self.filepath = filepath
		self.wrap = wrap
		self.text.tag_configure("bigfont", font=("Helvetica", "24", "bold"))
		self.is_modified = False
		self.label = NotebookTab(parent, name, len(parent.tabs), {"side": "left"}, 
			closebtn=True,
			font="Monospace 12" if not is_preview else "Monospace 12 italic",
			foreground=Color.DARKER_GREY,
			background=Color.FADED_GREY,
			selected_bg=Color.BACKGROUND,
			selected_fg=Color.WHITE
		)
		self.is_preview = is_preview

		self.log = tk.Frame(self, height=40, background=Color.RED)
		self.title = tk.Label(self.log, font="Monospace 16 bold italic", background=Color.RED, foreground=Color.BLUE)
		self.message = tk.Label(self.log, font="Nunito 16", background=Color.RED, foreground=Color.WHITE)
		self.title.pack(side="left", padx=32)
		self.message.pack(side="left")
		self.text.linenumbers.pack(side="left", fill="y")
		self.text.pack(side="right", fill="both", expand=True)
		if content:
			self.show(content, name=name)
		elif filepath:
			self.show(filepath=filepath, name=name)
		
		self.text.bind("<<Modified>>", self._on_modified)

	def show(self, content=None, name=None, filepath=None, italic=False, syntax=None):
		name = name or os.path.basename(filepath) if filepath else "Untitled"
		if filepath and not content:
			self.filepath = filepath
			content = open(filepath, "r").read()

		if syntax:
			self.text.syntax = syntax
			
		self.text.config(undo=False)
		self.text.delete()
		self.text.insert("1.0", content)
		self.text.delete("end-1c", "end")
		self.text.config(undo=True)
		self.is_modified = False
		self.text.edit_modified(False)
		
		if syntax == ".py" or filepath and os.path.splitext(filepath)[-1] == ".py":
			self.text.syntax_highlight()

		# if name or italic:
		# 	self.rename(name, italic=italic)

	def showmessage(self, title, text=None):
		# @REFACTOR move this into hide_message, its clearer, rename to show_message
		if title == None:
			return self.log.pack_forget()
		
		self.text.linenumbers.pack_forget()
		self.text.pack_forget()
		self.title.config(text=title)
		self.message.config(text=text)
		self.log.pack(side="bottom", fill="both")
		self.text.linenumbers.pack(side="left", fill="y")
		self.text.pack(side="right", fill="both", expand=True)

	def rename(self, name=None, italic=False):
		if name:
			self.name = name
		if self.label:
			self.label.label.config(text=self.name or "Untitled", font="Monospace 12 italic" if italic else "Monospace 12")

	def setfile(self, filepath):
		self.is_modified = False
		self.is_keypress = False
		self.filepath = filepath
		name = os.path.basename(filepath)
		ext = os.path.splitext(name)[1]
		self.rename(name)
		if self.label:
			self.label.toggle_unsaved(False)

	def getstate(self):
		return {
			"name": self.name,
			"filepath": self.filepath, 
			"content": self.text.get("1.0", "end-1c"),
			"is_preview": self.is_preview,
			"is_selected": self.label.is_selected,
			"is_modified": self.is_modified,
			"wrap": self.wrap
		}

	def _on_modified(self, event):
		self.is_modified = self.text.edit_modified()		
		self.label.toggle_unsaved(self.is_modified)
		if self.is_preview and self.is_modified:
			self.is_preview = False
			self.rename(italic=False)		


