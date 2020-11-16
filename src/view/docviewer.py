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
import inspect, textwrap, re, sys, os, webbrowser, builtins
from widget import HighlightedText
from util import makereadonly, FunctionDoc, get_class_name, name_and_extension
from settings import Color
import style.tags
import style.markdown

pattern = {
    "bold": r"``(.*?)``",
    "menlo_italic": r"(?<!`)`(?!`)(.*?)`",
    # "italic": r"`(?!`)([0-9a-zA-Z.<> =()^]*)`(?!`)",
    "link_url": r"(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+~]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)",
    "code_sample": r"(?s)(>>>.*?($|\n))\n",
    "console_prompt": r"(>>>)"
}

class DocViewer(HighlightedText):
    def __init__(self, app, parent=None):
        HighlightedText.__init__(self, parent or app, 
            font="Nunito-ExtraLight 16", 
            cursor="arrow", 
            bg=Color.BACKGROUND,
            insertbackground=Color.BACKGROUND
        )

        self.app = app
        self.hover_range = None
        self.selected_key = None
        self.selected_obj = None
        self.hover = None

        makereadonly(self)

        self.tag_bind("link_url", "<Enter>", lambda event: self._enter(event, "link_url"))
        self.tag_bind("link_url", "<Leave>", lambda event: self._leave(event, "link_url"))
        self.tag_bind("link_url", "<Button-1>", self._click_link)
    
        # self.tag_bind("doc_link", "<Enter>", lambda event: self._enter(event, "doc_link"))
        self.tag_bind("doc_link", "<Leave>", lambda event: self._leave(event, "doc_link"))
        self.tag_bind("doc_link", "<Motion>", self._motion)
        self.tag_bind("doc_link", "<Button-1>", self._click_doc_link)
    
        self.tag_bind("code_sample", "<Enter>", lambda event: self._enter(event, "code_sample"))
        self.tag_bind("code_sample", "<Leave>", lambda event: self._leave(event, "code_sample"))
        self.tag_bind("code_sample", "<Button-1>", self._click_code_sample)

        for tag in style.tags:
            self.tag_configure(tag, **style.tags[tag])

    def update_object(self, key):
        return

    def delete_object(self, key):
        if key == self.selected_key:
            self.select(None)

    def select(self, key, filepath=None):
        self.selected_key = key
        obj = self.app.objects[key] if key in self.app.objects else self.app.modules[key] if key in self.app.modules else None
        if filepath:
            ext = os.path.splitext(filepath)[-1]
            if ext == ".md":
                content = open(filepath, "r").read()
                self.show_markdown(content)
            return
        elif obj is None:
            # self.delete('1.0', 'end')
            self.selected_obj = None
            return
        
        self.showdoc(obj)

    def show(self, key): 
        if key == None: 
            # self.delete("1.0", "end")
            return

        # @REFACTOR: clean this up, not necc to use try/except I dont think
        try:
            module, attr = key.rsplit('.', 1)
            obj = getattr(self.app.modules[module], attr)
            doc = inspect.getdoc(obj)
        except:
            try:
                obj = self.app.modules[key]
                doc = inspect.getdoc(obj)
            except:
                doc = None
                pass


        if doc:
            self.showdoc(obj)
            return True
        
        if "." in key:
            items = key.split(".")
            module = items[0]
            attr = ".".join(items[1:])
            if module == "builtins":
                obj = getattr(builtins, attr)
                self.showdoc(obj)
                return

        if key in self.app.objects:
            obj = self.app.objects[key]
            self.showdoc(obj)
            return

        name, ext = name_and_extension(key)
        if ext == ".md":
            content = open(key, "r").read()
            self.show_markdown(content)

    def showdoc(self, obj, sections=None):
        # TODO - make this selected_key!!! causing a save problem ... sigh
        self.selected_obj = obj
        try:
            doc = FunctionDoc(obj)
        except:
            self.delete("1.0", "end")
            #@TODO: cleanup docs that fail by spliting into \n\n
            self.insert("1.0", obj.__doc__)
            return

        if inspect.isclass(obj):
            name = obj.__module__ + "." + obj.__name__
            # name = "." + obj.__name__
        elif inspect.isfunction(obj) and obj.__module__ in sys.modules:
            name = sys.modules[obj.__module__].__name__ + "." + obj.__name__
        else:
            if ( hasattr(obj,'__name__') ):
                # if obj.__class__.__module__ == "builtins":
                #     name = obj.__name__
                # else:
                name = obj.__class__.__module__ + "." + obj.__name__
            else:
                name = obj.__class__.__module__ + "." + obj.__class__.__name__

        self.delete("1.0", "end")
        if not sections or "Title" in sections:
            self.insert("1.0", name + "\n", "h1")
            self.tag_add("name", "1.0", "1." + str(len(name)))
        
        for i in doc:            
            if len(doc[i]) > 0:
                self.insert("end", "\n")
                if i == "Signature" and (not sections or i in sections):
                    signature = doc[i].replace(", /", "").replace(", \*", "").replace(", *", "")
                    self.insert("end", signature, "signature")
                    self.insert("end", "\n")
                elif i  == "Summary" and (not sections or i in sections):
                    self.insert("end", "".join(doc[i]) + "\n")
                elif i  == "Extended Summary" and (not sections or i in sections):
                    self.insert("end", self.join_items(doc[i]).replace("\n", "\n\n") + "\n")
                elif i  in ("Other Parameters", "Attributes", "Methods", "Warnings") and (not sections or i in sections):
                    #@NOTE these are sections which still need to be styled, need to find examples first...
                    self.insert("end", i + "\n", "see_also_title")
                    self.insert("end", " ".join(doc[i]) + "\n")
                elif i in ("Parameters", "Returns", "Raises", "Yields", "Warns") and (not sections or i in sections):
                    self.insert("end", i.upper() + "\n", ("section_title", "bordered_box", "spacing_top"))
                    for j in doc[i]:
                        self.insert("end", j[0], ("parameter_name", "bordered_box"))
                        self.insert("end", " : ", ("bordered_box"))
                        self.insert("end", j[1], ("italic", "blue", "bordered_box"))
                        self.insert("end", "\n", ("bordered_box"))
                        self.insert("end", self.join_items(j[2]), ("parameter_description", "bordered_box", "spacing_bottom"))
                        self.insert("end", "\n", ("bordered_box"))
                elif i == "See Also" and (not sections or i in sections):
                    self.insert("end", "See also:\n", ("see_also", "see_also_title"))
                    for j in doc[i]:
                        self.insert("end", j[0], ("doc_link", "see_also"))
                        if len(j[1]) > 0:
                            self.insert("end", " : " + "".join(j[1]) + "\n", "see_also")
                        else:
                            self.insert("end", "\n", "see_also")
                    self.insert("end", "\n", "see_also")
                elif i == "Notes" and (not sections or i in sections):
                    self.insert("end", "Notes\n", "underline_title")
                    self.insert("end", "\n", "horizontal_rule")
                    self.insert("end", "\n")
                    self.insert("end", self.join_items(doc[i]) + "\n", "notes")
                elif i == "References" and (not sections or i in sections):
                    items = [j.strip() for j in doc[i]]
                    self.insert("end", "References\n", "underline_title")
                    self.insert("end", "\n", "horizontal_rule")
                    self.insert("end", "\n")
                    self.insert("end", " ".join(items).replace(".. ", "\n\n") + "\n", "references")
                elif i == "Examples" and (not sections or i in sections):
                    # print(doc[i])
                    # items = [str(j) for j in doc[i] if j != ""]
                    self.insert("end", "Examples\n", "underline_title")
                    self.insert("end", "\n", "horizontal_rule")
                    self.insert("end", "\n")
                    self.insert("end", "\n".join(doc[i]) + "\n")

        for tag in pattern:
            self.highlight(pattern[tag], tag)

    def show_markdown(self, content):
        self.delete()
        self.insert("1.0", content)
        for tag in style.markdown:
            if isinstance(style.markdown[tag], tuple):
                for regex in style.markdown[tag]:
                    self.replace(regex, tag)
            else:
                self.replace(style.markdown[tag], tag)

        for tag in pattern:
            self.highlight(pattern[tag], tag)     

        self.replace(r"^[-\*+]", "unordered-list", "•")
        self.replace(r"^\t[-\*+]", "unordered-list", "\t◦")

    def join_items(self, str_list):
        result = ""

        for i in str_list:
            if len(i) == 0:
                result += "\n"
            else:
                result += i + " "

        return result

    def _motion(self, event):
        hover_range = self.tag_prevrange("doc_link", "@" + str(event.x) + "," + str(event.y))
        
        if not hover_range:
            return

        key = self.get(*hover_range)
        if not self.hover:
            self.hover = key
            self.hover_range = hover_range
            self.config(cursor="pointinghand")
            self.tag_add("doc_link_hover", *self.hover_range)
        elif self.hover != key:
            self.hover = key
            self.tag_add("doc_link_hover", *hover_range)
            self.tag_remove("doc_link_hover", *self.hover_range)            
            self.hover_range = hover_range

    def _enter(self, event, tag):
        self.config(cursor="pointinghand")
        self.hover_range = self.tag_prevrange(tag, "@" + str(event.x) + "," + str(event.y))
        
        if not self.hover_range:
            return

        content = self.get(*self.hover_range)
        if content:
            self.tag_add(tag + "_hover", *self.hover_range)

    def _leave(self, event, tag):
        self.hover = None
        self.config(cursor="")
        if self.hover_range:
            self.tag_remove(tag + "_hover", *self.hover_range)

    def _click_link(self, event):
        tag_range = self.tag_prevrange('link_url', "@" + str(event.x) + "," + str(event.y))
        webbrowser.open(self.get(*tag_range), new=2)

    def _click_doc_link(self, event):
        tag_range = self.tag_prevrange('doc_link', "@" + str(event.x) + "," + str(event.y))
        key = self.get(*tag_range)

        #@REFACTOR: clean this up
        if inspect.isclass(self.selected_obj):
            name = self.selected_obj.__module__
        elif inspect.isfunction(self.selected_obj):
            name = sys.modules[self.selected_obj.__module__].__name__
        else:
            if ( hasattr(self.selected_obj,'__name__') ):
                name = self.selected_obj.__class__.__module__
            else:
                name = self.selected_obj.__class__.__module__
        
        self.show(name + "." + key)

    def _click_code_sample(self, event):
        xy = '@{0},{1}'.format(event.x, event.y)
        tag_range = self.tag_prevrange('code_sample', xy)
        code = self.get(*tag_range)
        for cmd in re.findall(r">>> {0,}(.*)", code):
            self.app.console.run( cmd )


