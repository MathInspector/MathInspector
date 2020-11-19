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

from settings import Color

RE_PY = {   
    "orange_italic": r"([a-zA-Z0-9_]*)=(.*?)( |\n)*(,|\))",
    "green": r"def {1,}(\w+)\(",
    "blue": r"(\w+)\(",
}

TAGS = {
    "blue": {
        "foreground": Color.BLUE
    },

    "blue_italic": {
        "foreground": Color.BLUE, 
        "font": "Menlo 15 italic"
    },

    "green": {
        "foreground": Color.GREEN
    },

    "red": {
        "foreground": Color.RED
    },
    
    "underline": {
        "font": "Menlo 16 italic", 
        "underline": True
    },

    "purple": {
        "foreground": Color.PURPLE
    },

    "orange": {
        "foreground": Color.ORANGE
    },

    "dark_orange_bold": {
        "foreground": Color.DARK_ORANGE,
        "font": "Menlo 16 bold"
    },

    "orange_italic": {
        "foreground": Color.ORANGE, 
        "font": "Menlo 15 italic"
    },

    "comment": {
        "foreground": Color.VERY_DARK_GREY
    },

    "yellow": {
        "foreground": Color.YELLOW
    },	
}