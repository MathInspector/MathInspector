import ast

Constant = (ast.Num, ast.Str, ast.List, ast.Tuple, ast.Set, ast.Dict, ast.NameConstant)

class CodeParser(ast.NodeVisitor):
	def __init__(self, app):
		ast.NodeVisitor.__init__(self)
		self.app = app
		self.preprocess_visitor = PreProcessVisitor(app)
		self.call_visitor = CallVisitor(app)
		self.assign_visitor = AssignVisitor(app)
	
	def __call__(self, source):
		tree = ast.parse(source)
		self.call_visitor.visit(tree)
		self.assign_visitor.visit(tree)
		return tree

	def preprocess(self, source):
		self.preprocess_visitor.visit(ast.parse(source))

class PreProcessVisitor(ast.NodeVisitor):
	def __init__(self, app):
		ast.NodeVisitor.__init__(self)
		self.app = app

	def visit_Call(self, node):
		if isinstance(node.func, ast.Name) and node.func.id == "plot":
			for val in node.args:
				if isinstance(val, ast.Name):
					if val.id in self.app.node:
						self.app.node.output.connect(self.app.node[val.id], show_plot=False)
				elif isinstance(val, ast.Call) and val.func.id in self.app.node:
					self.visit_Call(val)
					self.app.node.output.connect(self.app.node[val.func.id], show_plot=False)

		
class CallVisitor(ast.NodeVisitor):
	def __init__(self, app):
		ast.NodeVisitor.__init__(self)
		self.app = app

	def visit_Call(self, node):
		if isinstance(node.func, ast.Name) and node.func.id in self.app.node:
			item = self.app.node[node.func.id] if node.func.id in self.app.node else None
			for i, val in enumerate(node.args):
				if item:
					if len(item.argspec[0]) > i:
						argname = item.argspec[0][i]
						attr = item.args
					elif len(item.argspec[1]) > 0:
						argname = list(item.kwargs.store.items())[i - len(item.argspec[0])][0]
						attr = item.kwargs
					else:
						return
					
				if isinstance(val, ast.Name):
					if val.id in self.app.node:
						attr[argname] = self.app.node[val.id]
				elif isinstance(val, ast.Num):
					attr[argname] = val.n
				elif isinstance(val, ast.Str):
					attr.store[argname] = val.s
				elif isinstance(val, ast.Call) and val.func.id in self.app.node:
					self.visit_Call(val)
					attr[argname] = self.app.node[val.func.id]
			for k in node.keywords:
				if isinstance(k.value, ast.Name):
					if k.value.id in self.app.node:
						item.kwargs[k.arg] = self.app.node[k.value.id]
				elif isinstance(val, ast.Num):
					item.kwargs.store[k.arg] = val.n
				elif isinstance(val, ast.Str):
					item.kwargs.store[k.arg] = val.s
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
		if isinstance(target, ast.Name):
			item = self.app.node[target.id]
			if isinstance(val, ast.Call):
				if isinstance(val.func, ast.Name) and val.func.id in self.app.node:
					if val.func.id in self.app.node:
						if "<value>" in item.args:
							item.args["<value>"] = self.app.node[val.func.id]
						else:
							self.app.objects[val.func.id] = item.value()
