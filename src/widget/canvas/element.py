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

class Element:
	def __init__(self, canvas, element_type="oval", coords=(0,0), smooth="true", fill=Color.WHITE, width=0.1, height=0.1, antialias=False):
		self.canvas = canvas
		self.type = element_type
		self.position = coords
		self.width = width
		self.height = height
		self.fill = fill

		if self.type == "oval":
			x,y = coords
			self.id = canvas.create_oval(x - width/2, y - height/2, x + width/2, y + height/2, fill=fill, outline=fill)
		elif self.type == "line":
			self.id = canvas.create_line(coords, fill=fill, smooth=smooth, width=1)
		elif self.type == "rectangle":
			self.id = canvas.create_rectangle(*coords, fill=fill, outline=fill)
