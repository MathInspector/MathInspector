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
import inspect, re, os, webbrowser
from .tags import DOC_TAGS
from ..widget import Notebook, Treeview, Menu, Text
from ..style import Color, getimage
from ..util.argspec import argspec
from ..util.docscrape import FunctionDoc
from ..util.common import open_editor, classname
from ..util.config import EXCLUDED_MODULES, BUTTON_RIGHT, BUTTON_RELEASE_RIGHT, INSTALLED_PKGS, BUILTIN_PKGS, DOC_FONT
from .show_functiondoc import show_functiondoc
from .show_textfile import show_textfile
from .show_markdown import show_markdown
from numpy import ufunc

class Doc(tk.Frame):
	def __init__(self, parent, obj=None, title=None, has_sidebar=None, run_code=None, **kwargs):
		tk.Frame.__init__(self, parent, background=Color.BLACK)
		self.parent = parent
		self.paned_window = ttk.PanedWindow(self, orient="horizontal")
		self.title = title

		frame = tk.Frame(self, background=Color.BACKGROUND)
		self.nav = Text(frame, padx=16, height=2, readonly=True, font=DOC_FONT, cursor="arrow", insertbackground=Color.BACKGROUND, selectbackground=Color.BACKGROUND)
		self.text = Text(frame, readonly=True, has_scrollbar=False, font=DOC_FONT, cursor="arrow", insertbackground=Color.BACKGROUND)

		self.notebook = Notebook(self)
		self.nav_count = 0

		self.tree = Treeview(self, drag=False)

		self.has_sidebar = (has_sidebar or inspect.ismodule(obj) or inspect.isclass(obj))
		self.run_code = run_code
		if self.has_sidebar:
			self.notebook.add("tree", self.tree)
			self.paned_window.add(self.notebook.frame)
			self.nav.pack(side="top", fill="x")

		self.text.pack(side="bottom", fill="both", expand=True)

		self.paned_window.add(frame)
		self.paned_window.pack(side="left", fill="both", expand=True)

		self.menu = Menu(self)
		self.functions = {}
		self.builtins = {}
		self.classes = {}
		self.submodules = {}

		self.parent.bind("<Escape>", lambda event: parent.destroy())
		self.text.bind("<Escape>", lambda event: parent.destroy())

		self.parent.bind("<Key>", self._on_key)
		self.text.bind("<Key>", self._on_key)

		self.tree.bind(BUTTON_RIGHT, self._on_button_right)

		self.tree.tag_bind("submodule", "<ButtonRelease-1>", self._on_button_release_1)
		self.tree.tag_bind("class", "<ButtonRelease-1>", self._on_button_release_1)
		self.tree.bind("<<TreeviewSelect>>", self._on_select)

		for i in ("link_url", "doc_link", "code_sample", "submodule"):
			self.text.tag_bind(i, "<Motion>", lambda event, key=i: self.text._motion(event, key))
			self.text.tag_bind(i, "<Leave>", lambda event, key=i: self.text._leave(event, key))
			self.text.tag_bind(i, "<Button-1>", lambda event, key=i: self._click(event, key))

		for i in ("root", "module_nav"):
			self.nav.tag_bind(i, "<Motion>", lambda event, key=i: self.nav._motion(event, key))
			self.nav.tag_bind(i, "<Leave>", lambda event, key=i: self.nav._leave(event, key))
			self.nav.tag_bind(i, "<Button-1>", lambda event, key=i: self._click_nav(event, key))

		for i in DOC_TAGS:
			self.nav.tag_configure(i, **DOC_TAGS[i])
			self.text.tag_configure(i, **DOC_TAGS[i])

		self.objects = []
		if obj:
			self.show(obj)

	def show(self, obj, clear_nav=True, display_only=False):
		self.obj = obj

		if display_only:
			pass
		elif clear_nav:
			name = self.getname(obj)
			self.nav.delete("1.0", "end")
			self.nav.insert("end", name, ("root", "basepath"))
			self.rootmodule = self.obj
			self.nav_count = 0
			self.objects.clear()
		else:
			name = self.getname(obj).split(".")[-1]
			tag_ranges = self.nav.tag_ranges("subpath")
			if tag_ranges:
				self.nav.delete(*tag_ranges)
			self.nav.insert("end", " > ", ("blue", "nav_count="+str(self.nav_count)))
			self.nav.insert("end", name, ("module_nav", "basepath", "nav_count="+str(len(self.objects))))
			self.objects.append(obj)

		self.clear()

		if isinstance(obj, str) and os.path.isfile(obj):
			content = open(obj).read()
			name, ext = name_ext(obj)
			if ext == ".md":
				# TODO - use `show_markdown(self.text, content)` instead
				show_textfile(self.text, content)
			else:
				show_textfile(self.text, content)
			return

		for i in dir(self.obj):
			attr = getattr(self.obj, i)
			if i[0] == "_":
				pass
			elif inspect.isclass(attr):
				self.classes[i] = attr
			elif inspect.ismodule(attr):# and i not in INSTALLED_PKGS + BUILTIN_PKGS + EXCLUDED_MODULES + ["os", "sys"]:
				self.submodules[i] = attr
			elif inspect.isfunction(attr):
				self.functions[i] = attr
			elif callable(attr):
				self.builtins[i] = attr
			else:
				pass

		if self.classes:
			classes = self.tree.insert("", "end", text="classes", open=True)
			for k in self.classes:
				temp = self.tree.insert(classes, "end", k, text=k, tags="class")

		if self.builtins:
			if inspect.isclass(self.obj):
				parent = self.tree.insert("", "end", text="methods", open=True)
			else:
				parent = self.tree.insert("", "end", text="builtins", open=True)
			for j in self.builtins:
				self.tree.insert(parent, "end", j, text=j)

		if self.functions:
			functions = self.tree.insert("", "end", text="functions", open=True)
			for j in self.functions:
				self.tree.insert(functions, "end", j, text=j, open=True)

		if self.submodules:
			for i in self.submodules:
				self.tree.insert("", "end", i, image=getimage(".py"), text="      " + i, tags="submodule")

		if self.has_sidebar:
			if not self.builtins and not self.functions and not self.classes and not self.submodules:
				if self.paned_window.winfo_width() > 1:
					self.paned_window.sashpos(0,0)
				else:
					self.paned_window.bind("<Configure>", lambda event: self.paned_window.sashpos(0,0))
			elif self.paned_window.sashpos(0) < 20:
				self.paned_window.sashpos(0,220)

		self.display_doc(obj)

	def display_doc(self, obj):
		if inspect.ismodule(obj) or inspect.isclass(obj):
			show_textfile(self.text, inspect.getdoc(obj))
			return

		try:
			doc = FunctionDoc(obj)
		except Exception:
			show_textfile(self.text, inspect.getdoc(obj))
			# self.toggle_scrollbar()
			return
		show_functiondoc(self.text, doc, classname(obj))
		# self.toggle_scrollbar()

	# REFACTOR - need a better system for scrollbars in general
	def toggle_scrollbar(self):
		self.doc.delete("1.0", "end")
		if self.text.yview()[1] == 1.0:
			self.text.scrollbar.pack_forget()
		elif not self.text.scrollbar.winfo_ismapped():
			if self.has_sidebar:
				self.text.scrollbar.pack(before=self.nav, side="right", fill="y")
			else:
				self.text.scrollbar.pack(before=self.text, side="right", fill="y")

	def getname(self, obj):
		return self.title if self.title else obj.__name__ if hasattr(obj, "__name__") else obj.__class__.__name__

	def clear(self):
		self.text.delete("1.0", "end")

		self.builtins.clear()
		self.functions.clear()
		self.classes.clear()
		self.submodules.clear()

		for i in self.tree.get_children():
			self.tree.delete(i)

	def _on_select(self, event):
		try:
			key = self.tree.selection()[0]
		except IndexError:
			return
		if not hasattr(self.obj, key): return

		obj = getattr(self.obj, key)
		self.text.delete("1.0", "end")
		tag_ranges = self.nav.tag_ranges("subpath")
		if tag_ranges:
			self.nav.delete(*tag_ranges)
		self.nav.insert("end", " > ", ("blue", "subpath"))
		self.nav.insert("end", key, ("module_nav", "subpath", "nav_count="+str(self.nav_count)))
		self.display_doc(obj)

	def _on_button_release_1(self, event):
		key = self.tree.selection()[0]
		self.show(getattr(self.obj, key), clear_nav=False)

	def _on_button_right(self, event):
		name = self.tree.identify_row(event.y)
		obj = getattr(self.obj, name)

		try:
			file = inspect.getsourcefile(obj)
		except:
			file = None

		if file:
			self.menu.show(event, [{
				"label": "View Source Code",
				"command": lambda: open_editor(file)
			}])

	def _click(self, event, tag):
		if tag == "link_url":
			webbrowser.open(self.text.get(*self.text.hover_range), new=2)
		elif tag == "doc_link":
			doc_link = self.text.get(*self.text.hover_range)
			obj = getattr(__import__(self.obj.__class__.__module__), doc_link)
			self.show(obj)
		elif tag == "code_sample" and self.run_code:
			match = re.findall(r"(>>>|\.\.\.) {0,2}(\t{0,}.*\n)", self.text.get(*self.text.hover_range))
			if not match: return
			for command in match:
				self.run_code(command[1])

	def _click_nav(self, event, tag):
		if tag == "root":
			self.show(self.rootmodule)
		elif tag == "module_nav":
			tags = self.nav.get_tags(*self.nav.hover_range)
			nav_count = None
			for i in tags:
				if i[:10] == "nav_count=":
					nav_count = int(i[10:])
					break
			if nav_count is None: return

			self.nav.delete(self.nav.hover_range[1], "end")
			self.show(self.objects[nav_count], display_only=True)


	def _on_key(self, event):
		ctrl = (event.state & 0x4) != 0
		meta = (event.state & 0x8) != 0
		is_mod = ctrl or meta
		if is_mod and event.char == "w":
			return self.parent.destroy()
		return self.text._on_key(event)
