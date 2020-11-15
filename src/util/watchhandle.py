from watchdog.events import FileSystemEventHandler
from .misc import name_and_extension
from settings import Excluded
import os

class WatchHandle(FileSystemEventHandler):
	def __init__(self, projecttree):
		FileSystemEventHandler.__init__(self)
		self.projecttree = projecttree

	def on_created(self, event):
		for rootfolder in self.projecttree.tags("rootfolder"):
			if rootfolder in event.src_path:
				name, ext = name_and_extension(event.src_path)
				
				parent = os.path.dirname(event.src_path)
				if event.is_directory:
					self.projecttree.addfolder(parent, event.src_path)
				elif ext != ".pyc": # make this from excluded files with regex
					self.projecttree.addfile(event.src_path, parent)

	def on_deleted(self, event):
		name, ext = name_and_extension(event.src_path)

		if ext == ".pyc" or name in Excluded.FOLDERS: return

		for j in self.projecttree.tags("rootfolder"):
			if j in event.src_path:
				self.projecttree.delete(event.src_path)

	def on_modified(self, event):
		if event.is_directory: return
		self.projecttree.update_item(event.src_path)


	def on_moved(self, event):
		# catch rename events here
		print("on_moved", event.src_path)