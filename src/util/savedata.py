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

"""
@NOTE: a better way to do this would be to try/catch loading and setting things one at a time
this way if something goes wrong or if I add a new thing, the save file wont break	
"""
import pickle, atexit, os, shutil
from .misc import basepath

AUTOSAVE_PATH = os.path.join(basepath(), "autosave.math")

class SaveData:
	def __init__(self, app):
		self.app = app
		self.load()
		atexit.register(self.save)

	def new(self):
		self.app.objects.clear()
		self.app.modules.clear()
		self.app.projecttree.clear()
		self.app.console.clear()
		self.app.docviewer.clear()
		self.app.output.clear()
		self.app.nav.select("top", "workspace")
		self.app.nav.select("bottom", "console")

	def save(self, filepath=AUTOSAVE_PATH):
		if filepath != AUTOSAVE_PATH:
			rootfolder = os.path.dirname(filepath)
			files = self.app.projecttree.tags("file")
			folders = self.app.projecttree.tags("folder")
			order = self.app.projecttree.order()

			for i in files + folders:
				self.app.projecttree.delete(i)
			
			if not os.path.isdir(rootfolder):
				os.mkdir(rootfolder)
			
			self.app.projecttree.stop_observing()
			for i in folders:
				if os.path.dirname(i) != rootfolder:
					shutil.copytree(i, os.path.join(rootfolder, os.path.basename(i)))
			
			for j in files:
				if os.path.dirname(j) != rootfolder:
					shutil.copy(j, rootfolder)

			self.app.projecttree.addfolder(rootfolder, is_rootfolder=True)
			self.app.projecttree.order(order)
		with open(filepath, "wb") as output:
			for i in (
				(self.app.workspace.zoomlevel, self.app.projecttree.order(), self.app.projecttree.expanded(), self.app.projecttree.selection(), self.app.selected),
				self.app.state(),
				self.app.workspace.save(),
				self.app.projecttree.state(),
				self.app.console.state(),
				self.app.objecttree.state(),
				self.app.output.save()):
				
				pickle.dump(i, output, pickle.HIGHEST_PROTOCOL)

	def load(self, filepath=AUTOSAVE_PATH):
		self.new()
		
		try:
			with open(filepath, "rb") as data:
				zoomlevel, order, expanded, selected_file, selected_object  = pickle.load(data)
				app = pickle.load(data)
				workspace = pickle.load(data)
				projecttree = pickle.load(data)
				console = pickle.load(data)
				objecttree = pickle.load(data)
				output = pickle.load(data)
		except Exception:
			self.new()			
			return

		if filepath != AUTOSAVE_PATH:
			projecttree[0] = os.path.dirname(filepath)

		self.app.workspace.zoomlevel = zoomlevel
		self.app.projecttree.state(*projecttree)
		self.app.state(*app)
		self.app.console.state(console)
		self.app.workspace.load(*workspace)
		self.app.objecttree.state(*objecttree)
		self.app.output.load(*output)
		self.app.select(selected_object)
		self.app.projecttree.order(order)
		self.app.projecttree.expanded(expanded)
		if selected_file:
			self.app.projecttree.selection_set(selected_file)
