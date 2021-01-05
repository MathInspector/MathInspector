import __main__, builtins
from util import INSTALLED_PKGS, BUILTIN_PKGS, BUILTIN_CLASS, name_ext
from os import path
from console.builtin_print import builtin_print
from .browser import Browser

class Help:
	def __init__(self, app):
		self.app = app

	def __call__(self, key=None):
		if not key:
			return Browser(self.app, __main__)
		obj = self.getobj(key)
		if not obj: return
		Browser(self.app, obj)
		return ""

	def __repr__(self):
		return "Type help() for interactive help, help(object) for help about object, or help.browse() to view all available documentation."

	def browse(self, callback=None):
		Browser(self.app, browse=True, on_import=callback)

	def import_module(self, callback):
		Browser(self.app, on_import=callback)

	def getobj(self, key):
		if key is None: return __main__

		if not isinstance(key, str):
			return key

		if key in INSTALLED_PKGS + BUILTIN_PKGS:
			try:
				obj = __import__(key)
				return obj
			except:
				pass
		
		if key in self.app.objects:
			if isinstance(self.app.objects[key], tuple([getattr(builtins,i) for i in BUILTIN_CLASS])):
				return self.app.objects[key].__class__
			return self.app.objects[key]
		if key in self.app.modules:
			return self.app.modules[key]
		if path.isfile(key):
			name, ext = name_ext(key)
			if name in self.app.modules:
				return self.app.modules[name]
			
			if name in ("LICENSE") or ext in (".md", ".rst"):
				return key
		try:
			module, attr = key.rsplit('.', 1)
			return getattr(self.app.modules[module], attr)
		except:
			try:
				obj, attr = key.split('.', 1)
				return getattr(self.app.objects[obj], attr)
			except:
				return None		