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

import tkinter as tk
from tkinter import ttk
from ..style import Color
from ..util.config import FONT_SIZE

class Notebook(ttk.Notebook):
	def __init__(self, *args, has_labels=False, **kwargs):
		self.frame = tk.Frame(*args, background=Color.BLACK, highlightthickness=4, highlightbackground=Color.BLACK, **kwargs)
		ttk.Notebook.__init__(self, self.frame)

		self._tabs = {}
		self.has_labels = has_labels

		if has_labels:
			self.nav = tk.Frame(self.frame, background=Color.BLACK, height=32)
			self.nav.pack(fill='x', expand=False)

		self.pack(fill='both', expand=True)
		self.bind('<<NotebookTabChanged>>', self._on_changetab)

	def add(self, name, widget, **kwargs):
		super(Notebook, self).add(widget, **kwargs)
		tab_id = super(Notebook, self).tabs()[-1]
		if self.has_labels:
			tab = NotebookTab(self, name)
			self._tabs[tab_id] = tab
			tab.label.bind("<Button-1>", lambda event: self.select(tab_id))

		return tab_id

	def _on_changetab(self, event):
		tab_id = self.select()
		if tab_id and self.has_labels:
			self._tabs[tab_id].select()
			selected = self.select()
			if selected and selected != tab_id:
				self._tabs[selected].unselect()

			for i in self._tabs:
				if i == tab_id:
					self.select(i)
				elif i in self._tabs:
					self._tabs[i].unselect()

class NotebookTab(tk.Frame):
	def __init__(self, parent, name):

		tk.Frame.__init__(self, parent.nav, background=Color.BLACK)
		self.label = tk.Label(self,
			text=name,
			font="SourceSansPro " + FONT_SIZE["extra-small"] + " bold",
			foreground=Color.WHITE,
			background=Color.BLACK,
			padx=12,
			pady=8
		)

		self.parent = parent
		self.name = name
		self.is_selected = False

		self.label.pack(side="left", fill="both", expand=True)
		self.pack(fill="x", expand=True, side="left")

		self.bind("<Enter>", self._on_enter)
		self.bind("<Leave>", self._on_leave)

	def select(self):
		self.is_selected = True
		self.label.config(background=Color.BLACK, foreground=Color.ORANGE)

	def unselect(self):
		self.is_selected = False
		self.label.config(background=Color.BLACK, foreground=Color.WHITE)

	def _on_enter(self, event):
		if not self.is_selected:
			self.label.config(background=Color.VERY_DARK_GREY)

	def _on_leave(self, event):
		if not self.is_selected:
			self.label.config(background=Color.BLACK)
