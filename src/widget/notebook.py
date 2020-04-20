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
	def __init__(self, parent, onchangetab=None, expandtabs=False, tabbackground=Color.GREY, 
			labels=True, is_draggable=False, *args, **kwargs):
		
		if "background" not in kwargs:
			kwargs["background"] = Color.BACKGROUND
		
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.nav = tk.Frame(self, background=tabbackground, height=32)
		self.notebook = ttk.Notebook(self)
		self.index = self.notebook.index
		self.tabs = {}
		self.selected_tab = None
		self.packargs = {"fill":"x", "expand":True, "side":"left"} if expandtabs else {"side":"left"}
		self.haslabels = labels
		self.drag = {
			"tab": None,
			"start_position": None
		} if is_draggable else None
		if labels:	
			self.nav.pack(fill='x', expand=False)
		
		if not labels:
			tk.Label(self, background=Color.BLACK, height=1, font="Monospace 1").pack(side="top", fill="both")
			self.config(highlightthickness=4, highlightbackground=Color.BLACK)

		self.notebook.pack(fill='both', expand=True)
		self.onchangetab = onchangetab
		self.notebook.bind('<<NotebookTabChanged>>', self._on_changetab)

	def add(self, name, widget,  **kwargs):		
		self.notebook.add(widget)
		tab_id = self.notebook.tabs()[-1]
		if hasattr(widget, "label"):
			tab = widget.label
		else:
			tab = NotebookTab(self, name, len(self.tabs), self.packargs, **kwargs)
		self.tabs[tab_id] = tab
		tab.label.bind("<Button-1>", lambda event: self.notebook.select(tab_id))
		if self.drag:
			tab.label.bind("<B1-Motion>", lambda event: self._on_b1_motion(event, tab))
			tab.label.bind("<ButtonRelease-1>", lambda event: self._on_button_release_1(event, tab))

		if hasattr(widget, "label"):
			widget.label = self.tabs[tab_id]
		
		if self.tabs[tab_id].closebtn:
			self.tabs[tab_id].closebtn.bind("<Button-1>", lambda event: self.close(tab_id))
		
		if self.notebook.select() == tab_id and self.haslabels:
			self.tabs[tab_id].select()

		return tab_id

	def tab(self, tab_id=None, filepath=None):		
		if filepath:
			for tab_id in self.notebook.tabs():
				if self.tab(tab_id).filepath == filepath:
					return self.tab(tab_id)
			return None		
		return self.notebook.nametowidget(tab_id or self.notebook.select())

	def tab_id(self, attr):
		for tab_id in self.notebook.tabs():
			tab = self.tab(tab_id)
			if hasattr(tab, attr[0]) and getattr(tab, attr[0]) == attr[1]:
				return tab_id
		return None		

	def close(self, tab_id):
		self.tabs[tab_id].destroy()
		self.notebook.forget(tab_id)
		if self.drag:
			for j in self.tabs:
				if self.tabs[j].index > self.tabs[tab_id].index:
					self.tabs[j].set_index(self.tabs[j].index - 1)
		del self.tabs[tab_id]


	def _on_changetab(self, event):
		tab_id = self.notebook.select()
		if tab_id and self.haslabels:
			self.tabs[tab_id].select()
			selected = self.notebook.select()
			if selected and selected != tab_id:
				self.tabs[selected].unselect()

			for i in self.tabs:
				if i == tab_id:
					self.notebook.select(i)
				elif i in self.tabs:
					self.tabs[i].unselect()
		
		if self.onchangetab:
			self.onchangetab()

	def _on_b1_motion(self, event, tab):
		if not self.drag["tab"]:
			self.drag["tab"] = tab
			self.drag["start_position"] = event.x
			tab.lift()

		x = self.nav.winfo_pointerx() - self.nav.winfo_rootx() - self.drag["start_position"]
		position = tab.winfo_rootx() - self.nav.winfo_rootx()
		width = tab.winfo_width()
		new_index = round(position/width)
		max_index = width * len(self.tabs)
		tab.place(x=x)
		if new_index != tab.index and 0 <= new_index < max_index:
			for i in self.tabs:
				if self.tabs[i].index == new_index:
					self.tabs[i].set_index(tab.index)
					tab.index = new_index
					break			

	def _on_button_release_1(self, event, tab):
		if self.drag:
			self.drag["tab"] = None
			position = tab.winfo_rootx() - self.nav.winfo_rootx()
			width = tab.winfo_width()
			maxwidth = (len(self.tabs) - 1)*width
			# tab.place_forget()
			tab.place(x=min(round(position/width) * width, maxwidth))
			# tab.pack(side="left")





