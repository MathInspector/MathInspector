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
from tkinter import ttk
from ..style import TAGS, Color
from ..util.config import BUTTON_RIGHT, BUILTIN_FUNCTION, BUILTIN_CLASS
from ..widget.menu import Menu
from ..console.builtin_print import builtin_print
import io, re, tokenize, keyword, builtins, inspect

RE_PY = {

	"orange_italic": r"^def (\w+)\s?\(((\w+(,\s?)?)+)\)",
	#"orange_italic": r"(\w+)\s?\(((\w+(,\s?)?)+)\)",
	# "orange_italic": r".([a-zA-Z0-9_]*)=(.*?)( |\n)*(,|\))",
	"green": r"(def {1,}(\w+))",
	"blue": r"((\w+)\()",
	"purple": r"((True|False|None))",
	"console_prompt": r"((>>>|\.\.\.))"
}

# REFACTOR - this is a good pattern, move this into style
DEFAULT_OPTS = {
	"foreground": Color.WHITE,
	"background": Color.BACKGROUND,
	"font": "Monospace 14",
	"insertbackground": Color.WHITE,
	"padx": 16,
	"pady": 8,
	"borderwidth": 0,
	"highlightthickness": 0,
	"selectbackground": Color.HIGHLIGHT,
	"inactiveselectbackground": Color.HIGHLIGHT_INACTIVE,
	"tabs": ("3c","4c", "5c"),
	"undo": True,
	"wrap": "word"
}


class Text(tk.Text):
	def __init__(self, parent, *args, readonly=False, has_scrollbar=False, **kwargs):
		opts = DEFAULT_OPTS.copy()
		opts.update(kwargs)
		tk.Text.__init__(self, parent, *args, **opts)

		if has_scrollbar:
			self.scrollbar = tk.Scrollbar(parent, command=self.yview)
			self.config(yscrollcommand=self.scrollbar.set)
			self.scrollbar.config(command=self.yview)
			# self.scrollbar.pack(side="right", fill="y")
			# self.bind("<<Scroll>>", self._on_scroll)

		for i in TAGS:
			self.tag_configure(i, **TAGS[i])

		if readonly:
			self.bind("<Key>", self._on_key)

		self.readonly = readonly
		self.hover_range = None

		self._orig = self._w + "_orig"
		self.tk.call("rename", self._w, self._orig)
		self.tk.createcommand(self._w, self._proxy)
		self.bind(BUTTON_RIGHT, self._on_button_right)
		self.menu = Menu(self)

	def _on_key(self, event):
		ctrl = (event.state & 0x4) != 0
		meta = (event.state & 0x8) != 0
		is_mod = ctrl or meta
		return None if is_mod and event.char == "c" else False if is_mod else "break"

	def insert(self, *args, syntax_highlight=False, **kwargs):
		idx = self.index(self.index(args[0]) + "-1c")
		linestart = self.index(idx + " linestart")
		super(Text, self).insert(*args, **kwargs)
		if syntax_highlight:
			self.syntax_highlight(linestart, idx + "+" + str(len(args[1])) + "c")


	def replace(self, pattern, tag=None, newtext=None, start="1.0", end="end"):
		current_index = "1.0"
		while True:
			content = self.get(current_index, end)
			match = re.compile(pattern, re.MULTILINE).search(content)
			if not match:
				break
			start_index=match.start()
			end_index=match.end()
			ind1 = current_index + "+" + str(start_index) + "c"
			ind2 = current_index + "+" + str(end_index) + "c"
			self.delete(ind1, ind2)
			replacement = newtext if newtext != None else match.group(1)
			# if pattern[-1] == "$":
			# 	replacement += "\n"
			self.insert(ind1, replacement, tag)
			current_index = self.index(ind1 + "+" + str(len(replacement)) + "c")


	def highlight(self, pattern, tag, start="1.0", end="end"):
		for match in re.compile(pattern, re.MULTILINE).finditer(self.get(start, end)):
			ind1 = self.index(self.index(start) + "+" + str(match.start(2)) + "c")
			ind2 = self.index(self.index(start) + "+" + str(match.end(2)) + "c")
			self.tag_add(tag, ind1, ind2)

	def syntax_highlight(self, start="1.0", end="end"):
		for i in TAGS:
			self.tag_remove(i, start, end)

		content = self.get(start, end)
		if not content: return

		try:
			for i in RE_PY:
				self.highlight(RE_PY[i], i, start, self.index(end))

			for typ, string, start_index, end_index, line in tokenize.generate_tokens(io.StringIO(content).readline):
				token = tokenize.tok_name[typ]

				ind1 = self.index(self.index(start) + "+" + str(start_index[0] - 1) + "l" + "+" + str(start_index[1]) + "c")
				ind2 = self.index(self.index(start) + "+" + str(end_index[0] - 1) + "l" + "+" + str(end_index[1]) + "c")

				if token == "NAME":
					if string in ["def", "clear", "app", "help", "plot", "class"]:
						self.tag_add("blue_italic", ind1, ind2)
					elif string in keyword.kwlist:
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

	def remove_selection(self):
		tag_ranges = self.tag_ranges("sel")
		if tag_ranges:
			self.tag_remove("sel", *tag_ranges)

	def _proxy(self, *args):
		try:
			cmd = (self._orig,) + args
			result = self.tk.call(cmd)
		except:
			return

		if args[0] in ("insert", "replace", "delete"):
			self.event_generate("<<Modify>>")

		if args[0:2] == ("yview", "scroll"):
			self.event_generate("<<Scroll>>")

		if args[0:3] == ("mark", "set", "insert"):
			self.event_generate("<<MarkSet>>")

		return result

	def _on_button_right(self, event):
		tag_ranges = self.tag_ranges("sel")
		if self.readonly:
			if tag_ranges:
				self.menu.show(event, [{
					"label": "Copy",
					"command": lambda: self.clipboard_append(self.get(*tag_ranges))
				}])
			return

		if tag_ranges:
			self.menu.show(event, [{
				"label": "Copy",
				"command": lambda: self.clipboard_append(self.get(*tag_ranges))
			}, {
				"label": "Paste",
				"command": lambda: self._on_paste(tag_ranges)
			}])
		else:
			self.menu.show(event, [{
				"label": "Paste",
				"command": lambda: self.insert("insert", self.clipboard_get())
			}])

	def _motion(self, event, tag):
		self.config(cursor="pointinghand")
		hover_range = self.tag_prevrange(tag, "@" + str(event.x) + "," + str(event.y))
		if not hover_range: return

		if self.hover_range and hover_range != self.hover_range:
			self.tag_remove(tag + "_hover", *self.hover_range)

		self.hover_range = hover_range
		content = self.get(*hover_range)
		if content:
			# print ("ddd", tag + "_hover", content)
			self.tag_add(tag + "_hover", *hover_range)

	def _leave(self, event, tag):
		self.config(cursor="")
		if self.hover_range:
			self.tag_remove(tag + "_hover", *self.hover_range)

	def get_tags(self, start, end):
	    index = start
	    tags = []
	    while self.compare(index, "<=", end):
	        tags.extend(self.tag_names(index))
	        index = self.index(f"{index}+1c")

	    return tuple(set(tags))
