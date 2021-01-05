from .builtin_print import builtin_print

class History(list):
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

	def extend(self, *args):
		self.cmds.extend(args)
		self.i = len(self.cmds)