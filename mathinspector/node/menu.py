import math, builtins, plot
from util import BUILTIN_FUNCTION, BUILTIN_CLASS, BUILTIN_CONSTANT

TRIG_FUNCTIONS = [i for i in ("acos", "acosh", "asin", "asinh", "atan", "atan2", "atanh", "cos", "cosh", "degrees", "sin", "sinh", "tan", "tanh")]
MATH_FUNCTIONS = [i for i in dir(math) if callable(getattr(math, i)) and i not in TRIG_FUNCTIONS and i[:1] != "_"]
MATH_CONSTANTS = [i for i in dir(math) if i not in MATH_FUNCTIONS + TRIG_FUNCTIONS and i[:1] != "_"]

def object_menu(app):
	return [{
		"label": "Math",
		"menu": [{
			"label": "Constant",
			"menu":[{
				"label": i,
				"command": lambda key=i: create_object(app, key, module=math)
			} for i in MATH_CONSTANTS]
		},{
			"separator": None
		},{
			"label": "Trig",
			"menu":[{
				"label": i,
				"command": lambda key=i: create_object(app, key, module=math)
			} for i in TRIG_FUNCTIONS]
		},{
			"separator": None
		}] + [{
			"label": i,
			"command": lambda key=i: create_object(app, key, module=math)
		} for i in MATH_FUNCTIONS]
	},{
		"label": "Builtin Class",
		"menu": [{	
			"label": str(i),
			"command": lambda key=i: create_object(app, key, module=builtins)
		} for i in BUILTIN_CLASS if i[:1] != "_" and not i[:1].isupper() and "Error" not in i and "Warning" not in i]
	},{
		"label": "Builtin Function",
		"menu": [{	
			"label": str(i),
			"command": lambda key=i: create_object(app, key, module=builtins)
		} for i in BUILTIN_FUNCTION if i[:1] != "_" and not i[:1].isupper()]
	},{
		"label": "Plot Example",
		"menu": [{	
			"label": str(i).replace("_", " ").capitalize(),
			"command": lambda key=i: create_object(app, key, module=plot.example)
		} for i in dir(plot.example) if i[:1] != "_" and not i[:1].isupper() and i != "np"]
	}]

def create_object(app, name, module):
	obj = getattr(module, name)
	app.objects.setobj(name, obj, create_new=True)