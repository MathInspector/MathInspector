"""
Math Inspector: a visual programming environment for scientific computing with python
Copyright (C) 2020 Matt Calhoun

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

"""
@NOTE: a better way to do this would be to try/catch loading and setting things one at a time
this way if something goes wrong or if I add a new thing, the save file wont break	
"""
import pickle, os, atexit, shutil, traceback, cloudpickle, plot
from tkinter import messagebox, filedialog
from .common import name_ext
from importlib import import_module
from .config import AUTOSAVE_PATH
# from console.builtin_print import builtin_print

class SaveData:
	def __init__(self, app):
		self.app = app
		self.is_first_load = True
		atexit.register(self.save)

	def new(self, event=None, with_dialog=True, title="Math Inspector"):
		if with_dialog:
			if not messagebox.askokcancel("MathInspector", 
				"Are you sure you want to start a new file?  Any unsaved data will be lost."):
				return

		self.app.title(title)
		object_keys = list(self.app.objects.store.keys())
		module_keys = list(self.app.modules.store.keys())

		for i in object_keys:
			del self.app.objects[i]

		for j in module_keys:
			del self.app.modules[j]
				
		children = self.app.modules.get_children()
		for k in children:
			self.app.modules.delete(k)

		self.app.modules.rootfolder = None
		self.app.modules.stop_observer()

		self.app.console.clear()
		self.app.node.zoom = 1
		self.app.console.prompt.history.clear()
		self.app.horizontal_panel.sashpos(0,0)
		self.app.vertical_panel.sashpos(0,0)
		self.app.console.do_greet()

	def save(self, file=AUTOSAVE_PATH):
		if file is None or file not in (AUTOSAVE_PATH, self.app.modules.rootfolder):
			file = filedialog.asksaveasfilename(defaultextension="")
			if not file: return
		
		files = self.app.modules.files("file")
		folders = self.app.modules.files("folder")
		
		is_rootfolder = file != AUTOSAVE_PATH and len(files + folders) > 0
		
		if file != AUTOSAVE_PATH:
			self.app.title(os.path.basename(file))
		
		if is_rootfolder:
			self._copy_project_files(file)

		objects = {}
		modules = []
		file_locals = self.app.modules.locals
		for j in self.app.modules.store:
			if not self.app.modules.has_tag(j, "local"):
				modules.append({ "alias": j, "name": self.app.modules[j].__name__})
		# modules = [{ "alias": j, "name": self.app.modules[j].__name__} for j in self.app.modules.store]	
		functions = {}
		methods = {}
		custom_fn = {}
		for name in self.app.objects:
			objects[name] = self.app.objects.store[name]

		itemdata = {}
		for i in self.app.node:
			item = self.app.node[i]
			itemdata[i] = {
				"name": item.name,
				"position": item.position(),
				"connection": item.connection,
				"coord": item.position(),
				"args": { j: item.args[j] for j in item.args if j != "<value>" },
				"kwargs": { k: item.kwargs[k] for k in item.kwargs },
				"opts": item.opts.store,
			}	

		plot_config = plot.config()

		data = [{
			"name": "app_title",
			"value": self.app.title()
		},{
			"name": "zoom",
			"value": self.app.node.zoom
		},{
			"name": "geometry",
			"value": self.app.geometry() if self.app.geometry()[:3] != "1x1" else "1280x720"
		},
		{
			"name": "horizontal_panel_sash",
			"value": self.app.horizontal_panel.sashpos(0)
		},{
			"name": "vertical_panel_sash",
			"value": self.app.vertical_panel.sashpos(0)
		},
		{
			"name": "rootfolder",
			"value": self.app.modules.rootfolder
		},{
			"name": "modules",
			"value": modules
		},{
			"name": "file_locals",
			"value": file_locals
		},{
			"name": "objects",
			"value": objects
		},{
			"name": "itemdata",
			"value": itemdata
		},{
			"name": "files",
			"value": files
		},{
			"name": "folders",
			"value": self.app.modules.files("folder")
		},{
			"name": "disabled_files",
			"value": self.app.modules.files("disabled", True)
		},{
			"name": "plot_window_size",
			"value": plot_config["size"] if plot_config else None
		},{
			"name": "plot_window_position",
			"value": plot_config["window_pos"] if plot_config else None
		},{
			"name": "plot2d_options",
			"value": { i: plot.OPTIONS_2D[i] for i in ["show_grid", "show_range"] }
		},{
			"name": "plot3d_options",
			"value": { i: plot.OPTIONS_3D[i] for i in ["show_grid"] }
		},{
			"name": "plot_window_position",
			"value": os.environ["SDL_VIDEO_WINDOW_POS"] if "SDL_VIDEO_WINDOW_POS" in os.environ else None
		},{
			"name": "objects_order",
			"value": self.app.objects.order()
		},{
			"name": "objects_expanded",
			"value": self.app.objects.expanded()
		},{
			"name": "console_history",
			"value": self.app.console.prompt.history.cmds
		},{
			"name": "side_select",
			"value": self.app.side_view.select()
		},{
			"name": "module_order",
			"value": self.app.modules.order()
		},{
			"name": "module_expanded",
			"value": self.app.modules.expanded()
		}]

		name, ext = name_ext(file)
		if is_rootfolder:
			filepath = os.path.join(file, os.path.basename(file) + ".math")
		else:
			filepath = os.path.join(os.path.dirname(file), name + ".math")
		with open(filepath, "wb") as output:
			cloudpickle.dump(data, output)

	def on_configure(self, name, sashpos=0):
		widget = getattr(self.app, name)
		widget.sashpos(0, sashpos)
		widget.unbind("<Configure>")

	def load(self, file=AUTOSAVE_PATH, is_first_load=False):
		if file != AUTOSAVE_PATH:
			file = filedialog.askopenfilename(filetypes=[('Math Inspector Files','*.math'), ('All Files','*.*')])
			if not file:
				return
		
		try:
			with open(file, "rb") as i:
				data = pickle.load(i)
		except Exception:
			self.new(with_dialog=False)
			self.app.geometry("1280x720+140+100")
			self.app.horizontal_panel.bind("<Configure>", 
				lambda event: self.on_configure("horizontal_panel", 0))
			self.app.vertical_panel.bind("<Configure>", 
				lambda event: self.on_configure("vertical_panel", 0))
			self.new(with_dialog=False)
			return
		
		data = { i["name"]:i["value"] for i in data }
		
		self.new(with_dialog=False, title=data["app_title"])

		try:
			if "zoom" in data:
				self.app.node.zoom = data["zoom"]
			if "geometry" in data:
				self.app.geometry(data["geometry"])
			if "horizontal_panel_sash" in data:
				self.app.horizontal_panel.bind("<Configure>", 
					lambda event: self.on_configure("horizontal_panel", data["horizontal_panel_sash"]))
			if "vertical_panel_sash" in data:
				self.app.vertical_panel.bind("<Configure>", 
					lambda event: self.on_configure("vertical_panel", data["vertical_panel_sash"]))
			if "modules" in data:
				for i in data["modules"]:
					self.app.menu.import_module(i["name"], i["alias"])
			if "file_locals" in data:
				self.app.modules.locals = data["file_locals"]
			if "objects" in data:
				for j in data["objects"]:
					self.app.objects.setobj(j, data["objects"][j], coord=data["itemdata"][j]["coord"])
			if "itemdata" in data:
				items = data["itemdata"]
				for m in items:
					item = self.app.node[m]
					for j in items[m]["args"]:
						item.args[j] = items[m]["args"][j]
					for k in items[m]["kwargs"]:
						item.kwargs[k] = items[m]["kwargs"][k]
					for l in items[m]["opts"]:
						item.opts[l] = items[m]["opts"][l]

				for m in self.app.node:
					item = self.app.node[m]
					if items[m]["connection"]:
						name, argname = items[m]["connection"]
						other = self.app.node[name]
						if argname in other.args.store:
							other.args[argname] = item
						elif argname in other.kwargs.store:
							other.kwargs[argname] = item
			if "rootfolder" in data:
				if data["rootfolder"]:
					self.app.modules.addfolder(data["rootfolder"], is_rootfolder=True, exec_file=False)
			if "folders" in data:
				for i in data["folders"]:
					if os.path.dirname(i) != data["rootfolder"]:
						self.app.modules.addfolder(i, exec_file=False)
			if "files" in data:
				for j in data["files"]:
					if os.path.dirname(j) != data["rootfolder"]:
						self.app.modules.addfile(j, exec_file=False)
			if "disabled_files" in data:
				for k in data["disabled_files"]:
					self.app.modules.disable_file(k)
			if "side_select" in data:
				self.app.side_view.select(data["side_select"])
			if "plot2d_options" in data:
				if data["plot2d_options"]:
					self.app.menu.plotconfig(**data["plot2d_options"])
			if "plot3d_options" in data:
				if data["plot3d_options"]:
					self.app.menu.plotconfig(**data["plot3d_options"])
			if "plot_window_size" in data:
				if data["plot_window_size"]:
					plot.config(size=data["plot_window_size"])
			if "plot_window_position" in data:
				if data["plot_window_position"]:
					os.environ["SDL_VIDEO_WINDOW_POS"] = data["plot_window_position"]
			if "console_history" in data:
				self.app.console.prompt.history.cmds = data["console_history"]
				self.app.console.prompt.history.i = len(data["console_history"])
			if "objects_order" in data:
				self.app.objects.order(data["objects_order"])
			if "objects_expanded" in data:
				self.app.objects.expanded(data["objects_expanded"])
			if "module_order" in data:
				self.app.modules.order(data["module_order"])
			if "module_expanded" in data:
				self.app.modules.expanded(data["module_expanded"])
			if file != AUTOSAVE_PATH and self.app.modules.rootfolder and self.app.modules.exists("README"):
				help(self.app.modules.item("README")["values"][0])

			self.app.node.scale_font()
			self.app.node.scale_width()

		except:
			traceback.print_exc()

	def _copy_project_files(self, file):
		rootfolder = os.path.splitext(file)[0]
		files = self.app.modules.files("file")
		folders = self.app.modules.files("folder")
		order = self.app.modules.order()

		for i in files + folders:
			self.app.modules.delete(i)
		
		if not os.path.isdir(rootfolder):
			os.mkdir(rootfolder)
		
		self.app.modules.stop_observer()
		for i in folders:
			if os.path.dirname(i) != rootfolder:
				shutil.copytree(i, os.path.join(rootfolder, os.path.basename(i)))
		
		for j in files:
			if os.path.dirname(j) != rootfolder:
				shutil.copy(j, rootfolder)

		self.app.modules.addfolder(rootfolder, is_rootfolder=True)
		self.app.modules.order(order)
