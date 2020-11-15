from PIL import ImageTk, Image
from .misc import assetpath

ICONS = {
	"python": "pythonlogo-color.png",
	"markdown": "markdown.png",
	"folder": "folder.png",
	"folder-open": "folder-open.png",
	"blank-file": "blank-file.png"
}

ICON_MAP = {
	".py": "python",
	".md": "markdown"
}

icons = {}

def init():
	for i in ICONS:
		icons[i] = ImageTk.PhotoImage(Image.open(assetpath() + ICONS[i]))

def geticon(key):
	if len(icons) == 0:
		init()

	if key in ICON_MAP:
		return icons[ICON_MAP[key]]
	
	if key in icons:
		return icons[key]

	return icons["blank-file"]