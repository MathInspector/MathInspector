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
import keyword, platform
from .history import History
from .builtin_print import builtin_print
from .autocomplete import AutoComplete
from ..util.config import FONT, PROMPT_FONTSIZE as FONTSIZE
from ..widget import Text
from ..style import Color

class Prompt(Text):
	def __init__(self, console, frame):
		Text.__init__(self, frame,
			background=Color.DARK_BLACK,
			font=FONT,
			padx=0,
			pady=0,
			height=2)

		self.console = console
		self.is_on_bottom = False

		self.autocomplete = AutoComplete(self)
		self.history = History(self)
		self.yscroll = 1.0

		self.bind("<Key>", self._on_key)
		self.bind("<<Modify>>", self.on_modify)
		self.bind("<<MarkSet>>", self.on_mark_set)
		self.bind("<<Selection>>", self.on_text_selection)
		self.bind("<FocusIn>", self.on_focus_in)
		self.console.bind("<<Scroll>>", self._on_scroll_log)
		self.lift()

	def __call__(self):
		self.delete("1.0", "end")
		self.insert("end", "...  " if self.console.buffer else ">>>  ", "console_prompt")
		self.console.see("end")
		self.move()
		self.focus()
		self.edit_reset() # NOTE: this resets the tkinter undo stack

	def get(self, start="1.5", end="end-1c"):
		return super(Prompt, self).get(start, end)

	def _on_key(self, event):
		self.console.remove_selection()
		if event.keysym == "Return":
			self.push(self.get())
			return "break"

		if event.keysym == "Tab" and self.get().strip():
			self.autocomplete()
			return "break"

		if event.keysym in ("Up", "Down"):
			self.history.toggle(-1 if event.keysym == "Up" else +1)
			return "break"

		line, col = self.index("insert").split(".")
		if event.keysym in ("BackSpace", "Left"):
			selected_range = self.tag_ranges("sel")
			if selected_range and int(col) == 5 and event.keysym == "BackSpace":
				self.delete(*selected_range)
				return "break"
			elif int(col) < 6:
				builtin_print("\a")
				return "break"

		tag_ranges = self.tag_ranges("sel")
		if tag_ranges and event.keysym in ("parenleft", "quotedbl", "quoteright", "bracketleft"):
			content = self.get(*tag_ranges)
			self.delete(*tag_ranges)

			if event.keysym == "parenleft":
				self.insert(tag_ranges[0], "(" + content + ")")
			elif event.keysym == "quotedbl":
				self.insert(tag_ranges[0], "\"" + content + "\"")
			elif event.keysym == "quoteright":
				self.insert(tag_ranges[0], "'" + content + "'")
			elif event.keysym == "bracketleft":
				self.insert(tag_ranges[0], "[" + content + "]")
			return "break"

		ctrl = (event.state & 0x4) != 0
		meta = (event.state & 0x8) != 0
		is_mod = (ctrl or meta) and platform.system() != "Windows"
		if is_mod:
			if event.char == "v":
				return self._on_paste()

			if event.char == "d":
				self.tag_add("sel", "insert wordstart", "insert wordend")
				return "break"

		## TODO - reenable this, designed to emulate the ipython ? functionality
		# if event.keysym == "question":
		# 	try:
		# 		obj = self.console.eval(self.get())
		# 	except:
		# 		builtin_print("\a")
		# 		return "break"

		# 	if help.getobj(obj):
		# 		help(obj)
		# 	else:
		# 		builtin_print("\a")
		# 	return "break"

	def push(self, s):
		if s or not self.console.buffer:
			if self.console.get("1.0", "end").strip() and not self.console.buffer:
				self.console.insert("end", "\n")
			self.console.insert("end", "...  " if self.console.buffer else ">>>  ", "console_prompt")
			self.console.insert("end", s + "\n", syntax_highlight=True)
		self.console.push(s)

	def on_configure_log(self, event):
		self.console.config(height=self.console.frame.winfo_height() - 2*FONTSIZE)
		if self.is_on_bottom and not self.on_bottom():
			self.is_on_bottom = False

		if self.winfo_ismapped() and self.console.yview() != 1.0:
			self.is_on_bottom = False
		self.move()

	def _on_scroll_log(self, event):
		if not self.is_on_bottom: return

		yscroll = self.console.yview()[1]
		if yscroll < 1:
			self.pack_forget()
		elif not self.winfo_ismapped():
			self.is_on_bottom = False
			self.move()
		self.yscroll = yscroll

	def move(self, event=None):
		if self.is_on_bottom:
			return

		if self.on_bottom():
			self.is_on_bottom = True
			self.pack(side="bottom", fill="x", expand=True, before=self.console)
			self.config(height=2)
			# self.console.pack_forget()
			self.console.pack(fill="both", expand=True)
			self.console.config(height=self.console.winfo_height()/FONTSIZE)
			self.console.see("end")
		else:
			self.place(x=0, y=FONTSIZE*self.linecount(), width=self.console.winfo_width())

	def on_bottom(self):
		count = self.linecount()
		if self.is_on_bottom:
			return FONTSIZE*(1+count) > self.console.frame.winfo_height()
		return FONTSIZE*(1+count) > self.console.winfo_height()

	def linecount(self):
		count = self.console.count("1.0", "end", "displaylines")[0]
		if count == 1:
			return 0
		return count

	def on_modify(self, event):
		self.syntax_highlight("end-1c linestart+5c", "end-1c")

	def on_mark_set(self, event):
		line, col = self.index("insert").split(".")

		if int(col) < 5:
			self.mark_set("insert", line + ".5")

	def on_text_selection(self, event):
		selected = self.tag_ranges("sel")
		if len(selected) == 0: return

		line, col = str(selected[0]).split(".")
		endline = self.index("end-1c").split(".")[0]
		if line == endline and int(col) < 5:
			self.tag_remove("sel", selected[0], str(line) + ".5")

	def _on_paste(self, content=None):
		content = content or self.clipboard_get()
		if not content or "\n" not in content: return

		tag_ranges = self.tag_ranges("sel")
		if tag_ranges:
			self.delete(*tag_ranges)

		self.console.write(">>>  " + content, syntax_highlight=True)
		try:
			self.console.exec(content)
		except:
			self.console.showtraceback()
		return "break"

	def on_focus_in(self, event):
		self.console.remove_selection()

	def _on_button_right(self, event):
		tag_ranges = self.tag_ranges("sel")
		items = []
		if tag_ranges:
			items.extend([{
				"label": "Copy",
				"command": lambda: self.clipboard_append(self.get(*tag_ranges))
			}, {
				"label": "Paste",
				"command": self._on_paste
			}])
		else:
			items.append({
				"label": "Paste",
				"command": self._on_paste
			})

		items.extend([{
			"label": "Clear Log",
			"command": clear
		}, {
			"label": "Keyword List",
			"menu": [{
				"label": str(i),
				"command": lambda key=i: self.insert("insert", key)
			} for i in keyword.kwlist]
		}])

		self.menu.show(event, items)
