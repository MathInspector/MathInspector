"""
Math Inspector: a visual programming environment for scientific computing
https://mathinspector.com

You can use the mathinspector components from your own source code files without launching the mathinspector app.  

All of the examples that follow assume that you have already imported mathinspector

>>> import mathinspector

viewdoc
---
The viewdoc function lets you use the mathinspector documentation system from your own source code files.

For example, to view the documentation for the inspect module

>>> import inspect
>>> mathinspector.viewdoc(inspect)

For more information about any of the items which follow, see the corresponding docstrings for that item.
These can be viewed using the viewdoc function.  For example, to view this documentation in the mathinspector doc system, use the command 

>>> mathinspector.viewdoc(mathinspector)

main
---
This will launch the mathinspector app

>>> mathinspector.main()

See the documentation for the main function to understand the structure of the arguments it accepts

plot
---
The mathinspector plotting library was designed to update and replace the functionality in matplotlib.

This will launch the mathinspector plotting window.  

>>> mathinspector.plot(1,2,3)

The way you format data you pass as arguments to the plot function will determine what is plotted.  It will automatically detect when the input is 2-dimensional or 3-dimensional, and treats tuple's as points and lists & arrays as lines.  See the documentation for the plot function for a complete list of accepted argument types.

vdict
---
This module also has the class vdict, which stands for virtual dictionary.  It's a class which extends dict
and has callbacks for getting, setting, and deleting items.

>>> A = mathinspector.vdict(setitem=lambda key, value: print(key))
>>> A["x"] = 1
x

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

import sys, os
from tkinter import ttk
from ttkthemes import themed_tk
from .console import Interpreter
from .node import NodeEditor
from .objects import ObjectTree
from .modules import ModuleTree
from .mainmenu import MainMenu
from .project import SaveData
from .animation import Animation
from .widget import Notebook

from .util import vdict, version, name_ext, AUTOSAVE_PATH
from .plot import plot
from .doc import Help

class ImportInterface:
	def __dir__(self):
		return ALLOWED_NAMES

	def __getattr__(self, name):
		if name in ALLOWED_NAMES:
			return globals()[name]
		raise AttributeError(f"module {__name__} has no attribute {name}")

ALLOWED_NAMES = [
	"__builtins__",
	"__cached__",
	"__doc__",
	"__file__",
	"__loader__",
	"__name__",
	"__package__",
	"__path__",
	"__spec__",
	"__version__",
	"animate",
	"main",
	"plot",
	"vdict",
	"viewdoc",
]

__version__ = version()
viewdoc = Help()
sys.modules[__name__] = ImportInterface()

class App(themed_tk.ThemedTk):
	def __init__(self, *args):
		themed_tk.ThemedTk.__init__(self)
		self.set_theme("arc")
		ttk.Style(self)

		self.horizontal_panel = ttk.PanedWindow(self, orient="horizontal")
		self.vertical_panel = ttk.PanedWindow(self, orient="vertical")
		self.side_view = Notebook(self, has_labels=True)

		self.node = NodeEditor(self)
		self.console = Interpreter(self)
		self.modules = ModuleTree(self)
		self.objects = ObjectTree(self)

		self.vertical_panel.add(self.node.frame)
		self.vertical_panel.add(self.console.frame)
		self.side_view.add("Modules", self.modules)
		self.side_view.add("Objects", self.objects)
		self.horizontal_panel.add(self.side_view.frame)
		self.horizontal_panel.add(self.vertical_panel)
		self.horizontal_panel.pack(side="left", fill="both", expand=True)

		self.animate = Animation(self)
		self.project = SaveData(self)
		self.menu = MainMenu(self)
		self.config(menu=self.menu)

		mathfile = AUTOSAVE_PATH
		pyfiles = []
		for i in args:
			if not os.path.isfile(i):
				raise ValueError(i + " is not a .math or a .py file")
			
			name, ext = name_ext(i)
			if ext == ".math":
				mathfile = os.path.abspath(i)
			elif ext == ".py":
				mathfile = ""
				pyfiles.append(os.path.abspath(i))
			else:
				raise ValueError(i + " is not a currently supported file type.")
		
		self.project.load(mathfile, is_first_load=True, sashpos=240 if pyfiles else 0)
		
		for i in pyfiles:
			self.modules.addfile(i)


def main(*args, **kwargs):
	"""
	launches the mathinspector app

	Parameters
	----------
	*args : This function accepts an arbitrary number of arguments
		Each argument must be a filename in the relative path which has at most a single .math file and can have an arbitrary number of .py files.  When arguments are passed to this function, the app will launch with the .math file loaded and all of the .py files added

	help: string (optional)
		launches the mathinspector documentation system as if the command help(STRING) was called from the mathinspector app, where STRING is the value of the help kwarg.

	new: bool
		When set to True, this will replace the current autosave file with a blank file and when the app launches it will be the same thing as if you selecte File > New from the main menu.


	Examples
	--------

	launch the app with a brand new project
	>>> mathinspector.main(new=True)
	
	launch the app and add test.py to the project
	>>> mathinspector.main("~/Projects/test.py")

	launch the app with the project stored in myproject.math open
	>>> mathinspector.main(mathfile="myproject.math")
	
	"""
	if "help" in kwargs:
		return viewdoc(kwargs["help"])

	if "new" in kwargs and kwargs["new"] is True:
		with open(AUTOSAVE_PATH, "w") as f:
			f.write("")
			f.close()

	app = App(*args)
	app.mainloop()
