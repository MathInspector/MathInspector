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

import tkinter as tk
import inspect, textwrap, re, sys, webbrowser, builtins
from widget.text import Text
from util import makereadonly, FunctionDoc, classname, name_and_extension, strjoin
from settings import Color
from style import DOC_TAGS
from os import path
import style.markdown

pattern = {
    "bold": r"``(.*?)``",
    "menlo_italic": r"(?<!`)`(?!`)(.*?)`",
    # "italic": r"`(?!`)([0-9a-zA-Z.<> =()^]*)`(?!`)",
    "link_url": r"(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+~]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)",
    "code_sample": r"(?s)(>>>.*?\n)\n",
    "console_prompt": r"(>>>)"
}

class DocViewer(Text):
    def __init__(self, app):
        Text.__init__(self, app, font="Nunito-ExtraLight 16", cursor="arrow", insertbackground=Color.BACKGROUND)
        self.app = app
        self.obj = None
        self.hover_range = None
        makereadonly(self)

        for i in ("link_url", "doc_link", "code_sample"):
            self.tag_bind(i, "<Motion>", lambda event, key=i: self._motion(event, key))
            self.tag_bind(i, "<Leave>", lambda event, key=i: self._leave(event, key))
            self.tag_bind(i, "<Button-1>", lambda event, key=i: self._click(event, key))    

        for i in DOC_TAGS:
            self.tag_configure(i, **DOC_TAGS[i])

    def select(self, key):
        self.clear()
        if key == None: return
        
        if key in self.app.objects:
            self.obj = self.app.objects[key]
        elif key in self.app.modules:
            self.obj = self.app.modules[key]
        elif path.isfile(key):
            name, ext = name_and_extension(key)
            if ext == ".md":
                content = open(filepath, "r").read()
                self.show_markdown(content)
            return
        else:
            try:
                module, attr = key.rsplit('.', 1)
                self.obj = getattr(self.app.modules[module], attr)
            except:
                return

        try:
            doc = FunctionDoc(self.obj)
        except:
            self.show_textfile(self.obj.__doc__)
            return

        self.show_functiondoc(doc, classname(self.obj))

    def show_functiondoc(self, doc, name):
        self.insert("1.0", name + "\n", "h1")
        self.tag_add("name", "1.0", "1." + str(len(name)))
        
        for i in doc:            
            if len(doc[i]) > 0:
                self.insert("end", "\n")
                if i == "Signature":
                    signature = doc[i].replace(", /", "").replace(", \*", "").replace(", *", "")
                    self.insert("end", signature, "signature")
                    self.syntax_highlight("end-1c linestart")
                    self.insert("end", "\n")
                elif i  == "Summary":
                    self.insert("end", "".join(doc[i]) + "\n")
                elif i  == "Extended Summary":
                    self.insert("end", strjoin(doc[i]).replace("\n", "\n\n") + "\n")
                elif i  in ("Other Parameters", "Attributes", "Methods", "Warnings"):
                    self.insert("end", i + "\n", "see_also_title")
                    self.insert("end", " ".join(doc[i]) + "\n")
                elif i in ("Parameters", "Returns", "Raises", "Yields", "Warns"):
                    self.insert("end", i.upper() + "\n", ("section_title", "bordered_box", "spacing_top"))
                    for j in doc[i]:
                        self.insert("end", j[0], ("parameter_name", "bordered_box"))
                        self.insert("end", " : ", ("bordered_box"))
                        self.insert("end", j[1], ("italic", "blue", "bordered_box"))
                        self.insert("end", "\n", ("bordered_box"))
                        self.insert("end", strjoin(j[2]), ("parameter_description", "bordered_box", "spacing_bottom"))
                        self.insert("end", "\n", ("bordered_box"))
                elif i == "See Also":
                    self.insert("end", "See also:\n", ("see_also", "see_also_title"))
                    for j in doc[i]:
                        self.insert("end", j[0], ("doc_link", "see_also"))
                        if len(j[1]) > 0:
                            self.insert("end", " : " + "".join(j[1]) + "\n", "see_also")
                        else:
                            self.insert("end", "\n", "see_also")
                    self.insert("end", "\n", "see_also")
                elif i == "Notes":
                    self.insert("end", "Notes\n", "underline_title")
                    self.insert("end", "\n", "horizontal_rule")
                    self.insert("end", "\n")
                    self.insert("end", strjoin(doc[i]) + "\n", "notes")
                elif i == "References":
                    items = [j.strip() for j in doc[i]]
                    self.insert("end", "References\n", "underline_title")
                    self.insert("end", "\n", "horizontal_rule")
                    self.insert("end", "\n")
                    self.insert("end", " ".join(items).replace(".. ", "\n\n") + "\n", "references")
                elif i == "Examples":
                    self.insert("end", "Examples\n", "underline_title")
                    self.insert("end", "\n", "horizontal_rule")
                    self.insert("end", "\n")
                    self.insert("end", "\n".join(doc[i]) + "\n")

        for tag in pattern:
            self.highlight(pattern[tag], tag)

        ranges = self.tag_ranges("code_sample")
        for i in range(0, len(ranges), 2):
            start = ranges[i]
            stop = ranges[i+1]
            self.syntax_highlight(start, stop)

    def show_markdown(self, content):
        self.delete("1.0", "end")
        self.insert("1.0", content)
        for tag in style.markdown:
            if isinstance(style.markdown[tag], tuple):
                for regex in style.markdown[tag]:
                    self.highlight(regex, tag)
            else:
                self.highlight(style.markdown[tag], tag)

        for tag in pattern:
            self.highlight(pattern[tag], tag)     

        self.highlight(r"^[-\*+]", "unordered-list", newtext="•")
        self.highlight(r"^\t[-\*+]", "unordered-list", newtext="\t◦")

    def show_textfile(self, content):
        self.insert("end", content)
        self.highlight(r"^(?!\n)(.*\n)==={1,}$", "h1")
        self.highlight(r"^(==={1,})$", newtext="\n")
        
        self.highlight(r"^(.*\n)---{1,}$", "section_title")
        self.highlight(r"^(---{1,})$", "horizontal_rule", newtext="\n")
        
        # self.highlight(r"^(?!\n)(.*\n---{1,})$", "section_title")
        # self.highlight(r"^(---{1,})$", "horizontal_rule", newtext="\n")

        # for tag in style.markdown:
        #     if isinstance(style.markdown[tag], tuple):
        #         for regex in style.markdown[tag]:
        #             self.highlight(regex, tag)
        #     else:
        #         self.highlight(style.markdown[tag], tag)

        # for tag in pattern:
        #     self.highlight(pattern[tag], tag)     
        
        # content = content.split("\n\n")        
        # for i in content:
        #     self.insert("end", i + "\n==HELLLLLOOOO--==\n")
        #     self.highlight(r"(-{3,})", )
        

    def clear(self):
        self.delete("1.0", "end")

    def _motion(self, event, tag):
        self.config(cursor="pointinghand")
        hover_range = self.tag_prevrange(tag, "@" + str(event.x) + "," + str(event.y))
        if not hover_range: return

        if self.hover_range and hover_range != self.hover_range:
            self.tag_remove(tag + "_hover", *self.hover_range)

        self.hover_range = hover_range
        content = self.get(*hover_range)
        if content:
            self.tag_add(tag + "_hover", *hover_range)

    def _leave(self, event, tag):
        self.config(cursor="")
        if self.hover_range:
            self.tag_remove(tag + "_hover", *self.hover_range)

    def _click(self, event, tag):
        if tag == "link_url":
            webbrowser.open(self.get(*self.hover_range), new=2)
        elif tag == "doc_link":            
            self.select(classname(self.obj).rsplit(".")[0] + "." + self.get(*self.hover_range))
        elif tag == "code_sample":
            for command in re.findall(r">>> {0,}(.*)", self.get(*self.hover_range)):
                self.app.console.command(command)
                self.app.nav.select("bottom" if self.app.nav.selected["top"] == "docviewer" else "top", "console")
