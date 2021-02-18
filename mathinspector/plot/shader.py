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
import sys
from os import path
from ..util.config import BASEPATH
from OpenGL.GL import GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, glGetUniformLocation
from OpenGL.GL import shaders

SHADER_DIR = path.join(BASEPATH, "shader")

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
