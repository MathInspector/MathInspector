import inspect, sys, os, random, platform, builtins
from functools import reduce
from PIL import ImageTk, Image
from settings import Color

BUILTIN_CLASS = [i for i in dir(builtins) if inspect.isclass( getattr(builtins, i) )]
BUILTIN_FUNCTION = [i for i in dir(builtins) if not inspect.isclass( getattr(builtins, i) )]

def get_font_color(value):
    if isinstance(value, str):
        return Color.YELLOW
    elif isinstance(value, dict):
        return Color.GREY
    elif isinstance(value, int) or isinstance(value, float) or isinstance(value, complex):
        return Color.PURPLE
    elif callable(value) or value is None:
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

def strjoin(items):
    return "".join([i + " " if len(i) > 0 else "\n" for i in items])

def basepath():
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    else:
        return os.path.abspath("../")

def classname(obj):
    if inspect.isfunction(obj) and obj.__module__: # in sys.modules:
        # return obj.__name__
        return obj.__module__ + "." + obj.__name__
        # return sys.modules[obj.__module__].__name__ + "." + obj.__name__
    elif obj.__class__.__module__ and hasattr(obj, "__name__"):
        return obj.__class__.__module__ + "." + obj.__name__
    elif obj.__class__.__name__ in BUILTIN_CLASS:
        return "builtins." + obj.__class__.__name__
    else:
        return obj.__class__.__name__

def getalias(modules, name):
    toplevel = name.split(".")
    if name in modules:
        key = name
    else:
        for i in modules:
            if modules[i].__name__ == name:                    
                key = i
                break
        key = toplevel[0]

    return key if len(toplevel) == 1 else key + "." + ".".join(toplevel[1:])


def on_configure_panel(widget, sashpos):
    widget.sashpos(0, sashpos)
    widget.unbind("<Configure>")

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
        return os.path.abspath(os.path.join((sys._MEIPASS), "./Resources/assets/img" if platform.system() == "Windows" else "../Resources/assets/img")) + "/"
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
    return os.path.splitext(os.path.basename(filepath))
 
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