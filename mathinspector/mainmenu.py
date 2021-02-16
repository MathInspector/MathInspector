"""
Math Inspector: a visual programming environment for scientific computing
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
import numpy as np
import scipy, math, builtins, os, sys
from functools import partial
from tkinter import filedialog

from . import plot, doc, examples
from .util import binop
from .widget import Popup, Menu
from .style import Color
from .util import BUILTIN_FUNCTION, BUILTIN_CLASS, BUILTIN_CONSTANT
from .util.common import open_editor
from .util.config import CONTROL_KEY, BASEPATH, BUILTIN_FUNCTION, BUILTIN_CLASS, BUILTIN_CONSTANT
from .console import builtin_print

TRIG_FUNCTIONS = [i for i in ("acos", "acosh", "asin", "asinh", "atan", "atan2", "atanh", "cos", "cosh", "degrees", "sin", "sinh", "tan", "tanh")]
MATH_FUNCTIONS = [i for i in dir(math) if callable(getattr(math, i)) and i not in TRIG_FUNCTIONS + ["pow"] and i[:1] != "_"]
MATH_FUNCTIONS.append("power")
MATH_FUNCTIONS.sort()
MATH_CONSTANTS = [i for i in dir(math) if i not in MATH_FUNCTIONS + TRIG_FUNCTIONS and i[:1] != "_"]
SASHPOS_MIN = 20

class MainMenu(Menu):
	def __init__(self, app):
		self.project_menu = [{
			"label": "New File",
			"command": self.new_file
		},{
			"label": "Add File...",
			"command": app.modules.addfile
		},{
			"label": "Add Folder...",
			"command": app.modules.addfolder
		},{
			"label": "Import Module...",
			"command": lambda event=None: help.import_module(self.import_module)
		}]

		self.object_menu = [{
			"label": "Operator",
			"menu": [{
				"label": i,
				"command": lambda key=i: self.create_object(key, binop)
			} for i in dir(binop) if i[0] != "_"]
		},{
			"label": "Math",
			"menu": [{
				"label": "Constant",
				"menu":[{
					"label": i,
					"command": lambda key=i: self.create_object(key, np if hasattr(np, key) else math)
				} for i in MATH_CONSTANTS]
			},{
				"separator": None
			},{
				"label": "Trig",
				"menu":[{
					"label": i,
					"command": lambda key=i: self.create_object(key, np if hasattr(np, key) else math)
				} for i in TRIG_FUNCTIONS]
			},{
				"separator": None
			}] + [{
				"label": i,
				"command": lambda key=i: self.create_object(key, np if hasattr(np, key) else math)
			} for i in MATH_FUNCTIONS]
		},{
			"label": "Builtin Class",
			"menu": [{
				"label": str(i),
				"command": lambda key=i: self.create_object(key, builtins)
			} for i in BUILTIN_CLASS if i[:1] != "_" and not i[:1].isupper() and "Error" not in i and "Warning" not in i]
		},{
			"label": "Builtin Function",
			"menu": [{
				"label": str(i),
				"command": lambda key=i: self.create_object(key, module=builtins)
			} for i in BUILTIN_FUNCTION if i[:1] != "_" and not i[:1].isupper()]
		},{
			"label": "Examples",
			"menu": [{
				"label": str(i).replace("_", " ").capitalize(),
				"command": lambda key=i: self.create_object(key, module=examples)
			} for i in dir(examples) if i[:1] != "_" and not i[:1].isupper() and i != "np"]
		}]

		Menu.__init__(self, app, [{
			"label": "File",
			"menu": [{
					"label": "New                    ",
					"command": app.project.new,
					"accelerator": CONTROL_KEY + "+n",
				},
				{
					"label": "Open...            ",
					"command": lambda event=None: app.project.load(None),
					"accelerator": CONTROL_KEY + "+o"
				},
				{
					"label": "Save            ",
					"command": lambda event=None: app.project.save(app.modules.rootfolder),
					"accelerator": CONTROL_KEY + "+s"
				},
				{
					"label": "Save As...            ",
					"command": lambda event=None: app.project.save(None),
					"accelerator": CONTROL_KEY + "+Shift+s"
				}]
			},{
				"label": "Project",
				"menu": self.project_menu
			},{
				"label": "Object",
				"menu": self.object_menu
			},{
				"label": "Plot",
				"menu": [{
					"label": "Show Grid Lines                      ✓",
					"command": partial(self.plotconfig, "show_grid"),
				},{
					"label": "Show Range                             ",
					"command": lambda: self.plotconfig("show_range")
				}],
			},
			{
				"label": "View",
				"menu": [{
					"label": "Show Sidebar",
					"command": lambda: self.setview("sidebar")
				},{
					"label": "Show Node Editor",
					"command": lambda: self.setview("node_editor")
				},{
					"label": "Hide Console",
					"command": lambda: self.setview("console")
				}]
			},
			{
				"label": "Help",
				"menu": [{
					"label": "Getting Started",
					"command": lambda: help(doc.manual.GettingStarted)
				},{
					"label": "User Manual",
					"command": lambda: help(doc.manual)
				},{
					"label": "Examples",
					"command": lambda: help(examples)
				},
				# {
				##### for some reason this is failing in pyinstaller, can include this with .rst files maybe
				# 	"label": "Numpy Doc",
				# 	"command": lambda: help(np.doc)
				# },
				{
					"separator": None
				},{
					"label": "Browse Modules...",
					"command": lambda: help.browse()
				}
				# ,{
				# 	"label": "Scipy Tutorial",
				# 	"command": lambda: help(scipy)
				# }
				# ,{
				# 	"label": "Builtin Functions",
				# 	"command": lambda: help(builtins)
				# }
				]
			}])

		self.app = app
		self.is_sidebar_visible = False
		self.has_hidden_panel = False

		if hasattr(sys, "_MEIPASS"):
			app.createcommand('tkAboutDialog', lambda: help(os.path.join(BASEPATH, "ABOUT.md"), "About Math Inspector"))

		app.side_view.bind("<Configure>", self.on_config_sidebar)
		app.node.output.bind("<Configure>", self.on_config_vertical_panel)

	def on_config_sidebar(self, event):
		sashpos = self.app.horizontal_panel.sashpos(0)
		if self.is_sidebar_visible and sashpos > SASHPOS_MIN: return

		if sashpos <= SASHPOS_MIN:
			self._["View"].entryconfig(0, label="Show Sidebar")
			self.is_sidebar_visible = False
		else:
			self._["View"].entryconfig(0, label="Hide Sidebar")
			self.is_sidebar_visible = True

	def on_config_vertical_panel(self, event):
		sashpos = self.app.vertical_panel.sashpos(0)
		height = self.app.winfo_height()
		if SASHPOS_MIN < sashpos < height - SASHPOS_MIN:
			if self.has_hidden_panel:
				self.has_hidden_panel = False
				self._["View"].entryconfig(1, label="Hide Node Editor")
				self._["View"].entryconfig(2, label="Hide Console")
			return

		self.has_hidden_panel = True
		if sashpos <= SASHPOS_MIN:
			self._["View"].entryconfig(1, label="Show Node Editor")
			self._["View"].entryconfig(2, label="Hide Console")
		else:
			self._["View"].entryconfig(1, label="Hide Node Editor")
			self._["View"].entryconfig(2, label="Show Console")

	def create_object(self, name, module):
		self.app.objects.setobj(name, getattr(module, name), create_new=True)

	def setview(self, key, force_open=False):
		h_sashpos = self.app.horizontal_panel.sashpos(0)
		v_sashpos = self.app.vertical_panel.sashpos(0)

		if key == "sidebar":
			self.is_sidebar_visible = not self.is_sidebar_visible
			if self.is_sidebar_visible:
				self._["View"].entryconfig(0, label="Hide Sidebar")
				self.app.horizontal_panel.sashpos(0,240)
			elif not force_open:
				self._["View"].entryconfig(0, label="Show Sidebar")
				self.app.horizontal_panel.sashpos(0,0)
		elif key == "node_editor":
			if v_sashpos <= SASHPOS_MIN:
				self.app.vertical_panel.sashpos(0, int(self.app.winfo_height()/2))
				self._["View"].entryconfig(1, label="Hide Node Editor")
			elif not force_open:
				self.app.vertical_panel.sashpos(0, 0)
				self._["View"].entryconfig(1, label="Show Node Editor")
		elif key == "console":
			height = self.app.winfo_height()
			if v_sashpos >= height - SASHPOS_MIN:
				self.app.vertical_panel.sashpos(0, int(height/2))
			elif not force_open:
				self.app.vertical_panel.sashpos(0, int(height))
		elif key == "modules":
			self.app.side_view.select(0)
			if h_sashpos <= 10:
				self.app.horizontal_panel.sashpos(0,240)
		elif key == "objects":
			self.app.side_view.select(1)
			if h_sashpos <= 10:
				self.app.horizontal_panel.sashpos(0,240)
			# else:
			# 	self.app.vertical_panel.sashpos(0, 0)

	def new_file(self):
		file = filedialog.asksaveasfilename(defaultextension=".py")
		if not file: return
		f = open(file, "a")
		f.write("")
		f.close()
		self.app.modules.addfile(file)
		open_editor(file)

	def import_module(self, module, alias="", open_folders=False):
		self.app.modules[alias or module] = __import__(module)
		if open_folders:
			self.app.focus()
			key = alias or module
			self.app.modules.selection_set(key)
			self.app.modules.item(key, open=True)

	def plotconfig(self, key=None, **kwargs):
		opts = plot.config()
		if not opts: return # BUG: make sure this works when loading a project

		if key is None:
			plot.config(**kwargs)
			if "show_grid" in kwargs:
				self._["Plot"].entryconfig(0, label="Show Grid Lines                      " + ("✓" if opts["show_grid"] else ""))
			elif "show_range" in kwargs:
				self._["Plot"].entryconfig(1, label="Show Range                           " + ("✓" if opts["show_range"] else ""))
			return

		plot.config(**{ key : not opts[key] })
		if key == "show_grid":
			self._["Plot"].entryconfig(0, label="Show Grid Lines                      " + ("✓" if opts[key] else ""))
		elif key == "show_range":
			self._["Plot"].entryconfig(1, label="Show Range                           " + ("✓" if opts[key] else ""))



	def set_plot_resolution(self, val):
		self.plotconfig(resolution=val)
