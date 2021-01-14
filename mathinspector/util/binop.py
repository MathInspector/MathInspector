"""
Maps the ast BinOp classes to functions that can be used in the node editor
"""
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
def Add(a,b):
	"""
	a + b : a plus b
	"""
	return a + b

def Sub(a,b):
	"""
	a - b : a minus b
	"""
	return a - b

def Mult(a,b):
	"""
	a * b : a times b
	"""
	return a * b

def Div(a,b):
	"""
	a / b : a divided by b
	"""
	return a / b

def FloorDiv(a,b):
	"""
	a // b : the largest integer less than a divided by b
	"""
	return a // b

def Mod(a,b):
	"""
	a % b : a modulo b
	"""
	return a % b

def Pow(a,b):
	"""
	a ** b : a to the power b
	"""
	return a ** b

def LShift(a,b):
	"""
	a << b : left shift bitwise operator
	"""
	return a << b

def RShift(a,b):
	"""
	a >> b : right shift bitwise operator
	"""
	return a >> b

def BitOr(a,b):
	"""
	a | b : bitwise or operator
	"""
	return a | b

def BitXor(a,b):
	"""
	a ^ b : bitwise xor operator
	"""
	return a ^ b

def BitAnd(a,b):
	"""
	a & b : bitwise and operator
	"""
	return a & b