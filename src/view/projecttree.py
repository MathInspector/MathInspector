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

from util import getnamefrompath, assetpath, unique_name, name_and_extension
from widget import Treeview, ContextMenu, Popup
from tkinter import filedialog
from PIL import ImageTk, Image
from settings import Color, Excluded, ButtonRight
from importlib import reload
import re, os, inspect, uuid, importlib.util, subprocess, sys, traceback


# @REFACTOR move images to its own file for organization
ICONS = {
	"python": "pythonlogo-color.png",
	"markdown": "markdown.png",
	"folder": "folder.png",
	"folder-open": "folder-open.png"
}

ICON_MAP = {
	".py": "python",
	".md": "markdown"
}

DELIMETER = "<-->"

class ProjectTree(Treeview):
	def __init__(self, app, *args, **kwargs):
		Treeview.__init__(self, app, *args, **kwargs)

		self.app = app
		self.contextmenu = ContextMenu(app)
		self.submodules = []
		self.folders = []
		self.files = []
		self.rootfolders = []
		self.custom_modules = {}
		self.modules = {}
		self.drag = {
			"selected": None,
			"position": (0,0),
			"in_workspace": False,
			"new_object": None
		}

		self.icons = {}
		for i in ICONS:
			self.icons[i] = ImageTk.PhotoImage(Image.open(assetpath() + ICONS[i]))

		self.bind(ButtonRight, self._on_button_2)
		self.bind('<B1-Motion>', self.b1_motion)
		self.bind('<ButtonRelease-1>', self._on_button_release_1)
		self.bind('<<TreeviewSelect>>', self._on_select)		

	def getstate(self):
		return [self.selection(), self.custom_modules, self.files, self.rootfolders, self.getexpanded()]

	# @REFACTOR get rid of selected, it causes a problem with opening editor files on startup
	def setstate(self, selected, custom_modules, files, rootfolders, openfolders):
		for i in custom_modules:
			self.addfile(custom_modules[i])

		for i in files:
			self.addfile(filepath=i)

		for i in rootfolders:
			self.addfolder(filepath=i)
		
		self.setexpanded(openfolders)
		if len(selected) > 0:
			self.selection_set(selected)

	def _on_select(self, event):
		selection = self.selection()[0]
		print ("in select", selection)
		name, ext = name_and_extension(selection)

		# in this case look up the file, read contents from file, and put it into docviewer
		if selection in self.custom_modules:
			return self.app.editor.select(None, filepath=self.custom_modules[selection])

		if selection in self.folders: 
			return self.item(selection, 
				image=self.icons["folder-open"] if self.item(selection)["open"] else self.icons["folder"])		
		
		if selection in self.files:	
			self.app.docviewer.select(None, filepath=selection)
			return self.app.editor.select(None, filepath=selection)

		self.app.docviewer.show(selection)
		# if not ext or ext == '.py':
		# else:
		# 	self.app.docviewer.select(None, filepath=selection)
		


		self.app.editor.select(selection)

	def clear(self):
		self.custom_modules.clear()
		self.files.clear()
		self.rootfolders.clear()

		for j in self.get_children():
			self.delete(j)

	def delete(self, key=None, type="module"):		
		key = key or self.contextmenu.key
		self.hover_item = None

		# @NOTE - this was for preventing del of modules when have stuff in workspace from that module
		try:
			super(ProjectTree, self).delete(key)
		except Exception as err:
			if key in self.custom_modules:
				for j in self.get_children(self.custom_modules[key]):
					super(ProjectTree, self).delete(j)
		
		if key in self.app.modules:
			del self.app.modules[key]
		
		if key in self.rootfolders:
			del self.rootfolders[self.rootfolders.index(key)]
		
		# make a rule so you cannot remove a module while it has its objects in the workspace, that makes sense!
		if key in self.custom_modules:
			del self.custom_modules[key]

		if key in self.files:
			del self.files[self.files.index(key)]

		# if key in sys.modules:
		# 	del sys.modules[key]


	def create_new_object(self, key):
		# may need to use syntax from X import Y as Z because pickle is failing on custom modules
		if key.count(DELIMETER) > 0:			
			path, attr = key.split(DELIMETER, 1)
			module = self.modules[path]
			item = getattr(module, attr)
		else:
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

	def addfile(self, filepath, parent=""):
		name, ext = name_and_extension(filepath)

		if ext == ".py":		
			name = name[:-3]
		else:
			image = None
			if ext == ".md":
				image = self.icons["markdown"]

			if filepath not in self.files and parent == "":
				self.files.append(filepath)
				if image:
					self.insert(parent, 'end', filepath, text="      " + name, open=True, image=image)
				else:
					self.insert(parent, 'end', filepath, text="      " + name, open=True)
			return

		if name in sys.modules:
			del sys.modules[name]

		expanded = self.getexpanded()

		spec = importlib.util.spec_from_file_location(name, filepath)
		module = importlib.util.module_from_spec(spec)
		
		try:
			spec.loader.exec_module(module)
		except Exception as err:
			return (err, traceback.format_exc())			
		
		if name in self.custom_modules:
			if name in self.files:
				parent = self.custom_modules[name]
			self.delete(name)

		self.custom_modules[name] = filepath
		
		if parent == "":
			self.app.modules[name] = module
		else:
			self.modules[filepath] = module
			self.create_folders(parent, module, filepath)

		self.setexpanded(expanded)
	
	def addfolder(self, parent="", filepath=None, event=None):
		if not filepath:
			filepath = filedialog.askdirectory(initialdir=".")
		
		if parent == "":
			self.rootfolders.append(filepath)

		name = os.path.basename(filepath)
		self.folders.append(filepath)
		parent = self.insert(parent, "end", filepath, text="      " + name, open=parent=="", image=self.icons["folder"])		
		
		items = [(i, os.path.isdir(os.path.join(filepath, i))) for i in os.listdir(filepath)]
		items.sort()

		for name, is_dir in items:
			if is_dir and name not in Excluded.FOLDERS:
				self.addfolder(parent, os.path.join(filepath, name))
		
		for name, is_dir in items:
			if not is_dir and name not in Excluded.FILES:
				fullpath = os.path.join(filepath, name)
				ext = os.path.splitext(name)[1]				

				image = ICON_MAP[ext] if ext in ICON_MAP else None
				
				if image:
					temp = self.insert(parent, "end", fullpath, text="      " +  name, image=self.icons[image])
				else:
					temp = self.insert(parent, "end", fullpath, text="      " +  name)

				self.addfile(fullpath, temp)


	def addmodule(self, key, parent=None):
		module = self.app.modules[key]
		if not parent:
			parent = self.insert("", 'end', module.__name__, text="      " + key, open=False, image=self.icons["python"])
		
		if key not in self.submodules:
			self.create_folders(parent, module)	


	def create_folders(self, parent, module, filepath=None):
		folders = {}
		extras = []

		for fn in dir(module):
			
			attr = getattr(module, fn)
			
			if fn not in Excluded.MODULES and fn[:1] != "_":
				if inspect.isclass( attr ):
					if ('classes' not in folders):
						folders['classes'] = self.insert(parent, "end", "classes" + str(uuid.uuid4()), text="classes")

					self.insert(folders['classes'], "end", (filepath + DELIMETER + fn) if filepath else module.__name__ + '.' + fn, text=fn)
				elif inspect.isfunction( attr ):
					if ('fns' not in folders):
						folders['fns'] = self.insert(parent, "end", "fns" + str(uuid.uuid4()), text="functions")

					self.insert(folders['fns'], "end", (filepath + DELIMETER + fn) if filepath else module.__name__ + '.' + fn, text=fn)					
				elif inspect.ismodule( attr ):

					sub_module = False

					try:
						sub_module = __import__(module.__name__ + '.' + fn, fromlist=[''])
					except:
						pass

					if (sub_module != False):	
						temp = self.insert(parent, "end", sub_module.__name__, text=fn)
						self.create_folders(temp, sub_module)						
						self.submodules.append(module.__name__ + '.' + fn)
						self.app.modules.setitem(self.app.getalias(attr.__name__), sub_module)

				elif attr.__class__.__name__ == 'ufunc':
					if ('ufunc_item' not in folders):
						folders['ufunc_item'] = self.insert(parent, "end", "ufunc_item" + str(uuid.uuid4()), text="ufuncs")
					
					self.insert(folders['ufunc_item'], "end", (filepath + DELIMETER + fn) if filepath else module.__name__ + '.' + fn, text=fn)
				else:
					extras.append( (module.__name__ + '.' + fn, fn) )
			

		for idx, text in extras:
			self.insert(parent, "end", (filepath + DELIMETER + text) if filepath else idx, text=text)

	def b1_motion(self, event):
		self.drag["selected"] = self.selection()
		
		if self.drag["in_workspace"] and self.drag["new_object"]:
			item = self.app.workspace.get_item(self.drag["new_object"])
			if item:
				item.move(event.x - self.drag["position"][0], event.y - self.drag["position"][1])
			else:
				print ('no item!')
		elif self.drag["selected"] and self.app.workspace == self.winfo_containing(event.x_root, event.y_root):
			self.drag["in_workspace"] = True
			self.drag["new_object"] = self.create_new_object(self.drag["selected"][0])
			
		self.drag["position"] = (event.x, event.y)

	def _on_button_release_1(self, event):
		self.drag["selected"] = None
		self.drag["in_workspace"] = False				

	def import_module(self, name, alias=""):
		cmd = "import " + str(name) + ("" if not alias else " as " + alias)
		self.app.execute(cmd, __SHOW_RESULT__=False)

	def _on_button_2(self, event):
		key = self.identify_row(event.y)
		key = key.replace("savedata.", "")

		if not key:
			self.contextmenu.set_menu(items=[{
				"label": "New File",
				"command": lambda: self.app.editor.add()
			},{
				"label": "Open File...",
				"command": self.app.editor.open
			}, {
				"label": "Add Folder...",
				"command": self.addfolder
			}, {
				"label": "Import Module...",
				"command": lambda: Popup(self.app, "Import Module", self.app, obj=self.import_module, eval_args=False)
			}])
			self.contextmenu.show(event, key)
		
		if key in self.rootfolders or key in self.app.modules or key in self.files:
			self.contextmenu.set_menu(items=[{
				"label": "Remove " + os.path.basename(key),
				"command": self.delete
			}])
			self.contextmenu.show(event, key)
