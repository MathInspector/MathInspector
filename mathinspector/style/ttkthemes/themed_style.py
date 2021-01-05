"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2017-2018 RedFantom
"""
from ._widget import ThemedWidget
from ._tkinter import ttk


class ThemedStyle(ttk.Style, ThemedWidget):
    """
    Style that supports setting the theme for a Tk instance. Can be
    used as a drop-in replacement for normal ttk.Style instances.
    Supports the themes provided by this package.
    """
    def __init__(self, *args, **kwargs):
        """
        :param theme: Theme to set up initialization completion. If the
                      theme is not available, fails silently.
        """
        theme = kwargs.pop("theme", None)
        gif_override = kwargs.pop("gif_override", False)
        # Initialize as ttk.Style
        ttk.Style.__init__(self, *args, **kwargs)
        # Initialize as ThemedObject
        ThemedWidget.__init__(self, self.tk, gif_override)
        # Set the initial theme
        if theme is not None and theme in self.get_themes():
            self.set_theme(theme)

    def theme_use(self, theme_name=None):
        """
        Set a new theme to use or return current theme name

        :param theme_name: name of theme to use
        :returns: active theme name
        """
        if theme_name is not None:
            self.set_theme(theme_name)
        return ttk.Style.theme_use(self)

    def theme_names(self):
        """
        Alias of get_themes() to allow for a drop-in replacement of the
        normal ttk.Style instance.

        :returns: Result of get_themes()
        """
        return self.get_themes()
