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

import inspect, re
from .docscrape import FunctionDoc

RE_FN = re.compile(r"[a-zA-Z_0-9]*\((.*)\)")
RE_ARG = re.compile(r"[a-zA-Z_0-9]*")
RE_EXTRA = re.compile(r"(\[.*\])")

def argspec(obj, withself=True):
	"""
	A way to parse signature of fn's from FunctionDoc to get argspec of builtins and ufuncs
	"""
	### NOTE - this is actually not as reliable as the other method... would be nice to default to this but w/e can deal with that later
	if isinstance(obj, dict):
		return False

	try:
		fullargspec = inspect.getfullargspec(obj)
	except:
		fullargspec = None

	if fullargspec and callable(obj):
		num_kwargs = len(fullargspec[3]) if fullargspec[3] else 0
		args = fullargspec[0][0 if withself else 1:len(fullargspec[0]) - num_kwargs]
		num_args = len(args) if withself else 1 + len(args)
		kwargs = {}
		if num_kwargs > 0:
			kwargs = { fullargspec[0][i]:fullargspec[3][i - num_args] for i in range(num_args, len(fullargspec[0])) }
		if fullargspec[5] and len(fullargspec[5]) > 0:
			for name in fullargspec[5]:
				kwargs[name] = fullargspec[5][name]

		return args, kwargs

	doc = FunctionDoc(obj)
	signature = doc["Signature"].replace(", /", "").replace(", \*", "").replace(", *", "")
	signature = RE_EXTRA.sub("", signature)
	params = RE_FN.findall(signature)
	if len(params) == 0:
		return False
	items = [i.lstrip() for i in params[0].split(",")]	

	return [i for i in items if "=" not in i], { i.split("=")[0] : eval(i.split("=")[1]) for i in items if "=" in i}