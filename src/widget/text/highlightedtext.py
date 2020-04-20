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
import style.syntax
import io, re, tokenize, builtins, keyword, inspect

BUILTIN_CLASS = [i for i in dir(builtins) if inspect.isclass( getattr(builtins, i) )]
BUILTIN_FUNCTION = [i for i in dir(builtins) if not inspect.isclass( getattr(builtins, i) )]
CUSTOM_KEYWORD = ["self"]

RE_PY = {   
	"orange_italic": r"(\w+)=(.*?)( |\n)*(,|\))",
	"comment": r"(?s)('''.*?''')",
	"green": r"def {1,}(\w+)\(",
	"blue": r"(\w+)\(",
}

DEFAULT_STYLE = {
	"font": 'Monospace 14',
	"bg": Color.BACKGROUND,
	"foreground": Color.WHITE,
	"borderwidth": 0, 
	"highlightthickness": 0, 			
	"insertbackground": Color.WHITE,
	"selectbackground": Color.HIGHLIGHT,
	"inactiveselectbackground": Color.HIGHLIGHT_INACTIVE,
	"padx": 16, 
	"pady": 8,
	"tabs": 24,
	"undo": True,
	"wrap": "word"	
}

def get_coordinate(start,end,string):
	srow=string[:start].count('\n')+1 # starting row
	scolsplitlines=string[:start].split('\n')
	if len(scolsplitlines)!=0:
		scolsplitlines=scolsplitlines[len(scolsplitlines)-1]
	scol=len(scolsplitlines)# Ending Column
	lrow=string[:end+1].count('\n')+1
	lcolsplitlines=string[:end].split('\n')
	if len(lcolsplitlines)!=0:
		lcolsplitlines=lcolsplitlines[len(lcolsplitlines)-1]
	lcol=len(lcolsplitlines)+1# Ending Column
	
	return '{}.{}'.format(srow, scol),'{}.{}'.format(lrow, lcol)#, (lrow, lcol)

def increment_index(ind, amount):
	line, col = ind.rsplit('.', 1)
	return '{}.{}'.format(str(int(line) + amount), col)

class HighlightedText(tk.Text):
	def __init__(self, *args, syntax=".py", **kwargs):
		opts = DEFAULT_STYLE.copy()
		opts.update(kwargs)
		tk.Text.__init__(self, *args, **opts)
		self.set_syntax(syntax)
		self.spam_control = False

	def set_syntax(self, syntax):
		self.syntax = syntax
		if syntax == ".py":
			for tag in style.syntax:
				self.tag_configure(tag, **style.syntax[tag])		

	def get(self, start="1.0", stop="end", *args, **kwargs):
		return super(HighlightedText, self).get(start, stop, *args, **kwargs)

	def delete(self, start="1.0", stop="end", *args, **kwargs):
		return super(HighlightedText, self).delete(start, stop, *args, **kwargs)

	def index_boundaries(self):
		return self.index("@0,0"), self.index("@0," + str(self.winfo_height()))

	def replace(self, pattern, tag=None, newtext=None, start="1.0", end="end"):
		current_index = "1.0"
		newlines = 0
		iters = 0
		# BUG - make this a while loop where the content=self.get(new_ind, "end")
		while True:
			content = self.get(current_index, "end")
			match = re.compile(pattern, re.MULTILINE).search(content)
			if not match:
				break
			start=match.start()
			end=match.end()	
			ind1,ind2 = get_coordinate(start,end-1,content)
			# ind1 = increment_index(ind1, newlines)
			# ind2 = increment_index(ind2, newlines)
			ind1 = current_index + "+" + str(start) + "c"
			ind2 = current_index + "+" + str(start + len(match.group(0))) + "c"
			self.delete(ind1, ind2)
			replacement = newtext or match.group(1)
			if pattern[-1] == "$":
				replacement += "\n"
				newlines_count = pattern.count(r"\n")
				newlines += 1 - newlines_count
			self.insert(ind1, replacement, tag)
			current_index = self.index(ind1 + "+" + str(start + len(replacement)) + "c")
			break
	
	def highlight(self, pattern, tag, start="1.0", end="end"):
		content = self.get(start, end)
		for i in re.compile(pattern).finditer(content):
			idx = 1 if i.groups() else 0		
			start=i.start(idx)
			end=i.end(idx)

			ind1,ind2 = get_coordinate(start,end-1,content)
			self.tag_add(tag, ind1, ind2)
			if tag == "sel":
				self.mark_set("insert", ind2)

	"""
	Unfortunately this is very slow, looking into this the reason is that tokenzing
	on every single key press is a little crazy.  Without any optimizations its never going to be fast enough

	I really like the generality of the tokenization approach, but, it needs to be run in a background thread
	and complimented with a small amount of manual parsing which is very fast.  

	it would be nice to just have it be as fast as in sublime text tho!  I guess they dont tokenize at all

	geez - doing a text editor is a lot of work!! its so important for this tho .. plus its kind of a cool project and very general programming thing
	

	---***--- NEED TO FULLY SUPPORT ANY EXTERNAL TEXT EDITOR ---***---
	can use watch on the file and if there is an error display it in math inspector
	or maybe build a plugin for sublime text that can populate the error in there, thats a nice idea too!
	but I do need to get away from the in app editor, its just too much work to recreate an entire text editor
	when there is no good reason for it.  meh, maybe can leave since i took it so far for now
	

	"""
	def syntax_highlight(self):
		if self.spam_control: return
		self.spam_control = True
		for tag in style.syntax:
			self.tag_remove(tag,"1.0","end")

		content = self.get()
		try:
			for typ, string, start, end, line in tokenize.generate_tokens(io.StringIO(content).readline):
				token = tokenize.tok_name[typ]
				ind1 = "{}.{}".format(*start)
				ind2 = "{}.{}".format(*end)
				# can use this highlight fn args in orange
				if token == "NAME":
					if string in keyword.kwlist:
						self.tag_add("red", ind1, ind2)
					elif string in BUILTIN_FUNCTION:
						self.tag_add("blue", ind1, ind2)
					elif string in BUILTIN_CLASS:
						self.tag_add("blue_italic", ind1, ind2)
					elif string in CUSTOM_KEYWORD:
						self.tag_add("orange_italic", ind1, ind2)
				elif token == "OP":
					if string in ["=", "*", "**"]:
						self.tag_add("red", ind1, ind2)
				elif token == "STRING":
					self.tag_add("yellow", ind1, ind2)
				elif token == "NUMBER":
					self.tag_add("purple", ind1, ind2)
				elif token == "COMMENT":
					self.tag_add("comment", ind1, ind2)
		except Exception as e:
			print (e)
			pass

		for tag in RE_PY:
			self.highlight(RE_PY[tag], tag, *self.index_boundaries())

		self.after(250, self.toggle_spam_control)

	def toggle_spam_control(self):
		self.spam_control = False
