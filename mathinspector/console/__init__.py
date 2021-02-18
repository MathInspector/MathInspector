"""
The math inspector console extends the traditional python interpreter, and has many quality of
life improvements such as syntax highlighting and a wide variety of hotkeys.

There are only two built in functions in math inspector which are not available in a normal python
environment: `app` and `plot`.  The `app` object opens up the entire math inspector codebase,
allowing you to interact with the any part of the app directly from the console.  This can be
very useful when prototyping new features.

For example, to toggle the left hand sidebar open and closed, you can use the command:

>>> app.menu.setview("sidebar")

Hotkeys
---
`up-arrow`: toggle history up

`down-arrow`: toggle history down

`Tab`: autocomplete

`Cmd+d`: highlight the currently selected word

"""
from .interpreter import Interpreter
from .builtin_print import builtin_print