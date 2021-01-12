import builtins
from util.config import INSTALLED_PKGS, BUILTIN_PKGS, BUILTIN_CLASS
from util.common import name_ext
from os import path
from console.builtin_print import builtin_print
from .browser import Browser
from . import manual

class Help:
	def __init__(self, app):
		self.app = app
		self.geometry = None
		self.browser = None		

	def __call__(self, key=None, title=None):
		if not key:
			self.browser = Browser(self.app, manual, "mathinspector", geometry=self.geometry)
			return
		obj = self.getobj(key)
		if not obj: return
		self.browser = Browser(self.app, obj, title=title, geometry=self.geometry)

	def __repr__(self):
		return "Type help() for interactive help, help(object) for help about object, or help.browse() to view all available documentation."

	def browse(self, callback=None):
		self.browser = Browser(self.app, browse=True, on_import=callback)

	def import_module(self, callback):
		self.browser = Browser(self.app, on_import=callback)

	def getobj(self, key):
		if key is None: return manual

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