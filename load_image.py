import os
import pathlib
import sys

import pygame as pg

def load_image(name, colorkey=None):
    fullname = pathlib.Path("data") / name
    if not os.path.isfile(fullname):
        print(f"Файла {fullname} не найдено")
        sys.exit()
    image = pg.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image