import pygame, platform
from .util import color

FONT_SIZE = 12
SPACING = 128
MARGIN = int(3 * FONT_SIZE + FONT_SIZE/2)
BACKGROUND = color("272822")
PALE_BLUE = color("c7cbd1")
BLACK = color("333333")
WHITE = color("f8f8f2")
BLUE = color("60d9f1")
VERY_DARK_GREY = color("75715d")
RADIUS = 4

if platform.system() in ("Windows", "Linux"):
    MULTIPROCESS_CONTEXT = "spawn"
    ZOOM_MODIFIER = 5
else:
    MULTIPROCESS_CONTEXT = "fork"
    ZOOM_MODIFIER = 1
