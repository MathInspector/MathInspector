"""
The modules which are currently available in the global namespace
are displayed in the left hand sidebar of the main window.  From this
tab, you can explore the available functionality of any module, which
can be very helpful for learning new parts of the python and numpy
ecosystems.

It's possible to drag and drop any object listed in the Modules tab
into the node editor.  This can be a convinient way to instantiate
new objects without typing any code.

Right clicking in an empty part of the Modules tab will bring up a
menu of available options.  When you add a file or folder, they
will be available in the global namespace just like any other module.

The difference between importing a module and adding a file, is that
when a file is added to the Modules tab, each line of that file is
executed, and any changes that are saved to that file are updated
in the node editor, as well as across all the other views.

To directly access the global object which stores the names and values
of all modules in the global namespace, use the command

>>> app.modules

See the class `ModuleTree` for a full list of available attributes.

"""
"""
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

import re, os, inspect, uuid, importlib.util, sys, traceback
from tkinter import filedialog
from importlib import reload
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from .util import vdict
from .util import *
from .widget import Treeview
from .style import Color, getimage
from .console.builtin_print import builtin_print

class ModuleTree(vdict, Treeview):
	"""
	In order to synchronize the available modules across views,
	math inspector stores the aliases and values of all modules in a vdict called the Module Tree.

	When a file or folder is added to the Module Tree, the `watchdog` module
	is used to monitor changes in those files and update
	the values of variables across all views.

	Execution of code from source code is done by calling self.app.console.exec(source).
	See the documentation for `app.console` for more information.
	"""
	def __init__(self, app):
		vdict.__init__(self, getitem=self.getmodule, setitem=self.setmodule, delitem=self.delete)
		Treeview.__init__(self, app)

		self.drag = None
		self.rootfolder = None
		self.handler = None
		self.observer = None
		self.watchers = {}
		self.locals = {}
		self.bind(BUTTON_RIGHT, lambda event: self.selection_set(self.identify_row(event.y)))
		self.bind(BUTTON_RELEASE_RIGHT, self._on_button_release_right)
		self.bind("<Double-Button-1>", self._on_double_button_1)

	def getmodule(self, key):
		if key not in self.store:
			for i in self.store:
				if self.store[i].__name__ == key or self.item(i)["values"][0] == key:
					return self.store[i]
		return self.store[key]

	def setmodule(self, name, module, parent=None, file=None):
		if not parent:
			if self.exists(module.__name__):
				self.delete(module.__name__)
			self.store[name] = module
			parent = self.insert("", 'end', module.__name__,
				text="      " + name,
				values=name,
				image=getimage(".py"),
				open=True,
				tags="file" if file else "module")

		if len(self.store) == 1:
			self.app.menu.setview("modules", True)

		functions = []
		builtin_fn = []
		classes = []
		constants = []
		submodules = []
		for fn in dir(module):
			try:
				attr = getattr(module, fn)
			except:
				fn = "_" + fn

			if fn[:1] != "_":
				if inspect.isclass(attr):
					classes.append(fn)
				elif inspect.isfunction(attr):
					functions.append(fn)
				elif callable(attr):
					builtin_fn.append(fn)
				elif inspect.ismodule(attr):
					if attr.__name__ not in EXCLUDED_MODULES:# + BUILTIN_PKGS + INSTALLED_PKGS:
						submodules.append((fn, attr))
				else:
					constants.append(fn)

		if builtin_fn:
			folder = self.insert(parent, "end", text="builtins")
			for i in builtin_fn:
				self.insert(folder, "end", text=i, values=module.__name__ + "." + i)

		if functions:
			folder = self.insert(parent, "end", text="functions")
			for i in functions:
				self.insert(folder, "end", text=i, values=module.__name__ + "." + i)

		if classes:
			folder = self.insert(parent, "end", text="classes")
			for j in classes:
				self.insert(folder, "end", text=j, values=module.__name__ + "." + j)

		if constants:
			folder = self.insert(parent, "end", text="objects")
			for k in constants:
				if k[0] != "_":
					self.insert(folder, "end", text=k, values=module.__name__ + "." + k)

		if submodules and file is None:
			for fn, attr in submodules:
				if not self.exists(attr.__name__):
					folder = self.insert(parent, "end", attr.__name__, text="      " + fn, values=attr.__name__, image=getimage(".py"))
					self.setmodule(attr.__name__, attr, folder)
		return False

	def delete(self, key, del_objs=True):
		if self.has_tag(key, "folder"):
			for i in self.get_children(key):
				self.delete(i)

		if self.exists(key):
			super(Treeview, self).delete(key)
		else:
			name, ext = name_ext(key)
			if self.exists(name):
				super(Treeview, self).delete(name)

		if del_objs and key in self.locals:
			for i in self.locals[key]:
				if i in self.app.objects:
					del self.app.objects[i]
			del self.locals[key]

			if key in self.watchers:
				if self.observer:
					# TODO: use a better system for unscheduling
					try:
						self.observer.unschedule(self.watchers[key])
					except:
						pass
				del self.watchers[key]

		if key in self.store:
			del self.store[key]
		return False

	def addfile(self, file=None, parent="", index="end", watch=True, is_open=True, exec_file=True):
		file = file or filedialog.askopenfilename()
		if not file: return

		name, ext = name_ext(file)
		if os.path.basename(file) in EXCLUDED_FILES or ext in EXCLUDED_EXT: return

		if self.exists(name):
			self.delete(name, del_objs=False)

		parent = self.insert(parent if (self.rootfolder and parent != self.rootfolder) else "", index, name,
			text="      " + name,
			image=getimage(ext),
			tags="local" if parent else ("local", "file"),
			open=is_open,
			values=file)

		if ext != ".py": return

		if name in sys.modules:
			del sys.modules[name]

		if watch:
			if not self.observer:
				self.observer = Observer()
				self.observer.start()

			self.watchers[name] = self.observer.schedule(FileHandler(self, file=file),
				path=os.path.dirname(file), recursive=False)

		expanded = self.expanded()
		spec = importlib.util.spec_from_file_location(name, file)
		module = importlib.util.module_from_spec(spec)
		try:
			spec.loader.exec_module(module)
		except Exception as err:
			traceback.print_exc()
			self.disable_file(parent)
			return

		if exec_file:
			for i in dir(module):
				attr = getattr(module, i)
				if not inspect.ismodule(attr) and i in self.app.objects and i not in self.locals[name]:
					self.disable_file(parent)
					print (Exception("ImportError: object with name " + i + " already exists.\n  File \"" + file + "\", line 1, in <module>"))
					builtin_print ("\a")
					return

		if name not in self.store:
			self.store[name] = module

		self.setmodule(name, module, parent, file)
		self.expanded(expanded)

		if exec_file:
			prev = self.app.objects.store.copy()
			source = open(file, "r").read()
			try:
				self.app.console.exec(source, file)
			except:
				print ("TODO - exec failed")
				return

			new = self.app.objects.store.copy()

			if name in self.locals:
				self.locals[name].update({ k: new[k] for k in set(new) - set(prev) })
			else:
				self.locals[name] = { k: new[k] for k in set(new) - set(prev) }

			objects = [i for i in dir(module)]
			keys = list(self.locals[name].keys())
			for i in keys:
				if i not in objects:
					del self.locals[name][i]
					del self.app.objects[i]

			# for i in objects:
			# 	attr = getattr(module, i)
			# 	if inspect.ismodule(attr):
			# 		self.setmodule(i, attr, name)


	def addfolder(self, dirpath=None, parent="", watch=True, is_rootfolder=False, exec_file=True):
		dirpath = dirpath or filedialog.askdirectory(initialdir=".")
		if not dirpath: return

		name = os.path.basename(dirpath)
		parent = "" if parent == self.rootfolder else parent

		if is_rootfolder:
			self.rootfolder = dirpath
		else:
			parent = self.insert(parent, "end", dirpath,
				text="      " + name,
				open=(not parent),
				image=getimage("folder"),
				tag="folder" if not parent else "",
				values=dirpath)

		items = [(i, os.path.isdir(os.path.join(dirpath, i))) for i in os.listdir(dirpath)]
		items.sort()
		for name, is_dir in items:
			if is_dir and name not in EXCLUDED_DIR:
				self.addfolder(os.path.join(dirpath, name), parent, watch=False, exec_file=exec_file)

		for name, is_dir in items:
			if not is_dir and name not in EXCLUDED_FILES:
				fullpath = os.path.join(dirpath, name)
				self.addfile(fullpath, parent, watch=False, exec_file=exec_file)

		if watch:
			if not self.observer:
				self.observer = Observer()
				self.observer.start()

			self.watchers[name] = self.observer.schedule(FileHandler(self, dirpath=dirpath),
				path=dirpath, recursive=True)

	def stop_observer(self):
		if self.observer:
			self.observer.stop()
			self.observer = None

	def files(self, tag, recursive=False, key=""):
		children = self.get_children(key)
		if recursive is True:
			result = []
			if self.has_tag(key, tag):
				result.append(key)

			for i in children:
				result.extend(self.files(tag, True, i))
			return result

		keys = [j for j in children if self.has_tag(j, tag)]
		return [self.app.modules.item(i)["values"][0] for i in keys]

	def disable_file(self, key):
		self.item(key, image=getimage("python-disabled"))
		self.add_tag(key, "disabled")
		children = self.get_children(key)
		for i in children:
			self.delete(i)

	def _on_double_button_1(self, event):
		key = self.identify_row(event.y)
		if not key: return

		value = self.item(key)["values"]
		if not value: return
		value = value[0]

		if key in self and os.path.isfile(value):
			try:
				sourcefile = inspect.getsourcefile(self[key])
			except:
				sourcefile = None

			if sourcefile:
				open_editor(sourcefile)
				return "break"

		obj = help.getobj(value)
		if obj:
			help(obj)
			return "break"

	def _on_button_release_right(self, event):
		key = self.identify_row(event.y)
		if not key:
			self.menu.set_menu(self.app.menu.project_menu)
			return self.menu.show(event)

		value = self.item(key)["values"][0]
		items = []
		obj = help.getobj(value)
		if obj is not None:
			items.append({
				"label": "View Doc",
				"command": lambda: help(value)
			})

		try:
			file = inspect.getsourcefile(obj)
		except:
			file = None

		if file:
			items.append({
				"label": "View Source Code",
				"command": lambda: open_editor(inspect.getsourcefile(obj))
			})

		# print ('v', value)
		if key in self.get_children() and value != self.rootfolder:
			items.extend([{
				"separator": None
			}, {
				"label": "Remove " + key,
				"command": lambda: self.delete(value)
			}])

		self.menu.set_menu(items)
		self.menu.show(event)


class FileHandler(FileSystemEventHandler):
	def __init__(self, modules, file=None, dirpath=None):
		FileSystemEventHandler.__init__(self)
		self.modules = modules
		self.file = file

	def on_created(self, event):
		if self.is_excluded(event): return

		dirname = os.path.dirname(event.src_path)
		parent = "" if dirname == self.modules.rootfolder else os.path.basename(dirname)

		if event.is_directory:
			self.modules.addfolder(event.src_path, parent)
		else:
			self.modules.addfile(event.src_path, parent)

	def on_deleted(self, event):
		if self.is_excluded(event): return
		name, ext = name_ext(event.src_path)

		if event.is_directory:
			del self.modules[os.path.basename(event.src_path)]
		else:
			del self.modules[name]

	def on_modified(self, event):
		if self.is_excluded(event): return

		name, ext = name_ext(event.src_path)
		order = self.modules.order()
		expanded = self.modules.expanded()
		index = self.modules.index(name)

		dirname = os.path.dirname(event.src_path)
		parent = "" if (dirname == self.modules.rootfolder or name in self.modules) else dirname
		if parent:
			self.modules.addfile(event.src_path, parent, index=index, watch=False)
		else:
			self.modules.addfile(event.src_path, index=index, watch=False)
		self.modules.order(order)
		self.modules.expanded(expanded)

	def on_moved(self, event):
		name, ext = name_ext(event.src_path)
		self.modules.item(name, text="      " + os.path.basename(event.dest_path), values=event.dest_path)

	def is_excluded(self, event):
		name, ext = name_ext(event.src_path)
		return (self.file and self.file != event.src_path
			or event.is_directory
			or (name + ext) in EXCLUDED_FILES
			or ext in EXCLUDED_EXT
			or name in EXCLUDED_DIR
		)
