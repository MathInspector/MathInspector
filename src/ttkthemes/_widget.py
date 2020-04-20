"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2017-2018 RedFantom
"""
# Standard library
import os
from shutil import copytree, rmtree
# Packages
from PIL import Image, ImageEnhance
# Project Modules
from . import _utils as utils
from . import _imgops as imgops
from ._tkinter import tk
from ._utils import get_file_directory


class ThemedWidget(object):
    """
    Provides functions to manipulate themes in order to reduce code
    duplication in the ThemedTk and ThemedStyle classes.
    """

    pixmap_themes = [
        "arc",
        "blue",
        "clearlooks",
        "elegance",
        "kroc",
        "plastik",
        "radiance",
        "ubuntu",
        "winxpblue"
    ]

    PACKAGES = {
        "keramik_alt": "keramik",
        "scidblue": "scid",
        "scidgreen": "scid",
        "scidgrey": "scid",
        "scidmint": "scid",
        "scidpink": "scid",
        "scidpurple": "scid",
        "scidsand": "scid",
    }

    _EXCLUDED = {"scid"}

    def __init__(self, tk_interpreter, gif_override=False):
        """
        Initialize attributes and call _load_themes

        :param tk_interpreter: tk interpreter for tk.Widget that is
            being initialized as ThemedWidget. Even if this Widget is
            just a single widget, the changes affect all widgets with
            the same parent Tk instance.
        :param gif_override: Force loading of GIF-themes even if
            PNG-themes can be loaded
        """
        self.tk = tk_interpreter

        # Change working directory temporarily to allow Tcl to work
        self.png_support = True and not gif_override
        if tk.TkVersion <= 8.5 and not gif_override:
            self.png_support = False
            try:
                from tkimg import load_tkimg_into_interpreter
                load_tkimg_into_interpreter(self.tk)
                self.png_support = True
            except (ImportError, tk.TclError):
                pass
        self._load_themes()

    def _load_themes(self):
        """Load the themes into the Tkinter interpreter"""
        with utils.temporary_chdir(utils.get_file_directory()):
            self._append_theme_dir("themes")
            self.tk.eval("source themes/pkgIndex.tcl")
            theme_dir = "gif" if not self.png_support else "png"
            self._append_theme_dir(theme_dir)
            self.tk.eval("source {}/pkgIndex.tcl".format(theme_dir))
        self.tk.call("package", "require", "ttk::theme::scid")

    def _append_theme_dir(self, name):
        """Append a theme dir to the Tk interpreter auto_path"""
        path = "[{}]".format(get_file_directory() + "/" + name)
        self.tk.call("lappend", "auto_path", path)

    def set_theme(self, theme_name):
        """
        Set new theme to use. Uses a direct tk call to allow usage
        of the themes supplied with this package.

        :param theme_name: name of theme to activate
        """
        package = theme_name if theme_name not in self.PACKAGES else self.PACKAGES[theme_name]
        self.tk.call("package", "require", "ttk::theme::{}".format(package))
        self.tk.call("ttk::setTheme", theme_name)

    def get_themes(self):
        """Return a list of names of available themes"""
        return list(set(self.tk.call("ttk::themes")) - self._EXCLUDED)

    @property
    def themes(self):
        """Property alias of get_themes()"""
        return self.get_themes()

    def set_theme_advanced(self, theme_name, brightness=1.0,
                           saturation=1.0, hue=1.0,
                           preserve_transparency=True, output_dir=None,
                           advanced_name="advanced"):
        """
        Load an advanced theme that is dynamically created

        Applies the given modifiers to the images of the theme given and
        then creates a theme from these new images with the name
        'advanced' and then applies this theme. Is not available without
        support for PNG-based themes, then raises RuntimeError.
        """
        if not self.png_support:
            raise RuntimeError("PNG-based themes are not supported in the environment")
        # Check if the theme is a pixmap theme
        if theme_name not in self.pixmap_themes:
            raise ValueError("Theme is not a valid pixmap theme")
        # Check if theme is available in the first place
        if theme_name not in self.themes:
            raise ValueError("Theme to create new theme from is not available: {}".format(theme_name))
        if advanced_name in self.themes:
            raise RuntimeError("The same name for an advanced theme cannot be used twice")
        # Unload advanced if already loaded
        output_dir = os.path.join(utils.get_temp_directory(), advanced_name) if output_dir is None else output_dir
        self._setup_advanced_theme(theme_name, output_dir, advanced_name)
        # Perform image operations
        image_directory = os.path.join(output_dir, advanced_name, advanced_name)
        self._setup_images(image_directory, brightness, saturation, hue, preserve_transparency)
        # Load the new theme
        with utils.temporary_chdir(output_dir):
            self.tk.call("lappend", "auto_path", "[{}]".format(output_dir))
            self.tk.eval("source pkgIndex.tcl")
            self.set_theme(advanced_name)

    def _setup_advanced_theme(self, theme_name, output_dir, advanced_name):
        """
        Setup all the files required to enable an advanced theme.

        Copies all the files over and creates the required directories
        if they do not exist.

        :param theme_name: theme to copy the files over from
        :param output_dir: output directory to place the files in
        """
        """Directories"""
        output_theme_dir = os.path.join(output_dir, advanced_name)
        output_images_dir = os.path.join(output_theme_dir, advanced_name)
        input_theme_dir = os.path.join(
            utils.get_themes_directory(theme_name, self.png_support), theme_name)
        input_images_dir = os.path.join(input_theme_dir, theme_name)
        advanced_pkg_dir = os.path.join(utils.get_file_directory(), "advanced")
        """Directory creation"""
        for directory in [output_dir, output_theme_dir]:
            utils.create_directory(directory)
        """Theme TCL file"""
        file_name = theme_name + ".tcl"
        theme_input = os.path.join(input_theme_dir, file_name)
        theme_output = os.path.join(output_theme_dir, "{}.tcl".format(advanced_name))
        with open(theme_input, "r") as fi, open(theme_output, "w") as fo:
            for line in fi:
                # Setup new theme
                line = line.replace(theme_name, advanced_name)
                # Setup new image format
                line = line.replace("gif89", "png")
                line = line.replace("gif", "png")
                # Write processed line
                fo.write(line)
        """pkgIndex.tcl file"""
        theme_pkg_input = os.path.join(advanced_pkg_dir, "pkgIndex.tcl")
        theme_pkg_output = os.path.join(output_theme_dir, "pkgIndex.tcl")
        with open(theme_pkg_input, "r") as fi, open(theme_pkg_output, "w") as fo:
            for line in fi:
                fo.write(line.replace("advanced", advanced_name))
        """pkgIndex_package.tcl -> pkgIndex.tcl"""
        theme_pkg_input = os.path.join(advanced_pkg_dir, "pkgIndex_package.tcl")
        theme_pkg_output = os.path.join(output_dir, "pkgIndex.tcl")
        with open(theme_pkg_input, "r") as fi, open(theme_pkg_output, "w") as fo:
            for line in fi:
                fo.write(line.replace("advanced", advanced_name))
        """Images"""
        if os.path.exists(output_images_dir):
            rmtree(output_images_dir)
        copytree(input_images_dir, output_images_dir)

    @staticmethod
    def _setup_images(directory, brightness, saturation, hue, preserve_transparency):
        """
        Apply modifiers to the images of a theme

        Modifies the images using the PIL.ImageEnhance module. Using
        this function, theme images are modified to given them a
        unique look and feel. Works best with PNG-based images.
        """
        for file_name in os.listdir(directory):
            with open(os.path.join(directory, file_name), "rb") as fi:
                image = Image.open(fi).convert("RGBA")
            # Only perform required operations
            if brightness != 1.0:
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(brightness)
            if saturation != 1.0:
                enhancer = ImageEnhance.Color(image)
                image = enhancer.enhance(saturation)
            if hue != 1.0:
                image = imgops.shift_hue(image, hue)
            if preserve_transparency is True:
                image = imgops.make_transparent(image)
            # Save the new image
            image.save(os.path.join(directory, file_name.replace("gif", "png")))
            image.close()
        for file_name in (item for item in os.listdir(directory) if item.endswith(".gif")):
            os.remove(os.path.join(directory, file_name))
