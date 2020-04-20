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

class BlinkingCursor(tk.Frame):
	def __init__(self, parent, x, y):
		tk.Frame.__init__(self, parent, background=Color.WHITE, width=1, height=16)
		self.hidden = True
		self.place(x=x - 16, y=y - 8)
		self.toggle()

	def toggle(self):
		self.hidden = not self.hidden
		self.config(background=Color.BACKGROUND if self.hidden else Color.WHITE)
		self.after(500, self.toggle)

