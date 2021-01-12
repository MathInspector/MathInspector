import sys
from os import path
from util.config import BASEPATH
from OpenGL.GL import GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, glGetUniformLocation
from OpenGL.GL import shaders

SHADER_DIR = path.join(BASEPATH, "assets/shader" if hasattr(sys, "_MEIPASS") else "shader")

class Shader:
	def __init__(self, vert_path, frag_path, uniform=()):
		self.vert_shader = open(path.join(SHADER_DIR, vert_path)).read()
		self.frag_shader = open(path.join(SHADER_DIR, frag_path)).read()
		vert = shaders.compileShader(self.vert_shader, GL_VERTEX_SHADER)
		frag = shaders.compileShader(self.frag_shader, GL_FRAGMENT_SHADER)
		self.program = shaders.compileProgram(vert, frag)
		
		uniform = uniform if isinstance(uniform, tuple) else (uniform,)
		self.uniform = { i: glGetUniformLocation(self.program, i) for i in uniform }

	def __getitem__(self, key):
		return self.uniform[key]	