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

DOC_TAGS = {
    "name": {
        "font": "Montserrat 32 bold", 
        "foreground": Color.WHITE
    },

    "signature": {
        "font": "Monospace 14"
    },

    "class_name": {
        "font": "Nunito 24"
    },

    "section_title": {
        "font": "Montserrat 22 bold", 
        "foreground": Color.YELLOW,
        "spacing1": 32,
        "spacing3": 16
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
        "font": "Montserrat 32 bold",
        "background": Color.DARK_PURPLE,
        "lmargin1": 16,
        "lmargin2": 8,
        "spacing1": 8,
        "spacing3": 8
    },

    "h2": {
        "font": "Nunito 30 bold",
        "lmargin1": 8,
        "lmargin2": 8,
    },

    "h3": {
        "font": "Nunito 24 bold",
        "spacing1": 1,
        "spacing3": 1        
    },

    "parameter_name": {
        "spacing1": 8,
        "font": "Monospace 16 bold",
        "lmargin1": 24,
        "foreground": Color.ORANGE
    },

    "parameter_type": {
        "font": "Nunito 24"
    },

    "parameter_description": {
        "lmargin1": 48,
        "lmargin2": 48,
    },

    "underline_title": {
        "font": "Montserrat 22 bold", 
        "foreground": Color.VERY_LIGHT_GREY, 
        "spacing1": 16
    },

    "notes": {
        
    },

    "references": {
        "font": "Nunito 14 bold"
    },

    "see_also_title": {
        "font": "Montserrat 18 bold",
        "spacing1": 16,
        "spacing3": 8,
    },

    "see_also": {
        "background": Color.HIGHLIGHT_INACTIVE,
        "lmargin1": 16,
        "lmargin2": 32,
    },

    "blockquote": {
        "font": "SourceSansPro 18",
        "lmargin1": 8, 
        "lmargin2": 8,
        "spacing1": 0,
        "spacing2": 0,
        "spacing3": 0        
    },

    "code_block": {
        "background": Color.FADED_GREY,
        "font": "Menlo 18",
        "lmargin1": 8, 
        "lmargin2": 8,
        "spacing1": 16,
        "spacing2": 16,
        "spacing3": 16,
    },

    "doc_link": {
        "foreground": Color.BLUE, 
    },

    "doc_link_hover": {
        "foreground": Color.LINK_URL, 
    },

    "examples": {
        "background": Color.CONSOLE_BACKGROUND,
        "font": "Menlo 16",
        "spacing1": 2,
        "spacing2": 0,
        "spacing3": 8,
        "lmargin1": 8,
        "lmargin2": 38
    },

    "code_sample": {
        "background": Color.CONSOLE_BACKGROUND, 
        # "foreground": Color.WHITE, 
        "font": "Monospace 16",
        "spacing1": 2,
        "spacing2": 0,
        "spacing3": 8,
        "lmargin1": 8,
        "lmargin2": 38
    }, 
    
    "console_prompt": {
        "foreground": Color.PROMPT,
        "font": "Menlo 15 bold"
    },

    "code_sample_hover": {
        "background": Color.HIGHLIGHT_INACTIVE
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
        "font": "Lato 18", 
        "foreground": Color.BLACK, 
        "underline": "true"
    },
    
    # @TODO: move bold/italic into different system because italics is getting done wrong
    "bold": {
        "font": "Menlo 15 bold"
    },
    
    "menlo_italic": {
        "font": "Nunito 16 bold",
    },
    
    "italic": {
        "font": "Monospace 16 italic"        
    },

    "unordered_list": {
        "font": "Menlo 15",
        "lmargin1": 16,
        "lmargin2": 24,
    },

    "code": {
        "font": "Menlo 15",
        "foreground": Color.RED
    },

    "horizontal_rule": {
        "font": "Monospace 1",
        "background": Color.VERY_LIGHT_GREY
    }

}
