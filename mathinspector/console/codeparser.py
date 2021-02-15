"""
Used for preprocessing and post-processing commands strings in order to perform any updates to the
various views throughout the app which are not captured by other methods.
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
import ast
from ..util import binop

class CodeParser(ast.NodeVisitor):
	def __init__(self, app):
		ast.NodeVisitor.__init__(self)
		self.app = app
		self.call_visitor = CallVisitor(app)
		self.assign_visitor = AssignVisitor(app)

	def preprocess(self, source):
		try:
			tree = ast.parse(source)
		except:
			return

		self.call_visitor.visit(tree)
		return tree

	def postprocess(self, source):
		try:
			tree = ast.parse(source)
		except:
			return

		## NOTE: the reason for removing the assign visitor is to ensure the math inspector interpreter
		##			always exec's all sequences of command strings, and produces the same output,
		##			exactly as would occur when using the python command line interpreter
		# self.assign_visitor.visit(tree)  ## TODO - add this as a toggle option in the main menu, default is turned off
		return tree

class CallVisitor(ast.NodeVisitor):
	def __init__(self, app):
		ast.NodeVisitor.__init__(self)
		self.app = app

	def visit_Call(self, node):
		if isinstance(node.func, ast.Name) and node.func.id in self.app.node:
			item = self.app.node[node.func.id]
			for i, val in enumerate(node.args):
				if item:
					if len(item.argspec[0]) > i:
						argname = item.argspec[0][i]
						attr = item.args
					elif len(item.argspec[1]) > 0:
						argname = list(item.kwargs.store.items())[i - len(item.argspec[0])][0]
						attr = item.kwargs
						item.opts["show_kwargs"] = True
					else:
						return

				if isinstance(val, ast.Name):
					if val.id in self.app.node:
						attr[argname] = self.app.node[val.id]
				elif isinstance(val, ast.Num):
					attr[argname] = val.n
				elif isinstance(val, ast.Str):
					attr[argname] = val.s
				elif (isinstance(val, ast.BinOp)
					and isinstance(val.left, ast.Name)
					and isinstance(val.right, ast.Name)
					and val.left.id in self.app.node
					and val.right.id in self.app.node
				):
					fn = get_binop(val.op)
					name = fn + "_" + val.left.id + val.right.id
					self.app.objects.setobj(name, getattr(binop, fn))
					_binop = self.app.node[name]
					_binop.args["a"] = self.app.node[val.left.id]
					_binop.args["b"] = self.app.node[val.right.id]
					attr[argname] = _binop
				elif isinstance(val, ast.Call) and val.func.id in self.app.node:
					self.visit_Call(val)
					attr[argname] = self.app.node[val.func.id]
				elif isinstance(val, ast.UnaryOp):
					if isinstance(val.op, ast.USub) and isinstance(val.operand, ast.Num):
						attr[argname] = -val.operand.n
			for k in node.keywords:
				if isinstance(k.value, ast.Name):
					if k.value.id in self.app.node:
						item.kwargs[k.arg] = self.app.node[k.value.id]
						item.opts["show_kwargs"] = True
				elif isinstance(k.value, ast.Num):
					item.kwargs[k.arg] = k.value.n
					item.opts["show_kwargs"] = True
				elif isinstance(k.value, ast.Str):
					item.kwargs[k.arg] = k.value.s
					item.opts["show_kwargs"] = True
		elif isinstance(node.func, ast.Name) and node.func.id == "plot":
			for val in node.args:
				if isinstance(val, ast.Name):
					if val.id in self.app.node:
						self.app.node.output.connect(self.app.node[val.id], show_plot=False)
				elif isinstance(val, ast.Call) and val.func.id in self.app.node:
					self.visit_Call(val)
					self.app.node.output.connect(self.app.node[val.func.id], show_plot=False)
		elif isinstance(node.func, ast.Attribute):
			if isinstance(node.func.value, ast.Name) and node.func.value.id in self.app.node:
				self.app.node[node.func.value.id].value(self.app.objects[node.func.value.id])

class AssignVisitor(ast.NodeVisitor):
	def __init__(self, app):
		ast.NodeVisitor.__init__(self)
		self.app = app

	def visit_Assign(self, node):
		target = node.targets[0]
		val = node.value
		if isinstance(target, ast.Name) and target.id in self.app.node:
			item = self.app.node[target.id]
			if isinstance(val, ast.Call):
				if isinstance(val.func, ast.Name) and val.func.id in self.app.node:
					if val.func.id in self.app.node:
						if "<value>" in item.args:
							item.args["<value>"] = self.app.node[val.func.id]
						else:
							self.app.objects[val.func.id] = item.value()
			elif (isinstance(val, ast.BinOp)
				and isinstance(val.left, ast.Name)
				and isinstance(val.right, ast.Name)
				and val.left.id in self.app.node
				and val.right.id in self.app.node
			):
				fn = get_binop(val.op)
				name = fn + "_" + val.left.id + val.right.id
				self.app.objects.setobj(name, getattr(binop, fn))
				_binop = self.app.node[name]
				_binop.args["a"] = self.app.node[val.left.id]
				_binop.args["b"] = self.app.node[val.right.id]
				item.args["<value>"] = _binop

def get_binop(node):
	for i in dir(binop):
		if isinstance(node, getattr(ast, i)):
			return i
