import numpy as np
import plot, numpy.doc, __main__, scipy, math, builtins
from widget import Popup, Menu
import plot.example
from style import Color
from util import CONTROL_KEY
from console import builtin_print
from functools import partial

SASHPOS_MIN = 20

class MainMenu(Menu):
	def __init__(self, app):
		Menu.__init__(self, app, [{
			"label": "File",
			"menu": [{
					"label": "New                    ",
					"command": app.savedata.new,
					"accelerator": CONTROL_KEY + "+n",
				},
				{
					"label": "Open...            ",
					"command": lambda event=None: app.savedata.load(None),
					"accelerator": CONTROL_KEY + "+o"	
				},
				{
					"label": "Save            ",
					"command": lambda event=None: app.savedata.save(app.modules.rootfolder),
					"accelerator": CONTROL_KEY + "+s"	
				},
				{
					"label": "Save As...            ",
					"command": lambda event=None: app.savedata.save(None),
					"accelerator": CONTROL_KEY + "+Shift+s"	
				}]
			},{
				"label": "Project",
				"menu": [{
					"label": "Add File...",
					"command": app.modules.addfile
				},{
					"label": "Add Folder...",
					"command": app.modules.addfolder
				},{
					"label": "Import Module...",
					"command": lambda event=None: help.import_module(self.import_module)
				}]
			},{
				"label": "Plot",
				"menu": [{
					"label": "Show Grid Lines                      ✓",
					"command": partial(self.plotconfig, "show_grid"),
				},{
					"label": "Show Range                            ✓",
					"command": lambda: self.plotconfig("show_range")
				},
				# {
				# 	"label": "PixelMap Resolution",
				# 	"menu": [{
				# 			"label": "Increase 25%",
				# 			"command": lambda: self.plotconfig("increase_resolution")
				# 		},{
				# 			"label": "Decrease 25%",
				# 			"command": lambda: self.plotconfig("decrease_resolution")
				# 		},{
				# 			"label": "Restore Default",
				# 			"command": lambda: self.plotconfig(resolution=1)
				# 		},
				# 		# {
				# 		# 	"label": "Custom...",
				# 		# 	"command": lambda: Popup(app, "Set Resolution", self.set_plot_resolution, eval_args=False)
				# 		# }
				# 		]
				# }
				],
			},
			{
				"label": "View",
				"menu": [{
					"label": "Show Sidebar",
					"command": lambda: self.setview("sidebar")
				},{
					"label": "Show Node Editor",
					"command": lambda: self.setview("node_editor")
				},{
					"label": "Hide Console",
					"command": lambda: self.setview("console")
				}]
			},
			{
				"label": "Help",
				"menu": [{
					"label": "Math Inspector",
					"command": lambda: help(__main__)
				},{
					"label": "Numpy Doc",
					"command": lambda: help(numpy.doc)
				},{
					"separator": None
				},{
					"label": "Browse Modules...",
					"command": lambda: help.browse()
				}
				# ,{
				# 	"label": "Scipy Tutorial",
				# 	"command": lambda: help(scipy)
				# }
				# ,{
				# 	"label": "Builtin Functions",
				# 	"command": lambda: help(builtins)
				# }
				]
			}])

		self.app = app
		self.is_sidebar_visible = False
		self.has_hidden_panel = False
		app.side_view.bind("<Configure>", self.on_config_sidebar)
		app.node.output.bind("<Configure>", self.on_config_vertical_panel)

	def on_config_sidebar(self, event):
		sashpos = self.app.horizontal_panel.sashpos(0)
		if self.is_sidebar_visible and sashpos > SASHPOS_MIN: return
		
		if sashpos <= SASHPOS_MIN:
			self._["View"].entryconfig(0, label="Show Sidebar")
			self.is_sidebar_visible = False
		else:
			self._["View"].entryconfig(0, label="Hide Sidebar")
			self.is_sidebar_visible = True
	
	def on_config_vertical_panel(self, event):
		sashpos = self.app.vertical_panel.sashpos(0)
		height = self.app.winfo_height()
		if SASHPOS_MIN < sashpos < height - SASHPOS_MIN: 
			if self.has_hidden_panel:
				self.has_hidden_panel = False
				self._["View"].entryconfig(1, label="Hide Node Editor")
				self._["View"].entryconfig(2, label="Hide Console")
			return

		self.has_hidden_panel = True
		if sashpos <= SASHPOS_MIN:
			self._["View"].entryconfig(1, label="Show Node Editor")
			self._["View"].entryconfig(2, label="Hide Console")
		else:
			self._["View"].entryconfig(1, label="Hide Node Editor")
			self._["View"].entryconfig(2, label="Show Console")

	def setview(self, key, force_open=False):
		h_sashpos = self.app.horizontal_panel.sashpos(0)
		v_sashpos = self.app.vertical_panel.sashpos(0)
		
		if key == "sidebar":
			self.is_sidebar_visible = not self.is_sidebar_visible
			if self.is_sidebar_visible:
				self._["View"].entryconfig(0, label="Hide Sidebar")
				self.app.horizontal_panel.sashpos(0,240)
			elif not force_open:
				self._["View"].entryconfig(0, label="Show Sidebar")
				self.app.horizontal_panel.sashpos(0,0)
		elif key == "node_editor":
			if v_sashpos <= SASHPOS_MIN:
				self.app.vertical_panel.sashpos(0, int(self.app.winfo_height()/2))
				self._["View"].entryconfig(1, label="Hide Node Editor")
			elif not force_open:
				self.app.vertical_panel.sashpos(0, 0)
				self._["View"].entryconfig(1, label="Show Node Editor")
		elif key == "console":
			height = self.app.winfo_height()
			if v_sashpos >= height - SASHPOS_MIN:
				self.app.vertical_panel.sashpos(0, int(height/2))
			elif not force_open:
				self.app.vertical_panel.sashpos(0, int(height))
		elif key == "modules":
			self.app.side_view.select(0)
			if h_sashpos <= 10:
				self.app.horizontal_panel.sashpos(0,240)
		elif key == "objects":
			self.app.side_view.select(1)
			if h_sashpos <= 10:
				self.app.horizontal_panel.sashpos(0,240)
			# else:
			# 	self.app.vertical_panel.sashpos(0, 0)

	def import_module(self, module, alias="", open_folders=False):
		self.app.modules[alias or module] = __import__(module)
		if open_folders:
			self.app.focus()
			key = alias or module
			self.app.modules.selection_set(key)
			self.app.modules.item(key, open=True)

	def plotconfig(self, key=None, **kwargs):
		opts = plot.config()
		if key is None:
			plot.config(**kwargs)
			if "show_grid" in kwargs:
				self._["Plot"].entryconfig(0, label="Show Grid Lines                      " + ("✓" if opts["show_grid"] else ""))
			elif "show_range" in kwargs:
				self._["Plot"].entryconfig(1, label="Show Range                           " + ("✓" if opts["show_range"] else ""))
			return

		plot.config(**{ key : not opts[key] })
		if key == "show_grid":
			self._["Plot"].entryconfig(0, label="Show Grid Lines                      " + ("✓" if opts[key] else ""))
		elif key == "show_range":
			self._["Plot"].entryconfig(1, label="Show Range                           " + ("✓" if opts[key] else ""))



	def set_plot_resolution(self, val):
		self.plotconfig(resolution=val)
