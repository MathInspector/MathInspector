"""
How to use the doc browser
---
In the left hand side panel you will find a directory of all available documentation
for the object you are currently viewing.  In this case, you are viewing the documentation
for the python module `doc.manual`, which is part of the math inspector source code.

Most modules and classes in python come with a lot of documentation for all their
functionality.  When you select an object from the side panel, the doc browser will display the
documentation for that object.  If you select a class or module, the side panel
will also be updated with a directory of the contents of that class or module.  To return to a
previous document, click the name of the previous object in the top navigation area.

To see how it works, try clicking on the class GettingStarted in the side panel,
and use the top navigation area to return to this document.

Running code samples
---
If you see a code sample in a document you want to run, simply click on the
code block and it will be executed by the interpreter.  Try it out!

>>> import numpy as np

Many of the code samples assume that you have already imported the numpy
package with the alias "np", as shown in the command above.  Numpy is the fundamental
package for scientific computing with python, and math inspector is designed to be a
graphical interface for interacting with the numpy family of python modules.
You can learn more about numpy at https://numpy.org

The module tree
---
If you ran the previous code example, then the module `np` should now be displayed
in the left hand side panel of the main window.  Each time a new
module is imported, the directory of it's contents will appear in the sidebar.

Math inspector comes with numpy and scipy pre-installed, as well as a number of other modules
which can be imported in a similar manner.  Any python module on your system can be
imported as long as it's compatible with python version 3.9.1

The node editor
---
The node editor is a block coding environment, and it's one of the main features of math inspector.
To display the node editor, select View > Show Node Editor from
the main menu.  It's possible to drag and drop objects, functions, and classes into the node editor directly
from the module tree.

In what follows we will use the numpy function `linspace` as an example.  From the sidebar in the main window,
expand the functions folder in the `np` module, find the function named `linspace`, and
drag it into the node editor.

An alternative way to create a `linspace` object is by using the following command

>>> from numpy import linspace

Right clicking on items in the node editor will bring up a menu of the available options.
If you right click on the `linspace` item, you will have various options, including
"show kwargs", kwargs stands for "key word arguments", and these are optional parameters
which can be passed to a function.

The `linspace` function outputs an array of evenly spaced numbers. The required arguments
are `start` and `stop`, and it has an optional keyword argument `num`, which determines
the size of the array. If you would like to learn more about linspace before continuing,
right click on the item and choose View Doc.

Displaying Plots
---
If you checked out the documentation for linspace, you may have noticed at the end there
was a code example which used matplotlib to display a plot of the output.  Math inspector's
plotting library updates and modernize the functionality available in matplotlib, and
was designed to be a replacement for matplotlib.

To plot 25 evenly spaced real numbers between -10 and 10, use the command

>>> plot(linspace(-10, 10, num=25))

To pan the camera, hold down the right mouse button and move the cursor.  You can also
use the mouse scroll wheel to zoom in and out.

Every time you update an object which is being plotted, the changes will be reflected in the plot
window. Try changing the `start` argument to the linspace item by clicking on the argument value in the
node editor.  This will bring up the text entry widget which you can use to type in a new value.
It's also possible to change the value of an argument by hovering the mouse cursor over the vaule,
holding down the left mouse button, and then dragging the cursor around.

See the modules `plot` and `animation` for more information.

Using the examples
---
Math inspector comes with a number of examples to demonstrate some of the available
functionality.  Let's import the examples module, and view the 3D plot for the cylinder
example

>>> from mathinspector import examples
>>> cylinder = examples.cylinder
>>> plot(cylinder())

You can find more information about the available examples from the documentation,
each one has a detailed explaination and multiple code samples

See the module `examples` for more information.

Further Documentation
---
Math inspector provides a number of views for interacting with the running program.
In the left hand side panel are links to the core modules which constitute
the math inspector source code.  These links contain documentation
detailing the available features, and an overview about how the code works.


Free open source software
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
along with this program.  If not, see https://www.gnu.org/licenses/.

"""

from .. import console, plot, node, objects, modules, examples, animation, project

class GettingStarted:
	"""To learn about the various features provided by math inspector, lets create
a simple program directly in the interpreter.  Click this code block to create
a variable `x` in memory with a value of `1`

>>> x=1

Math inspector provides a visual represenation of the variables in the local namespace in the
form of a block coding environment, called the node editor.  The node editor makes it possible to
experiment and interact with otherwise complex programs without needing to write any code, or
even know much about python at all.

Item's in the node editor can be dragged by hovering the cursor over an item,
holding down the left mouse button, and dragging.  Holding down
the right mouse button in an empty part of the node editor and moving the
cursor pans all the items, and the scroll wheel is used for zooming in and out.

Let's define a function `f(x)` which returns `x + 1`

>>> def f(x):
... 	return x + 1

When you call a function from the interpreter, the value of it's arguments are updated in the node editor,
as you can see by calling `f(1)`.

>>> f(1)
2

Let's now create a new variable `y` and assign it the value `f(x)`, using the variable `x` we previously created

>>> y = f(x)
>>> y
2

The wires between `x` and `f` should now be connected in the node editor, reflecting
the code we just executed.

Binary Operators
---
A binary operator is an operator like `+`,`-`,`*`,`/` which acts on the objects
on it's left and right hand sides.  To illustrate this, lets create
two new variables `a`,`b` and set them both equal to `1`

>>> a = b = 1

>>> c = a + b

When using a binary operator in a function call, a new object will appear in the
node editor representing the operator, and the wires will be connected.

>>> z = f(x+c)

You can find a full list of python's binary operators by
right clicking in an empty part of the node editor to bring up
the Add Objects menu.
	"""
	pass
