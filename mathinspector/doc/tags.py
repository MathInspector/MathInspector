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
from ..style import Color
from ..util.config import FONT, FONT_SIZE

DOC_TAGS = {
    "name": {
        "font": "Montserrat " + FONT_SIZE["extra-large"] + " bold",
        "foreground": Color.WHITE
    },

    "signature": {
        "font": "Monospace " + FONT_SIZE["small"]
    },

    "function_name": {
        "spacing1": 8,
        "spacing3": 8,
        "font": "Monospace " + FONT_SIZE["medium"]
    },

    "class_name": {
        "font": "Nunito " + FONT_SIZE["extra-large"]
    },

    "section_title": {
        "font": "Montserrat " + FONT_SIZE["large"] + " bold",
        "foreground": Color.YELLOW,
        "spacing1": 0,
        "spacing3": 8
    },

    "module_nav": {
        "font": "Montserrat " + FONT_SIZE["medium"] + " bold",
        "foreground": Color.DARK_GREY,
        "spacing1": 12,
    },

    "module_nav_hover": {
        "foreground": Color.WHITE,
    },

    "root": {
        "font": "Montserrat " + FONT_SIZE["medium"] + " bold",
        "foreground": Color.DARK_ORANGE,
    },

    "root_hover": {
        "foreground": Color.ORANGE,
    },

    "bordered_box": {
        "background": Color.COOL_GREY,
        "lmargin1": 16,
        "rmargin": 16
    },

    "spacing_top": {
        "spacing1": 16
    },

    "spacing_bottom": {
        "spacing3": 16
    },

    "h1": {
        "font": "Montserrat " + FONT_SIZE["extra-large"] + " bold",
        "background": Color.DARK_PURPLE,
        "lmargin1": 16,
        "lmargin2": 8,
        "spacing1": 8,
        "spacing3": 8
    },

    "parameter_name": {
        "spacing1": 8,
        "font": "Monospace "+ FONT_SIZE["default"] + " bold",
        "lmargin1": 24,
        "foreground": Color.ORANGE
    },

    "submodule": {
        "spacing1": 8,
        "spacing3": 8,
        "font": "Monospace "+ FONT_SIZE["default"] + " bold",
        "lmargin1": 24,
        "foreground": Color.ORANGE
    },

    "submodule_hover": {
        "foreground": Color.DARK_ORANGE
    },

    "parameter_type": {
        "font": "Nunito " + FONT_SIZE["extra-large"]
    },

    "parameter_description": {
        "lmargin1": 48,
        "lmargin2": 48,
    },

    "underline_title": {
        "font": "Montserrat " + FONT_SIZE["large"] + " bold",
        "foreground": Color.VERY_LIGHT_GREY,
        "spacing1": 16
    },

    "notes": {
    },

    "references": {
        "font": "Nunito " + FONT_SIZE["small"] + " bold"
    },

    "see_also_title": {
        "font": "Montserrat " + FONT_SIZE["medium"] + " bold",
        "spacing1": 16,
        "spacing3": 8,
    },

    "see_also": {
        "background": Color.HIGHLIGHT_INACTIVE,
        "lmargin1": 16,
        "lmargin2": 32,
    },

    "doc_link": {
        "foreground": Color.BLUE,
    },

    "doc_link_hover": {
        "foreground": Color.LINK_URL,
    },

    "code_sample": {
        "background": Color.CONSOLE_BACKGROUND,
        # "foreground": Color.WHITE,
        "font": FONT,
        "spacing1": 8,
        "spacing2": 0,
        "spacing3": 8,
        "lmargin1": 8,
        "lmargin2": 38
    },

    "code_sample_hover": {
        "background": Color.HIGHLIGHT_INACTIVE
    },

    "code": {
        "foreground": Color.GREY,
        "font": FONT + " bold"
    },

    "console_prompt": {
        "foreground": Color.PROMPT,
        "font": FONT + " bold",
        "selectbackground": "red"
    },

    "link_url": {
        "foreground": Color.BLUE
    },

    "link_url_hover": {
        "foreground": Color.LINK_URL
    },

    "section_heading": {
        "font": "Monospace 20 bold",
        "foreground": Color.BLACK,
        "background": Color.LIGHTER_GREY
    },

    "underline_heading": {
        "font": "Lato " + FONT_SIZE["medium"],
        "foreground": Color.BLACK,
        "underline": "true"
    },

    "bold": {
        "font": "Montserrat " + FONT_SIZE["default"] + " bold",
    },
    "italic": {
        "font": FONT + " italic",
    },

    "horizontal_rule": {
        "font": "Monospace 1",
        "background": Color.VERY_LIGHT_GREY,
    },

    "h1": {
        "font": "Monospace 32 bold", 
        "foreground": Color.WHITE, 
    },
    "h2": {
        "font": "Monospace 24 bold", 
        "foreground": Color.ORANGE
    },
    "h3": {
        "font": "Monospace 20 bold", 
        "foreground": Color.DARK_ORANGE
    },

    "code_block": {
        "font": "Monospace 18", 
        "foreground": Color.BLACK,
        "background": Color.COOL_BLUE,
        "lmargin1": 8,
        "spacing1": 8,
        "spacing3": 8,
    },

    "list_number": {
        "font": "Arial 16 Bold"
    }
}

