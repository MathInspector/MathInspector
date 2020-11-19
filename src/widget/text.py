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
from style import TAGS, RE_PY
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
		
		for i in TAGS:
			self.tag_configure(i, **TAGS[i])		

		self._orig = self._w + "_orig"
		self.tk.call("rename", self._w, self._orig)
		self.tk.createcommand(self._w, self._proxy)						

	def highlight(self, pattern, tag=None, start="1.0", end="end", newtext=None):
		for match in re.compile(pattern, re.MULTILINE).finditer(self.get(start, end)):
			ind1 = self.index(start) + "+" + str(match.start()) + "c"
			ind2 = self.index(start) + "+" + str(match.start() + len(match.group(1))) + "c"
			if newtext:
				# deleting and inserting with different lengths is breaking the find_iter indicies
				self.delete(ind1, ind2)
				self.insert(ind1, newtext)
				ind2 = 	self.index(start) + "+" + str(match.start() + len(newtext)) + "c"
				ccc = self.get(ind1,ind2)
				print (ind1,ind2, "content", ccc)			
			self.tag_add(tag, ind1, ind2)
		
	def syntax_highlight(self, start="1.0", end="end"):
		for i in TAGS:
			self.tag_remove(i, start, end)

		content = self.get(start, end)
		if not content: return
		
		try:
			for i in RE_PY:
				self.highlight(RE_PY[i], i, start, end)
			
			for typ, string, start_index, end_index, line in tokenize.generate_tokens(io.StringIO(content).readline):
				token = tokenize.tok_name[typ]

				ind1 = self.index(start) + "+" + str(start_index[0] - 1) + "l" + "+" + str(start_index[1]) + "c"
				ind2 = self.index(start) + "+" + str(end_index[0] - 1) + "l" + "+" + str(end_index[1]) + "c"

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
