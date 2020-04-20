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

from .objectcontainer import ObjectContainer
from .argcount import argcount
from .argspec import argspec
from .docscrape import FunctionDoc, ClassDoc
from pdb import set_trace as breakpoint
from .savedata import SaveData
import inspect, sys, os, random
from functools import reduce
from PIL import ImageTk, Image
from settings import Color

def get_font_color(value):
    if isinstance(value, str):
        return Color.YELLOW
    elif isinstance(value, dict):
        return Color.GREY
    elif isinstance(value, int) or isinstance(value, float) or isinstance(value, complex):
        return Color.PURPLE
    elif callable(value):
        return Color.RED
    else:
        return Color.BLUE

def unique_name(app, name):
    i = 2
    temp = name
    while True:
        if temp not in app.objects:
            return temp
        temp = name + "_" + str(i)
        i += 1


def get_class_name(obj):
    if inspect.isfunction(obj) and obj.__module__ in sys.modules:
        # return obj.__name__
        return sys.modules[obj.__module__].__name__ + "." + obj.__name__
    elif obj.__class__.__module__:
    	return obj.__class__.__module__ + "." + obj.__class__.__name__
    else:
        return obj.__class__.__name__

def readfile(filepath):
    file = open(filepath, "r")
    result = file.read()
    file.close()
    return result

def random_color():
    return "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])

def subfolders(path):
    return [name for name in os.listdir(path)
            if os.path.isdir(os.path.join(path, name))]

def assetpath():
    if hasattr(sys, "_MEIPASS"):
        return os.path.abspath(os.path.join((sys._MEIPASS), "../Resources/assets/img")) + "/"
    else:
        return os.path.abspath("../assets/img") + "/"

def loadimage(file):
    filepath = assetpath() + file + ".png"
    raw = Image.open(filepath)
    raw = raw.resize((32, 32), Image.ANTIALIAS)
    return ImageTk.PhotoImage(raw)

def hexstring(num):
    return '#' + str(hex(num))[2:].zfill(6)

def makereadonly(tkWdg):
	tkWdg.bind('<Key>', readonly)

def readonly(event):
	if event.keysym is not 'c':
		return 'break'

def getnamefrompath(filepath):
    return os.path.basename(filepath)

def name_and_extension(filepath):
    name = os.path.basename(filepath)
    ext = os.path.splitext(name)[1]
    return name, ext

def getcommonletters(strlist):
    return ''.join([x[0] for x in zip(*strlist) if reduce(lambda a,b:(a == b) and a or None,x)])

def findcommonstart(strlist):
    strlist = strlist[:]
    prev = None
    while True:
        common = getcommonletters(strlist)
        if common == prev:
            break
        strlist.append(common)
        prev = common

    return getcommonletters(strlist)

