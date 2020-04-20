"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2017-2018 RedFantom
"""


def shift_hue(image, hue):
    """
    Shifts the hue of an image in HSV format.
    :param image: PIL Image to perform operation on
    :param hue: value between 0 and 2.0
    """
    hue = (hue - 1.0) * 180
    img = image.copy().convert("HSV")
    pixels = img.load()
    for i in range(img.width):
        for j in range(img.height):
            h, s, v = pixels[i, j]
            h = abs(int(h + hue))
            if h > 255:
                h -= 255
            pixels[i, j] = (h, s, v)
    return img.convert("RGBA")


def make_transparent(image):
    """Turn all black pixels in an image into transparent ones"""
    data = image.copy().getdata()
    modified = []
    for item in data:
        if _check_pixel(item) is True:
            modified.append((255, 255, 255, 255))  # White transparent pixel
            continue
        modified.append(item)
    image.putdata(modified)
    return image


def _check_pixel(tup):
    """Check if a pixel is black, supports RGBA"""
    return tup[0] == 0 and tup[1] == 0 and tup[2] == 0
