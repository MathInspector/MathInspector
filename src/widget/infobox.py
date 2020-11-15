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
from settings import Color, Log

class InfoBox(tk.Frame):
	def __init__(self, parent, *args, hide_callback=None, **kwargs):		
		if "height" not in kwargs:
			kwargs["height"] = 40
		
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.parent = parent
		self.hide_callback = hide_callback
		self.title = tk.Label(self, font="Monospace 16 bold italic", background=Color.RED, foreground=Color.BLUE)
		self.message = tk.Label(self, font="Nunito 16", background=Color.RED, foreground=Color.WHITE)
		self.title.pack(side="left", padx=32)
		self.message.pack(side="left")
		self.closebtn = tk.Label(self, 
			text="×", 
			font="Monospace 15 bold",
			background=Color.GREY, 
			foreground=Color.DARK_GREY,
			padx=4, 
			pady=4
		)
		self.closebtn.pack(side="right")
		self.closebtn.bind("<Enter>", self._on_enter)
		self.closebtn.bind("<Leave>", self._on_leave)
		self.closebtn.bind("<Button-1>", lambda event: self.hide())

	def show(self, title=None, text=""):
		if title == None:
			return self.pack_forget()
		
		if isinstance(title, Exception):
			text = title
			title = "Error"
			print ("\a")
			
		if isinstance(text, Exception):
			bg = Color.RED
		else:
			bg = Color.VERY_DARK_GREY

		self.config(background=bg)
		self.title.config(text=title, background=bg)
		self.message.config(text=str(text), background=bg)
		self.closebtn.config(background=bg)
		# self.config(width=self.parent.winfo_width())
		self.lift()
		self.place(x=4,y=self.parent.winfo_height() - 36, width=self.parent.winfo_width() - 8)
		self.after(Log.MESSAGE_TIMEOUT, self.hide)


	def hide(self):
		self.place_forget()
		if self.hide_callback:
			self.hide_callback()

	def _on_enter(self, event):
		self.closebtn.config(foreground=Color.WHITE)
	
	def _on_leave(self, event):
		self.closebtn.config(foreground=Color.DARK_GREY)

