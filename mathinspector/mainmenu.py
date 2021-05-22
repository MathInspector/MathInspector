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

from . import doc, examples
from .plot import plot
from .util import binop, name_ext
from .widget import Popup, Menu
from .style import Color
from .project import FILETYPES
from .util.builtin_lists import *
from .config import open_editor, CONTROL_KEY, BASEPATH

SASHPOS_MIN = 20

class MainMenu(Menu):
	def __init__(self, app):
		self.savefile = ""

		self.file = [{
			"label": "New                    ",
			"command": app.project.new,
			"accelerator": CONTROL_KEY + "+n",
		},{
			"label": "Open...            ",
			"command": lambda event=None: app.modules.addfile(),
			"accelerator": CONTROL_KEY + "+o"
		},{
			"label": "Save           ",
			"command": lambda event=None: self.save_console_history(self.savefile),
		},{
			"label": "Save As...            ",
			"command": lambda event=None: self.save_console_history(),
		}]

		self.plot = [{
			"label": "Show Grid Lines                      ✓",
			"command": partial(self.plotconfig, "show_grid"),
		},{
			"label": "Show Range                             ",
			"command": lambda: self.plotconfig("show_range")
		}]

		self.object = [{
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

		self.project = [{
			"label": "Open Project",
			"command": app.project.load		
		},{
			"label": "Open Recent",
			"menu": [{
				"separator": None
			}]
		},{
			"separator": None
		},{
			"label": "Save Project",
			"command": lambda event=None: app.project.save(app.project.mathfile or app.modules.rootfolder),
			"accelerator": CONTROL_KEY + "+s"
		},{
			"label": "Save Project As...",
			"command": lambda event=None: app.project.save(),
			"accelerator": CONTROL_KEY + "+Shift+s"
		},{
			"separator": None
		},{
				"label": "Add a New File...",
				"menu": [{
					"label": "Python (.py)",
					"command": lambda: self.app.modules.new_file(ext=".py")
				},{
					"label": "Markdown (.md)",
					"command": lambda: self.app.modules.new_file(ext=".md")
				},{
					"label": "Rich Structured Text (.rst)",
					"command": lambda: self.app.modules.new_file(ext=".rst")
				},{
					"label": "Other...",
					"command": lambda: self.app.modules.addfile(None)
				}]
		},{
			"label": "Add File to Project...",
			"command": app.modules.addfile
		},{
			"label": "Add Folder to Project...",
			"command": app.modules.addfolder
		},{
			"label": "Import Module...",
			"command": lambda event=None: help.import_module(self.import_module)
		},{
			"separator": None
		},{
			"label": "Remove all Files",
			"command": lambda: self.app.modules.clear("file", with_dialog=1)
		},{
			"label": "Remove all Folders",
			"command": lambda: self.app.modules.clear("folder", with_dialog=1)
		},{
			"label": "Remove all Modules",
			"command": lambda: self.app.modules.clear("module", with_dialog=1)
		}]		

		self.view = [{
			"label": "Show Sidebar",
			"command": lambda: self.setview("sidebar")
		},{
			"label": "Show Node Editor",
			"command": lambda: self.setview("node_editor")
		},{
			"label": "Hide Console",
			"command": lambda: self.setview("console")
		}]

		self.help = [{
			"label": "Getting Started",
			"command": lambda: help(doc.manual.GettingStarted)
		},{
			"label": "User Manual",
			"command": lambda: help()
		},{
			"label": "Examples",
			"command": lambda: help(examples)
		},{
			"separator": None
		},{
			"label": "Browse Modules...",
			"command": lambda: help.browse()
		}]
		# 	"TODO": "Numpy Doc",
		# 	"TODO": "Scipy Tutorial",
		# 	"TODO": "Builtin Functions",
		

		Menu.__init__(self, app, [{
			"label": "File",
			"menu": self.file
		},{
			"label": "Plot",
			"menu": self.plot,
		},{
			"label": "Object",
			"menu": self.object
		},{
			"label": "Project",
			"menu": self.project
		},{
			"label": "View",
			"menu": self.view
		},{
			"label": "Help",
			"menu": self.help
		}])

		self.app = app
		self.is_sidebar_visible = False
		self.has_hidden_panel = False

		if hasattr(sys, "_MEIPASS"):
			app.createcommand('tkAboutDialog', lambda: help(os.path.join(BASEPATH, "ABOUT.md"), "About Math Inspector"))

		app.side_view.bind("<Configure>", self.on_config_sidebar)
		app.node.output.bind("<Configure>", self.on_config_vertical_panel)
		self.sync_recent_projects()

	def sync_recent_projects(self):
		recents = [{
			"label":  name_ext(i)[0],
			"command": lambda key=i: self.app.project.load(key)
		} for i in self.app.project.recents]
		
		if recents:
			recents.append({ "separator": None })
		
		self._["Project"].entryconfig(1, menu=Menu(self, recents + [{
			"label": "Clear Items",
			"command": self.clear_recents
		}]))

	def clear_recents(self):
		self.app.project.recents.clear()
		self.sync_recent_projects()

	def save_console_history(self, savefile=None):
		if not savefile or savefile != self.savefile:
			self.savefile = filedialog.asksaveasfilename(
				filetypes=FILETYPES,
				title="Save Command History",
				message="Choose a default location for the command history be saved")
			if not self.savefile: return
		
		with open(self.savefile, "w") as output:
			output.write("\n".join(self.app.console.prompt.history.cmds))
			output.close()

		print ("Command history saved to " + self.savefile)

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

	def restore_defaults(self):
		self._["View"].entryconfig(0, label="Show Sidebar")
		self._["View"].entryconfig(1, label="Show Node Editor")
		self._["View"].entryconfig(2, label="Hide Console")	

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
