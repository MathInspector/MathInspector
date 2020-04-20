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

import json, os, sys

def basepath():
	if hasattr(sys, "_MEIPASS"):
	    return os.path.abspath(os.path.join(sys._MEIPASS, "../Resources/data/settings.json"))
	else:
	    return os.path.abspath(os.path.dirname(__file__)) + "/settings.json"

class ConfigItem:
	def __init__(self, option, **kwargs):
		for i in settings[option]:
			setattr(self, i, settings[option][i])
		for j in kwargs:
			setattr(self, j, kwargs[j])

	def __repr__(self):
		result = {}
		for i in dir(self):
			if i[:2] != '__':
				result[i] = getattr(self, i)

		return str(result)


# with open(basepath(), "r") as f:
# 	settings = json.load(f)

settings = {
	"Color": {		
		"WHITE": "#f8f8f2",
		"PURE_WHITE": "#fff",
		"NAV": "#f3f3f3",
		"LEFT_NAV": "#42433e",
		"EVEN_LIGHTER_GREY": "#f5f5f5",
		"LIGHTER_GREY": "#eeeeee",
		"LIGHT_GREY": "#ececec",
		"VERY_LIGHT_GREY": "#f5f6f7",
		"GREY": "#e6e6e6",
		"DARK_GREY": "#e2e2e2",
		"COOL_GREY": "#474842",
		"DARKER_GREY": "#989898",
		"HIGHLIGHT": "#48473d",
		"HIGHLIGHT_INACTIVE": "#383830",
		"QUALITY_GREY": "#90918b",		
		"VERY_DARK_GREY": "#75715d",
		"FADED_GREY": "#42433e",
		"BACKGROUND": "#272822",
		"CONSOLE_BACKGROUND": "#191919",
		"ALT_BACKGROUND": "#252526",
		"RED": "#fc1e70",
		"GREEN": "#a4e405",
		"DARK_ORANGE": "#c65d09",
		"ORANGE": "#ff9800",
		"PROMPT": "#c65d09",
		"LIGHT_PURPLE": "#3b3b62",
		"VERY_LIGHT_PURPLE": "#343460",

		"DARK_PURPLE": "#7a52b9",
		"WIRE_INACTIVE": "#7a52b9",
		
		"PURPLE": "#af7dff",
		"INACTIVE": "#af7dff",
		
		"BLUE": "#60d9f1",
		"LINK_URL": "#0088cc",
		"LINK_URL_HOVER": "#005580",
		"ACTIVE": "#60d9f1",
		"SELECT_HOVER": "#60d9f1",
		
		"LIGHT_BLUE": "#308bb5",
		"HOVER": "#308bb5",
		"ACTIVE_WIRE": "#308bb5",
		"WIRE_ACTIVE": "#308bb5",
		"SELECTED": "#308bb5",
		
		"PALE_BLUE": "#c7cbd1",
		
		"LIGHT_BLACK": "#555",
		"DARK_BLACK": "#000",
		"EMPTY_NODE": "#000",
		
		"BLACK": "#333",
		"SILVER": "#bcc6cc",
		"YELLOW": "#e6dc6d",
		"LIGHT_YELLOW": "#ffffcc"
	},

	"Font": {
		"MAIN": "Nunito",
		"CODE": "Monospace",
		"ALT": "SourceSansPro"
	},

	"Log": {
		"MESSAGE_TIMEOUT": 4000
	},
	
	"Zoom": {
		"IN": 1.1,
		"OUT": 0.9
	},

	"Excluded": {
		"MODULES": [
			"absolute_import",
			"division",
			"print_function",
			"testing",
			"version",
			"add_newdoc",
			"add_newdocs",
			"add_docstring",
			"add_newdoc_ufunc"
		],
		
		"FOLDERS": [
			"__pycache__",
			".git"
		],
		
		"FILES": [
			".DS_Store"
		]
	},

	"Widget": {	
		"HITBOX": 8,
		"NODE_SIZE": 6,
		"VALUE_LABEL_SIZE": 16,
		"VARIABLE_LABEL_SIZE": 18,
		"CLASS_LABEL_SIZE": 10,
		"ARG_LABEL_SIZE": 8,
		"ARG_VALUE_SIZE": 12,
		"ITEM_SIZE": 80
	}
	
}

for i in settings:
	globals()[i] = ConfigItem(i) if isinstance(settings[i], dict) else settings[i]