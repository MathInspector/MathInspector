"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2017-2018 RedFantom
"""
import sys


def is_python_3():
    return sys.version_info[0] == 3


if is_python_3():
    import tkinter as tk
    from tkinter import ttk
else:
    import Tkinter as tk
    import ttk
