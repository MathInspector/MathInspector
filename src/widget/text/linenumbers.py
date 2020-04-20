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
from settings import Color

class LineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None
        self.error_linenum = None
        self.config(
            background=Color.BACKGROUND,
            bd=0, 
            highlightthickness=0
        )

    def attach(self, text_widget):
        self.textwidget = text_widget

    def error(self, linenum):
        self.error_linenum = linenum
        self.redraw()

    def redraw(self, *args):
        '''redraw line numbers'''
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True :
            dline= self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            color = Color.QUALITY_GREY
            if linenum == self.error_linenum:
                color = Color.RED
                linenum = linenum + " •"
            self.create_text(40,y,anchor="ne", text=linenum, fill=color, font="Menlo-Regular 15")
            i = self.textwidget.index("%s+1line" % i)
