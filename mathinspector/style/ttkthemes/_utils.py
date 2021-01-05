"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2017-2018 RedFantom
"""
import contextlib
import os
from shutil import rmtree
from tempfile import gettempdir

platforms = {
    "win32": "win",
    "linux2": "linux"
}


@contextlib.contextmanager
def temporary_chdir(new_dir):
    """
    Like os.chdir(), but always restores the old working directory

    For example, code like this...

        old_curdir = os.getcwd()
        os.chdir('stuff')
        do_some_stuff()
        os.chdir(old_curdir)

    ...leaves the current working directory unchanged if do_some_stuff()
    raises an error, so it should be rewritten like this:

        old_curdir = os.getcwd()
        os.chdir('stuff')
        try:
            do_some_stuff()
        finally:
            os.chdir(old_curdir)

    Or equivalently, like this:

        with utils.temporary_chdir('stuff'):
            do_some_stuff()
    """
    old_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(old_dir)


def get_file_directory():
    """Return an absolute path to the current file directory"""
    return os.path.dirname(os.path.realpath(__file__))


def get_temp_directory():
    """Return an absolute path to an existing temporary directory"""
    # Supports all platforms supported by tempfile
    directory = os.path.join(gettempdir(), "ttkthemes")
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory


def get_themes_directory(theme_name=None, png=False):
    """Return an absolute path the to /themes directory"""
    dir_themes = os.path.join(get_file_directory(), "themes")
    if theme_name is None:
        return dir_themes
    if theme_name in os.listdir(dir_themes):
        return dir_themes
    dir = "png" if png is True else "gif"
    return os.path.join(get_file_directory(), dir)


def create_directory(directory):
    """Create directory but first delete it if it exists"""
    if os.path.exists(directory):
        rmtree(directory)
    os.makedirs(directory)
    return directory
