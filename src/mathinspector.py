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
from util import ObjectContainer, Animate, SaveData, argspec, on_configure_panel
from view import Menu, Nav, Console, DocViewer, Output, WorkSpace, ObjectTree, ProjectTree
from widget import Notebook
from settings import Color
from inspect import ismodule
from importlib import import_module
import style.theme
import numpy as np
import scipy

class MathInspector(themed_tk.ThemedTk):
	def __init__(self):
		themed_tk.ThemedTk.__init__(self)
		style.theme.apply(self)
		
		self.title("Math Inspector")
		self.nav = Nav(self)
		self.horizontal_panel = ttk.PanedWindow(self, orient="horizontal")
		self.vertical_panel = ttk.PanedWindow(self, orient="vertical")		
		self.top_view = Notebook(self)
		self.bottom_view = Notebook(self)
		self.side_view = Notebook(self, has_labels=True)
		
		self.projecttree = ProjectTree(self)
		self.objecttree = ObjectTree(self)
		self.console = Console(self)
		self.docviewer = DocViewer(self)
		self.output = Output(self)
		self.workspace = WorkSpace(self)
		self.menu = Menu(self)

		self.modules = ObjectContainer(
			getitem=self.getmodule, 
			setitem=self.projecttree.addmodule)
		
		self.objects = ObjectContainer(
			setitem=self.update, 
			delitem=self.delete)

		self.side_view.add("Project", self.projecttree)
		self.side_view.add("Objects", self.objecttree)
		self.horizontal_panel.add(self.side_view)
		self.horizontal_panel.add(self.vertical_panel)
		self.vertical_panel.add(self.top_view)
		self.vertical_panel.add(self.bottom_view)
		self.animate = Animate(self)
		self.selected = None

		self.savedata = SaveData(self)		
		self.nav.pack(side="left", fill="both")
		self.horizontal_panel.pack(side="left", fill="both", expand=True)
		

	def update(self, key):
		self.workspace.update(key)
		self.objecttree.update(key) 
		self.output.update(key)		
		
	def delete(self, key):
		self.objecttree.delete_object(key)
		self.workspace.delete_object(key)
		self.output.delete_object(key)

	def select(self, key=None):
		self.selected = key
		self.workspace.select(key)
		self.objecttree.select(key)
		self.output.select(key)
		self.docviewer.select(key)

	def execute(__SELF__, __CMD__, __EVAL_ONLY__=False):	
		"""
		execute is called whenever a command is entered from the console view. 
		It uses locals() and globals() and to inject the existing objects 
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
			if ismodule(local_objects[j]):
				__SELF__.modules[j] = local_objects[j]
			else:
				__SELF__.objects[j] = local_objects[j]

		for j in del_list:
			del __SELF__.objects[j]
				
		return __RESULT__

	def eval(self, cmd):
		return self.execute(cmd, __EVAL_ONLY__=True)

	def getmodule(self, key):
		if key not in self.modules.store:
			for name in self.modules.store:
				if self.modules.store[name].__name__ == key:
					return self.modules.store[name]
			return None

		return self.modules.store[key]

	def state(self, *args):
		if not args:
			objects = {}
			functions = {}
			modules = [{ "alias": j, "name": self.modules[j].__name__} for j in self.modules]
			config = {
				"geometry": self.geometry() if self.geometry()[:3] != "1x1" else "720x480",
				"h_panel_sash": self.horizontal_panel.sashpos(0), 
				"v_panel_sash": self.vertical_panel.sashpos(0),
				"top_select": self.top_view.notebook.select()[2:],
				"bottom_select": self.bottom_view.notebook.select()[2:],
				"side_select": self.side_view.notebook.select()	
			}
			
			for key in self.objects:
				if callable(self.objects[key]) and hasattr(self.objects[key], "__module__"):
					functions[key] = self.objects[key].__module__, self.objects[key].__name__
				else:
					objects[key] = self.objects[key]

			return objects, functions, modules, self.animate.cache, config

		objects, functions, modules, animation_cache, config = args

		self.geometry(config["geometry"])
		self.horizontal_panel.bind("<Configure>", lambda event: on_configure_panel(self.horizontal_panel, config["h_panel_sash"]))
		self.vertical_panel.bind("<Configure>", lambda event: on_configure_panel(self.vertical_panel, config["v_panel_sash"]))
		self.nav.select("top", config["top_select"])
		self.nav.select("bottom", config["bottom_select"])
		self.side_view.notebook.select(config["side_select"])
		self.animate.cache = animation_cache
		
		for i in objects:
			self.objects[i] = objects[i]

		for j in modules:
			self.execute("import " + j["name"] + " as " + j["alias"])

		for key in functions:
			module, attr = functions[key]
			if module in self.modules:
				temp = self.modules[module]
			else:
				temp = import_module(module)

			self.objects[key] = getattr(temp, attr)


if __name__ == '__main__':
	app = MathInspector()
	app.mainloop()