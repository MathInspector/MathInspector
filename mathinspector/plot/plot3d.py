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
import pygame, glm, ctypes, os
import numpy as np
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLU import *
from .util import is_iterable, instanceof
from .shader import Shader
from pygame._sdl2.video import Window


OPTIONS = {
	"size": (1280,768),
	"title": "Math Inspector",
	"on_update": None,
	"on_close": None,
	"show_grid": True,
}

window = None

class OpenGLWindow:
	def __init__(self):
		self.zoom = 1;
		self.model = glm.mat4(1.0)
		self.camera_pos = glm.vec3(0,10,7)
		self.camera_front = glm.normalize(glm.vec3(0,-1,-1))
		self.camera_up = glm.vec3(0,1,0)

		self.view = glm.lookAt(self.camera_pos, self.camera_pos * self.camera_front, self.camera_up)
		self.projection = glm.perspective(glm.radians(45), OPTIONS["size"][0]/OPTIONS["size"][1], 0.1, 1000)
		self.model = glm.rotate(self.model, glm.radians(-90.0), glm.vec3(0,1,0))
		self.light_pos = glm.vec3(10,10,10)
		self.is_running = False
		self.is_animation_running = False
		# self.points = []
		# self.lines = []
		# self.quads = []
		# self.line_offset = []
		# self.quad_offset = []

	def plot(self, *args, **kwargs):
		OPTIONS.update(kwargs)
		self.projection = glm.perspective(glm.radians(45), OPTIONS["size"][0]/OPTIONS["size"][1], 0.1, 1000)
		pygame.init()
		pygame.display.gl_set_attribute(GL_CONTEXT_MAJOR_VERSION, 4)
		pygame.display.gl_set_attribute(GL_CONTEXT_MINOR_VERSION, 1)
		pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
		self.screen = pygame.display.set_mode(OPTIONS["size"], DOUBLEBUF | OPENGL | RESIZABLE | HWSURFACE)

		glClearColor(39/255,40/255,44/255,1)
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
		glEnable(GL_DEPTH_TEST)
		# glEnable(GL_MULTISAMPLE);
		# glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)

		self.generate_vertices(*args)
		pygame.display.set_caption(OPTIONS["title"])

		last_tick = 0
		animation_timer = 0
		did_change = True
		self.is_running = True
		is_focused = False
		keypress = pygame.key.get_pressed()

		if OPTIONS["on_update"]:
			OPTIONS["on_update"]()

		while self.is_running:
			tick = pygame.time.get_ticks()/1000
			delta_time = tick - last_tick
			last_tick = tick
			speed = 10 * delta_time
			camera_right = glm.normalize(glm.cross(self.camera_front, self.camera_up))

			for event in pygame.event.get():
				if event.type == MOUSEWHEEL:
					delta = 1 + event.y/100
					self.zoom *= delta
					self.model = glm.scale(self.model, glm.vec3(delta))
					did_change = True
				elif event.type == MOUSEMOTION:
					if event.buttons[0]:
						fx,fy,fz = self.camera_front
						rotate_front = glm.rotate(glm.mat4(1), glm.radians(-event.rel[0]/10), self.camera_up)
						rotate_up = glm.rotate(glm.mat4(1), glm.radians(-event.rel[1]/10), camera_right)
						self.camera_front = (rotate_front * glm.vec4(fx,fy,fz,1)).xyz
						ux,uy,uz = self.camera_front
						self.camera_front = (rotate_up * glm.vec4(ux,uy,uz,1)).xyz
						did_change = True
					elif event.buttons[2]:
						self.camera_pos -= speed * event.rel[0] * camera_right
						self.camera_pos += speed * event.rel[1] * self.camera_up
						did_change = True
				elif event.type == pygame.USEREVENT:
					if hasattr(event, "args"):
						if event.args:
							self.generate_vertices(*event.args)
					if hasattr(event, "kwargs"):
						OPTIONS.update(event.kwargs)
					elif hasattr(event, "animate"):
						delay = event.animate[0]
						callback = event.animate[1]
						self.is_animation_running = True
					did_change = True
				elif event.type == VIDEORESIZE:
					did_change = True
					OPTIONS["size"] = event.size
					self.projection = glm.perspective(glm.radians(45), event.size[0]/event.size[1], 0.1, 1000)
				elif event.type == ACTIVEEVENT:
					is_focused = bool(event.gain)
				elif (event.type == pygame.QUIT
					or (event.type == KEYUP and event.key == K_ESCAPE)
					or (event.type == KEYUP and event.key == K_w and keypress[K_LMETA])
				):
					self.is_running = False
					if OPTIONS["on_close"]:
						OPTIONS["on_close"]()

			if self.is_animation_running:
				if animation_timer >= delay:
					animation_timer = 0
					values = callback()
					if values:
						self.generate_vertices(*values)
						did_change = True
					else:
						self.is_animation_running = None
				else:
					animation_timer += delta_time

			if not is_focused and OPTIONS["on_update"]:
				OPTIONS["on_update"]()

			keypress = pygame.key.get_pressed()
			if is_focused:
				if keypress[K_w] or keypress[K_UP]:
					self.camera_pos += speed * self.camera_front
					did_change = True
				if keypress[K_s] or keypress[K_DOWN]:
					self.camera_pos -= speed * self.camera_front
					did_change = True
				if keypress[K_d] or keypress[K_RIGHT]:
					self.camera_pos += speed * camera_right
					did_change = True
				if keypress[K_a] or keypress[K_LEFT]:
					self.camera_pos -= speed * camera_right
					did_change = True

			if did_change:
				self.view = glm.lookAt(self.camera_pos, self.camera_pos + self.camera_front, self.camera_up)
				mvp = self.projection * self.view * self.model

				glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

				if len(self.points) > 0:
					glUseProgram(self.shader["points"].program)
					glUniformMatrix4fv(self.shader["points"]["mvp"], 1, GL_FALSE, glm.value_ptr(mvp))
					glBindVertexArray(self.point_vao)
					glDrawArrays(GL_POINTS, 0, int(len(self.points)/3))

				if len(self.lines) > 0:
					glUseProgram(self.shader["lines"].program)
					glUniformMatrix4fv(self.shader["lines"]["mvp"], 1, GL_FALSE, glm.value_ptr(mvp))
					glBindVertexArray(self.line_vao)
					for i in range(0, len(self.line_offset)):
						glDrawArrays(GL_LINE_STRIP, *self.line_offset[i])

				if len(self.quads) > 0:
					glUseProgram(self.shader["quads"].program)
					glUniformMatrix4fv(self.shader["quads"]["model"], 1, GL_FALSE, glm.value_ptr(self.model))
					glUniformMatrix4fv(self.shader["quads"]["view"], 1, GL_FALSE, glm.value_ptr(self.view))
					glUniformMatrix4fv(self.shader["quads"]["projection"], 1, GL_FALSE, glm.value_ptr(self.projection))
					glUniform3f(self.shader["quads"]["lightPos"], *self.light_pos.xyz)
					glBindVertexArray(self.quad_vao)
					for i in range(0, len(self.quad_offset)):
						glDrawArrays(GL_TRIANGLE_STRIP, *self.quad_offset[i])

				if OPTIONS["show_grid"]:
					glUseProgram(self.shader["grid"].program)
					glUniformMatrix4fv(self.shader["grid"]["model"], 1, GL_FALSE, glm.value_ptr(self.model))
					glUniformMatrix4fv(self.shader["grid"]["view"], 1, GL_FALSE, glm.value_ptr(self.view))
					glUniformMatrix4fv(self.shader["grid"]["proj"], 1, GL_FALSE, glm.value_ptr(self.projection))
					glUniform1f(self.shader["grid"]["zoom"], self.zoom)
					glUniform3f(self.shader["grid"]["cameraPos"], *self.camera_pos.xyz)
					glBindVertexArray(self.grid_vao)
					glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

				pygame.display.flip()
				did_change = False

		win_w, win_h = Window.from_display_module().position
		OPTIONS["window_pos"] = str(win_w) + ", " + str(win_h)
		os.environ["SDL_VIDEO_WINDOW_POS"] = OPTIONS["window_pos"]
		pygame.display.quit()

	def generate_vertices(self, *args):
		# TODO - run the loop over args here, that way i can use recursion in self.get_vertices easily
		self.points, self.lines, self.quads, self.line_offset, self.quad_offset = self.get_vertices(*args)

		self.grid = np.array([-1,-1, 0,
							-1, 1, 0,
							 1,-1, 0,
							 1, 1, 0 ], dtype='float32')

		self.grid_vao = glGenVertexArrays(1)
		glBindVertexArray(self.grid_vao)
		self.grid_vbo = glGenBuffers(1)
		glBindBuffer(GL_ARRAY_BUFFER, self.grid_vbo)
		glBufferData(GL_ARRAY_BUFFER, self.grid, GL_STATIC_DRAW)
		glEnableVertexAttribArray(0)
		glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
		self.shader = { "grid": Shader("grid_vert.glsl", "grid_frag.glsl", ("view", "proj", "model", "zoom", "cameraPos")) }

		if len(self.points) > 0:
			self.point_vao = glGenVertexArrays(1)
			glBindVertexArray(self.point_vao)
			self.point_vbo = glGenBuffers(1)
			glBindBuffer(GL_ARRAY_BUFFER, self.point_vbo)
			glBufferData(GL_ARRAY_BUFFER, self.points, GL_STATIC_DRAW)
			glEnableVertexAttribArray(0)
			glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
			self.shader["points"] = Shader("point_vert.glsl", "point_frag.glsl", "mvp")

		if len(self.lines) > 0:
			self.line_vao = glGenVertexArrays(1)
			glBindVertexArray(self.line_vao)
			self.line_vbo = glGenBuffers(1)
			glBindBuffer(GL_ARRAY_BUFFER, self.line_vbo)
			glBufferData(GL_ARRAY_BUFFER, self.lines, GL_STATIC_DRAW)
			glEnableVertexAttribArray(0)
			glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
			self.shader["lines"] = Shader("line_vert.glsl", "line_frag.glsl", "mvp")

		if len(self.quads) > 0:
			self.quad_vao = glGenVertexArrays(1)
			glBindVertexArray(self.quad_vao)
			self.quad_vbo = glGenBuffers(1)
			glBindBuffer(GL_ARRAY_BUFFER, self.quad_vbo)
			glBufferData(GL_ARRAY_BUFFER, self.quads, GL_STATIC_DRAW)
			glEnableVertexAttribArray(0)
			glEnableVertexAttribArray(1)
			glEnableVertexAttribArray(2)
			glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8*4, ctypes.c_void_p(0))
			glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 8*4, ctypes.c_void_p(3*4))
			glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 8*4, ctypes.c_void_p(5*4))
			self.shader["quads"] = Shader("quad_vert.glsl", "quad_frag.glsl", ("model", "view", "projection", "lightPos"))

	def get_vertices(self, *args, line_num=0, quad_num=0):
		points, lines, quads, line_offset, quad_offset = [], [], [], [], []
		for arg in args:
			if instanceof(arg, list) and instanceof(arg[0], list) and instanceof(arg[0][0], (int,float)):
				line_offset.append((line_num, len(arg[0])))
				line_num += len(arg[0])
				for i in range(0, len(arg[0])):
					lines.extend([arg[0][i], arg[1][i], arg[2][i]])
			elif instanceof(arg, tuple):
				if len(arg) == 2 and instanceof(arg[0], list):
					for line in arg[0]:
						line_offset.append((line_num, len(line)))
						line_num += len(line)
						for vert in line:
							lines.extend(list(vert))

					for line in arg[1]:
						line_offset.append((line_num, len(line)))
						line_num += len(line)
						for vert in line:
							lines.extend(list(vert))
				elif instanceof(arg[0], list) and len(arg) == 3 and len(arg[0]) == len(arg[1]) == len(arg[2]):
					for i in range(0, len(arg[0])):
						points.extend([arg[0][i], arg[1][i], arg[2][i]])
				elif len(arg) == 3 and instanceof(arg[0], (int,float)):
					points.extend(list(arg))
				else:
					temp = self.get_vertices(*arg, line_num=line_num, quad_num=quad_num)
					points.extend(temp[0])
					lines.extend(temp[1])
					quads.extend(temp[2])
					line_offset.extend(temp[3])
					quad_offset.extend(temp[4])
			elif instanceof(arg, list):
				if instanceof(arg[0], tuple):
					line_offset.append((line_num, len(arg)))
					line_num += len(arg)
					for j in arg:
						lines.extend(list(j))
				elif instanceof(arg[0], list):
					quad_start = quad_num
					for i in range(0, len(arg)-1):
						for j in range(0, len(arg[i])-1):
							a = glm.vec3(*arg[i][j+1]) - glm.vec3(*arg[i][j])
							b = glm.vec3(*arg[i+1][j]) - glm.vec3(*arg[i][j])
							normal = glm.normalize(glm.cross(b,a))
							x_len = len(arg) - 1
							y_len = len(arg[j]) - 1
							quads.extend(list(arg[i][j]) + [i/x_len, j/y_len] + list(normal))
							quads.extend(list(arg[i][j+1]) + [i/x_len, (j+1)/y_len] + list(normal))
							quads.extend(list(arg[i+1][j]) + [(i+1)/x_len, j/y_len] + list(normal))
							quads.extend(list(arg[i+1][j+1]) + [(i+1)/x_len, (j+1)/y_len] + list(normal))
							quad_num += 4
					quad_offset.append((quad_start, quad_num))

		return (
			np.array(points, dtype="float32"),
			np.array(lines, dtype="float32"),
			np.array(quads, dtype="float32"),
			line_offset,
			quad_offset
		)

	def config(self, **kwargs):
		pygame.event.post(pygame.event.Event(pygame.USEREVENT, kwargs=kwargs))

	def update(self, *args, **kwargs):
		pygame.event.post(pygame.event.Event(pygame.USEREVENT, args=args, kwargs=kwargs))

	def animate(self, delay, callback):
		pygame.event.post(pygame.event.Event(pygame.USEREVENT, animate=(delay,callback)))

	def close(self):
		pygame.event.post(pygame.event.Event(pygame.QUIT))


