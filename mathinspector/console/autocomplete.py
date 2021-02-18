"""
class which manages tab autocomplete and integrates with the rest of the app.
"""
"""
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
import builtins, re
from functools import reduce
from ..util import BUILTIN_PKGS, BUILTIN_FUNCTION, BUILTIN_CLASS, INSTALLED_PKGS, KEYWORD_LIST
from .builtin_print import builtin_print

RE_WORD = re.compile(r"[() ]")

class AutoComplete():
	def __init__(self, prompt):
		self.prompt = prompt
		self.console = prompt.console
		self.tabcount = 0

	def __call__(self):
		content = self.prompt.get().strip()
		self.tabcount += 1
		s = RE_WORD.split(content)[-1] #REFACTOR - split to also split by any nonword characters (besides .) like paren
		query = s.rsplit(".", 1)
		is_import = (content[:7] == "import ")
		if is_import:
			choices = [i for i in self.console.app.modules] + BUILTIN_PKGS + INSTALLED_PKGS
		elif s.count("."):
			choices = self.console.eval("dir(" + query[0] + ") + " + "dir(" + str(query[0].__class__.__name__) + ")")
		else:
			self.console.synclocals()
			choices = [i for i in self.console.locals] + BUILTIN_FUNCTION + BUILTIN_CLASS + KEYWORD_LIST

		if not choices:
			builtin_print("\a")
			return

		result = []
		for j in choices:
			word = content[7:] if is_import else query[0] if len(query) == 1 else query[1]
			if j[:len(word)] == word:
				result.append(j)

		if not result:
			builtin_print("\a")
			return

		common = findcommonstart(result)

		if len(result) == 1:
			self.prompt.insert("end", result[0][len(word):])
			self.tabcount = 0
		elif word[:len(common)] != common:
			self.prompt.insert("end", common[len(word):])
		elif self.tabcount > 0:
			self.console.write("\n" + "        ".join(result) + "\n\n")
			self.prompt.move()
			self.tabcount = 0
		else:
			builtin_print("\a")
			self.tabcount += 1

def getcommonletters(strlist):
    return ''.join([x[0] for x in zip(*strlist) if reduce(lambda a,b:(a == b) and a or None,x)])

def findcommonstart(strlist):
    strlist = strlist[:]
    prev = None
    while True:
        common = getcommonletters(strlist)
        if common == prev:
            break
        strlist.append(common)
        prev = common

    return getcommonletters(strlist)