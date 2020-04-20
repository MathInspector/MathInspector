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
from widget import NavIcon
from settings import Color

class Nav(tk.Frame):
	def __init__(self, app):
		tk.Frame.__init__(self, app, background=Color.BLACK)		
		
		self.icons = {
			".!editor": NavIcon(self, "editor", app),
			".!console": NavIcon(self, "console", app),
			".!workspace": NavIcon(self, "workspace", app),
			".!docviewer": NavIcon(self, "docviewer", app),
			".!output": NavIcon(self, "output", app),
		}
		
		tk.Frame(self, background=Color.BLACK, height=12).pack(side="top", fill="both")
		
		for j in self.icons:
			self.icons[j].pack()		
