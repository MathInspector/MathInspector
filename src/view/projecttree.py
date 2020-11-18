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

from util import getnamefrompath, unique_name, name_and_extension, WatchHandle, geticon, getalias
from widget import Treeview, ContextMenu, Popup
from tkinter import filedialog
from settings import Color, Excluded, ButtonRight
from importlib import reload
from util.savedata import AUTOSAVE_PATH
import re, os, inspect, uuid, importlib.util, subprocess, sys, traceback, platform
from watchdog.observers import Observer

class ProjectTree(Treeview):
	def __init__(self, app, *args, **kwargs):
		Treeview.__init__(self, app, *args, **kwargs)

		self.app = app
		self.contextmenu = ContextMenu(app)
		self.watch_handle = WatchHandle(self)
		self.rootfolder = None

		self.observer = None
		self.drag = {
			"selected": None,
			"position": (0,0),
			"in_workspace": False,
			"new_object": None
		}

		self.bind(ButtonRight, self._on_button_2)
		self.bind("<Double-Button-1>", self._on_double_button_1)
		self.bind('<B1-Motion>', self._on_b1_motion)
		self.bind('<ButtonRelease-1>', self._on_button_release_1)
		self.bind('<<TreeviewSelect>>', self._on_select)		

	def state(self, *args):
		if not args:
			return [self.rootfolder, self.selection(), self.tags("file"), self.tags("folder"), self.order()]

		rootfolder, selected, files, folders, order = args
		if rootfolder:
			self.addfolder(rootfolder, is_rootfolder=True)

		for i in folders:
			if os.path.dirname(i) != rootfolder:
				self.addfolder(i)

		for j in files:
			if os.path.dirname(j) != rootfolder:
				self.addfile(j)

	def _on_select(self, event):
		selection = self.selection()[0]		
		self.app.docviewer.show(selection)

	def clear(self, *tags):
		if len(tags):
			for t in tags:
				for i in self.tags(t):
					if os.path.dirname(i) != rootfolder:
						self.delete(i)
		else:
			for j in self.get_children():
				self.delete(j)
		
		self.rootfolder = None
		self.app.title("Math Inspector")
		self.stop_observing()

	def delete(self, key=None):		
		key = key or self.contextmenu.key
		self.hover_item = None

		if self.exists(key):
			super(ProjectTree, self).delete(key)
		
		if key in self.app.modules:
			del self.app.modules[key]		

	def create_new_object(self, key):
		try:
			path, attr = key.rsplit('.', 1)
			module = self.app.modules[path]
			item = getattr(module, attr)
		except Exception as err:
			print ("Could not instantiate object", err)
			return

		name = unique_name(self.app, attr)
		self.app.objects[name] = getattr(module, attr)
		return name


	def addfile(self, filepath=None, parent="", index="end"):
		if not filepath:
			filepath = filedialog.askopenfilename()

		if parent == self.rootfolder:
			parent = ""

		name, ext = name_and_extension(filepath)		
		if ext in (".math"): return

		tags = []
		if ext in (".py", ".md"):
			tags.append("editable_file")
		if not parent:
			tags.append("file")

		parent = self.insert(parent, index, filepath, text="      " +  name + ext, image=geticon(ext), tags=tuple(tags))
		
		if ext != ".py": return

		if name in sys.modules:
			del sys.modules[name]

		expanded = self.expanded()

		spec = importlib.util.spec_from_file_location(name, filepath)
		module = importlib.util.module_from_spec(spec)
		
		try:
			spec.loader.exec_module(module)
		except Exception as err:
			print ("-- MODULE LOAD ERROR --")
			print (err, traceback.format_exc())
			return
				
		if parent == "":
			self.app.modules[name] = module
		else:
			self.app.modules.store[name] = module
			self.addmodule(module, parent, filepath)

		self.expanded(expanded)

	def addfolder(self, filepath=None, parent="", watch=True, is_rootfolder=False):
		if not filepath: 
			filepath = filedialog.askdirectory(initialdir=".")
		
		if not filepath: return

		name = os.path.basename(filepath)
		if parent == self.rootfolder:
			parent = ""

		if is_rootfolder:
			parent = ""
			self.rootfolder = filepath
			self.app.title(os.path.basename(filepath) + "    -    Math Inspector")
		elif self.exists(filepath):
			parent = self.item(filepath)
		else:
			parent = self.insert(parent, "end", filepath, text="      " + name, open=parent=="", image=geticon("folder"), tag="folder" if parent == "" else "")		
		
		items = [(i, os.path.isdir(os.path.join(filepath, i))) for i in os.listdir(filepath)]
		items.sort()

		for name, is_dir in items:
			if is_dir and name not in Excluded.FOLDERS:
				self.addfolder(os.path.join(filepath, name), parent, watch=False)
		
		for name, is_dir in items:
			if not is_dir and name not in Excluded.FILES:
				fullpath = os.path.join(filepath, name)
				self.addfile(fullpath, parent)

		if watch:
			if self.observer == None:
				self.observer = Observer()
				self.observer.start()
			
			self.observer.schedule(self.watch_handle, path=filepath, recursive=True)


	def addmodule(self, module, parent=None, filepath=None):
		key = ""
		if isinstance(module, str):
			key = module
			module = self.app.modules[module]

		if not parent:
			parent = self.insert("", 'end', module.__name__, text="      " + key, open=False, image=geticon("python"))

		folders = {}
		extras = []

		for fn in dir(module):
			
			attr = getattr(module, fn)
			
			if fn not in Excluded.MODULES and fn[:1] != "_":
				if inspect.isclass( attr ):
					if ('classes' not in folders):
						folders['classes'] = self.insert(parent, "end", "classes" + str(uuid.uuid4()), text="classes")

					self.insert(folders['classes'], "end", module.__name__ + '.' + fn, text=fn)
				elif inspect.isfunction( attr ):
					if ('fns' not in folders):
						folders['fns'] = self.insert(parent, "end", "fns" + str(uuid.uuid4()), text="functions")

					self.insert(folders['fns'], "end", module.__name__ + '.' + fn, text=fn)					
				elif inspect.ismodule( attr ):

					sub_module = False

					try:
						sub_module = __import__(module.__name__ + '.' + fn, fromlist=[''])
					except:
						pass

					if (sub_module != False):	
						temp = self.insert(parent, "end", sub_module.__name__, text="      " + fn, image=geticon("python"))
						self.addmodule(sub_module, temp)
						self.app.modules.setitem(getalias(self.app.modules, attr.__name__), sub_module)

				elif attr.__class__.__name__ == 'ufunc':
					if ('ufunc_item' not in folders):
						folders['ufunc_item'] = self.insert(parent, "end", "ufunc_item" + str(uuid.uuid4()), text="ufuncs")
					
					self.insert(folders['ufunc_item'], "end", module.__name__ + '.' + fn, text=fn)
				else:
					extras.append( (module.__name__ + '.' + fn, fn) )
			

		for idx, text in extras:
			self.insert(parent, "end", idx, text=text)


	def update_file(self, key):
		if not self.exists(key): return

		order = self.order()
		expanded = self.expanded()
		index = self.index(key)
		self.delete(key)
		self.addfile(key, os.path.dirname(key), index=index)
		print ("update_file called")

		name, ext = name_and_extension(key)

		for j in self.app.workspace.items:
			item = self.app.workspace.items[j]
			obj = item.value
			if inspect.isfunction(obj) and hasattr(obj, "__module__"):
				if obj.__module__ == name:
					item.set_value( getattr(self.app.modules[name], obj.__name__) )
					self.app.objects[item.name] = item.value

		self.order(order)
		self.expanded(expanded)

	def open_editor(self, filepath):
		if platform.system() == "Windows":
			os.system("open " + filepath)
		elif platform.system() == "Darwin":
			os.system("open " + filepath)
	
	def stop_observing(self):
		if self.observer:
			self.observer.stop()
			self.observer = None

	def _on_b1_motion(self, event):
		self.drag["selected"] = self.selection()
		
		if self.drag["in_workspace"] and self.drag["new_object"]:
			item = self.app.workspace.get_item(self.drag["new_object"])
			if item:
				item.move(event.x - self.drag["position"][0], event.y - self.drag["position"][1])
		elif self.drag["selected"] and self.app.workspace == self.winfo_containing(event.x_root, event.y_root):
			self.drag["in_workspace"] = True
			self.drag["new_object"] = self.create_new_object(self.drag["selected"][0])
			
		self.drag["position"] = (event.x, event.y)
		super(ProjectTree, self)._on_b1_motion(event)

	def _on_button_release_1(self, event):
		self.drag["selected"] = None
		self.drag["in_workspace"] = False				

	def _on_button_2(self, event):
		key = self.identify_row(event.y)

		if not key:
			self.contextmenu.set_menu(items=[{
				"label": "Add File...",
				"command": self.addfile
			}, {
				"label": "Add Folder...",
				"command": self.addfolder
			}, {
				"label": "Import Module...",
				"command": lambda: Popup(self.app, "Import Module", self.app, obj=self.import_module, eval_args=False)
			}])
			self.contextmenu.show(event, key)
		# refactor this to have variable contextmenu if its editable
		elif self.has_tag(key, "folder") or key in self.app.modules:
			self.contextmenu.set_menu(items=[{
				"label": "Remove " + os.path.basename(key),
				"command": self.delete
			}])
			self.contextmenu.show(event, key)
		elif self.has_tag(key, "editable_file"):
			self.contextmenu.set_menu(items=[{
				"label": "Open " + os.path.basename(key) + " in editor",
				"command": lambda filepath=key: self.open_editor(filepath)
			}])
			self.contextmenu.show(event, key)

	def _on_double_button_1(self, event):
		selection = self.selection()
		if selection:
			name, ext = name_and_extension(selection[0])
			if ext == ".py":
				self.open_editor(selection[0])
				return "break"

	def import_module(self, module, alias=""):
		self.app.execute("import " + module + ("" if not alias else " as " + alias))
