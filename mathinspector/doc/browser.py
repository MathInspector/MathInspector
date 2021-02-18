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

import tkinter as tk
from tkinter import ttk
import inspect
from ..util.argspec import argspec
from ..util.common import classname
from ..util.config import BUTTON_RIGHT, EXCLUDED_MODULES, INSTALLED_PKGS, BUILTIN_PKGS
from ..console.builtin_print import builtin_print
from ..widget import Notebook, Treeview, Button, Menu
from .show_textfile import show_textfile
from .doc import Doc
from ..style import Color

class Browser(tk.Toplevel):

    def __init__(self, app, obj=None, title=None, browse=False, on_import=None, geometry=None):
        tk.Toplevel.__init__(self, app, background=Color.BLACK)
        if geometry:
            self.geometry(geometry)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        if obj:
            if isinstance(obj, str) and os.path.isfile(obj):
                title = os.path.basename(obj)
            self.title(title or classname(obj))
            self.doc = Doc(self, obj, run_code=app.console.prompt.push)
            self.doc.pack(fill="both", expand=True)
            return

        self.app = app
        self.on_import = on_import
        self.menu = Menu(self)

        self.paned_window = ttk.PanedWindow(self, orient="horizontal")
        self.notebook = Notebook(self, has_labels=True)
        self.installed_pkgs = Treeview(self, self)
        self.builtin_pkgs = Treeview(self, self)
        self.notebook.add("Built In", self.builtin_pkgs)
        self.notebook.add("Installed", self.installed_pkgs)
        self.doc = Doc(self, has_sidebar=True, run_code=app.console.prompt.push)

        frame = tk.Frame(self)
        input_area = tk.Frame(frame, background=Color.BLACK)
        name_label = tk.Label(input_area, text="import ", font="Menlo 14", background=Color.BLACK, foreground=Color.WHITE)
        self.name_entry = tk.Entry(input_area, font="Monospace 14", highlightbackground=Color.BLACK)

        input_area_2 = tk.Frame(frame, background=Color.BLACK)
        as_label = tk.Label(input_area_2, text="    as ", font="Menlo 14", background=Color.BLACK, foreground=Color.WHITE)
        self.as_entry = tk.Entry(input_area_2, font="Monospace 14", highlightbackground=Color.BLACK)

        btn_area = tk.Frame(frame, background=Color.BLACK)
        cancel_btn = Button(btn_area, text="Cancel", command=self.destroy)
        self.ok_btn = Button(btn_area, text="Ok", command=self._on_ok)

        for i in INSTALLED_PKGS:
            self.installed_pkgs.insert("", "end", i, text=str(i).split(" ")[0])

        for j in BUILTIN_PKGS:
            self.builtin_pkgs.insert("", "end", j, text=j)

        if on_import:
            self.notebook.frame.pack(fill="both", expand=True)
            frame.pack(side="left", fill="both", expand=True)
            self.name_entry.focus()
        else:
            self.paned_window.add(self.notebook.frame)
            self.paned_window.add(self.doc)
            self.paned_window.pack(side="left", fill="both", expand=True)

        if on_import:
            cancel_btn.pack(side="left", fill="x", expand=True, anchor="center", padx=4, pady=4)
            self.ok_btn.pack(side="left", fill="x", expand=True, anchor="center", padx=4, pady=4)
            btn_area.pack(side="bottom", fill="both")

            input_area_2.pack(side="bottom", fill="both")
            as_label.pack(side="left")
            self.as_entry.pack(side="left", expand=True)

            input_area.pack(side="bottom", fill="both")
            name_label.pack(side="left")
            self.name_entry.pack(side="left", expand=True)

            self.bind("<Return>", self._on_ok)
            self.bind("<Escape>", lambda event: self.destroy())
        else:
            self.doc.paned_window.bind("<Configure>", self._on_configure_doc)

        for i in ("installed_pkgs", "builtin_pkgs"):
            getattr(self, i).bind("<<TreeviewSelect>>", lambda event, key=i: self._on_selection(event, key))
            getattr(self, i).bind(BUTTON_RIGHT, lambda event, key=i: self._on_button_right(event, key))

    def _on_configure_doc(self, event):
        self.doc.paned_window.sashpos(0,0)
        self.doc.paned_window.unbind("<Configure>")

    def _on_selection(self, event, name):
        key = getattr(self, name).selection()[0]

        self.doc.clear()
        if self.on_import:
            self.name_entry.delete(0, "end")
            self.name_entry.insert("end", key)
            return

        try:
            module = __import__(key)
        except:
            return

        self.doc.show(module)

    def _on_close(self):
        help.geometry = self.geometry()
        self.destroy()

    def _on_ok(self, event=None):
        name = self.name_entry.get()
        if not name:
            builtin_print("\a")
            return

        if self.on_import:
            self.on_import(self.name_entry.get(), self.as_entry.get())
        self.destroy()

    def _on_button_right(self, event, name):
        attr = getattr(self, name)
        key = attr.identify_row(event.y)
        attr.selection_set(key)

        if self.on_import:
            try:
                module = __import__(key)
            except:
                return

            items = [{
                "label": "View Doc",
                "command": lambda: help(module)
            }]
        else:
            items = [{
                "label": "Import Module",
                "command": lambda: self.app.menu.import_module(key, open_folders=True)
            }]

        self.menu.set_menu(items)
        self.menu.show(event)
