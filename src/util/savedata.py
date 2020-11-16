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

"""
@NOTE: a better way to do this would be to try/catch loading and setting things one at a time
this way if something goes wrong or if I add a new thing, the save file wont break	
"""
import pickle, traceback, sys, atexit, os
from importlib import import_module

def get_basepath():
	if hasattr(sys, "_MEIPASS"):
	    return sys._MEIPASS
	else:
	    return os.path.abspath("../")

AUTOSAVE_PATH = os.path.join(get_basepath(), "autosave.math")
HISTORY_SIZE = 100

def _on_configure_panel(widget, sashpos):
	widget.sashpos(0, sashpos)
	widget.unbind("<Configure>")

class SaveData:
	def __init__(self, app):
		self.app = app
		self.filepath = None
		atexit.register(self.save)

	def _set_filepath(self, filepath):
		if filepath == AUTOSAVE_PATH or filepath is None:
			self.filepath = None
			self.app.title("                Math Inspector                ")
			return

		self.filepath = filepath
		self.app.title(os.path.splitext("          " + os.path.basename(self.filepath))[0] + " - Math Inspector" + "          ")

	def new(self):
		self.app.projecttree.clear()
		self.app.console.clear()
		self.app.docviewer.delete("1.0", "end")
		self.app.output.select()
		self._set_filepath(None)
		for i in [j for j in self.app.workspace.items]:
			del self.app.objects[ self.app.workspace.items[i].name ]
		self.app.setview("workspace", False)
		self.app.setview("console", True)
		self.app.horizontal_panel.bind("<Configure>", lambda event: _on_configure_panel(self.app.horizontal_panel, 220))
		# self.app.vertical_panel.bind("<Configure>", lambda event: _on_configure_panel(self.app.vertical_panel, 0))

	def getobjects(self):
		objects = {}
		functions = {}
		for key in self.app.objects:
			if callable(self.app.objects[key]) and hasattr(self.app.objects[key], "__module__"):
				functions[key] = self.app.objects[key].__module__, self.app.objects[key].__name__
			else:
				objects[key] = self.app.objects[key]

		# print ("FUNCTIONS", functions)
		return objects, functions

	def save(self, filepath=AUTOSAVE_PATH):
		if not filepath:
			return

		with open(filepath, "wb") as output:
			# i think this line is causing the pickle to fail for custom modules, try name/regen trick
			objects, functions = self.getobjects()
			pickle.dump(objects, output, pickle.HIGHEST_PROTOCOL)		
			pickle.dump(functions, output, pickle.HIGHEST_PROTOCOL)	
			pickle.dump([{ "key": j, "modulename": self.app.modules[j].__name__} for j in self.app.modules], output, pickle.HIGHEST_PROTOCOL)
			pickle.dump(self.app.animation_cache, output, pickle.HIGHEST_PROTOCOL)	
			pickle.dump(self.app.workspace.get_state(), output, pickle.HIGHEST_PROTOCOL)
			pickle.dump(self.app.geometry(), output, pickle.HIGHEST_PROTOCOL)
			pickle.dump(self.app.horizontal_panel.sashpos(0), output, pickle.HIGHEST_PROTOCOL)
			pickle.dump(self.app.vertical_panel.sashpos(0), output, pickle.HIGHEST_PROTOCOL)
			pickle.dump(self.app.top_view.notebook.select(), output, pickle.HIGHEST_PROTOCOL)
			pickle.dump(self.app.bottom_view.notebook.select(), output, pickle.HIGHEST_PROTOCOL)
			pickle.dump(self.app.treenotebook.notebook.select(), output, pickle.HIGHEST_PROTOCOL)
			pickle.dump(self.filepath, output, pickle.HIGHEST_PROTOCOL)
			pickle.dump(self.app.projecttree.getstate(), output, pickle.HIGHEST_PROTOCOL)
			# pickle.dump(self.app.editor.getstate(), output, pickle.HIGHEST_PROTOCOL)
			pickle.dump(self.app.console.history, output, pickle.HIGHEST_PROTOCOL)
			pickle.dump(self.app.objecttree.getexpanded(), output, pickle.HIGHEST_PROTOCOL)
			pickle.dump(self.app.output.canvas.getstate(), output, pickle.HIGHEST_PROTOCOL)
			pickle.dump(self.app.docviewer.selected_key, output, pickle.HIGHEST_PROTOCOL)
			pickle.dump(self.app.selected, output, pickle.HIGHEST_PROTOCOL)

		self._set_filepath(filepath)

	def load(self, filepath=AUTOSAVE_PATH, firstload=False):
		if not filepath:
			return

		if not firstload:
			self.new()

		try:
			with open(filepath, "rb") as data:
				saved_objs = pickle.load(data)
				saved_functions = pickle.load(data)
				saved_modules = pickle.load(data)
				animation_cache = pickle.load(data)
				state = pickle.load(data)
				geometry = pickle.load(data)
				sash_x = pickle.load(data)
				sash_y = pickle.load(data)
				top_tab = pickle.load(data)
				bottom_tab = pickle.load(data)
				treenotebooktab = pickle.load(data)
				prevfilepath = pickle.load(data)
				projecttree_state = pickle.load(data)
				# editor_state = pickle.load(data)
				history = pickle.load(data)
				openobjects = pickle.load(data)
				output_state = pickle.load(data)
				docviewer_key = pickle.load(data)
				selected = pickle.load(data)

		except Exception:
			# traceback.print_exc(file=sys.stdout)
			self.new()			
			return

		self.app.workspace.zoomlevel = state["zoomlevel"]
		
		for j in saved_objs:
			self.app.objects[j] = saved_objs[j]

		for k in saved_modules:
			self.app.execute("import " + k["modulename"] + " as " + k["key"], __SHOW_RESULT__=False)
		
		self.app.animation_cache = animation_cache

		# NOTE - this is loading the custom modules, which is required for the non-pickleable fn's to load
		self.app.projecttree.setstate(*projecttree_state)
		# print (self.app.modules)
		for key in saved_functions:
			module, attr = saved_functions[key]
			if module in self.app.modules:
				temp = self.app.modules[module]
			else:
				temp = import_module(module)

			self.app.objects[key] = getattr(temp, attr)

		if geometry[:len("1x1")] == "1x1":
			self.app.geometry(str(self.app.winfo_screenwidth()) + "x" + str(self.app.winfo_screenheight()))
		else:
			self.app.geometry(geometry)
		
		self.app.horizontal_panel.bind("<Configure>", lambda event: _on_configure_panel(self.app.horizontal_panel, sash_x or 0))
		self.app.vertical_panel.bind("<Configure>", lambda event: _on_configure_panel(self.app.vertical_panel, sash_y or 0))

		self.app.treenotebook.notebook.select(treenotebooktab)
		self.app.console.history = history[len(history) - HISTORY_SIZE:]
		self.app.console.history_index = len(self.app.console.history)
		# self.app.editor.setstate(*editor_state)
		self.app.workspace.set_state(state)
		self.app.objecttree.set_state(openobjects)
		
		self.app.setview(top_tab)
		self.app.setview(bottom_tab, True)		
		
		self.app.output.canvas.setstate(output_state)
		# self.app.select(selected)
		self.app.docviewer.select(docviewer_key)
		self.app.output.canvas.bind("<Configure>", lambda event: self._on_configure_graph(event, selected))
		

		self._set_filepath(prevfilepath or filepath)

	def _on_configure_graph(self, event, key):
		self.app.select(key)
		self.app.output.canvas.unbind("<Configure>")

