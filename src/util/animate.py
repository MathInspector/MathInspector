from .misc import hexstring

class Animate():
	def __init__(self, app):
		self.app = app
		self.cache = {}

	def timer(self, key, **kwargs):		
		if "timer_running" not in kwargs:
			kwargs["timer_running"] = True
			self.cache[key] = {i:kwargs[i] for i in kwargs}

		if kwargs["step"] > 0 and kwargs["start"] >= kwargs["stop"] or kwargs["step"] < 0 and kwargs["start"] <= kwargs["stop"]: 
			return
		
		if kwargs["colorchange"]:
			kwargs["color"] += 1		
			self.app.output.canvas.set_line_color( hexstring(kwargs["color"]) )

		self.app.objects[key] = max(kwargs["start"] + kwargs["step"], kwargs["stop"]) if kwargs["step"] < 0 else min(kwargs["start"] + kwargs["step"], kwargs["stop"])
		kwargs["start"] += kwargs["step"]
		self.app.after(kwargs["delay"], lambda: self.timer(key, **kwargs))
