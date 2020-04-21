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
from tkinter import ttk
from ttkthemes import themed_tk
from util import ObjectContainer, SaveData, hexstring
from view import Menu, Nav, Editor, Console, DocViewer, Output, WorkSpace, ObjectTree, ProjectTree
from widget import Notebook, NavIcon
from settings import Color
import style.theme
import inspect, traceback, os, sys, syslog
import numpy as np

class MathInspector(themed_tk.ThemedTk):
	def __init__(self):
		themed_tk.ThemedTk.__init__(self)
		style.theme.apply(self)
		self.nav = Nav(self)
		self.horizontal_panel = ttk.PanedWindow(self, orient="horizontal")
		self.vertical_panel = ttk.PanedWindow(self, orient="vertical")		
		self.top_view = Notebook(self, labels=False)
		self.bottom_view = Notebook(self, labels=False)
		self.treenotebook = Notebook(self, **style.theme.treenotebook)
		self.projecttree = ProjectTree(self)
		self.objecttree = ObjectTree(self)
		self.editor = Editor(self)
		self.console = Console(self)
		self.docviewer = DocViewer(self)
		self.output = Output(self)
		self.workspace = WorkSpace(self)
		self.menu = Menu(self)
		self.modules = ObjectContainer(getitem=self.getmodule, setitem=self.projecttree.addmodule)
		self.objects = ObjectContainer(setitem=self.on_set_object, delitem=self.on_delete_object)
		self.selected = None
		self.treenotebook.add("Project", self.projecttree, **style.theme.treenotebook_tab)
		self.treenotebook.add("Objects", self.objecttree, **style.theme.treenotebook_tab)
		self.horizontal_panel.add(self.treenotebook)
		self.horizontal_panel.add(self.vertical_panel)
		self.vertical_panel.add(self.top_view)
		self.vertical_panel.add(self.bottom_view)
		self.savedata = SaveData(self)
		self.savedata.load(firstload=True)
		self.nav.pack(side="left", fill="both")
		self.horizontal_panel.pack(side="left", fill="both", expand=True)

	def on_set_object(self, key):
		"""
		The callback for self.objects, an instance of ObjectContainer, which stores all 
		of the objects which the user can interact with from any view.  on_set_object is 
		called every time that an object is modified from any view. It's main purpose is 
		to synchronize all the views by updating them with new values.
		"""
		item = self.workspace.get_item(key)
		
		if item and item.output_connection:
			obj = self.objects[item.output_connection.name]
			if callable(obj):
				argname = item.output_connection.getarg("connection", item, name=True)
				if argname:
					item.output_connection.setarg(argname, item.get_output())
					self.on_set_object(item.output_connection.name)
			else:
				try:
					if callable(self.objects[key]):
						result = item.get_output()
					else:
						result = obj.__class__(self.objects[key])
				except Exception as err:
					item.config(hide_wire=True);
					self.workspace.log.show(err);
					return False

				self.objects[item.output_connection.name] = result
		
		self.workspace.update_object(key)
		self.objecttree.update_object(key)
		# self.output.select(key)		
		self.output.update_object(key)		
		return True

	def on_delete_object(self, key):
		self.objecttree.delete_object(key)
		self.workspace.delete_object(key)
		self.docviewer.delete_object(key)
		self.output.delete_object(key)

	def execute(__SELF__, __CMD__, __SHOW_RESULT__=True, __EVAL_ONLY__=False):	
		"""
		execute is called whenever a command is entered from the console view. 
		The idea is to leverage locals() and globals() and to inject the objects 
		into the local scope and the modules into the global scope before 
		calling eval/exec.  Then after the command is executed, the current values of 
		locals() is checked and any objects or modules which have been added or 
		changed are updated.

		In order to preserve the local namespace the arguments to execute have been
		given a double underscore all caps naming convention.  All variables that 
		begin with __ are excluded from the local namespace on the console. 
		"""
		if __CMD__ is None: return

		for __NAME__ in __SELF__.objects:
			locals()[__NAME__] = __SELF__.objects[__NAME__]

		for __NAME__ in __SELF__.modules:
			globals()[__NAME__] = __SELF__.modules[__NAME__]

		__RESULT__ = None

		try:
			__RESULT__ = eval(__CMD__)
		except Exception as e1:
			if __EVAL_ONLY__: raise e1
			try:
				__RESULT__ = exec(__CMD__)
			except Exception as e2:
				__RESULT__ = e2

		local_objects = locals().copy()
		
		set_list = []
		update_list = []
		del_list = []
		for __NAME__ in local_objects:
			if __NAME__[:2] != "__" and __NAME__ not in __SELF__.modules:
				if __NAME__ not in __SELF__.objects:
					set_list.append(__NAME__)
				elif isinstance(__SELF__.objects[__NAME__], np.ndarray):
					if not np.array_equal(__SELF__.objects[__NAME__], local_objects[__NAME__]):
						update_list.append(__NAME__)					
				elif __SELF__.objects[__NAME__] != local_objects[__NAME__]:
					update_list.append(__NAME__)					

		for __NAME__ in __SELF__.objects:
			if __NAME__ not in local_objects:
				del_list.append(__NAME__)

		for j in set_list + update_list:
			if inspect.ismodule(local_objects[j]):
				__SELF__.modules[j] = local_objects[j]
			else:
				__SELF__.objects[j] = local_objects[j]

		for j in del_list:
			del __SELF__.objects[j]
				
		if __SHOW_RESULT__:
			__SELF__.console.result(__RESULT__)

		return __RESULT__

	def getmodule(self, key):
		if key not in self.modules.store:
			for name in self.modules.store:
				if self.modules.store[name].__name__ == key:
					return self.modules.store[name]
			return None

		return self.modules.store[key]

	# REFACTOR - would be nice to get rid of this if possible
	#		would it be possible to make getmodule automatically fall back to getalias if it cant find it?
	def getalias(self, name):
		toplevel = name.split(".")
		if name in self.modules:
			key = name
		else:
			for i in self.modules:
				if self.modules[i].__name__ == name:					
					key = i
					break
			key = toplevel[0]

		return key if len(toplevel) == 1 else key + "." + ".".join(toplevel[1:])

	def select(self, key=None, filepath=None):
		self.selected = key
		if filepath:
			self.editor.select(filepath=filepath)
			return

		self.workspace.select(key)
		self.docviewer.select(key, filepath=filepath)
		self.objecttree.select(key)
		self.output.select(key)
		# NOTE - commented out to prevent source from showing on select
		# self.editor.select(key)

	def setview(self, name, bottom=False):
		if not name: return

		name = name if name[:2] == ".!" else ".!" + name
		notebook = self.bottom_view if bottom else self.top_view

		if name in notebook.tabs and name in notebook.notebook.tabs():
			notebook.tabs[name].select()
			selected = notebook.notebook.select()
			if selected and selected != name:
				notebook.tabs[selected].unselect()
		elif hasattr(self, name[2:]):
			notebook.add(name,  getattr(self, name[2:]))

		self.nav.icons[name].select(style="alt" if bottom else None)
		notebook.notebook.select(name)

	def timer(self, key=None, start=1, stop=10, step=1, delay=100, colorchange=False, color=0x000000):		
		if step > 0 and start >= stop or step < 0 and start <= stop: 
			return
		
		if colorchange:
			color += 1		
			self.output.canvas.set_line_color( hexstring(color) )

		self.objects[key] = max(start + step, stop) if step < 0 else min(start + step, stop)
		self.after(delay, lambda: self.timer(key, start + step, stop, step, delay, colorchange=colorchange, color=color))


if __name__ == '__main__':
	print ("OS-CWD", os.getcwd())
	if hasattr(sys, "_MEIPASS"):
		print ("_MEIPASS", sys._MEIPASS)
		# os.chdir(os.path.expanduser('~'))

	"""
	@NOTE This code is for the executable and is useful for debugging on production builds when print statements don't print to the command line
	"""
	# APP_NAME = 'mathinspector'
	# Define identifier for Mac Console Logging
	# syslog.openlog(APP_NAME)
	# Record a message
	# working_dir = 'Working dir: %s' % (os.getcwd())
	# working_dir = tk.Tcl().eval("info patchlevel")
	# syslog.syslog(syslog.LOG_ALERT, working_dir)


	app = MathInspector()
	app.mainloop()