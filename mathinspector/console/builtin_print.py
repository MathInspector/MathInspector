"""
The builtin_print function is used for printing to the command line
outside of the app whenever needed, its a is a custom implementation
of the default python print function

>>> builtin_print (1)  # prints to the command line which was used to launch the app

as opposed to

>>> print (1)  # prints to the mathinspector interpreter
1

The interpreter overrides the function __builtins__["print"] using the
displayhook from the builtins module.
"""
from sys import stdout

# TODO - implement kwargs of the standard python print function
def builtin_print(*args, **kwargs):
	stdout.write("\t".join([str(i) for i in args]) + "\n")
	stdout.flush()
