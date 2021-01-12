import os, sys
from PIL import ImageTk, Image
from util.config import BASEPATH

ASSET_PATH = os.path.join(BASEPATH, "assets/img" if hasattr(sys, "_MEIPASS") else "img")

IMAGE = {
	".py": "pythonlogo-color.png",
	"python-disabled": "pythonlogo-disabled.png",
	".md": "markdown.png",
	"folder": "folder.png",
	"folder-open": "folder-open.png",
	"blank-file": "blank-file.png",
	"node": "node.png",
	"node-connect": "node-connect.png",
	"node-active": "node-active.png",
	"function-f": "function-f.png",
}

cache = {}

def init():
	for i in IMAGE:
		cache[i] = ImageTk.PhotoImage(Image.open(os.path.join(ASSET_PATH, IMAGE[i])))

def getimage(key):
	if len(cache) == 0:
		init()
	if key in cache:
		return cache[key]
	return cache["blank-file"]