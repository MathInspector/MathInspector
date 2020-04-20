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
import numpy as np
from .canvas import PanZoomDragCanvas, Element
from math import sqrt
from util import random_color
from settings import Color, Zoom

OFFSET = 32
GRID_MARKS = 12

class SciPlot(PanZoomDragCanvas):
	def __init__(self, parent, *args, **kwargs):
		self.frame = tk.Frame(parent, background=Color.BACKGROUND)
		PanZoomDragCanvas.__init__(self, self.frame, draggable=False, highlightthickness=0, *args, **kwargs)
		self.cache = {}
		self.parent = parent
		self.key = None
		self.gridlines = []
		self.gridsize = 32 
		
		self.prev_val = [None, None]
		self.current_val = [None, None]
		self.x_axis_marker = None
		self.y_axis_marker = None
		self.x_axis_spacing = 1
		
		self.show_grid_lines = True
		self.smooth = "true"
		self.has_random_color = False
		self.line_color = Color.BLUE
		self.overlay_items = {}
		
		self.x_axis = tk.Canvas(self.frame, background=Color.BLACK, height=20, highlightthickness=0)
		self.y_axis = tk.Canvas(self.frame, background=Color.BLACK, width=20, highlightthickness=0)
		self.y_axis.pack(side="left", fill="both")
		self.x_axis.pack(side="bottom", fill="both")
		self.pack(fill="both", expand=True)
		self.bind("<Configure>", self._on_configure)

	def set_line_color(self, color):
		self.line_color = color

	def get_line_bounds(self, line, attr="real"):
		minimum = None
		maximum = None
		for i in line:
			if not minimum or getattr(i, attr) < minimum:
				minimum = getattr(i, attr)			
			if not maximum or getattr(i, attr) > maximum:
				maximum = getattr(i, attr)
		return maximum, minimum

	# TODO: make this work for non square grids
	def plot(self, points, key, color=Color.BLUE):
		# self.update_idletasks() 
		self.clear()
		self.zoom(1)
		# self.drawgrid()

		plot_items = [self.overlay_items[key] for key in self.overlay_items]
		if key not in self.overlay_items:
			plot_items.append({
				"points": points,
				"color": color
			})
	
		self.x_axis_marker = self.create_element("line", coords=(0,-0.05, 0, 0.05), fill=Color.PALE_BLUE)
		self.y_axis_marker = self.create_element("line", coords=(-0.05, 0, 0.05, 0), fill=Color.PALE_BLUE)
		coords = []
		minimum = 0
		maximum = 0
		prev_real = None
		prev_imag = None
		T = 1e-14
		line_coords = []

		for graph in plot_items:
			points = graph["points"]
			line_color = graph["color"]
			coords.clear()
			line_coords.clear()
			for orientation in points:
				if isinstance(orientation, (np.ndarray, list)):
					for line in orientation:
						if isinstance(line, (int,float)):
							line_coords.append(line if len(line_coords)%2 == 0 else -line)
						elif isinstance(line, (complex, np.complex)):
							coords.append(line.real)
							coords.append(-line.imag)
						elif isinstance(line[0], complex):
							for point in line:
								if point.real < minimum:
									minimum = point.real
								if point.real > maximum:
									maximum = point.real
								coords.append(point.real)
								coords.append(-point.imag)
							self.create_element("line", coords=coords, smooth=self.smooth, fill=graph["color"] if not self.has_random_color else random_color())
							coords.clear()
						elif isinstance(line, (np.ndarray, list)):
							if len(line) == 2:
								coords.append(line[0])
								coords.append(-line[1])
							else:
								for half_plane in line:
									if isinstance(half_plane, (np.ndarray, list)):
										for point in half_plane:
											if point.real < minimum:
												minimum = point.real
											if point.real > maximum:
												maximum = point.real
											coords.append(point.real)
											coords.append(-point.imag)
									self.create_element("line", coords=coords, smooth=self.smooth, fill=graph["color"] if not self.has_random_color else random_color())
									coords.clear()
						elif isinstance(line, tuple):
							coords.append(line)
					if coords:
						self.create_element("line", coords=coords, smooth=self.smooth, fill=graph["color"] if not self.has_random_color else random_color())
						coords.clear()
				elif isinstance(orientation, (int,np.int64, float)):
					self.create_element(coords=(orientation, 0), fill=graph["color"])
				elif isinstance(orientation, complex):
					self.create_element(coords=(orientation.real, -1 * orientation.imag), fill=graph["color"])
				elif isinstance(orientation, tuple):
					line_coords.append((orientation[0], -1 * orientation[1]))
			
			if line_coords:
				self.create_element("line", coords=line_coords, smooth=self.smooth, fill=graph["color"] if not self.has_random_color else random_color())

			if maximum == minimum == 0:
				maximum = 1
				minimum = -1


			self.key = key
			if key not in self.cache:
				self.cache[key] = {
					"zoomlevel": self.winfo_width() / abs(maximum - minimum),
					"delta": [self.winfo_width()/2,self.winfo_height()/2]
				}		

		self.zoom(self.cache[key]["zoomlevel"], (0,0))
		self.pan(self.cache[key]["delta"])
		self.drawgrid()

	def plot_pixels(self, pixels, bounds, key):
		pixel_width = len(pixels)
		pixel_height = len(pixels[0])
		coord_width = bounds[1] - bounds[0]
		coord_height = bounds[3] - bounds[2]
		size = coord_width / pixel_width
		for i in range(0, len(pixels)):
			row = pixels[i]
			for j in range(0, len(row)):
				if row[j] > 0:
					coords = (
						bounds[0] + i * size, bounds[2] + j * size,
						bounds[0] + (i+1)*size, bounds[2] + (j+1)*size,
					)
					# hmm I need to actually make bigger rectangles for when its 
					# a bunch of true's all next to each other to save memory
					# need a good idea of how to consolidate all the little rectangles into a few big ones
					# with a complicated bounday
					# @TODO: different colors based on value in grid
					self.create_element("rectangle", coords, Color.DARK_BLACK)

	def create_element(self, *args, **kwargs):
			item = Element(self, *args, **kwargs)
			self.items[item.id] = item
			self.canvas_ids.append({
				"canvas_id": item.id,
				"parent_id": None	
			})

			return item

	def overlay(self, key, points=None, color=Color.BLUE):
		if not points:
			del self.overlay_items[key]
			return

		self.overlay_items[key] = {
			"points": points,
			"color": color
		}

	def setstate(self, saved):
		self.cache = saved["cache"]
		self.key = saved["key"]
		# self.axis()

	def getstate(self):
		return {
			"cache": self.cache,
			"key": self.key
		}

	def cleargrid(self):
		for i in self.gridlines:
			self.delete(i)
		self.gridlines.clear()

	def gridmarks(self):
		return int(GRID_MARKS * self.winfo_width() / self.winfo_screenwidth()) or 1

	def drawgrid(self):
		if not self.show_grid_lines: return
		self.cleargrid()
		
		# xaxis, yaxis = (range(-self.gridsize, self.gridsize), range(-self.gridsize, self.gridsize))
		
		x0,y0 = self.cache[self.key]["delta"] if self.key else (0,0)
# push start of range over to same remainder trick as axis so 0 line is always there
		x_marks = self.winfo_width() / self.zoomlevel + 2
		x_spacing = int(x_marks / self.gridmarks()) or 1
		y_marks = self.winfo_height() / self.zoomlevel + 2
		y_spacing = int(y_marks / self.gridmarks()) or 1

		if x_marks < self.gridmarks():
			# print ("less than 0 transition")
			pass

		left_endpoint = -self.gridsize
		while left_endpoint % x_spacing != 0:
			left_endpoint += 1

		spacing = x_spacing
		xaxis, yaxis = range(left_endpoint, self.gridsize, spacing), range(left_endpoint, self.gridsize, spacing)

		for i in xaxis:
			x = i*self.zoomlevel + x0
			item = self.create_element("line", 
				(x, -self.gridsize*self.zoomlevel + y0, x, self.gridsize*self.zoomlevel + y0), fill=Color.BLACK if i != 0 else Color.LIGHT_BLACK)
			self.gridlines.append(item.id)
			self.tag_lower(item)
		
		for j in yaxis:
			y = j * self.zoomlevel + y0
			item = self.create_element("line", 
				(-self.gridsize * self.zoomlevel, y, self.gridsize * self.zoomlevel, y), fill=Color.BLACK if j != 0 else Color.LIGHT_BLACK)
			self.gridlines.append(item.id)
			self.tag_lower(item)

		for k in self.gridlines:
			self.tag_lower(k)

	def axis(self, event=None):
		if not self.key: return
		self.x_axis.delete("all")
		self.y_axis.delete("all")

		if event:
			self.cache[self.key]["delta"][0] += (self.current_val[0] - self.prev_val[0])	
			self.cache[self.key]["delta"][1] += (self.current_val[1] - self.prev_val[1])	

		xaxis, yaxis = self.range()

		for i in xaxis:
			self.x_axis.create_text(i*self.zoomlevel + self.cache[self.key]["delta"][0], 12, 
				fill=Color.PALE_BLUE, text=str(i), font="Nunito 12")

		for j in yaxis:
			y = j*self.zoomlevel + self.cache[self.key]["delta"][1]
			if 0 < y < self.winfo_height() - 20:
				self.y_axis.create_text(12, y, 
					fill=Color.PALE_BLUE, text=str(-j), font="Nunito 12")

		x_marks = self.winfo_width() / self.zoomlevel + 2
		x_spacing = int(x_marks / self.gridmarks()) or 1
		gridwidth = abs(xaxis[0] - xaxis[-1])
		if gridwidth < self.gridsize / 4:
			self.gridsize = int(self.gridsize / 2)
			self.drawgrid()				
		elif not gridwidth < self.gridsize:
			self.gridsize *= 2
			self.drawgrid()				

	def range(self):
		if not self.key:
			return range(-self.gridsize, self.gridsize), range(-self.gridsize, self.gridsize)

		x_marks = self.winfo_width() / self.zoomlevel + 2
		x_spacing = int(x_marks / self.gridmarks()) or 1
		left_endpoint = int(-1 * self.cache[self.key]["delta"][0] / self.zoomlevel) - 1
		right_endpoint = int(x_marks + left_endpoint)
		while left_endpoint % x_spacing != 0:
			left_endpoint += 1
		
		y_marks = self.winfo_height() / self.zoomlevel + 2
		y_spacing = int(y_marks / self.gridmarks()) or 1
		bottom_endpoint = int(-1 * self.cache[self.key]["delta"][1] / self.zoomlevel) - 1
		top_endpoint = int(y_marks + bottom_endpoint)
		while bottom_endpoint % y_spacing != 0:
			bottom_endpoint += 1

		return range(left_endpoint, right_endpoint, x_spacing), range(bottom_endpoint, top_endpoint, y_spacing)



	def clear(self):
		super(SciPlot, self).clear()
		self.key = None
		self.x_axis.delete("all")
		self.y_axis.delete("all")

	def _on_mouse_wheel(self, event):
		if not self.key:
			return super(SciPlot, self)._on_mouse_wheel(event)
		
		self.prev_val[0] = self.x_axis_marker.canvas.coords(self.x_axis_marker.id)[0]
		self.prev_val[1] = self.y_axis_marker.canvas.coords(self.y_axis_marker.id)[1]
		super(SciPlot, self)._on_mouse_wheel(event)
		self.current_val[0] = self.x_axis_marker.canvas.coords(self.x_axis_marker.id)[0]
		self.current_val[1] = self.y_axis_marker.canvas.coords(self.y_axis_marker.id)[1]
		if self.key:
			self.cache[self.key]["zoomlevel"] = self.zoomlevel
			self.axis(event)

	def _on_b2_motion(self, event):
		if self.key == None: return super(SciPlot, self)._on_b2_motion(event)
	
		self.cache[self.key]["delta"][0] += event.x - self.pan_position[0]
		self.cache[self.key]["delta"][1] += event.y - self.pan_position[1]
		self.axis()
		super(SciPlot, self)._on_b2_motion(event)

	def center(self, points, key=None, bounds=None):
		bounds = bounds or self.getbounds(points)
		width = bounds[1] - bounds[0]
		height = bounds[3] - bounds[2]
		
		if width > height:
			zoomlevel = self.winfo_width() / width
		else:
			zoomlevel = self.winfo_height() / height

		origin = (bounds[0] + width / 2, bounds[2] + height / 2)
		delta = [self.winfo_width() / 2 - OFFSET, self.winfo_height() / 2 - OFFSET]
	
		if key in self.cache:
			self.zoom(self.cache[key]["zoomlevel"], origin)
			self.pan(self.cache[key]["delta"])
		else:
			self.zoom(zoomlevel, origin)
			self.pan(delta)
			self.cache[key] = {
				"zoomlevel": zoomlevel,
				"delta": delta
			}
		self.axis()

	def getbounds(self, points):
		result = [0,0,0,0]

		for i in points:
			if i[0] < result[0]:
				result[0] = i[0]
			if i[0] > result[1]:
				result[1] = i[0]
			if i[1] < result[2]:
				result[2] = i[1]
			if i[1] > result[3]:
				result[3] = i[1]

		return result

	def _on_configure(self, event):
		print ("on configure")
		if self.key:
			# self.drawgrid()
			self.axis()