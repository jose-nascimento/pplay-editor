from typing import List, Literal, Optional, Union

from pygame.locals import Color
from PPlayMaps.types import Vector
import json
import os
from PIL import Image
import pygame
from PPlayMaps import Tileset, config as conf
from .helpers import add_v, clamp, sub_v
config = conf.config
active = config["active"]

class Map:

    def __init__(
            self,
            name,
            layers = None,
            movement = None,
            tileset = None,
            height = 16,
            width = 30,
            project = None,
            path = None,
            background = {},
            bgimage = None,
            **kwargs
        ):
        self.name = name
        self.height = height
        self.width = width
        self.background = background
        tileset = tileset
        bgcolor = background["background_color"] if "background_color" in background else (0, 0, 0)
        self.bgcolor = (bgcolor[0], bgcolor[1], bgcolor[2])
        self.bgimage = bgimage
        self.tileset = tileset
        self.project = project
        self.path = path
        self.movement = movement if movement else self.init_layer()
        self.layers = layers if layers else [self.init_layer() for _ in range(4)]

    def save_map(self):
        path = os.path.join(self.path, "map.json")
        with open(path, "w") as json_file:
            json.dump(
                {
                    "name": self.name,
                    "tileset": self.tileset,
                    "size": {
                        "width": self.width,
                        "height": self.height
                    },
                    "background": self.background,
                    "movement": self.movement,
                    "layers": self.layers
                },
                json_file
            )

    @classmethod
    def load_from(cls, path):
        filename = "map.json"
        if filename in os.listdir(path):
            with open(os.path.join(path, filename), "r") as json_file:
                data = json.load(json_file)
            if "image" in data["background"]:
                img_path = os.path.join(path, data["background"]["image"])
                bgimage = pygame.image.load(img_path).convert_alpha()
            else:
                bgimage = None
            return cls(
                    path = path,
                    width = data["size"]["width"],
                    height = data["size"]["height"],
                    bgimage = bgimage,
                    **data,
                )
        else:
            raise FileNotFoundError

    @classmethod
    def load(cls, name: str, project: Optional[str] = None):
        path = config.default_folder(project)
        path = os.path.join(path, "maps", name)
        return cls.load_from(path)

    @property
    def size(self) -> Vector:
        return Vector(self.width, self.height)
    
    def export(self, project: Optional[str] = None):
        tileset_name = self.tileset
        tileset = Tileset.load(name = tileset_name, project = project, mode = "export")
        delta = tileset.tile_size
        map_size = (self.width * delta, self.height * delta)
        canvas = Image.new("RGBA", map_size, self.bgcolor)
        if "image" in self.background:
            bgimage = Image.open(os.path.join(self.path, self.background["image"]))
            canvas.paste(bgimage, (0, 0), bgimage)
        for layer in self.layers:
            for y, line in enumerate(layer):
                for x, tile in enumerate(line):
                    if tile > 0:
                        canvas.paste(tileset[tile], (x * delta, y * delta), tileset[tile])
        canvas.save(os.path.join(self.path, f"{self.name}.png"))

    def clear_layer(self, layer: int):
        index = layer - 1
        self.layers[index] = self.init_layer()

    def clear_movement(self):
        self.movement = self.init_layer()

    def place_tile(
        self,
        tile: int,
        pos: Vector,
        layer: int,
        movement_layer: bool = False
    ):
        x, y = pos
        if min(pos) < 0:
            return
        if (x >= self.width) or (y >= self.height):
            return
        if movement_layer:
            self.movement[y][x] = tile
        else:
            self.layers[layer - 1][y][x] = tile

    def fill_area(
        self,
        tile: int,
        start: Vector,
        end: Vector,
        layer: int,
        movement_layer: bool = False
    ):
        mp = self.movement if movement_layer else self.layers[layer - 1]
        x0, y0 = start
        x1, y1 = end
        x0, x1 = clamp((x0, x1), (0, self.width))
        y0, y1 = clamp((y0, y1), (0, self.height))
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        x1 += 1
        for line in mp[y0:y1]:
            for x, _ in enumerate(line[x0:x1]):
                line[x + x0] = tile
    
    def flood_fill(self, tile: int, point: Vector, layer: int, movement_layer: bool = False):
        # usa o algoritmo "scanline fill"
        if min(point) < 0: return
        mp = self.movement if movement_layer else self.layers[layer - 1]
        ymax = self.height - 1
        xmax = self.width - 1
        x, y = point
        if (x > xmax) or (y > ymax):
            return
        target_tile = mp[point[1]][point[0]]
        if target_tile == tile:
            return
        stack = [point]

        while(len(stack)):
            x, y = stack.pop()
            if mp[y][x] == target_tile:
                mp[y][x] = tile
                if x > 0: stack.append((x - 1, y))
                if x < xmax: stack.append((x + 1, y))
                if y > 0: stack.append((x, y - 1))
                if y < ymax: stack.append((x, y + 1))
    
    def get_tile(self, pos: Vector, z: int) -> int:
        x, y = pos
        if min(pos) < 0:
            return 0
        if (x >= self.width) or (y >= self.height):
            return 0
        return self.layers[z - 1][y][x]
    
    def resize(self, value: Vector, *, op: Literal["=", "+", "-"] = "="):
        w, h = size = self.size
        if op == "=":
            new_size = value
        elif op == "+":
            new_size = add_v(size, value)
        elif op == "-":
            new_size = sub_v(size, value)
        else:
            return
        self.width, self.height = x, y = new_size
        dx, dy = x - w, y - h
        self.layers = [[line[:x] + [0]*dx for line in (layer[:y] + ([[0]*x]*dy))] for layer in self.layers]
        self.movement = [line[:x] + [0]*dx for line in (self.movement[:y] + ([[0]*x]*dy))]

    def set_bgcolor(self, color: Color):
        self.bgcolor = color

    def set_bgimage(self, image: str):
        path = os.path.join(self.path, image)
        bgimage = pygame.image.load(path).convert_alpha()
        self.bgimage = bgimage

    def init_layer(self) -> List[List[int]]:
        w, h = self.height, self.width
        return [[0] * w for _ in range(h)]
