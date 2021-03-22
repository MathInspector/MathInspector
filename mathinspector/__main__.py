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
from . import main

if __name__ == "__main__":
	args = []
	kwargs = {}
	i = 1

	while i < len(sys.argv):
		arg = sys.argv[i]
		if arg[:2] != "--":
			args.append(sys.argv[i])
		elif "=" in arg:
			key, value = arg[2:].split("=")
			kwargs[key] = value
		elif i + 1 < len(sys.argv) and sys.argv[i+1] and sys.argv[i+1][:2] != "--":
			kwargs[arg[2:]] = sys.argv[i+1]
			i += 1
		else:
			kwargs[arg[2:]] = True
		i += 1

	if "help" in kwargs and kwargs["help"] is True:
		print ("""usage: mathinspector [files] ... [options] ... 

Options and arguments:
[files]...       : a list of files with either a .math or .py extension.  The
                  .math file will be loaded, and all of the .py files will be
                  added to the current project

--help obj       : view the documentation for obj as if you called help(obj)
                  in mathinspector

--new            : starts a new project and resets the state of the app.
                  This flag will overwrites the autosave file with a blank
                  file

--disable[=opts] : mathinspector overrides a lot of builtins (e.g. help(),
                  print()) which may cause undesirable behaviour, this flag
                  disables these features
                    opts are 'print', 'traceback', 'stderr'
                    e.g. mathinspector --disable=print,stderr

--debug          : prints log messages to the command line used to launch the
                  app.  Useful for debugging issues when something isn't
                  working properly, or while working on the mathinspector
                  source code
		""")
	else:
		main(*args, **kwargs)
