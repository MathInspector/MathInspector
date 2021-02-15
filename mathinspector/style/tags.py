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

from .color import Color
from ..util.config import FONT

TAGS = {
    "red": {
        "foreground": Color.RED
    },

    "blue": {
        "foreground": Color.BLUE
    },

    "blue_italic": {
        "foreground": Color.BLUE,
        "font": FONT + " italic"
    },

    "green": {
        "foreground": Color.GREEN
    },

    "underline": {
        "font": FONT + " italic",
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
        "font": FONT + " bold",
    },

    "console_prompt": {
        "foreground": Color.DARK_ORANGE,
        "font": FONT + " bold",
        "selectbackground": Color.DARK_BLACK,
    },

    "orange_italic": {
        "foreground": Color.ORANGE,
        "font": FONT + " italic"
    },

    "comment": {
        "foreground": Color.VERY_DARK_GREY
    },

    "yellow": {
        "foreground": Color.YELLOW
    },

    "error_file": {
        "foreground": Color.YELLOW
    },

    "error_file_hover": {
        "foreground": Color.WHITE
    },
}

TREE_TAGS = {
    "blue": {
        "foreground": Color.BLUE
    },

    "yellow": {
        "foreground": Color.YELLOW
    },

    "grey": {
        "foreground": Color.GREY
    },

    "purple": {
        "foreground": Color.PURPLE
    },

    "red": {
        "foreground": Color.RED
    },
}
