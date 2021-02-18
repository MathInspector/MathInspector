"""
used for loading images from ../assets
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
import os, sys
from PIL import ImageTk, Image
from ..util.config import BASEPATH

ASSET_PATH = os.path.join(BASEPATH, "img")

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
