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
from settings import Color

SELECTED = Color.PALE_BLUE
INACTIVE = Color.GREY
HOVER = Color.VERY_LIGHT_GREY

class NotebookTab(tk.Frame):
	def __init__(self, parent, name):

		tk.Frame.__init__(self, parent.nav, background=Color.BLACK)
		self.label = tk.Label(self, 
			text=name, 
			font="SourceSansPro 12 bold", 
			foreground=Color.WHITE,
			background=Color.BLACK, 
			padx=12, 
			pady=4
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
