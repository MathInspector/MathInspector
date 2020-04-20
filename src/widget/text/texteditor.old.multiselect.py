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
from .highlightedtext import HighlightedText
from .blinkingcursor import BlinkingCursor
from .linenumbers import LineNumbers
from settings import Color, Font
from util import ObjectContainer
import style.syntax
import io, re, tokenize, builtins, keyword, inspect

BUILTIN_CLASS = [i for i in dir(builtins) if inspect.isclass( getattr(builtins, i) )]
BUILTIN_FUNCTION = [i for i in dir(builtins) if not inspect.isclass( getattr(builtins, i) )]
CUSTOM_KEYWORD = ["self"]
RE_WORD = re.compile(r"[a-zA-Z_0-9]")
RE_INSERT = re.compile(r"insert([+-][0-9]*)c")
RE_MARK_SET_INSERT = re.compile(r"insert([+-][0-9]*)displayindices")
RE_TAB = re.compile(r"\t{1,}(?! ).")

regex = {   
    "orange_italic": r"(\w+)=(.*?)( |\n)*(,|\))",
    "comment": r"(?s)('''.*?''')",
    "green": r"def {1,}(\w+)\(",
    "blue": r"(\w+)\(",
}

def advance_index(ind, amount):
    line, col = ind.rsplit('.', 1)
    col = col + "+" + str(amount) + "c" if amount > 0 else col + str(amount) + "c"
    return '{}.{}'.format(line, col)

def shift_col_index(ind, amount):
    line, col = ind.rsplit('.', 1)
    return '{}.{}'.format(str(int(line) + amount), col)


class TextEditor(HighlightedText):
    def __init__(self, parent, content=None, syntax=".py", on_change_callback=None, *args, **kwargs):
        HighlightedText.__init__(self, parent, *args, **kwargs, font="Menlo-Regular 15")
        
        for tag in style.syntax:
            self.tag_configure(tag, **style.syntax[tag])
        
        self.linenumbers = LineNumbers(parent, width=56)
        self.linenumbers.attach(self)
            
        self.is_command_pressed = False
        self.multiselect = None
        self.is_multiselect_mode = False
        self.is_clicking = False
        self.select_type = None
        self.ignore_change = False
        self.prev_index = "1.0"
        self.cursors = []
        self.lines = []
        self.syntax = syntax
        self.is_first_load = True
        self.keypress = ObjectContainer(getitem=lambda key: self.keypress.store[key] if key in self.keypress.store else False)

        self.tag_configure("multi_sel", background=Color.DARK_PURPLE)

        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)
        self.bind("<Configure>", self._on_configure)
        self.bind("<Key>", self._on_key)
        self.bind("<KeyRelease>", self._on_key_release)
        self.bind("<Button-1>", self._on_button_1)
        self.bind("<ButtonRelease-1>", self._on_button_release_1)
        self.bind("<<Change>>", self._on_change)
        self.bind("<<Selection>>", self._on_text_selection)
          
    def syntax_highlight(self):
        for tag in style.syntax:
            self.tag_remove(tag,"1.0","end")

        content = self.get()
        try:
            for typ, string, start, end, line in tokenize.generate_tokens(io.StringIO(content).readline):
                token = tokenize.tok_name[typ]
                ind1 = "{0}.{1}".format(*start)
                ind2 = "{0}.{1}".format(*end)
                if token == "NAME":
                    if string in keyword.kwlist:
                        self.tag_add("red", ind1, ind2)
                    elif string in BUILTIN_FUNCTION:
                        self.tag_add("blue", ind1, ind2)
                    elif string in BUILTIN_CLASS:
                        self.tag_add("blue_italic", ind1, ind2)
                    elif string in CUSTOM_KEYWORD:
                        self.tag_add("orange_italic", ind1, ind2)
                elif token == "OP":
                    if string in ["=", "*", "**"]:
                        self.tag_add("red", ind1, ind2)
                elif token == "STRING":
                    self.tag_add("yellow", ind1, ind2)
                elif token == "NUMBER":
                    self.tag_add("purple", ind1, ind2)
                elif token == "COMMENT":
                    self.tag_add("comment", ind1, ind2)
        except:
            pass

        for tag in regex:
            self.highlight(regex[tag], tag)

    def clear_cursors(self):
        for index, cursor in self.cursors:
            cursor.place_forget()
        self.cursors.clear()

# @REFACTOR move this fn into highlighted text    
    def get_insert_word(self):
        start = 1
        stop = 1
        letter = self.get("insert-1c", "insert")
        while RE_WORD.search(letter):
            start += 1
            letter = self.get("insert-%sc" % str(start), "insert-%sc" % str(start - 1))

        letter = self.get("insert", "insert+1c")
        while RE_WORD.search(letter):
            stop += 1
            letter = self.get("insert+%sc" % str(stop - 1), "insert+%sc" % str(stop))

        index = self.index("insert")
        line, column = index.split(".")
        return self.get("insert-%sc" % str(start - 1), "insert+%sc" % str(stop - 1))

    def _on_key(self, event):
        self.keypress[event.keysym] = True

        if event.keysym == "Meta_L":
            self.is_command_pressed = True
        
        if event.keysym == "Escape":
            self.clear_cursors()

        if event.keysym == "Return":
            return "break"

        if self.is_multiselect_mode:
            selected = self.tag_ranges("sel")
            if event.keysym == "BackSpace":
                for i in range(0, len(selected), 2):
                    self.delete(selected[i], selected[i+1])

            return "break"
        elif self.keypress["Meta_L"]:
            if event.keysym == "d":
                try:
                    selection = self.selection_get()
                except:
                    selection = None
                
                # @REFACTOR method for get ind1, ind2 so code is cleaner/shorter
                if selection:                   
                    content = self.get("insert", "end")
                    # i need to find the full word which is highlighted and use that as the selection, not seletion_get()
                    match = re.compile(self.get_insert_word()).search(content)
                    start = match.start()
                    end = match.end()
                    ind1 = self.index("insert") + "+" + str(start) + "c"
                    ind2 = self.index("insert") + "+" + str(end) + "c"
                    self.tag_add("sel", ind1, ind2)
                    self.mark_set("insert", ind2)

                    # next_occurance = re.compile(selection).search(self.get())
                    # find index of next occurance of selected word
                else:
                    start = 1
                    stop = 1
                    letter = self.get("insert-1c", "insert")
                    while RE_WORD.search(letter):
                        start += 1
                        letter = self.get("insert-%sc" % str(start), "insert-%sc" % str(start - 1))

                    letter = self.get("insert", "insert+1c")
                    while RE_WORD.search(letter):
                        stop += 1
                        letter = self.get("insert+%sc" % str(stop - 1), "insert+%sc" % str(stop))

                    index = self.index("insert")
                    line, column = index.split(".")
                    self.tag_add("sel", "insert-%sc" % str(start - 1), "insert+%sc" % str(stop - 1))
                    self.mark_set("insert", "insert+%sc" % str(stop - 1))
        
    def _on_key_release(self, event):
        self.keypress[event.keysym] = False
        index = self.index("insert")
        if not index: return
        line = int(index.split(".")[0])
        start = str(line) + ".0"
        end = str(line + 1) + ".0-1c"
        num_tabs = self.get(start, end).count("\t")
        if event.keysym == "Return":
            self.insert(index, "\n" + "\t" * num_tabs)
            self.see("insert")
        
    def _on_text_selection(self, event):
        selected = self.tag_ranges("sel")
        self.is_multiselect_mode = len(selected) > 2

    def _on_button_1(self, event):
        self.is_clicking = True
        # if self.keypress["Meta_L"]:
        #     x, y, width, height = self.bbox("insert")
        #     #   - on scroll text, need blinking cursors to scroll as well
        #     self.cursors.append([self.index("insert"), BlinkingCursor(self, x,y)])
        # elif len(self.cursors) > 0:
        #     self.clear_cursors()

    def _on_button_release_1(self, event):
        self.is_clicking = False

    def _on_configure(self, event):
        if event.height > 1:            
            self.linenumbers.redraw()
            self.unbind("<Configure>")        

    def _on_change(self, event):
        self.linenumbers.redraw()

    # lmao do I even need to bother writing it? just look down
    def _proxy(self, *args):
        try:
            cmd = (self._orig,) + args
            result = self.tk.call(cmd)
        except:
            return

        did_change = args[0] in ("insert", "replace", "delete") or args[0:3] == ("mark", "set", "insert")

        # if args[0:2] == ("xview", "scroll") or args[0:2] == ("yview", "scroll"):
        #     self.event_generate("<<Scroll>>", when="tail")



        # # ('tag', 'add', 'sel', 'insert', '210.15')
        # # ('tag', 'remove', 'sel', '210.14', 'end')

        # # if args[0] == "tag":

        # if args[0:4] in (('tag', 'add', 'sel', 'tk::anchor1'), ('tag', 'add', 'sel', 'insert')):
        #     self.select_type = "add"
        # elif args[0:5] == ('tag', 'remove', 'sel', '1.0', 'tk::anchor1'):
        #     self.select_type = "remove"

        # if not self.ignore_change and did_change and len(self.cursors) > 0:
        #     if self.is_clicking:
        #         self.prev_index = self.index("insert")
        #         return
        #     # TODO need various ways to determine how to advance the index/blinking cursor based
        #     #   on what comes through in the args
        #     self.ignore_change = True
        #     prev_index = self.index("insert")
        #     for i in range(0, len(self.cursors)):
        #         index, cursor = self.cursors[i]
        #         self.mark_set("insert", index)
        #         try:
        #             cmd = (self._orig,) + args
        #             result = self.tk.call(cmd)
        #             if args[0] == "insert":
        #                 new_index = advance_index(index, len(args[2]))
        #             elif args[0] == "delete":
        #                 amount = int( RE_INSERT.search(args[1]).group(1) )
        #                 # make self.index part of advance_index which can be a class method
        #                 new_index = self.index(advance_index(index, amount))
        #             elif args[0:3] == ("mark", "set", "insert"):
        #                 if RE_MARK_SET_INSERT.search(args[3]):
        #                     amount = int (RE_MARK_SET_INSERT.search(args[3]).group(1))
        #                     new_index = self.index(advance_index(index, amount))
        #                 else:
        #                     prev_line = int(self.prev_index.split(".")[0])
        #                     new_line = int(args[3].split(".")[0])
        #                     line_shift = new_line - prev_line
        #                     if line_shift == 0:
        #                         prev_col = int(self.prev_index.split(".")[1])
        #                         new_col = int(args[3].split(".")[1])
        #                         col_shift = new_col - prev_col
        #                         new_index = self.index(advance_index(index, col_shift))
        #                         if self.select_type:
        #                             if index < new_index:
        #                                 if self.select_type == "add":
        #                                     self.tag_add("multi_sel", index, new_index)
        #                                 else:
        #                                     self.tag_remove("multi_sel", index, new_index)
        #                             else:
        #                                 if self.select_type == "add":
        #                                     self.tag_add("multi_sel", new_index, index)
        #                                 else:
        #                                     self.tag_remove("multi_sel", new_index, index)
                                    
        #                             # self.select_type = None
        #                     else:
        #                         new_index = self.index(shift_col_index(index, line_shift))
        #                     # this seems really fishy
        #                     self.prev_index = self.index("insert")

        #             # make a method in the cursor for setting position and moving at the same time
        #             self.cursors[i][0] = new_index
        #             x, y, width, height = self.bbox(new_index)
        #             self.cursors[i][1].place(x=x - 16, y=y - 8)
        #         except Exception as e:
        #             pass


        #     self.mark_set("insert", prev_index)
        #     self.ignore_change = False

        # is_modified = args[0] in ("insert", "replace", "delete") or (args[0:3] == ("mark", "set", "insert") and RE_MARK_SET_INSERT.search(args[3]))

        # if is_modified and self.on_change_callback:
        #     self.on_change_callback()


        if did_change and self.syntax == ".py":
            self.syntax_highlight()

        if (did_change or
            args[0:2] == ("xview", "moveto") or
            args[0:2] == ("xview", "scroll") or
            args[0:2] == ("yview", "moveto") or
            args[0:2] == ("yview", "scroll")
        ):
            self.event_generate("<<Change>>", when="tail")

        return result             