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

import collections

class ObjectContainer(collections.MutableMapping):
	"""A dictionary that applies an arbitrary key-altering
	function before accessing the keys"""

	def __init__(self, setitem=None, delitem=None, getitem=None, *args, **kwargs):
		self.store = dict()
		self.store.update(dict(*args, **kwargs))  # use the free update to set keys
		self._callback = {
			"get": getitem,
			"set": setitem,
			"del": delitem,
		}

	def __getitem__(self, key):
		return self.store[key] if not self._callback["get"] else self._callback["get"](key)

	def __setitem__(self, key, value, preserve_class=False, raise_error=False):
		if preserve_class:			
			try:				
				self.store[key] = self.store[key].__class__(value)
			except Exception as err:
				if raise_error:
					raise err
				self.store[key] = value	
		else:
			self.store[key] = value
		
		if self._callback["set"]:
			self._callback["set"](key)

	def __delitem__(self, key):
		if key not in self.store and self._callback["get"]:
			try:
				item = self._callback["get"](key)
			except:
				item = None

			if item:
				for i in self.store:
					if self.store[i].__name__ == key:
						key = i
						break

		if self._callback["del"]:
			self._callback["del"](key)
		
		del self.store[key]

	def __contains__(self, key):
		item = None
		if key not in self.store and self._callback["get"]:
			try:
				item = self._callback["get"](key)
			except:
				pass
				
		return item or key in self.store

	def __iter__(self):
		return iter(self.store)

	def __len__(self):
		return len(self.store)

	def __repr__(self):
		return repr(self.store)

	def setitem(self, key, value):
		self.store[key] = value