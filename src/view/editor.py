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

from widget import Notebook, EditorTab
from settings import Color
from util import readfile, name_and_extension
from tkinter import filedialog, messagebox
import re, inspect, os
from numpy import ndarray

RE_LINE = re.compile(r"line ([0-9]*)")
RE_NAME_ERROR = re.compile(r"name '(\w+)'")

class Editor(Notebook):
	def __init__(self, app, *args, **kwargs):
		Notebook.__init__(self, app, onchangetab=self.focus, is_draggable=True, tabbackground=Color.BLACK)
		self.app = app

	def getstate(self):
		return self.notebook.select(), [self.tab(i).getstate() for i in self.tabs]

	def setstate(self, selected, state=[]):
		for tab in state: 
			tab_id = self.add(tab["name"], tab["filepath"], tab["content"], tab["is_preview"])
			if tab["is_selected"]:
				selected = tab_id
			if tab["is_preview"]:
				self.tab(tab_id).rename(tab["name"], italic=True)
			if tab["is_modified"]:
				self.tab(tab_id).is_modified = True
				if self.tab(tab_id).label:
					self.tab(tab_id).label.toggle_unsaved(True)
		
		if selected:
			self.notebook.select(selected)

	def select(self, key, filepath=None):
		obj = self.app.objects[key] if key in self.app.objects else self.app.modules[key] if key in self.app.modules else None

		if filepath:
			tab_id = self.tab_id(attr=("filepath", filepath))
			preview_tab_id = self.tab_id(attr=("is_preview", True))
			if tab_id:
				self.notebook.select(tab_id)
				return
			
			if preview_tab_id:
				self.close(preview_tab_id)
			
			new_tab_id = self.add(filepath=filepath, is_preview=True)
		elif isinstance(obj, ndarray):
			pass
		elif obj:
			try:
				src = inspect.getsource(obj)
			except Exception as e:
				print ("nah", e)
				return
			
			src = re.sub(r"(?s)\"\"\".*?\"\"\"", "", src)
			src = re.sub(r"(?s)'''.*?'''", "", src)
			tab_id = self.tab_id(attr=("filepath", obj.__name__))
			preview_tab_id = self.tab_id(attr=("is_preview", True))
			if tab_id:
				self.notebook.select(tab_id)
				return
			
			if preview_tab_id:
				self.close(preview_tab_id)
			new_tab_id = self.add(obj.__name__, filepath or obj.__name__, src, True, ".py")		

	# REFACTOR - try cleaning this up with **kwargs
	def add(self, name=None, filepath=None, content=None, is_preview=False, syntax=".py"):
		name = name if name else os.path.basename(filepath) if filepath else "Untitled"

		tab_id = super(Editor, self).add(
			name, 
			EditorTab(self, name=name, filepath=filepath, content=content, is_preview=is_preview, syntax=syntax),
			closebtn=True,
			foreground=Color.DARKER_GREY,
			background=Color.FADED_GREY,
			selected_bg=Color.BACKGROUND,
			selected_fg=Color.WHITE
		)

		self.notebook.select(tab_id)
		return tab_id


	def focus(self, event=None):
		self.notebook.focus()
		tab_id = self.notebook.select()
		if tab_id in self.notebook.tabs():
			self.tab().text.focus()

	def save(self, event=None, ask=False):
		tab = self.tab()
		if tab.filepath and not ask:
			filepath = self.tab().filepath		
		else:
			filepath = filedialog.asksaveasfilename(defaultextension=".py")
		if not filepath: return
	
		content = tab.text.get()
		file = open(filepath, "w+")
		file.write(content)
		file.close()
		tab.setfile(filepath)	
		
		# put this in try/except, all errors should be handled that way
		# need to specify parent when its in a dir somehow...
		err = self.app.projecttree.addfile(filepath)		

		if err:
			print ("\a")
			for j in err[1].split("\n"):
				if filepath in j:
					match = RE_LINE.search(j)
					if match:
						linenum = match.group(1)
						tab.text.linenumbers.error(linenum)
						# ValueError
						tab.showmessage(err[0].__class__.__name__, str(err[0]))
						if isinstance(err[0], NameError):
							name = RE_NAME_ERROR.search(str(err[0])).group(1)
							tab.text.highlight(name, "sel")
						elif isinstance(err[0], SyntaxError):
							tab.text.mark_set("insert", str(err[0].lineno) + "." + str(err[0].offset))
			return
		else:
			tab.showmessage(None)
			tab.text.linenumbers.error(None)	

		name, ext = name_and_extension(filepath)
		tab.text.set_syntax(ext)
		tab.text.syntax_highlight()
			

	def open(self, filepath=None, event=None, addmodule=True, is_preview=False):
		if filepath == None:
			filepath = filedialog.askopenfilename(defaultextension=".py")
		
		if not filepath: return
		
		tab = self.tab(filepath=filepath)
		self.close( self.tab_id(attr=("is_preview", True)) )
		if tab:
			self.notebook.select(tab)
		else:
			self.add(os.path.basename(filepath), filepath, readfile(filepath), is_preview=is_preview)
			tab = self.tab(filepath=filepath)
			
	
		if addmodule:
			err = self.app.projecttree.addfile(filepath)
			if err:
				print ("\a")
				for j in err[1].split("\n"):
					if filepath in j:
						match = RE_LINE.search(j)
						if match:
							linenum = match.group(1)
							tab.text.linenumbers.error(linenum)
							# ValueError
							tab.showmessage(err[0].__class__.__name__, str(err[0]))
							if isinstance(err[0], NameError):
								name = RE_NAME_ERROR.search(str(err[0])).group(1)
								tab.text.highlight(name, "sel")
							elif isinstance(err[0], SyntaxError):
								tab.text.mark_set("insert", str(err[0].lineno) + "." + str(err[0].offset))

	def close(self, tab_id=None):
		if tab_id == None:
			tab_id = self.notebook.select()

		if not tab_id: return

		tab = self.tab(tab_id)

		if tab.is_modified:
			if not messagebox.askokcancel("Math Inspector", "Are you sure you want to close this file without saving?"):
				return
		
		return super(Editor, self).close(tab_id)

	def toggle_wordwrap(self):
		tab = self.tab()
		if tab.wrap == "word":
			tab.wrap = "none"
		else:
 			tab.wrap = "word"
		
		self.tab().text.config(wrap=tab.wrap)

	def clear(self):
		tab_ids = [i for i in self.tabs]
		for j in tab_ids:
			self.close(j)
