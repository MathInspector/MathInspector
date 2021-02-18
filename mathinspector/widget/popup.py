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
from collections import OrderedDict
from ..style import Color
from .button import Button

OPTIONS = {
	"background": Color.BLACK,
	"padx": 12,
	"pady": 8
}

class Popup(tk.Toplevel):
	def __init__(self, app, params, callback, title="", header="", **kwargs):
		OPTIONS.update(kwargs)
		tk.Toplevel.__init__(self, app, **OPTIONS)
		self.app = app
		self.title(title)
		self.callback = callback

		if header:
			tk.Label(self,
				text=header,
				font="Montserrat 16 bold",
				foreground=Color.WHITE,
				background=Color.PURPLE,
				anchor="w",
				padx=8,
				pady=2
			).grid(row=0,column=0, columnspan=2, sticky="nsew", pady=4)

		self.params = OrderedDict()
		for i,val in enumerate(params):
			label = tk.Label(self, text=val["label"], font="Menlo 14", foreground=Color.WHITE, background=Color.BLACK)
			entry = tk.Entry(self, foreground=Color.BLACK, background=Color.VERY_LIGHT_GREY)

			if "value" in val:
				entry.insert("end", str(val["value"]))

			self.params[val["label"]] = entry
			label.grid(row=i+1, column=0, sticky="w", padx=2, pady=4)
			entry.grid(row=i+1, column=1, sticky="w", padx=2, pady=4)

		self.bind("<Return>", self._on_ok)
		self.bind("<Escape>", self._on_cancel)

		btn_area = tk.Frame(self, background=Color.BLACK)
		Button(btn_area, text="Cancel", command=self._on_cancel, width=8).grid(row=0, column=0, padx=8)
		Button(btn_area, text="OK", command=self._on_ok, width=8).grid(row=0, column=1, padx=8)
		btn_area.grid(row=i+2, columnspan=2, pady=12)


	def _on_ok(self, event=None):
		result = {}
		for i in self.params:
			try:
				temp = self.app.console.eval(self.params[i].get())
			except:
				temp = self.params[i].get()
			result[i] = temp
		self.callback(result)
		self.destroy()

	def _on_cancel(self, event=None):
		self.destroy()