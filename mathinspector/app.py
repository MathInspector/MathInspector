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


class App(themed_tk.ThemedTk):
	def __init__(self):
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
		self.project.load(is_first_load=True)


def main():
	app = App()
	app.mainloop()
