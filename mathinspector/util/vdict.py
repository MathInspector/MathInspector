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

from collections import OrderedDict

class vdict(dict): # need to extend dict so it can be passed as an argument to exec()
	"""
	vdict: a dictionary class that has callbacks for get, set, and del events
	"""
	def __init__(self, *args, getitem=None, setitem=None, delitem=None, **kwargs):
		self.store = OrderedDict()
		self.store.update(dict(*args, **kwargs))
		self._get = getitem
		self._del = delitem
		self._set = setitem
		self.keys = self.store.keys
		self.values = self.store.values

	def __getitem__(self, key):
		if self._get:
			return self._get(key)
		return self.store[key]

	def __setitem__(self, key, value):
		if self._set:
			ret = self._set(key, value)
			if ret is False:
				return
		self.store[key] = value

	def __delitem__(self, key):
		if self._del:
			ret = self._del(key)
			if ret is False:
				return
		del self.store[key]

	def __contains__(self, key):
		return key in self.store

	def __iter__(self):
		return iter(self.store)

	def __len__(self):
		return len(self.store)

	def __repr__(self):
		return repr(self.store)