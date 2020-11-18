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
from tkinter import ttk
from settings import Color
from widget.notebooktab import NotebookTab

class Notebook(tk.Frame):
	def __init__(self, parent, has_labels=False, *args, **kwargs):
		tk.Frame.__init__(self, parent, background=Color.BLACK, highlightthickness=4, highlightbackground=Color.BLACK, *args, **kwargs)
		self.notebook = ttk.Notebook(self)
		self.tabs = {}
		self.has_labels = has_labels

		tk.Label(self, background=Color.BLACK, height=1, font="Monospace 1").pack(side="top", fill="both")

		if has_labels:	
			self.nav = tk.Frame(self, background=Color.BLACK, height=32)
			self.nav.pack(fill='x', expand=False)

		self.notebook.pack(fill='both', expand=True)
		self.notebook.bind('<<NotebookTabChanged>>', self._on_changetab)

	def add(self, name, widget):		
		self.notebook.add(widget)
		tab_id = self.notebook.tabs()[-1]
		if self.has_labels:
			tab = NotebookTab(self, name)
			self.tabs[tab_id] = tab
			tab.label.bind("<Button-1>", lambda event: self.notebook.select(tab_id))
				
		return tab_id

	def _on_changetab(self, event):
		tab_id = self.notebook.select()
		if tab_id and self.has_labels:
			self.tabs[tab_id].select()
			selected = self.notebook.select()
			if selected and selected != tab_id:
				self.tabs[selected].unselect()

			for i in self.tabs:
				if i == tab_id:
					self.notebook.select(i)
				elif i in self.tabs:
					self.tabs[i].unselect()		