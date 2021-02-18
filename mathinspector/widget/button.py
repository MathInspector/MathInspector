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
from ..style import Color

class Button(tk.Label):
	def __init__(self, parent, *args, command=None, **kwargs):
		if "background" not in kwargs:
			kwargs["background"] = Color.ALT_BACKGROUND

		if "foreground" not in kwargs:
			kwargs["foreground"] = Color.WHITE

		if "highlightbackground" not in kwargs:
			kwargs["highlightbackground"] = Color.DARK_BLACK

		if "highlightthickness" not in kwargs:
			kwargs["highlightthickness"] = 4

		tk.Label.__init__(self, parent, *args, **kwargs)

		self.is_active = False

		self.bind("<Enter>", self._on_enter)
		self.bind("<Leave>", self._on_leave)
		self.bind("<Button-1>", self._on_button_1)
		self.bind("<ButtonRelease-1>", lambda event=None: command() if self.is_active else None)

	def _on_enter(self, event):
		self.is_active = True
		self.config(foreground=Color.DARK_GREY)

	def _on_leave(self, event):
		self.is_active = False
		self.config(foreground=Color.WHITE)

	def _on_button_1(self, event):
		self.config(foreground=Color.VERY_DARK_GREY)
