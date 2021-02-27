# Math Inspector

<https://mathinspector.com>

[![PyPI](https://img.shields.io/pypi/v/mathinspector)](https://pypi.org/project/mathinspector)
[![License](https://img.shields.io/pypi/l/mathinspector)](https://github.com/MathInspector/MathInspector/blob/master/LICENSE)

Math Inspector is a visual programming environment for scientific computing based on numpy. Appropriate for users of all ages and skill levels. 

Math Inspector will always be 100% free and open source.

## Install

`python -m pip install mathinspector`

To start math inspector, run the following command

`mathinspector`

or

`python -m mathinspector`


![BetaVersionAnimation](https://mathinspector.com/img/beta-scene-full.gif)

## Overview

Math inspector is a traditional python interpreter that has a number of quality of life improvements.  What really makes it different is that math inspector creates a visual representation of the memory of the running python program in the form of a block coding environment called the node editor.

### Block Coding
The block coding system is capable of representing arbitrary python functions and objects of any kind; it has been designed to make it as easy as possible to experiment and interact with complex programs without the need to write any code.  It's the only block coding system which exists which is capable of mapping an entire programming language.  

### Interactive Plots
The plotting library updates and modernizes the functionality available in matplotlib. It provides high performance interactive 2D and 3D plots. Capable of plotting parametric curves, algebraic varieties, fractals, curved surfaces, and much more.

### Animation
The animation system has been designed to render production quality animations for educational content creators. A lot of care has been put into optimizing the performance of animations to enable a smooth 60 frames per second while panning and zooming during animations.

### Doc Browser
The doc browser is an offline browser that uses advanced parsing and rendering systems to create a beautifully styled and highly interactive document.  It's capable of working with the entire python ecosystem of documentation.  Using a web browser to view python documentation creates a number of limitations that result from being constrained to a browser.  Because the doc browser is written in python specifically for the purpose of reading documentation, it makes it possible to create a new kind of interactive document.

## Use mathinspector in your python source code files

You can use the mathinspector plotting and documentation systems in your own projects without needing to launch the app.

For example
```python
import mathinspector
mathinspector.plot(1,2,3)
```

To view the documentation for the mathinspector module with the doc browser
```python
>>> mathinspector.help(mathinspector)
``` 

## Use mathinspector as a command line tool
```
usage: mathinspector [files] ... [options] ... 

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

```

## Share
Math Inspector makes it easy to save your project and share it with others, and has been designed in particular to supplement educational video's by providing a free tool for content creators to create animations.  This makes it easy to share projects online, and helps viewers explore concepts from the video using the same tool that was used to create the animations.


License
---
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

