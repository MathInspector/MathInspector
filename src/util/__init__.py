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

from .objectcontainer import ObjectContainer
from .argspec import argspec
from .watchhandle import WatchHandle
from .docscrape import FunctionDoc, ClassDoc
from pdb import set_trace as breakpoint
from .savedata import SaveData
from .icons import geticon
from .animate import Animate
from .misc import *