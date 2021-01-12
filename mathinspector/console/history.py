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