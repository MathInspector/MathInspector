import numpy as np
import plot
from widget.popup import Popup

def hexstring(num):
    return '#' + str(hex(num))[2:].zfill(6)

class Animation:
	def __init__(self, app):
		self.app = app
		self.item = None
		self.is_running = False
		self.cache = {}

	def __call__(self, item):
		self.item = item

		Popup(self.app, [{
			"label": "start",
			"value": item.obj	
		},{
			"label": "stop",
			"value": item.obj + 10	
		},{
			"label": "delay",
			"value": 0.1		
		},{
			"label": "step",
			"value": 0.1
		}], self.start, "Animate Item", item.name)

	def start(self, params):
		self.is_running = True
		self.app.objects[self.item.name] = params["start"]
		if self.app.node.output.items:
			plot.animate(params["delay"], lambda: self._plot_update(params))
		else:
			self.run(self.item.name, params)

	def run(self, name, params):
		obj = self.app.objects[name]
		if self.is_running and (
			(params["step"] > 0 and obj < params["stop"]) 
			or (params["step"] < 0 and obj > params["stop"])
		):
			self.app.objects[name] += params["step"]
			self.app.after(int(params["delay"]*1000), lambda: self.run(name, params))
			return
		self.app.objects[name] = params["stop"]

	def _plot_update(self, params):
		name = self.item.name
		obj = self.app.objects[name]
		if self.is_running and (
			(params["step"] > 0 and obj < params["stop"]) 
			or (params["step"] < 0 and obj > params["stop"])
		):
			self.app.objects[name] += params["step"]
			self.app.update()
			return list(self.app.node.output.values.values())

		self.app.objects[name] = params["stop"]
		self.app.update()
		return False

	def pause(self):
		self.is_running = not self.is_running

