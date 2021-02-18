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

import numpy as np
import inspect, traceback
from .. import plot
from ..style import Color
from ..util import vdict
from ..util import classname, fontcolor, argspec
from ..util.config import ITEM_FONTSIZE as FONTSIZE
from .entry import Entry
from textwrap import fill
from pprint import pformat
from numpy import ufunc

FONT_SIZE = 20
MAX_NUMBER_WIDTH = 10
MAX_STR_WIDTH = 256
TEXTWRAP_SIZE = 28
NODE_SIZE = 6

class Item:
    def __init__(self, canvas, name, coord=(0,0), args={}, kwargs={}, connection=None, opts={}, class_name=None, is_output_item=False):
        self.canvas = canvas
        self.app = canvas.app
        self.name = name
        self.obj = self.app.objects[name]
        self.connection = connection
        self.argspec = argspec(self.obj)#, withself=inspect.isclass(self.obj))

        self.args = vdict({},
            getitem=lambda key: self.getarg(key, "args"),
            setitem=self.setarg)

        self.kwargs = vdict({},
            getitem=lambda key: self.getarg(key, "kwargs"),
            setitem=self.setarg)

        self.opts = vdict({
            "show_kwargs": opts["show_kwargs"] if "show_kwargs" in opts else False,
            "sticky_graph": opts["sticky_graph"]  if "sticky_graph" in opts else  False,
            "line_color": opts["line_color"]  if "line_color" in opts else  Color.BLUE
        }, setitem=self.option)

        self.entry = Entry(self)
        self.is_callable = callable(self.obj)
        self.classname = class_name or classname(self.obj)
        self.show_wire = False
        self.method = None
        self.cached_value = None
        self.should_cache_value = True

        self.ids = {}
        x, y = coord
        width, height = self.dimensions(self.obj)
        node = NODE_SIZE * self.canvas.zoom
        create_parent = getattr(self.canvas, "create_" + ("rectangle" if callable(self.obj) or isinstance(self.obj, (str, list, dict)) else "oval"))

        self.ids["parent"] = create_parent(x - width/2, y - height/2, x + width/2, y + height/2,
            tags=("parent", "draggable", "name=" + self.name),
            outline=Color.INACTIVE,
            fill=Color.BLACK)

        self.ids["name"] = canvas.create_text(0,0,
            tags=("name", "draggable", "name=" + self.name, "font", "fontsize="+FONTSIZE["name"], "stop_scaling"),
            text=name or '',
            fill=Color.WHITE,
            font="Menlo 18")

        self.ids["class"] = canvas.create_text(0,0,
            tags=("class", "draggable", "name=" + self.name, "font", "fontsize="+FONTSIZE["argvalue"], "stop_scaling"),
            width=0,
            text=self.classname,
            fill=Color.BLUE)

        self.ids["output"] = canvas.create_oval(0,0,0,0,
            tags=("output", "name=" + self.name),
            outline=Color.INACTIVE,
            fill=Color.EMPTY_NODE)

        self.ids["wire"] = canvas.create_line(0,0,0,0,
            tags=("wire", "name=" + self.name, "scale_width"),
            fill=Color.INACTIVE,
            smooth=True,
            state="hidden",
            width=1)

        if not self.is_callable:
            self.ids["value"] = canvas.create_text(x,y,
                tags=("value", "draggable", "editable", "name=" + self.name, "argvalue=<value>", "font", "fontsize="+FONTSIZE["value"]),
                text=self.content(),
                fill=fontcolor(self.obj),
                font="Menlo 16")

            self.args.store["<value>"] = args["<value>"] if "<value>" in args else self.obj
            self.ids["arg=<value>"] = canvas.create_oval(0,0,0,0,
                tags=("input", "arg=<value>", "name=" + self.name),
                outline=Color.INACTIVE,
                fill=Color.EMPTY_NODE)
        else:
            num_args = len(self.argspec[0]) if not self.opts["show_kwargs"] else (len(self.argspec[0]) + len(self.argspec[1]))
            offset = ((2 * num_args) or 1 - height/2) * self.canvas.zoom
            i = 0 if num_args == 1 else (1 - num_args + 0.2)
            for j in self.argspec[0]:
                if j not in self.args:
                    self.args.store[j] = args[j] if j in args else None
                self.ids["arg=" + j] = canvas.create_oval(0,0,0,0,
                    tags=("input", "arg=" + j, "name=" + self.name),
                    outline=Color.INACTIVE,
                    fill=Color.EMPTY_NODE)

                self.ids["argname=" + j] = canvas.create_text(0,0,
                    tags=("name=" + self.name, "draggable", "font", "fontsize="+FONTSIZE["argname"]),
                    text=j,
                    fill=Color.DARK_ORANGE,
                    anchor="w")

                self.ids["argvalue=" + j] = canvas.create_text(0,0,
                    tags=("argvalue=" + j, "draggable", "editable", "name=" + self.name, "font", "fontsize="+FONTSIZE["argvalue"]),
                    text="None",
                    fill=Color.RED,
                    anchor="w")
                i += 2

            for k in self.argspec[1]:
                if k not in self.kwargs:
                    self.kwargs.store[k] = kwargs[k] if k in kwargs else self.argspec[1][k]
                self.ids["arg=" + k] = canvas.create_oval(0,0,0,0,
                    tags=("arg=" + k, "input", "name=" + self.name),
                    state="normal" if self.opts["show_kwargs"] else "hidden",
                    outline=Color.INACTIVE,
                    fill=Color.EMPTY_NODE)

                self.ids["argname=" + k] = canvas.create_text(0,0,
                    text=k,
                    tags=("name=" + self.name, "argname="+k, "draggable", "font", "fontsize="+FONTSIZE["argname"]),
                    state="normal" if self.opts["show_kwargs"] else "hidden",
                    fill=Color.ORANGE,
                    anchor="w")

                self.ids["argvalue=" + k] = canvas.create_text(0,0,
                    text=str(self.kwargs[k]),
                    tags=("argvalue=" + k, "draggable", "editable", "name=" + self.name, "font", "fontsize="+FONTSIZE["argvalue"]),
                    state="normal" if self.opts["show_kwargs"] else "hidden",
                    fill=fontcolor(self.kwargs[k]),
                    anchor="w")
                i += 2

        self.resize()
        if connection:
            output_name, output_arg = connection
            output = self.canvas[output_name]
            if output_arg in output.args:
                output.args[output_arg] = self
            else:
                output.kwargs[output_arg] = self
            self.move_wire()

        if is_output_item:
            self.app.node.output.connect(self)

    # REFACTOR - not crazy about this function having two purposes, should use .setvalue instead
    # TODO - indicate the error more clearly when the item.hasargs() is true but it raises an exception
    def value(self, obj=None):
        """
        item.value can be called in the following two ways, and has these two different purposes
            - (no args) returning the computed value of the item based on what it has plugged in
            - (has a single arg) changing the value of the underlying self.obj the item references

        If the item has arguments, but the function raises an exception, then it will fall back to 
        returning the __repr__ of that function.

        item.value is also responsible for detecting when the output needs to be transformed
        in whatever way is required by the plotting system, and in a way which is the most intuitive
        in the node editor for how it "should" work when you plug items together and try to plot them.
        
        For example, to plot sin(x) using x=linspace(0,1), this method will transform the value recieved
        by app.output, without affecting the underlying environment in the interpreter in any way.

        This ability of the item.value function to transform output can be used as a general purpose
        system for optimizing the layout of items in the node editor when plotting things.
        """
        if obj is None:
            if self.is_callable and self.hasargs():

                try:
                    result = self.obj(*[self.args[i] for i in self.args], **{ k: self.kwargs[k] for k in self.kwargs if self.kwargs.store[k] is not None })
                except Exception as err:
                    return self.obj

                # TODO - use a better system for detecting functions that are trying to be plotted
                if (self in self.canvas.output.items
                    and not isinstance(result, (int,float,complex))
                    and isinstance(result[0], (int,float))
                    and len(self.args) > 0
                ):
                    try:
                        arg = self.args[list(self.args.keys())[0]]
                        result = np.array([(arg[i],result[i]) for i in range(0,len(result))])
                    except Exception as err:
                        # print ("error", err)
                        pass

                return result
            return self.obj

        # if "<value>" in self.args["connection"]:
        #     self.args["connection"]["<value>"].disconnect()

        self.obj = obj
        if not self.is_callable:
            self.config("value", text=self.content())

        if self.connection:
            name, argname = self.connection
            if argname in self.canvas[name].args:
                self.canvas[name].args[argname] = self
            elif argname in self.canvas[name].kwargs:
                self.canvas[name].kwargs[argname] = self

        if self in self.canvas.output.items:
            self.canvas.output.update_value(self)

        self.move_wire()
        self.resize()

    def getarg(self, key, attr):
        params = getattr(self, attr).store
        if key == "connection":
            return { i: params[i] for i in params if isinstance(params[i], Item) }
        return params[key].value() if isinstance(params[key], Item) else params[key]

    def setarg(self, key, value):
        prev = self.args.store[key] if key in self.args["connection"] else self.kwargs.store[key] if key in self.kwargs["connection"] else None
        result = value
        if isinstance(value, Item):
            if value == self: return False

            if key == "<value>":
                try:
                    result = self.obj.__class__(value.value())
                except Exception as err:
                    result = value.value()
            else:
                result = value.value()
            value.connection  = self.name, key
            self.config("arg="+key, fill=Color.PURPLE)
            value.config("output", fill=Color.PURPLE)
            value.move_wire()

            x, y = self.position()
            x1, y1 = value.position()
            offset = self.canvas.zoom * 160
            if x1 + offset > x:
                value.move(-(x1 - x + offset), 0)
                for i in value.args["connection"]:
                    value.args["connection"][i].move(-(x1 - x + offset), 0)
                for i in value.kwargs["connection"]:
                    value.kwargs["connection"][i].move(-(x1 - x + offset), 0)

        if prev:
            if value is None:
                if key in self.args:
                    self.args.store[key] = self.args.store[key].value()
                elif key in self.kwargs:
                    self.kwargs.store[key] = self.kwargs.store[key].value()
                prev.disconnect()
                return False
            elif prev != value:
                prev.disconnect()

        if key == "<value>":
            self.app.objects[self.name] = result
        else:
            self.config("argvalue="+key, text=str(result)[:MAX_NUMBER_WIDTH], fill=fontcolor(result))

        self.app.objects.item(self.name + "<arg=" + key + ">",
            text=str(result),
            tags=("editable", fontcolor(result, as_string=True)))

        if self.connection:
            name, argname = self.connection
            item = self.canvas[name]
            if argname in item.args:
                item.args[argname] = self
            elif argname in item.kwargs:
                item.kwargs[argname] = self

        if self in self.canvas.output.items:
            if key in self.args:
                self.args.store[key] = value
            elif key in self.kwargs:
                self.kwargs.store[key] = value
            self.canvas.output.update_value(self)
            return False


    def disconnect(self):
        if self.connection:
            name, argname = self.connection
            self.connection = None
            item = self.canvas[name]
            if argname in item.args:
                item.args[argname] = None
            elif argname in item.kwargs:
                item.kwargs[argname] = None
            item.config("arg="+argname, fill=Color.EMPTY_NODE)
            self.config("output", fill=Color.EMPTY_NODE)
        self.move_wire()

    def option(self, key, value=None):
        value = value if value is not None else not self.opts[key]
        self.opts.store[key] = value
        if key == "line_color":
            color = str(value) or Color.BLUE
        elif key == "show_kwargs":
            for j in self.kwargs:
                for k in ("arg="+j, "argname="+j, "argvalue="+j):
                    self.config(k, state="normal" if self.opts["show_kwargs"] else "hidden")
            self.resize()
            self.move()
        return False

    def content(self, *args, truncate=True):
        obj = self.obj if not args else args[0]
        if callable(obj): return str(self.value())

        if isinstance(obj, dict):
            return pformat(obj, indent=4, width=MAX_NUMBER_WIDTH)

        result = fill(str(obj), width=TEXTWRAP_SIZE) if isinstance(obj, (str, list)) else str(obj)
        if not truncate:
            return result

        width = MAX_STR_WIDTH if isinstance(obj, (str, list)) else MAX_NUMBER_WIDTH
        return result if len(result) < width else result[:width] + "..."

    def resize(self, content=None):
        content = content if content is not None else self.content()
        try:
            x, y = self.position()
        except:
            return
        width, height = self.dimensions(content)
        node = NODE_SIZE * self.canvas.zoom

        self.coords("parent", x - width/2, y - height/2, x + width/2, y + height/2)
        self.coords("output", x + width/2 - node, y - node, x + width/2 + node, y + node)
        self.coords("name", x, y - height/2 - 20 * self.canvas.zoom)
        # self.canvas.scale_font()
        self.coords("class", x, y + height/2 + 20 * self.canvas.zoom)
        self.move_wire()

        num_args = len(self.argspec[0]) if not self.opts["show_kwargs"] else len(self.argspec[0]) + len(self.argspec[1])
        num_args = num_args or 1
        offset = 2 * num_args
        i = 0 if num_args == 1 else (1 - num_args + 0.2)
        for j in self.args.store:
            self.coords("arg="+j, x - width/2 - node, y - node + i*height/offset, x - width/2 + node, y + node + i*height/offset)
            self.coords("argname="+j, x - width/2 + 12*self.canvas.zoom, y + i*height/offset - 12*self.canvas.zoom)
            self.coords("argvalue="+j, x - width/2 + 12*self.canvas.zoom, y + i*height/offset)
            i += 2

        if not self.opts["show_kwargs"]: return
        for k in self.kwargs.store:
            self.coords("arg="+k, x - width/2 - node, y - node + i*height/offset, x - width/2 + node, y + node + i*height/offset)
            self.coords("argname="+k, x - width/2 + 12*self.canvas.zoom, y + i*height/offset - 12*self.canvas.zoom)
            self.coords("argvalue="+k, x - width/2 + 12*self.canvas.zoom, y + i*height/offset)
            i += 2


    def move(self, x=0, y=0, wires_only=False):
        if not wires_only:
            for i in self.children():
                self.canvas.move(i, x, y)

        if self.connection or self in self.canvas.output.items:
            self.move_wire()

        for j in self.args["connection"]:
            self.args.store[j].move_wire()

        for k in self.kwargs["connection"]:
            self.kwargs.store[k].move_wire()


    def move_wire(self, *coord):
        if not coord:
            if self in self.canvas.output.items or self == self.canvas.output.log_item:
                coord = (self.canvas.winfo_width(), self.canvas.winfo_height()/2)
            elif self.connection:
                x1, y1, x2, y2 = self.canvas.coords(self.canvas[self.connection[0]].ids["arg=" + self.connection[1]])
                coord = ((x1 + x2)/2, (y1 + y2)/2)
            else:
                self.hide_wire()
                return
        if not self.show_wire:
            self.show_wire = True
            self.config("output", fill=Color.PURPLE)
            self.config("wire", fill=Color.PURPLE, state="normal")

        x,y = coord
        try:
            x1, y1, x2, y2 = self.coords()
        except:
            return
        delta_x = x - (x1 + x2)/2
        node = NODE_SIZE * self.canvas.zoom
        self.coords("wire",
            x2, y1 + (y2 - y1)/2,
            x2 + delta_x /3, (y1 + y2)/2,
            x - delta_x/3, y,
            x - node,y
        )

    def hide_wire(self):
        self.config("wire", state="hidden")
        self.config("output", fill=Color.EMPTY_NODE)
        self.show_wire = False

    def hasargs(self):
        for i in self.args:
            if self.args[i] is None:
                return False
        return True

    def dimensions(self, obj):
        if self.is_callable:
            args, kwargs = self.argspec
            num_args = len(self.argspec[0]) if not self.opts["show_kwargs"] else len(self.argspec[0]) + len(self.argspec[1])
            width = 120 * self.canvas.zoom
            height = max(80, num_args * 6 * 6) * self.canvas.zoom
            return width, height

        char = self.text_dimensions(obj)
        width = min(300, 80 if len(str(obj)) <= 4 else char["width"] * FONT_SIZE) * self.canvas.zoom
        height = (60 + char["height"] * FONT_SIZE) * self.canvas.zoom

        return width, height

    def text_dimensions(self, obj, **kwargs):
        content = self.content(obj, **kwargs)

        if isinstance(obj, dict):
            return {
                "width": min(20, 1 + len(content or "")),
                "height": 1 + content.count("\n")
            }

        return {
            "width": min(20, 1 + len(content or "")),
            "height": 1 + int(len(content or "") / 20)
        }

    def children(self):
        return [self.ids[j] for j in self.ids]

    def config(self, *tags, **kwargs):
        if len(tags) == 1:
            return self.canvas.itemconfig(self.ids[tags[0]], **kwargs)

        for t in tags:
            self.canvas.itemconfig(self.ids[t], **kwargs)

    def coords(self, tag="parent", *args):
        if tag not in self.ids: return False
        return self.canvas.coords(self.ids[tag], *args)

    def position(self):
        x1, y1, x2, y2 = self.coords()
        return (x1 + x2)/2, (y1 + y2)/2

    def destroy(self):
        for i in self.children():
            self.canvas.delete(i)
        del self.canvas[self.name]
        del self
