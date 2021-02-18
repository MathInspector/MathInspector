"""
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
import pygame, os, platform
import numpy as np
import multiprocessing as mp
from .config import *
from .util import instanceof, is_iterable
from pygame.locals import *
from pygame._sdl2.video import Window

OPTIONS = {
	"title": "Math Inspector",
	"show_grid": True,
	"show_range": False,
	"resolution": 1,
	"size": (1280, 720),
	"position": None,
	"step": 1/128,
	"timeout": 1,
	"on_update": None,
	"on_close": None,
	"pixelmap": None,
	"window_pos": None,
	"fontsize": 12
}

class SDLWindow:
	def __init__(self):
		self.zoom = 1
		self.screen = None
		self.font = None
		self.is_animation_running = False
		self.scale = 1
		self.args = []
		self.spacing = 1 / OPTIONS["step"]
		if platform.system() not in ("Windows", "Linux"):
			self.ctx = mp.get_context(MULTIPROCESS_CONTEXT)
			self.queue = self.ctx.Queue()

	def get_pixels(self, res, size):
		x0, y0 = OPTIONS["position"]
		w, h = OPTIONS["size"]
		step = OPTIONS["step"]
		return OPTIONS["pixelmap"](((-x0+w/2)*step, (y0-h/2)*step), (w*size*step,h*size*step), res*step)

	def draw_pixels(self):
		w,h = OPTIONS["size"]
		pix = self.get_pixels(1,1)
		pygame.surfarray.blit_array(self.screen, pix[0:w,0:h])
		if OPTIONS["show_grid"]:
			self.draw_grid()
		for values in self.args:
			self.draw_values(values)
		if OPTIONS["show_range"]:
			self.draw_range()
		pygame.display.flip()

	def update_offscreen(self, res=1, size=3):
		if self.is_processing or platform.system() in ("Windows", "Linux"): return
		self.is_processing = True
		w,h = OPTIONS["size"]
		self.coords.append([w/self.pan_res,h/self.pan_res,res])
		process = self.ctx.Process(target=self.process_target, args=(res,size))
		process.start()

	def process_target(self, res, size):
		self.queue.put(self.get_pixels(res,size))

	def plot(self, *args, **kwargs):
		self.args = args
		OPTIONS.update(kwargs)
		w, h = OPTIONS["size"]

		pygame.init()
		pygame.display.set_caption(OPTIONS["title"])
		self.screen = pygame.display.set_mode((w,h), pygame.RESIZABLE)

		# TODO - get position from OPTIONS
		if not OPTIONS["position"]:
			OPTIONS["position"] = w/2, h/2
		x0, y0 = OPTIONS["position"]

		is_running = True
		is_focused = True
		did_change = True
		offscreen_surf = None
		self.pan_res = 1
		pixels = None
		self.coords = [[w/3, h/3, self.pan_res]]
		mode = None
		self.is_processing = False
		timer = 0
		animation_timer = 0
		request_quit = False
		last_tick = 0
		clock = pygame.time.Clock()

		if OPTIONS["on_update"]:
			OPTIONS["on_update"]()

		if OPTIONS["pixelmap"]:
			offscreen_surf = pygame.Surface((0,0))
			offscreen_size = offscreen_surf.get_size()
			try:
				self.draw_pixels()
			except Exception as err:
				if OPTIONS["on_close"]:
					OPTIONS["on_close"]()
				pygame.display.quit()
				print (err)
				return
			self.update_offscreen()
			did_change = False

		while is_running:
			tick = pygame.time.get_ticks()/1000
			delta_time = tick - last_tick
			last_tick = tick

			keypress = pygame.key.get_pressed()
			for event in pygame.event.get(pump=False):
				if event.type == pygame.ACTIVEEVENT:
					is_focused = bool(event.gain)
					# is_focused = not bool(event.state)
				elif event.type == pygame.VIDEORESIZE:
					did_change = True
					OPTIONS["size"] = w, h = pygame.display.get_surface().get_size()
				elif event.type == pygame.MOUSEMOTION:
					if event.buttons[2]:
						did_change = True
						mode = "pan"
						x0 += event.rel[0]
						y0 += event.rel[1]
						for i, val in enumerate(self.coords):
							self.coords[i][0] -= event.rel[0]/val[2]
							self.coords[i][1] -= event.rel[1]/val[2]
				elif event.type == pygame.MOUSEWHEEL:
					did_change = True
					mode = "zoomin" if event.y > 0 else "zoomout"
					delta = event.y*ZOOM_MODIFIER/SPACING
					self.zoom *= 1 + delta
					x, y = pygame.mouse.get_pos()
					x0 += delta*(x0 - x)
					y0 += delta*(y0 - y)

					for i, val in enumerate(self.coords):
						self.coords[i][2] *= 1 + delta
						self.coords[i][0] += x*delta/val[2]
						self.coords[i][1] += y*delta/val[2]

					if self.scale * self.zoom > 1:
						self.scale /= 2
					elif self.scale * self.zoom < 1/2:
						self.scale *= 2
					self.spacing = self.scale * self.zoom * SPACING
				elif event.type == pygame.USEREVENT:
					if hasattr(event, "args") and event.args:
						self.args = event.args
					elif hasattr(event, "kwargs"):
						OPTIONS.update(event.kwargs)
						if "pixelmap" in kwargs:
							self.draw_pixels()
							offscreen_surf.fill(BACKGROUND)
							self.update_offscreen()
					elif hasattr(event, "animate"):
						delay = event.animate[0]
						callback = event.animate[1]
						self.is_animation_running = True
					did_change = True
				elif (event.type == pygame.QUIT
					or (event.type == KEYUP and event.key == K_ESCAPE)
					or (event.type == KEYUP and event.key == K_w and keypress[K_LMETA])
					or (event.type == KEYUP and event.key == K_q and keypress[K_LMETA])
				):
					request_quit = True

			if OPTIONS["on_update"] and not is_focused:
				OPTIONS["on_update"]()

			if self.is_animation_running:
				if animation_timer >= delay:
					animation_timer = 0
					values = callback()
					if values:
						self.args = values
						did_change = True
					else:
						self.is_animation_running = False
				else:
					animation_timer += delta_time

			if platform.system() not in ("Windows", "Linux"):
				if not self.queue.empty():
					pixels = self.queue.get()

					if offscreen_size != (pixels.shape[0], pixels.shape[1]):
						offscreen_surf = pygame.Surface((pixels.shape[0], pixels.shape[1]))
						offscreen_size = offscreen_surf.get_size()

					pygame.surfarray.blit_array(offscreen_surf, pixels)
					self.coords.pop(0)
					self.is_processing = False

			if request_quit and not self.is_processing:
				is_running = False

			# if keypress[K_w] or keypress[K_UP]:
			# 	y0 += 5
			# 	did_change = True
			# if keypress[K_s] or keypress[K_DOWN]:
			# 	y0 -= 5
			# 	did_change = True
			# if keypress[K_d] or keypress[K_RIGHT]:
			# 	x0 -= 5
			# 	did_change = True
			# if keypress[K_a] or keypress[K_LEFT]:
			# 	x0 += 5
			# 	did_change = True

			if did_change:
				timer = 0
				OPTIONS["position"] = x0, y0
				OPTIONS["step"] = step = self.scale / self.spacing
				if OPTIONS["pixelmap"] is not None and platform.system() not in ("Windows", "Linux"):
					self.screen.fill(BACKGROUND)
					x1, y1, zoom2 = self.coords[0]
					if len(self.coords) == 1 and not self.is_processing and (
						zoom2 > 2
						or zoom2 < 0.5
						or not w/(2*zoom2) < x1 < pixels.shape[0] - w/(2*zoom2)
						or not h/(2*zoom2) < y1 < pixels.shape[1] - h/(2*zoom2)
					):
						self.update_offscreen()

					if 0 < x1 < offscreen_size[0] - w/zoom2 and 0 < y1 < offscreen_size[1] - h/zoom2:
						s1 = offscreen_surf.subsurface((x1,y1),(w/zoom2, h/zoom2))
						pygame.transform.scale(s1, (w,h), self.screen)
					else:
						self.screen.fill(BACKGROUND)

				else:
					self.screen.fill(BACKGROUND)

				if OPTIONS["show_grid"]:
					self.draw_grid()

				for values in self.args:
					self.draw_values(values)

				if OPTIONS["show_range"]:
					self.draw_range()
				pygame.display.flip()
				did_change = False
			elif OPTIONS["pixelmap"] and 0 <= timer < OPTIONS["timeout"]:
				timer += delta_time

				if timer >= OPTIONS["timeout"]:
					self.draw_pixels()

			if not request_quit:
				pygame.event.pump()

		self.is_animation_running = False
		win_w, win_h = Window.from_display_module().position
		OPTIONS["window_pos"] = str(win_w) + ", " + str(win_h)
		os.environ["SDL_VIDEO_WINDOW_POS"] = OPTIONS["window_pos"]
		pygame.display.quit()

		if OPTIONS["on_close"]:
			OPTIONS["on_close"]()

	def draw_values(self, obj):
		if instanceof(obj, (int, float, complex)):
			pygame.draw.circle(self.screen, BLUE, self.get_points(obj), RADIUS)
		elif instanceof(obj, tuple):
			if len(obj) == 2 and instanceof(obj[0], (int, float, complex)):
				pygame.draw.circle(self.screen, BLUE, self.get_points(obj), RADIUS)
			else:
				for i in obj:
					self.draw_values(i)
		elif instanceof(obj, list):
			if instanceof(obj[0], complex):
				pygame.draw.aalines(self.screen, BLUE, False, self.get_points(obj))
			elif instanceof(obj[0], list) and len(obj[0]) == 2:
				pygame.draw.aalines(self.screen, BLUE, False, self.get_points(obj))
			elif instanceof(obj[0], tuple):
				pygame.draw.aalines(self.screen, BLUE, False, self.get_points(obj))
			else:
				for i in obj:
					self.draw_values(i)

	def draw_grid(self):
		x0, y0 = OPTIONS["position"]
		w, h = OPTIONS["size"]

		# sub grid lines
		s1 = pygame.Surface((w,h), SRCALPHA)
		alpha = int(255*(2 * self.spacing/SPACING - 1))
		_black = pygame.Color(51,51,51,alpha)
		x = x0 % self.spacing + self.spacing/2
		while x < w:
			pygame.draw.line(s1, _black, [x, 0], [x, h], 1)
			x += self.spacing

		y = y0 % self.spacing + self.spacing/2
		while y < h:
			pygame.draw.line(s1, _black, [0, y], [w, y], 1)
			y += self.spacing

		self.screen.blit(s1, (0,0))

		# main grid lines
		x = x0 % self.spacing
		while x < w:
			pygame.draw.line(self.screen, BLACK, [x, 0], [x, h], 1)
			x += self.spacing

		y = y0 % self.spacing
		while y < h:
			pygame.draw.line(self.screen, BLACK, [0, y], [w, y], 1)
			y += self.spacing

		# axis
		pygame.draw.line(self.screen, PALE_BLUE, [x0, 0], [x0, h], 1)
		pygame.draw.line(self.screen, PALE_BLUE, [0, y0], [w, y0], 1)

		# origin marker
		pygame.draw.line(self.screen, WHITE, [x0 - 4, y0], [x0 + 4,y0], 3)
		pygame.draw.line(self.screen, WHITE, [x0, y0 - 4], [x0,y0 + 4], 3)

	def draw_range(self):
		x0, y0 = OPTIONS["position"]
		w, h = OPTIONS["size"]

		if not self.font:
			self.font = pygame.font.SysFont("Monospace", 12)

		# margin
		pygame.draw.rect(self.screen, BLACK, (0,h-MARGIN, w, h))
		pygame.draw.rect(self.screen, BLACK, (0,0, MARGIN, h))

		# range number
		x = self.spacing + x0 % self.spacing
		while x < w - MARGIN:
			x_mark = str(round((x - x0) * self.scale/self.spacing, 2))
			text = self.font.render(x_mark, False, PALE_BLUE)
			self.screen.blit(text,(x - 4*len(x_mark), h - (OPTIONS["fontsize"] + MARGIN)/2))
			x += self.spacing

		y = y0 % self.spacing
		while y < h - MARGIN:
			y_mark = str(-round((y - y0) * self.scale/self.spacing, 2))
			text = self.font.render(y_mark, False, PALE_BLUE)
			self.screen.blit(text,(round(MARGIN / (1 + len(y_mark))), y - 8))
			y += self.spacing

	def get_points(self, points):
		x0, y0 = OPTIONS["position"]
		step = OPTIONS["step"]
		if instanceof(points, list):
			if len(points) == 2 and instanceof(points[0], (int, float)):
				return x0 + points[0]/step, y0 - points[1]/step
			return [self.get_points(p) for p in points]
		if instanceof(points, (int, float)):
			return x0 + points/step, y0
		if instanceof(points, complex):
			return x0 + points.real/step, y0 - points.imag/step
		if instanceof(points, tuple):
			return x0 + points[0]/step, y0 - points[1]/step

	def update(self, *args, **kwargs):
		if args:
			pygame.event.post(pygame.event.Event(pygame.USEREVENT, args=args))

	def config(self, **kwargs):
		pygame.event.post(pygame.event.Event(pygame.USEREVENT, kwargs=kwargs))

	def animate(self, delay, callback):
		pygame.event.post(pygame.event.Event(pygame.USEREVENT, animate=(delay,callback)))

	def close(self):
		pygame.event.post(pygame.event.Event(pygame.QUIT))
