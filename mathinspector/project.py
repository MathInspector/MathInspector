"""
Math inspector was designed to make it as simple as possible to share projects online. To share a project on social media, simply upload the project folder to a hosting platform like github and share the link with your friends.

To save the current project, select Project > Save Project from the main menu.  If the project doesn't contain any external files or folders, then it will be saved in a file with a .math extension, otherwise, math inspector will create a new directory on your file system with the name of the project, and will copy any external files into this new directory, and place the .math
file in the project folder.

To open a saved project, select Project > Open Project from the main menu, navigate to the project folder and choose the .math file.

Adding files to your project
---
You can add an existing python script to a project by selecting Project > Add File To Project from the main menu. There are no restrictions on the type of python programs which are compatible.

Whenever you save your changes to a file that has been added to the current project, the node editor is updated just as if the entire file was copy/pasted into the interpreter.  This can be very convinient for more complicated projects.

Let's create a new file to see how it works.  Select Project > New File > Python from the main menu and choose a name for the file.  When you create this file, it will appear in the left hand side panel of math inspector, right now there is nothing in the file, but as you add things the module tab of the side panel will contain a directory of all objects available from that file.

Try creating a complex number `z` by typing `z=1+1j` into the newly created file, and then save your changes.


README
---
If your project includes a file named README.md, then when someone opens the project the README file will be displayed in the doc browser.

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
import pickle, os, atexit, shutil, traceback, cloudpickle
from importlib import import_module
from tkinter import messagebox, filedialog
from .plot import plot
from .util import name_ext
from .config import AUTOSAVE_PATH, LOCAL_AUTOSAVE_PATH
from .console.builtin_print import builtin_print

MAX_RECENT_PROJECTS = 5
DEFAULT_GEOMETRY = "1280x720+140+100"
FILETYPES = [
	("Python", "*.py"),
	("Markdown", "*.md"),
	("Rich Structured Text", "*.rst"),
	("All Files", "*.*"),
]

class SaveData:
	def __init__(self, app):
		self.app = app
		self.is_first_load = True
		self.mathfile = None # Only used when project does not contain any files or folders
		self.did_save = False # REFACTOR - use self.needs_to_save() instead (currently used to prevent double save dialogs on exit)
		self.recents = [] # recent projects
		self.newproj_savedata = None
		atexit.register(self._on_close)
		app.protocol("WM_DELETE_WINDOW", self._on_click_close_app)

	def new(self, event=None, with_dialog=True, title="Math Inspector"):
		if with_dialog:
			filepath = self.filepath()

			if filepath != AUTOSAVE_PATH:
				if self.needs_to_save():
					if messagebox.askyesno("MathInspector",
						"You have unsaved changes.  Would you like to save before starting a new project?"
					):
						did_save = self.save(filepath)
						if did_save is False: return
			elif self.savedata() != self.newproj_savedata:
				if not messagebox.askokcancel("MathInspector",
					"Are you sure you want to start a new project?  Any unsaved data will be lost."):
					return

		plot.close()
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
		self.mathfile = None
		self.app.modules.stop_observer()

		self.app.console.clear()
		self.app.node.zoom = 1
		self.app.console.prompt.history.clear()
		self.app.horizontal_panel.sashpos(0,0)
		self.app.vertical_panel.sashpos(0,0)
		self.app.menu.restore_defaults()
		self.app.console.do_greet()
		self.newproj_savedata = self.savedata()
		self.app.menu.savefile = None
		self.app.menu.sync_recent_projects()

	def save(self, file=None, quit_app=False): #, savedata=None):  # use savedata kwarg to avoid computing it twice
		files = self.app.modules.files("file")
		folders = self.app.modules.files("folder")
		is_rootfolder = file != AUTOSAVE_PATH and len(files + folders) > 0

		if self.mathfile and len(files + folders) > 0:
			self.mathfile = None

		if file is None or file not in (
			AUTOSAVE_PATH, 
			self.app.modules.rootfolder, 
			self.mathfile
		):
			if len(files + folders) > 0:
				msg = "Choose a name & location for the root folder of this project"
				defaultextension = ""
				filetypes = ""
			else:
				msg = None
				defaultextension = ".math"
				filetypes = [("Math Inspector Files", "*.math")]
			
			file = filedialog.asksaveasfilename(
				defaultextension=defaultextension,
				filetypes=filetypes,
				title="Save Project",
				message=msg)
			if not file: return False


		if file != AUTOSAVE_PATH:
			self.app.title(name_ext(file)[0])

		if is_rootfolder:
			self._copy_project_files(file)
		elif file != AUTOSAVE_PATH:
			self.mathfile = file

		local_data = [{
			"name": "geometry",
			"value": self.app.geometry() if self.app.geometry()[:3] != "1x1" else "1280x720"
		}, {
			"name": "recent_projects",
			"value": self.recents
		}, {
			"name": "cmd_history_file",
			"value": self.app.menu.savefile
		}]

		data = self.savedata()

		name, ext = name_ext(file)
		filepath = self.filepath(file)
		
		try:
			with open(filepath, "wb") as output:
				cloudpickle.dump(data, output)
		except Exception as err:
			builtin_print ("\nThe autosave file failed to save, " + str(type(err).__name__) + ": " + str(err))

		try:
			with open(LOCAL_AUTOSAVE_PATH, "wb") as output:
				pickle.dump(local_data, output)
		except Exception as err:
			builtin_print (err)

		self.update_recent_projects_menu(file)
		if not os.path.isdir(file):
			self.mathfile = file			

		if quit_app:
			plot.close()
			self.app.quit()

	def savedata(self):
		"""
		Generates the data structure of the python object to pickle in .math save files.
		The reason the data structure is so verbose is to maintain a high level of 
		backwards compatibility when new versions of math inspector are released
		"""
		files = self.app.modules.files("file")
		folders = self.app.modules.files("folder")

		objects = {}
		modules = []
		file_locals = self.app.modules.locals
		for j in self.app.modules.store:
			if not self.app.modules.has_tag(j, "local"):
				modules.append({ "alias": j, "name": self.app.modules[j].__name__})

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

		try:
			help_geometry = help.browser.geometry()
		except:
			help_geometry = help.geometry

		return [{
			"name": "app_title",
			"value": self.app.title()
		},{
			"name": "zoom",
			"value": self.app.node.zoom
		},{
			"name": "horizontal_panel_sash",
			"value": self.app.horizontal_panel.sashpos(0)
		},{
			"name": "vertical_panel_sash",
			"value": self.app.vertical_panel.sashpos(0)
		},{
			"name": "rootfolder",
			"value": self.app.modules.rootfolder
		},{
			"name": "mathfile",
			"value": self.mathfile
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
			"name": "help_geometry",
			"value": help_geometry
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

	def load(self, file=None, is_first_load=False, sashpos=0):
		"""
		loads .math files and configures the app based on the loaded file.
		The reason everything is wrapped in if statements and try catch
		blocks is to preserve backwards compatibility when new versions
		of math inspector are released
		"""
		if is_first_load:
			pass
		elif self.needs_to_save():
			if messagebox.askyesno("MathInspector",
				"You have unsaved changes.  Would you like to save before switching projects?"
			):
				filepath = self.filepath()
				if filepath == AUTOSAVE_PATH:
					did_save = self.save()
				else:
					did_save = self.save(filepath)
				if did_save is False: return

		#########################
		##     GET FILEPATH    ##
		#########################		
		if not is_first_load and file is None:
			file = filedialog.askopenfilename(
				filetypes=[('Math Inspector Files','*.math'), ('All Files','*.*')],
				title="Open Project")
			
			if not file:
				return

		
		#########################
		## LOCAL AUTOSAVE FILE ##
		#########################
		if is_first_load:
			try:
				with open(LOCAL_AUTOSAVE_PATH, "rb") as i:
					local_data = pickle.load(i)
			except:
				local_data = [{
					"name": "geometry",
					"value": DEFAULT_GEOMETRY
				}]

		# keep items in local_data that should be preserved across projects
		# and should not be changed if the regular autosave file is deleted
			local_data = { i["name"]:i["value"] for i in local_data }
			
			try:
				if "geometry" in local_data:
					self.app.geometry(local_data["geometry"])
			except:
				pass

			try:
				if "recent_projects" in local_data:
					self.recents = local_data["recent_projects"]
			except:
				pass

			try:
				if "cmd_history_file" in local_data:
					self.app.menu.savefile = local_data["cmd_history_file"]
			except:
				pass


		#########################
		##    SAVE MATH FILE   ##
		#########################
		if os.path.isdir(file):
			file = self.filepath(file)

		try:
			with open(file, "rb") as i:
				data = pickle.load(i)
		except Exception as err:
			if self.app.debug:
				builtin_print("Failed to load " + os.path.basename(file), err)

			self.new(with_dialog=False)
			self.app.geometry(DEFAULT_GEOMETRY)
			self.app.horizontal_panel.bind("<Configure>",
				lambda event: self.on_configure("horizontal_panel", sashpos))
			self.app.vertical_panel.bind("<Configure>",
				lambda event: self.on_configure("vertical_panel", 0))
			self.new(with_dialog=False)
			if not is_first_load and os.path.isfile(file):
				if file == AUTOSAVE_PATH:
					self.app.console.write("\nThe autosave file failed to load, " + str(type(err).__name__) + ": " + str(err), tags="red")
				else:
					self.app.console.write("\nCould not load " + os.path.basename(file) + ", " + str(type(err).__name__) + ": " + str(err), tags="red")
			return

		data = { i["name"]:i["value"] for i in data }

		
		##########################
		##      LOAD DATA       ##
		##########################
		self.new(with_dialog=False, title=data["app_title"])
		
		try:
		# NOTE - it might be better to have each 'if' have its own try/catch block
		##		and determine which things can fail gracefully and which will
		##		require scrapping the entire autosave file because it's unusable
			if "zoom" in data:
				self.app.node.zoom = data["zoom"]

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
			if "mathfile" in data:
				self.mathfile = data["mathfile"]
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
			if "help_geometry" in data:
				help.geometry = data["help_geometry"]
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

		except Exception as err:
			if self.app.debug:
				builtin_print ("Failed to unpickle " + os.path.basename(file), err)

			if file == AUTOSAVE_PATH:
				self.app.console.write("\nThe autosave file failed to load, " + str(type(err).__name__) + ": " + str(err), tags="red")
			else:
				self.app.console.write("\nCould not load " + os.path.basename(file) + ", " + str(type(err).__name__) + ": " + str(err), tags="red")

		self.update_recent_projects_menu(file)
		# TODO

	def needs_to_save(self):
		data = self.savedata()		
		filepath = self.filepath()

		if not filepath:
			return data != self.newproj_savedata

		try:
			with open(filepath, "rb") as i:
				prev_data = pickle.load(i)
		except Exception as err:
			if self.app.debug:
				builtin_print ("Opening project path failed: ", err)
			return True

		return data != prev_data

	def filepath(self, file=None):
		if file is not None:
			if os.path.isdir(file):
				return os.path.join(
					file,
					os.path.basename(file) + ".math"
				)
			return file

		if self.mathfile:
			return self.mathfile
		elif not self.app.modules.rootfolder:
			return AUTOSAVE_PATH

		return os.path.join(
			self.app.modules.rootfolder,
			os.path.basename(self.app.modules.rootfolder) + ".math"
		)

	def update_recent_projects_menu(self, file):
		if file != AUTOSAVE_PATH and file not in self.recents:
			self.recents.append(file)
			if len(self.recents) > MAX_RECENT_PROJECTS:
				self.recents.pop(0)
		self.app.menu.sync_recent_projects()

	def on_configure(self, name, sashpos=0):
		widget = getattr(self.app, name)
		widget.sashpos(0, sashpos)
		widget.unbind("<Configure>")

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
				shutil.copytree(i, 
					os.path.join(rootfolder, os.path.basename(i)), 
					ignore=ignore_patterns("__pycache__/"))

		for j in files:
			if os.path.dirname(j) != rootfolder:
				shutil.copy(j, rootfolder)

		self.app.modules.addfolder(rootfolder, is_rootfolder=True)
		self.app.modules.order(order)

	def _on_click_close_app(self):
		if self.did_save: return
		
		self.did_save = True

		try:
			self.save(AUTOSAVE_PATH, quit_app=True)
		except Exception as err:
			builtin_print ("error: attempt to write to " + os.path.basename(AUTOSAVE_PATH) + " failed\n", err)
			
		plot.close()
		self.app.quit()			

	def _on_close(self):
		if self.did_save: return
		self.did_save = True
		self.save(AUTOSAVE_PATH)
