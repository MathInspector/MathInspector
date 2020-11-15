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
from tkinter import messagebox, filedialog, simpledialog
from widget import Popup
from settings import Cmd
import os

class Menu(tk.Menu):
	def __init__(self, app, *args, **kwargs):
		tk.Menu.__init__(self, app, *args, **kwargs)
		app.config(menu=self)

		OPTIONS = {


			"File": [{
				"label": "New Project            ",
				"command": self.new,
				"hotkey": Cmd + "+Shift+n",
			},
			{
				"label": "Open...            ",
				"command": self.open,
				"hotkey": Cmd + "+Shift+o"	
			},
			{
				"label": "Save            ",
				"command": self.save,
				"hotkey": Cmd + "+Shift+s"	
			},
			{
				"label": "Save As...            ",
				"command": self.save_as
			}],


			"Project": [{
				"label": "Add Folder...            ",
				"command": app.projecttree.addfolder
			},
			{
				"label": "Import Module...",
				"command": lambda: Popup(self.app, "Import Module", self.app, obj=self.app.projecttree.import_module, eval_args=False)
			}],

			"Plot": [{
				"label": "Show Grid Lines                 ✓",
				"command": lambda: self.toggle_output("show_grid_lines")
			},
			{
				"label": "Smooth Lines                 ✓",
				"command": lambda: self.toggle_output("smooth")
			},
			{
				"label": "Random Color Lines            ",
				"command": lambda: self.toggle_output("random_color")
			}],

			"Workspace": [{
				"label": "Add Object",
				"menu": [{
					"label": "linspace",
					"command": lambda: self.app.workspace.create_object("linspace")
				},{
					"label": "complex_grid",
					"command": lambda: self.app.workspace.create_object("complex_grid")
				}]
			}],

			"View": [{
				"label": "Console",
				"menu": [{
					"label": "Top Panel",
					"command": lambda event=None: self.app.setview("console"),
				}, {
					"label": "Bottom Panel",
					"command": lambda event=None: self.app.setview("console", bottom=True),
				}, {
					"label": "Maximize",
					"command": lambda event=None: None,
				}]
			},{
				"label": "Workspace",
				"menu": [{
					"label": "Top Panel",
					"command": lambda event=None: self.app.setview("workspace"),
				}, {
					"label": "Bottom Panel",
					"command": lambda event=None: self.app.setview("workspace", bottom=True),
				}]
			},{
				"label": "Doc Viewer",
				"menu": [{
					"label": "Top Panel",
					"command": lambda event=None: self.app.setview("docviewer"),
				}, {
					"label": "Bottom Panel",
					"command": lambda event=None: self.app.setview("docviewer", bottom=True),
				}]
			},{
				"label": "Output",
				"menu": [{
					"label": "Top Panel",
					"command": lambda event=None: self.app.setview("output"),
				}, {
					"label": "Bottom Panel",
					"command": lambda event=None: self.app.setview("output", bottom=True),
				}]
			}]
		}

		self.app = app
		self.menus = []
		self.filename = None
		for key in OPTIONS:
			menu = tk.Menu(self)
			self.menus.append(menu)
			self.add_cascade(menu=menu, label=key)
			for item in OPTIONS[key]:			
				if "menu" in item and len(item["menu"]) > 0:
					temp = tk.Menu(self)
					self.menus.append(temp)
					for k in item["menu"]:
						if "separator" in k:
							temp.add_separator(k["separator"])
						if "label" in k and "command" in k:
							temp.add_command(label=k["label"], command=k["command"], accelerator=None if "hotkey" not in k else k["hotkey"])
						if "hotkey" in k:
							# need a better system for assigning hotkeys, this doesn't allow all combinations
							self.app.bind("<" + k["hotkey"].replace("+", "-") + ">", k["command"])
					menu.add_cascade(label=item["label"], menu=temp)
				elif "separator" in item:
					menu.add_separator(item["separator"])
				else:
					menu.add_command(label=item["label"], command=item["command"], accelerator=None if "hotkey" not in item else item["hotkey"])
				
				if "hotkey" in item:
					self.app.bind("<" + item["hotkey"].replace("+", "-") + ">", item["command"])

	def new(self, event=None):
		self.filename = None
		if messagebox.askokcancel("MathInspector", "Are you sure you want to start a new file?  Any unsaved data will be lost."):
			self.app.savedata.new()

	def open(self, event=None):
		filepath = filedialog.askopenfilename()
		if filepath:
			if messagebox.askokcancel("MathInspector", "Are you sure you want to open " + os.path.basename(filepath) + "?  Any unsaved data will be lost."):
				self.app.savedata.load( filepath )

	def save(self, event=None):
		if self.app.savedata.filepath is None:
			self.save_as()
		else:			
			self.app.savedata.save(self.app.savedata.filepath)

	def save_as(self, event=None):
		self.app.savedata.save( filedialog.asksaveasfilename(defaultextension=".math") )

	# @TODO: create custom dialog that allows import X as Y
	def import_module(self, event=None):
		module = simpledialog.askstring("Import Module", "What is the name of the module you want to import?")
		if module:
			self.app.execute("import " + module, __SHOW_RESULT__=False)

	def show_projecttree(self, event=None):
		self.app.treenotebook.select("modules")

	def show_objecttree(self, event=None):
		self.app.treenotebook.select("objects")

	def open_file(self, event=None):
		pass

	def close_file(self, event=None):
		self.app.editor.close()

	def toggle_output(self, option):
		state = self.app.output.toggle(option)		
		if option == "show_grid_lines":
			idx = 0
			label = "Show Grid Lines              " + ("✓" if state else " ")
		if option == "smooth":
			idx = 1
			label = "Smooth Lines                 " + ("✓" if state else " ")
		elif option == "random_color":
			idx = 2
			label = "Random Color Lines           " + ("✓" if state else " ")
		self.menus[2].entryconfig(idx, label=label)
