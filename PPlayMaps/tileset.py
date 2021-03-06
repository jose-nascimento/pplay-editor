import os
import json
from typing import Optional
from PIL import Image
import pygame
from glob import glob
from PPlayMaps import config as conf
config = conf.config
active = config["active"]

class Tileset:

    def __init__(self, name: str, tiles = None, tile_size: int = 16, path: Optional[str] = None):
        if not tiles:
            tiles = []
        self.name = name
        self.tile_size = tile_size
        self.tiles = tiles
        self.path = path

    def __getitem__(self, key):
        if key == 0:
            return None
        return self.tiles[key - 1]

    def __setitem__(self, key, value):
        self.tiles[key - 1] = value

    def __len__(self):
        return len(self.tiles)

    def save(self):
        with open(os.path.join(self.path, "tileset.json"), "w") as json_file:
            json.dump({
                "name": self.name,
                "tile_size": self.tile_size
            }, json_file)

    @classmethod
    def load_from(cls, path: str, mode: str = "default"):
        with open(os.path.join(path, "tileset.json"), "r") as json_file:
            options = json.load(json_file)
        name = options["name"]
        tile_size = options["tile_size"]
        tile_list = sorted([x for x in glob(os.path.join(path, "*.png"))])
        if mode == "export":
            tiles = [Image.open(x).convert("RGBA") for x in tile_list]
        else:
            tiles = [pygame.image.load(x).convert_alpha() for x in tile_list]
        tileset = cls(name, tiles, tile_size = tile_size, path = path)
        return tileset


    @classmethod
    def load(cls, name: str = None, project: str = None, mode: str = "default"):
        if name == None:
            return cls("default")
        path = config.default_folder(project)
        path = os.path.join(path, "tilesets", name)
        return cls.load_from(path, mode)
