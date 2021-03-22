"""
Math Inspector: a visual programming environment for scientific computing
https://mathinspector.com

help
---
The mathinspector `help` function has been designed to override the builtin python `help` function.  This makes it easy to write code that displays documentation for your own projects with the mathinspector doc browser.

These can be viewed using the help function.  For example, to view this documentation in the mathinspector doc browser, use the command

>>> import mathinspector
>>> from mathinspector import help
>>> help(mathinspector)

For more information about any of the items which follow, see the corresponding docstrings for that item.  If you are using the doc browser to view this documentation, the sidebar contains a list of everything this module contains, and you can click on those items to learn more.  All code examples can be clicked on, and they will be executed and the output printed to the command line.

main
---
This will launch the mathinspector app

>>> import mathinspector
>>> mathinspector.main()

See the documentation for the main function to understand the structure of the arguments it accepts

plot
---
The mathinspector plotting library was designed to update and replace the functionality in matplotlib.

This will launch the mathinspector plotting window.

>>> import mathinspector
>>> mathinspector.plot(1,2,3)

The way you format data you pass as arguments to the plot function will determine what is plotted.  It will automatically detect when the input is 2-dimensional or 3-dimensional, and treats tuple's as points and lists & arrays as lines.  See the documentation for the plot function for a complete list of accepted argument types.

vdict
---
This module also has the class vdict, which stands for virtual dictionary.  It's a class which extends dict
and has callbacks for getting, setting, and deleting items.

>>> import mathinspector
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
from .console.interpreter import Interpreter, StdWrap
from .console.builtin_print import builtin_print
from .node import NodeEditor
from .objects import ObjectTree
from .modules import ModuleTree
from .mainmenu import MainMenu
from .project import SaveData
from .animation import Animation
from .widget import Notebook

from .util import vdict, name_ext
from .config import __version__, AUTOSAVE_PATH
from .plot import plot
from .doc import Help

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
	"help",
]

def __dir__():
	return ALLOWED_NAMES

help = Help()

class App(themed_tk.ThemedTk):
	def __init__(self, *args, debug=False, disable=[]):
		themed_tk.ThemedTk.__init__(self)
		self.set_theme("arc")
		ttk.Style(self)

		self.horizontal_panel = ttk.PanedWindow(self, orient="horizontal")
		self.vertical_panel = ttk.PanedWindow(self, orient="vertical")
		self.side_view = Notebook(self, has_labels=True)

		self.node = NodeEditor(self)
		self.console = Interpreter(self, disable=disable)
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

		self.title("Math Inspector")
		self.debug = debug

		mathfile = AUTOSAVE_PATH
		pyfiles = []
		for i in args:
			if not os.path.isfile(i):
				builtin_print("mathinspector failed to launch: " + i + " is not a file\n")
				exit()

			name, ext = name_ext(i)
			if ext == ".math":
				mathfile = os.path.abspath(i)
			elif ext == ".py":
				mathfile = ""
				pyfiles.append(os.path.abspath(i))
			else:
				builtin_print("mathinspector failed to launch: " + ext + " is not a currently supported file type.\n")
				exit()

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

	debug: bool
		When set to True, this will print a range of log messages to the command line used to launch the app.  Useful for debugging issues or while working on the math inspector source code.


	Examples
	--------

	launch the app with a brand new project
	>>> mathinspector.main(new=True)

	launch the app and add test.py to the project
	>>> mathinspector.main("~/Projects/test.py")

	launch the app with the project stored in myproject.math open
	>>> mathinspector.main(mathfile="myproject.math")

	launch the app in debug mode
	>>> mathinspector.main(debug=True)

	"""
	if "help" in kwargs:
		return help(kwargs["help"])

	if "new" in kwargs and kwargs["new"] is True:
		with open(AUTOSAVE_PATH, "w") as f:
			f.write("")
			f.close()

	params = {
		"debug": kwargs["debug"] if "debug" in kwargs else False,
		"disable": kwargs["disable"].split(",") if "disable" in kwargs else [],
	}

	if params["disable"] is True:
		params["disable"] = ["print", "traceback", "stderr"]

	if params["debug"]:
		print (params)

	app = App(*args, **params)
	if "stderr" not in params["disable"]:
		sys.stderr = StdWrap(sys.stderr, app.console) # overrides stderr after init app
	app.mainloop()
