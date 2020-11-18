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

from settings import Color, Font, Widget 
from util import get_class_name, get_font_color, argspec
from .entry import Entry
from textwrap import fill
from pprint import pformat
import tkinter as tk
import inspect, math
import numpy as np

MAX_LEN = 10
MAX_STR_LEN = 200
TEXTWRAP_WIDTH = 28
LABEL_OFFSET = 32
ARG_VALUE_OFFSET = 2
ARG_VALUE_MARGIN = 0

class Item:
    def __init__(self, canvas, value, name, coord=(0,0), zoomlevel=1):
        self.canvas = canvas
        self.name = name
        self.value = value
        self.args = {}     
        self.kwargs = {}  
        self.argspec = None   
        self.canvasentry = Entry(self)
        self.output_connection = None
        self.children = []
        self.show_kwargs = False
        self.sticky_graph = False 
        self.line_color = Color.BLUE

        self.argspec = argspec(value)
        if self.argspec and callable(value):
            args, kwargs = self.argspec

            height = 700
            self.canvas_id = canvas.create_rectangle(coord[0] - Widget.ITEM_SIZE/2,coord[1] - height/2,coord[0] + Widget.ITEM_SIZE/2,coord[1] + height/2, 
                outline=Color.INACTIVE, fill=Color.BLACK, tags='draggable')

            for j in args:
                self.args[j] = {
                    "input": canvas.create_oval(0,0,0,0, outline=Color.INACTIVE, fill=Color.EMPTY_NODE, tags='input'),
                    "label": canvas.create_text(0,0, fill=Color.DARK_ORANGE),
                    "value_label": canvas.create_text(0,0, tags=("draggable", "editable"), anchor="w"),
                    "value": None,
                    "connection": None
                }
                for k in ("input", "label", "value_label"):
                    self.children.append(self.args[j][k])

            state = "normal" if self.show_kwargs else "hidden"
            for j in kwargs:
                self.kwargs[j] = {
                    "input": canvas.create_oval(0,0,0,0, outline=Color.INACTIVE, fill=Color.EMPTY_NODE, tags='input', state=state),
                    "label": canvas.create_text(0,0, fill=Color.ORANGE, state=state),
                    "value_label": canvas.create_text(0,0, text=str(kwargs[j]), tags=("draggable", "editable"), anchor="w", state=state),
                    "value": kwargs[j],
                    "connection": None                    
                }
                for k in ("input", "label", "value_label"):
                    self.children.append(self.kwargs[j][k])

        else:
            fn = value.__class__ 
            if isinstance(value, (str, list, dict)):
                self.canvas_id = canvas.create_rectangle(coord[0] - Widget.ITEM_SIZE/2,coord[1] - Widget.ITEM_SIZE/2,coord[0] + Widget.ITEM_SIZE/2,coord[1] + Widget.ITEM_SIZE/2, outline=Color.INACTIVE,fill=Color.BLACK, tags='draggable')
            else:
                self.canvas_id = canvas.create_oval(coord[0] - Widget.ITEM_SIZE/2,coord[1] - Widget.ITEM_SIZE/2,coord[0] + Widget.ITEM_SIZE/2,coord[1] + Widget.ITEM_SIZE/2, outline=Color.INACTIVE,fill=Color.BLACK, tags='draggable')
            self.args["default"] = {
                "input": canvas.create_oval(0,0,0,0, outline=Color.INACTIVE, fill=Color.EMPTY_NODE, tags='input'),
                "connection": None
            }
            self.children.append(self.args["default"]["input"])
                
        self.output = canvas.create_oval(0,0,0,0, outline=Color.INACTIVE, fill=Color.EMPTY_NODE, tags="output")
        self.output_wire = canvas.create_line(0,0,0,0, fill=Color.INACTIVE, tags="output_wire", smooth=True)
        self.value_label = canvas.create_text(0,0, tags=('draggable', 'editable'))
        self.variable_label = canvas.create_text(0,0, text=name or '', fill=Color.WHITE, tags='draggable')
        self.class_label = canvas.create_text(0,0, fill=Color.RED, tags='draggable')
        
        for j in ("output", "output_wire", "value_label", "variable_label", "class_label"):
            self.children.append(getattr(self, j))

        self.set_value(value)
        self.zoom()

    def set_value(self, value):
        self.value = value
        x,y = self.get_position()
        node_size = Widget.NODE_SIZE*self.canvas.zoomlevel
        self.canvas.itemconfig(self.class_label, text=get_class_name(value))
        num_args = len(self.args)
        if self.show_kwargs:
            num_args += len(self.kwargs)

        if callable(self.value):
            self.canvas.itemconfig(self.value_label, outline=None)
            height = self.canvas.zoomlevel * max(Widget.ITEM_SIZE, num_args * 6 * Widget.NODE_SIZE) # @TODO: change this to adjust height and pretty print various things like list/dict/long strings
            width =  self.canvas.zoomlevel * 120
        else:
            if isinstance(self.value, (str, list, dict)):
                if isinstance(self.value, dict):
                    value_text = pformat(self.value, width=4)[1:-1]
                    max_len = 0
                    for j in self.value:
                        length = 8 + len(j) + len(str(self.value[j]))                      
                        max_len = length if length > max_len else max_len
                    width =  self.canvas.zoomlevel * min(12 * len(value_text), 16 + max(Widget.ITEM_SIZE, max_len * 8))
                else:
                    str_text = str(self.value)
                    sample_text = str_text if len(str_text) <= MAX_STR_LEN else str_text[:MAX_STR_LEN - 10] + " ... " + str_text[-10:]                    
                    value_text = fill(sample_text, TEXTWRAP_WIDTH, replace_whitespace=False)
                    width =  self.canvas.zoomlevel * max(Widget.ITEM_SIZE, 16 + 8 * min(len(value_text), TEXTWRAP_WIDTH))
                
                height = self.canvas.zoomlevel * max(Widget.ITEM_SIZE, 16 + 20 * (1 + value_text.count("\n"))) # @TODO: change this to adjust height and pretty print various things like list/dict/long strings
            else:
                value_text = str(self.value) if len(str(self.value) or "") <= MAX_LEN else str(self.value)[:MAX_LEN] + "..."
                width =  self.canvas.zoomlevel * (20 + max(60, len(value_text) * 12))
                height = self.canvas.zoomlevel * Widget.ITEM_SIZE # @TODO: change this to adjust height and pretty print various things like list/dict/long strings

            self.canvas.itemconfig(self.value_label, text=str(value_text), fill=get_font_color(self.value))

        offset = 2 * num_args
        if num_args == 1:
            i = 0
        else:
            i = 1 - num_args + 0.2

        for j in self.args:
            self.canvas.coords(self.args[j]["input"], x - width/2 - node_size, y + i*height/offset - node_size, x - width/2 + node_size, y + i*height/offset + node_size)

            if "label" in self.args[j]:
                value_text = self.args[j]["value"] if len(str(self.args[j]["value"]) or "") <= MAX_LEN else str(self.args[j]["value"])[:MAX_LEN] + "..."
                value_offset = 12
                self.canvas.coords(self.args[j]["label"], x - width/2 + 20*self.canvas.zoomlevel, y + i*height/offset - 12*self.canvas.zoomlevel)
                self.canvas.itemconfig(self.args[j]["label"], text=j, font=Font.ALT + " " + str(int(Widget.ARG_LABEL_SIZE * self.canvas.zoomlevel)))            
                self.canvas.coords(self.args[j]["value_label"], x - width/2 + value_offset*self.canvas.zoomlevel, y + i*height/offset)
                
                color = Color.BLUE if self.args[j]["connection"] else get_font_color(self.args[j]["value"])
                self.canvas.itemconfig(self.args[j]["value_label"], text=str(value_text), fill=color, font=Font.ALT + " " + str(int(Widget.ARG_VALUE_SIZE * self.canvas.zoomlevel)))

            i += 2

        if self.show_kwargs:
            for j in self.kwargs:
                self.canvas.coords(self.kwargs[j]["input"], x - width/2 - node_size, y + i*height/offset - node_size, x - width/2 + node_size, y + i*height/offset + node_size)

                if "label" in self.kwargs[j]:
                    value_text = str(self.kwargs[j]["value"]) if len(str(self.kwargs[j]["value"]) or "") <= MAX_LEN else str(self.kwargs[j]["value"])[:MAX_LEN] + "..."
                    value_offset = 12
                    self.canvas.coords(self.kwargs[j]["label"], x - width/2 + 20*self.canvas.zoomlevel, y + i*height/offset - 12*self.canvas.zoomlevel)
                    self.canvas.itemconfig(self.kwargs[j]["label"], text=j, font=Font.ALT + " " + str(int(Widget.ARG_LABEL_SIZE * self.canvas.zoomlevel)))            
                    self.canvas.coords(self.kwargs[j]["value_label"], x - width/2 + value_offset*self.canvas.zoomlevel, y + i*height/offset)
                    self.canvas.itemconfig(self.kwargs[j]["value_label"], text=value_text, fill=get_font_color(self.kwargs[j]["value"]), font=Font.ALT + " " + str(int(Widget.ARG_VALUE_SIZE * self.canvas.zoomlevel)))

                i += 2

        self.canvas.coords(self.canvas_id, x - width/2, y - height/2, x + width/2, y + height/2)
        self_x,self_y = self.get_position()
        self.canvas.coords(self.output, x + width/2 - node_size, self_y - node_size, x + width/2 + node_size, self_y + node_size)
        self.canvas.coords(self.value_label, x, y)        
        self.canvas.coords(self.class_label, x, y + height/2 + self.canvas.zoomlevel * LABEL_OFFSET)
        
        if self.variable_label:
            self.canvas.coords(self.variable_label, x, y - height / 2 - self.canvas.zoomlevel * LABEL_OFFSET)    

        if self.output_connection:
            name = self.output_connection.getarg("connection", self, name=True)
            if name in self.output_connection.args:
                x1,y1,x2,y2 = self.canvas.coords(self.output_connection.args[name]["input"])
            elif name in self.output_connection.kwargs:
                x1,y1,x2,y2 = self.canvas.coords(self.output_connection.kwargs[name]["input"])
            else:
                print ("WHOOPS!!!")
                return
            self.move_wire(x1 + (x2 - x1)/2, y1 + (y2 - y1)/2)
            self.output_connection.setarg(name, self.get_output())
        for j in self.args:
            if self.args[j]["connection"]:
                x1,y1,x2,y2 = self.canvas.coords(self.args[j]["input"])
                self.args[j]["connection"].move_wire(x1 + (x2 - x1)/2, y1 + (y2 - y1)/2)

        if self.sticky_graph:
            self.toggle_sticky()
            self.toggle_sticky()

        self.canvas.app.output.update(self.name)

    def methods(self):
        return [fn for fn in dir(self.value) if fn[:1] != "_" and callable(getattr(self.value, fn))]

    def getarg(self, key, item, name=False):
        for j in self.args:
            if key in self.args[j] and self.args[j][key] == item:
                if name: return j
                return self.args[j]
        for j in self.kwargs:
            if key in self.kwargs[j] and self.kwargs[j][key] == item:
                if name: return j
                return self.kwargs[j]

    def setarg(self, name, value):
        if name in self.args:
            self.args[name]["value"] = value
            if "value_label"  in self.args[name]:
                text = str(value) if len(str(value)) <= MAX_LEN else str(value)[:MAX_LEN] + "..."
                self.canvas.itemconfig(self.args[name]["value_label"], text=text, fill=get_font_color(value) )
        elif name in self.kwargs:
            self.kwargs[name]["value"] = value
            if "value_label" in self.kwargs[name] and self.show_kwargs:
                text = str(value) if len(str(value)) <= MAX_LEN else str(value)[:MAX_LEN] + "..."
                self.canvas.itemconfig(self.kwargs[name]["value_label"], text=text, fill=get_font_color(value) )
        
        self.canvas.app.objecttree.update(self.name)
        self.canvas.app.output.update(self.name)
        
        if self.output_connection:
            if callable(self.output_connection.value):
                self.canvas.app.update(self.name)
            else:
                try:
                    output = self.get_output(raise_err=True)
                except Exception as err:
                    self.canvas.log.show(err)
                    return
                
                self.canvas.app.objects.__setitem__(self.output_connection.name, output, preserve_class=True)

    def hasargs(self):
        for i in self.args:
            if "value" in self.args[i] and self.args[i]["value"] is None:
                return False
        return True

    def toggle_sticky(self):
        self.sticky_graph = not self.sticky_graph
        if self.sticky_graph:
            self.canvas.app.output.overlay(self)
        else:
            self.canvas.app.output.overlay(self, remove=True)

    def set_color(self, color):
        if not color:
            color = Color.BLUE

        color = str(color)
        if color[:1] != "#":
            color = "#" + color
        self.line_color = color
        self.canvas.app.output.select(self.name)
        if self.sticky_graph:
            self.toggle_sticky()
            self.toggle_sticky()


    def toggle_kwargs(self):
        self.show_kwargs = not self.show_kwargs
        state = "normal" if self.show_kwargs else "hidden"
        for j in self.kwargs:
            self.canvas.itemconfig(self.kwargs[j]["input"], state=state)

            if "label" in self.kwargs[j]:
                self.canvas.itemconfig(self.kwargs[j]["label"], state=state)            
                self.canvas.itemconfig(self.kwargs[j]["value_label"], state=state)

        self.set_value(self.value)

    def get_input(self):
        args = [self.args[j]["value"] for j in self.args if "value" in self.args[j] and self.args[j]["value"] is not None]
        kwargs = { j : self.kwargs[j]["value"] for j in self.kwargs if "value" in self.kwargs[j] }
        return args, kwargs

    def get_output(self, raise_err=False):
        if callable(self.value):
            try:
                args, kwargs = self.get_input()
                # print (self.value, len(args), kwargs)
                return self.value(*args, **kwargs)
            except Exception as err:
                if raise_err:
                    raise err
                else:
                    print ("item.get_output err", err)
                    return self.value
                pass
        return self.value

    def zoom(self):
        zoomlevel = self.canvas.zoomlevel
        font_size = str(Widget.VARIABLE_LABEL_SIZE) if zoomlevel < 1 else str(int(zoomlevel * Widget.VARIABLE_LABEL_SIZE))        
        self.canvasentry.config(font=Font.ALT + ' ' + str(int(Widget.VALUE_LABEL_SIZE * zoomlevel) or 1))
        self.canvas.itemconfig(self.value_label, font=Font.ALT + ' ' + str(int(Widget.VALUE_LABEL_SIZE * zoomlevel) or 1) )
        self.canvas.itemconfig(self.variable_label, font=Font.ALT + ' ' + font_size)
        self.canvas.itemconfig(self.output_wire, width=zoomlevel + 1)
        self.canvas.itemconfig(self.class_label, font=Font.ALT + ' ' + str(int(Widget.CLASS_LABEL_SIZE * zoomlevel) or 1) )
        for j in self.args:
            if "label" in self.args[j]:
                self.canvas.itemconfig(self.args[j]["label"], font=Font.ALT + " " + str(int(Widget.ARG_LABEL_SIZE * zoomlevel) or 1))
            if "value_label" in self.args[j]:
                self.canvas.itemconfig(self.args[j]["value_label"], font=Font.ALT + " " + str(int(Widget.ARG_VALUE_SIZE * zoomlevel) or 1))
        for j in self.kwargs:
            if "label" in self.kwargs[j]:
                self.canvas.itemconfig(self.kwargs[j]["label"], font=Font.ALT + " " + str(int(Widget.ARG_LABEL_SIZE * zoomlevel) or 1))
            if "value_label" in self.kwargs[j]:
                self.canvas.itemconfig(self.kwargs[j]["value_label"], font=Font.ALT + " " + str(int(Widget.ARG_VALUE_SIZE * zoomlevel) or 1))

    def get_position(self, dimensions=False):
        coords = self.canvas.coords(self.canvas_id) #(self.position[0] + delta_x, self.position[1] + delta_y)
        width = math.fabs(coords[2] - coords[0])
        height = math.fabs(coords[1] - coords[3])
        x,y = coords[0] + width/2, coords[1] + height/2
        if dimensions: return x,y,width,height
        return x,y

    def move(self, delta_x=0, delta_y=0):
        self.canvas.move(self.canvas_id, delta_x, delta_y)
        
        for canvas_id in self.children: 
            self.canvas.move(canvas_id, delta_x, delta_y)

        for j in self.args:
            if self.args[j]["connection"]:
                x1, y1, x2, y2 = self.canvas.coords(self.args[j]["input"])
                self.args[j]["connection"].move_wire(x1 + (x2 - x1)/2, y1 + (y2 - y1)/2)
            
        for j in self.kwargs:
            if self.kwargs[j]["connection"]:
                x1, y1, x2, y2 = self.canvas.coords(self.kwargs[j]["input"])
                self.kwargs[j]["connection"].move_wire(x1 + (x2 - x1)/2, y1 + (y2 - y1)/2)
            
        if self.output_connection:
            arg = self.output_connection.getarg("connection", self)
            if arg:
                x1, y1, x2, y2 = self.canvas.coords(arg["input"])
                self.move_wire(x1 + (x2 - x1)/2, y1 + (y2 - y1)/2)
   
    def move_wire(self, x,y):
        self_x,self_y,width,height = self.get_position(dimensions=True)
        delta_x = x - self_x
        self.canvas.coords(self.output_wire,
            self_x + width/2, self_y,
            self_x + delta_x /3 + width/2, self_y, 
            x - delta_x/3, y,
            x,y
        )

    def destroy(self):
        for j in [self.canvas_id] + self.children:
            self.canvas.delete(j)
        del self

    def tag_raise(self):
        self.canvas.tag_raise(self.canvas_id)
        for c in self.children:
            self.canvas.tag_raise(c)

    def set_output_connection(self, other=None, input_id=None):
        if other and not input_id: return

        if not other and self.output_connection:
            idx = self.output_connection.getarg("connection", self, name=True)
            if idx in self.output_connection.args:
                if idx == "default":
                    self.canvas.add_tag(self.output_connection.value_label, "editable")
                else:
                    self.canvas.add_tag(self.output_connection.args[idx]["value_label"], "editable")

                self.output_connection.args[idx]["connection"] = None
            if idx in self.output_connection.kwargs:
                self.canvas.add_tag(self.output_connection.kwargs[idx]["value_label"], "editable")
                self.output_connection.kwargs[idx]["connection"] = None
            self.config(hide_wire=True)
            self.output_connection.config(border="hide")
            self.output_connection = None
            return    

        if other:
            self.canvas.tag_raise(self.output_wire)
            self.output_connection = other
            for j in other.args:
                if other.args[j]["input"] == input_id:
                    other.args[j]["connection"] = self
                    if j == "default":
                        self.canvas.remove_tag(other.value_label, "editable")
                    else:
                        self.canvas.remove_tag(other.args[j]["value_label"], "editable")
            for j in other.kwargs:
                if other.kwargs[j]["input"] == input_id:
                    self.canvas.remove_tag(other.kwargs[j]["value_label"], "editable")
                    other.kwargs[j]["connection"] = self
            self.canvas.itemconfig(self.output, fill=Color.ACTIVE_WIRE)
            self.canvas.itemconfig(self.output_wire, fill=Color.ACTIVE_WIRE)
            self.canvas.itemconfig(input_id, fill=Color.ACTIVE_WIRE)
            self.config(border="show")
            self.output_connection.config(border="show", connect="default")

            self.canvas.app.update(self.name)
            if self.output_connection:
                self.canvas.app.output.select(self.output_connection.name)

        self.move()


    def config(self, hover=None, hover_editable=None, hide_wire=None, fill=None, border=None, output=None, hide_input=None, disconnect=None, connect=None):
        if hover:
            self.canvas.itemconfig(self.output, fill=hover)
            self.canvas.itemconfig(self.output_wire, fill=hover)
            if self.output_connection:
                arg = self.output_connection.getarg("connection", self)
                self.canvas.itemconfig(arg["input"], fill=hover)          
        
        if hover_editable:
            state, item = hover_editable
            arg = None
            if item == self.value_label:
                canvas_id = self.value_label
            elif item:
                arg = self.getarg("value_label", item)
                if arg:
                    canvas_id = arg["value_label"]
                else:
                    return
            else:
                return
            self.canvas.itemconfig(canvas_id, fill=Color.GREY if state == "enter" else get_font_color(arg["value"] if arg else self.value))
        
        if hide_wire:
            self.canvas.coords(self.output_wire,0,0,0,0)
            self.canvas.itemconfig(self.output, fill=Color.EMPTY_NODE)        
            if self.output_connection:
                self.output_connection.config(hide_input=True)
                # self.set_output_connection(None)
        
        if fill:
            self.canvas.itemconfig(self.canvas_id, fill=fill)
        
        if border:
            if border == "hide":
                color = Color.ACTIVE if self.output_connection else Color.INACTIVE        
                self.canvas.itemconfig(self.canvas_id, outline=color)
                self.canvas.itemconfig(self.output, outline=color)
                for j in self.args:
                    self.canvas.itemconfig(self.args[j]["input"], outline=color)
            else:
                self.canvas.itemconfig(self.canvas_id, outline=Color.ACTIVE)
                self.canvas.itemconfig(self.output, outline=Color.ACTIVE)
                for j in self.args:
                    if (self.args[j]["connection"] 
                            or "value" not in self.args[j] 
                            or (isinstance(self.args[j]["value"], np.ndarray) 
                            and self.args[j]["value"].any()) or self.args[j]["value"]):
                        self.canvas.itemconfig(self.args[j]["input"], outline=Color.ACTIVE)
        
        if output:
            self.canvas.itemconfig(self.output, fill=output)
            self.canvas.itemconfig(self.output_wire, fill=output)
        
        if hide_input:
            if "default" in self.args:
                self.canvas.itemconfig(self.args["default"]["input"], fill=Color.EMPTY_NODE)
        
        if disconnect:
            if "default" in self.args:
                self.canvas.itemconfig(self.value_label, fill=get_font_color(self.value))
            else:
                for i in self.args:
                    if disconnect == self.args[i]["input"]:
                        self.canvas.itemconfig(self.args[i]["value_label"], fill=get_font_color(self.args[i]["value"]))
            
            if disconnect in self.args:
                self.canvas.itemconfig(self.args[disconnect]["value_label"], fill=Color.BLUE)
            elif disconnect in self.kwargs:
                self.canvas.itemconfig(self.kwargs[disconnect]["value_label"], fill=Color.BLUE)
