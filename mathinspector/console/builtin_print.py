"""
The interpreter overrides the function __builtins__["print"] using the displayhook from the builtins module.
The builtin_print function maintains a reference to the default python print function.
"""
builtin_print = __builtins__["print"]
