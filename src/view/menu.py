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
from util import name_and_extension
from os import path

class Menu(tk.Menu):
	def __init__(self, app, *args, **kwargs):
		tk.Menu.__init__(self, app, *args, **kwargs)
		app.config(menu=self)

		OPTIONS = {
			"File": [{
				"label": "New                    ",
				"command": self.new,
				"hotkey": Cmd + "+n",
			},
			{
				"label": "Open...            ",
				"command": self.open,
				"hotkey": Cmd + "+o"	
			},
			{
				"label": "Save            ",
				"command": lambda event=None: self.save(self.app.projecttree.rootfolder),
				"hotkey": Cmd + "+s"	
			},
			{
				"label": "Save As...            ",
				"command": lambda event=None: self.save(),
				"hotkey": Cmd + "+Shift+s"	
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
				"label": "Top Panel",
				"menu": [{
					"label": "Console",
					"command": lambda event=None: self.app.nav.select("top", "console"),
				}, {
					"label": "Workspace",
					"command": lambda event=None: self.app.nav.select("top", "workspace"),
				}, {
					"label": "Doc Viewer",
					"command": lambda event=None: self.app.nav.select("top", "docviewer"),
				}, {
					"label": "Output",
					"command": lambda event=None: self.app.nav.select("top", "output"),
				}, {
					"separator": None
				}, {
					"label": "Maximize",
					"command": lambda: self.maximize("top")
				}, {
					"label": "Hide",
					"command": lambda: self.hide("top")
				}]
			}, {
				"label": "Bottom Panel",
				"menu": [{
					"label": "Console",
					"command": lambda: self.app.nav.select("bottom", "console"),
				}, {
					"label": "Workspace",
					"command": lambda: self.app.nav.select("bottom", "workspace"),
				}, {
					"label": "Doc Viewer",
					"command": lambda: self.app.nav.select("bottom", "docviewer"),
				}, {
					"label": "Output",
					"command": lambda: self.app.nav.select("bottom", "output"),
				}, {
					"separator": None
				}, {
					"label": "Maximize",
					"command": lambda: self.maximize("bottom")
				}, {
					"label": "Hide",
					"command": lambda: self.hide("bottom")
				}]
			}, ]
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
					self.app.bind("<" + item["hotkey"].replace("+", "-") + ">", lambda event, command=item["command"]: self.hotkey(command))

	def hotkey(self, command):
		command()
		self.app.focus_force()

	def new(self, event=None):
		self.filename = None
		if messagebox.askokcancel("MathInspector", "Are you sure you want to start a new file?  Any unsaved data will be lost."):
			self.app.savedata.new()

	def open(self, event=None):
		filepath = filedialog.askopenfilename(filetypes=[('Math Inspector Files','*.math'), ('All Files','*.*')])
		if filepath:
			self.app.savedata.load(filepath)

	def save(self, filepath=None):
		if not filepath:
			filepath = filedialog.asksaveasfilename(defaultextension="")
			if not filepath: return
		
		self.app.savedata.save(path.join(filepath, path.basename(filepath) + ".math"))

	def import_module(self, event=None):
		module = simpledialog.askstring("Import Module", "What is the name of the module you want to import?")
		if module:
			self.app.execute("import " + module)

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

	def maximize(self, key):
		if key == "top":
			self.app.horizontal_panel.sashpos(0,0)
			self.app.vertical_panel.sashpos(0,self.app.winfo_height())
		elif key == "bottom":
			self.app.horizontal_panel.sashpos(0,0)
			self.app.vertical_panel.sashpos(0,0)

	def hide(self, key):
		if key == "top":
			self.app.vertical_panel.sashpos(0,0)
		if key == "bottom":
			self.app.vertical_panel.sashpos(0,self.app.winfo_height())
