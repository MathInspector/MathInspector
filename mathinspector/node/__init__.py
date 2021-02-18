"""
The node editor is a block coding environment that was designed to make it as
simple as possible to experiment and interact with otherwise complex programs,
without needing to write any code, or even know much about python at all.  It's
consists of an infinte size canvas with pan, zoom, and drag functionality.  To display
the node editor, select View > Show Node Editor from the main menu.

Unlike other block coding systems, the node editor is capable of
representing arbitrary python functions and objects of any kind.  This means it's
operating at an extremely high level of generality.  This high level of generality makes
the node editor a useful tool for learning about many aspects of the python ecosystem.

Control Scheme
---
Item's in the node editor can be dragged by hovering the cursor over an item,
holding down the left mouse button, and dragging.  Holding down the left
mouse button and dragging in an empty part of the editor will create a multi-select rectangle,
which can be used for moving or deleting multiple item's at the same time.  Holding down
the right mouse button and moving the cursor pans all the items.

The scroll wheel is used for zooming in and out.

Right clicking in any empty part of the editor without panning will bring up
the "Add Objects" menu, which contains all the builtin python and math helper
functions.

You can edit the value of an item, or the argument of a function, by clicking
on it in the node editor, typing in a new value, and pressing Enter.

The Options Menu
---
Right clicking on any item will bring up a list of available options and
methods.  For example, let's create an out-of-order list `a` and use the
options menu to run the `sort` method.

Run the following code sample, then right click on
the item `a` in the node editor and select the `sort` options.

>>> a = [1,3,2]

Running the sort method from the options menu is eqivilent to running the command

>>> a.sort()

Instead of returning a sorted list, the `sort` method actually changes the value of `a`,
and this change is now reflected in the displayed value of the `a` item.

If a method has more than 0 arguments, then selecting that method from the options
menu will bring up a popup.

Methods which return objects will generally result in the creation of new items
in the editor.  However, in the case of methods which return numbers, booleans, or string,
the return value will be shown in the output log section.

Connecting Wires
---
All items have output nodes, to drag a wire from the input mode of one item and connect
it to the input node of another item, hover the mouse cursor over the output node,
hold down the left mouse button, and then drag the wire out and connect it, then let go
of the mouse button.

To plot a function, you can drag the wire to the output node section of the editor on
the right hand side.

When connecting items of different classes together, the editor will try to cast the value
of the incoming item to the class of the target item, so that the target item will preseve
it's class after connecting the wires.  If this is not possible, then the target item will
have it's class changed to be the same as the incoming item.

Add Object Menu
---
If you right click in an empty part of the node editor, it will bring up the
Add Object menu.  This menu contains all the builtin binary operators, functions,
classes, and examples.  Click on an object from the menu and it will appear in
the node editor.

Right clicking on items in the node editor will bring up a menu
of available options, including viewing the documentation.

"""
from .editor import NodeEditor