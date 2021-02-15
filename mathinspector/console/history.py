"""
class that manages the command history feature, which can be accessed from the console by
using the up and down arrow keys.
"""
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
from .builtin_print import builtin_print

class History:
	def __init__(self, prompt):
		self.cmds = []
		self.prompt = prompt
		self.i = 0

	def toggle(self, num):
		self.i += num
		if self.i < 0:
			self.i = 0
			builtin_print("\a")
			return

		self.prompt.delete("1.5", "end")
		if self.i > len(self.cmds):
			self.i = len(self.cmds)
			builtin_print("\a")
		elif self.i < len(self.cmds):
			self.prompt.insert("1.5", self.cmds[self.i])

	def clear(self):
		self.cmds.clear()
		self.i = 0

	def append(self, obj):
		self.cmds.append(obj)
		self.i = len(self.cmds)

	def extend(self, *args):
		self.cmds.extend([i.rstrip() for i in args])
		self.i = len(self.cmds)

	def __repr__(self):
		return str(self.cmds)