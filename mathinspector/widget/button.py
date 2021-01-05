import tkinter as tk
from style import Color

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
