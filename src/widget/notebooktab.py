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
	def __init__(self, parent, name, index, packags={"side": "left"},
				font="Monospace 12", closebtn=False, background=INACTIVE, foreground=Color.BLACK, 
				hover=HOVER, selected_bg=SELECTED, selected_fg=Color.BLACK, is_draggable=False):

		tk.Frame.__init__(self, parent.nav, background=background)
		self.label = tk.Label(self, 
			text=name, 
			font=font, 
			width=12 if closebtn else None,
			anchor="w" if closebtn else None,
			foreground=foreground,
			background=background, 
			padx=12, 
			pady=4
		)

		self.parent = parent
		self.name = name
		self.index = index
		# REFACTOR do a style dict for this stuff!
		self.foreground = foreground
		self.background = background
		self.selected_bg = selected_bg
		self.selected_fg = selected_fg
		self.hover = hover
		self.is_modified = False
		self.is_selected = False
		self.text = "×"
			
		self.label.pack(side="left", fill="both", expand=True)
		self.pack(**packags)

		if closebtn:
			self.place(x=151 * index)
			self.closebtn = tk.Label(self, 
				text="×", 
				font="Monospace 15 bold",
				background=background, 
				foreground=foreground,
				padx=4, 
				pady=4				
			)
			self.closebtn.pack(side="left")
			self.closebtn.bind("<Enter>", self._on_enter)
			self.closebtn.bind("<Leave>", self._on_leave)
		else:
			self.closebtn = None
			self.bind("<Enter>", self._on_enter)
			self.bind("<Leave>", self._on_leave)

	def rename(self, name):
		self.name = name
		self.label.config(text=self.name)

	def set_index(self, index):
		self.index = index
		self.place(x=self.winfo_width() * index)

	def toggle_unsaved(self, is_modified=None):
		self.is_modified = is_modified if is_modified != None else not self.is_modified
		self.text = "•" if self.is_modified else "×"
		self.closebtn.config(text=self.text)

	def select(self):
		self.is_selected = True
		self.label.config(background=self.selected_bg, foreground=self.selected_fg)
		if self.closebtn:
			self.closebtn.config(background=self.selected_bg, foreground=self.foreground)

	def unselect(self):
		self.is_selected = False
		self.label.config(background=self.background, foreground=self.foreground)
		if self.closebtn:
			self.closebtn.config(background=self.background, foreground=self.foreground)

	def _on_enter(self, event):
		if self.closebtn:
			self.closebtn.config(foreground=Color.WHITE, text="×")
		elif not self.is_selected:
			self.label.config(background=self.hover)
	
	def _on_leave(self, event):
		if self.closebtn:
			self.closebtn.config(foreground=self.foreground, text=self.text)
		elif not self.is_selected:
			self.label.config(background=self.background)
