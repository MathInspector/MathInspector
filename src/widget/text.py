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
from util import BUILTIN_CLASS, BUILTIN_FUNCTION
import style.syntax
import io, re, tokenize, keyword

class Text(tk.Text):
	def __init__(self, *args, background=Color.BACKGROUND, font="Monospace 14", insertbackground=Color.WHITE, padx=16, pady=8, **kwargs):
		tk.Text.__init__(self, *args,
			font=font,
			background=background,
			foreground=Color.WHITE,
			borderwidth=0, 
			highlightthickness=0, 			
			insertbackground=insertbackground,
			selectbackground=Color.HIGHLIGHT,
			inactiveselectbackground=Color.HIGHLIGHT_INACTIVE,
			padx=padx, 
			pady=pady,
			tabs=24,
			undo=True,
			wrap="word",
			**kwargs)
		
		for tag in style.syntax:
			self.tag_configure(tag, **style.syntax[tag])		

		self._orig = self._w + "_orig"
		self.tk.call("rename", self._w, self._orig)
		self.tk.createcommand(self._w, self._proxy)						

	def highlight(self, pattern, tag=None, start="1.0", end="end", newtext=None):
		current_index = self.index(start)
		newlines = 0
		iters = 0
		while True:
			content = self.get(start, end)
			match = re.compile(pattern, re.MULTILINE).search(content)
			if not match:
				break
			start=match.start()
			end=match.end()	
			ind1 = current_index + "+" + str(start) + "c"
			ind2 = current_index + "+" + str(start + len(match.group(1))) + "c"
			if newtext:
				self.delete(ind1, ind2)
				if pattern[-1] == "$":
					newtext += "\n"
					newlines_count = pattern.count(r"\n")
					newlines += 1 - newlines_count
				self.insert(ind1, newtext, tag)
			else:
				self.tag_add(tag, ind1, ind2)
			current_index = self.index(ind1 + "+" + str(start + len(newtext or match.group(1))) + "c")
			break
		
	def syntax_highlight(self, start, end):
		for tag in style.syntax:
			self.tag_remove(tag, start, end)

		content = self.get(start, end)
		if not content: return
		
		try:
			self.highlight(r"([a-zA-Z0-0_]*)\(", "blue", start, end)
			for typ, string, start_index, end_index, line in tokenize.generate_tokens(io.StringIO(content).readline):
				token = tokenize.tok_name[typ]

				ind1 = self.index(start) + "+" + str(start_index[1]) + "c"
				ind2 = self.index(start) + "+" + str(end_index[1]) + "c"

				if token == "NAME":
					if string in keyword.kwlist:
						self.tag_add("red", ind1, ind2)
					elif string in BUILTIN_FUNCTION:
						self.tag_add("blue", ind1, ind2)
					elif string in BUILTIN_CLASS:
						self.tag_add("blue_italic", ind1, ind2)
				elif token == "OP":
					if string in ["=", "*", "**"]:
						self.tag_add("red", ind1, ind2)
				elif token == "STRING":
					self.tag_add("yellow", ind1, ind2)
				elif token == "NUMBER":
					self.tag_add("purple", ind1, ind2)
				elif token == "COMMENT":
					self.tag_add("comment", ind1, ind2)
		except Exception as err:
			print (err)
			pass


	def _proxy(self, *args):
		try:
			cmd = (self._orig,) + args
			result = self.tk.call(cmd)
		except:
			return

		if args[0] in ("insert", "replace", "delete"):
			self.event_generate("<<Modify>>")

		if args[0:3] == ("mark", "set", "insert"):
			self.event_generate("<<MarkSet>>", when="tail")		

		return result             
