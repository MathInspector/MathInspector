"""
Math Inspector: a visual programming environment for scientific computing
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
import numpy as np
import math, builtins
from .. import examples
from ..util import BUILTIN_FUNCTION, BUILTIN_CLASS, BUILTIN_CONSTANT, binop

TRIG_FUNCTIONS = [i for i in ("acos", "acosh", "asin", "asinh", "atan", "atan2", "atanh", "cos", "cosh", "degrees", "sin", "sinh", "tan", "tanh")]
MATH_FUNCTIONS = [i for i in dir(math) if callable(getattr(math, i)) and i not in TRIG_FUNCTIONS and i[:1] != "_"]
MATH_CONSTANTS = [i for i in dir(math) if i not in MATH_FUNCTIONS + TRIG_FUNCTIONS and i[:1] != "_"]

def object_menu(app):
	return [{
		"label": "Operator",
		"menu": [{
			"label": i,
			"command": lambda key=i: create_object(app, key, binop)
		} for i in dir(binop) if i[0] != "_"]
	},{
		"label": "Math",
		"menu": [{
			"label": "Constant",
			"menu":[{
				"label": i,
				"command": lambda key=i: create_object(app, key, np if hasattr(np, key) else math)
			} for i in MATH_CONSTANTS]
		},{
			"separator": None
		},{
			"label": "Trig",
			"menu":[{
				"label": i,
				"command": lambda key=i: create_object(app, key, np if hasattr(np, key) else math)
			} for i in TRIG_FUNCTIONS]
		},{
			"separator": None
		}] + [{
			"label": i,
			"command": lambda key=i: create_object(app, key, np if hasattr(np, key) else math)
		} for i in MATH_FUNCTIONS]
	},{
		"label": "Builtin Class",
		"menu": [{
			"label": str(i),
			"command": lambda key=i: create_object(app, key, builtins)
		} for i in BUILTIN_CLASS if i[:1] != "_" and not i[:1].isupper() and "Error" not in i and "Warning" not in i]
	},{
		"label": "Builtin Function",
		"menu": [{
			"label": str(i),
			"command": lambda key=i: create_object(app, key, module=builtins)
		} for i in BUILTIN_FUNCTION if i[:1] != "_" and not i[:1].isupper()]
	},{
		"label": "Examples",
		"menu": [{
			"label": str(i).replace("_", " ").capitalize(),
			"command": lambda key=i: create_object(app, key, module=examples)
		} for i in dir(examples) if i[:1] != "_" and not i[:1].isupper() and i != "np"]
	}]

def create_object(app, name, module):
	obj = getattr(module, name)
	app.objects.setobj(name, obj, create_new=True)
