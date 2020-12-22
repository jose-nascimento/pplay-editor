from typing import List, Optional
from pygame.locals import Color
import json
import os
from PIL import Image
import pygame
from PPlayMaps import Tileset, config as conf
from PPlayMaps.types import Vector, Vec, OpType
from .helpers import add_v, clamp, sub_v
config = conf.config
active = config["active"]

class Map:

    def __init__(
            self,
            name: str,
            layers: List[List[List[int]]] = None,
            movement: List[List[int]] = None,
            tileset: str = None,
            height: int = 16,
            width: int = 30,
            project: str = None,
            path: str = None,
            background: dict = None,
            bgimage: pygame.Surface = None,
            **kwargs
        ):
        self.name = name
        self.height = height
        self.width = width
        if background is None: background = {}
        self.background = background
        tileset = tileset
        bgcolor = background["background_color"] if "background_color" in background else None
        self.bgcolor = (bgcolor[0], bgcolor[1], bgcolor[2])
        self.bgimage = bgimage
        self.tileset = tileset
        self.project = project
        self.path = path
        self.movement = movement if movement else self.init_layer()
        self.layers = layers if layers else [self.init_layer() for _ in range(4)]

    def get_params(self) -> dict:
        return {
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "bgcolor": self.bgcolor,
            "tileset": self.tileset,
            "bgimage": self.background.get("image", None)
        }

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
            image = data["background"].get("image", None)
            if image is not None:
                img_path = os.path.join(path, image)
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
    
    def export_image(self, path: str, project: Optional[str] = None):
        tileset_name = self.tileset
        tileset = Tileset.load(name = tileset_name, project = project, mode = "export")
        delta = tileset.tile_size
        map_size = (self.width * delta, self.height * delta)
        color = self.bgcolor or (255, 0, 0, 0)
        canvas = Image.new("RGBA", map_size, color)
        if "image" in self.background:
            bgimage = Image.open(os.path.join(self.path, self.background["image"]))
            canvas.paste(bgimage, (0, 0), bgimage)
        for layer in self.layers:
            for y, line in enumerate(layer):
                for x, tile in enumerate(line):
                    if tile > 0:
                        canvas.paste(tileset[tile], (x * delta, y * delta), tileset[tile])

        canvas.save(path)

    def clear_layer(self, layer: int):
        index = layer - 1
        self.layers[index] = self.init_layer()

    def clear_movement(self):
        self.movement = self.init_layer()

    def place_tile(
        self,
        tile: int,
        pos: Vec,
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
        start: Vec,
        end: Vec,
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
    
    def flood_fill(self, tile: int, point: Vec, layer: int, movement_layer: bool = False):
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
    
    def get_tile(self, pos: Vec, z: int) -> int:
        x, y = pos
        if min(pos) < 0:
            return 0
        if (x >= self.width) or (y >= self.height):
            return 0
        return self.layers[z - 1][y][x]
    
    def resize(self, value: Vec, *, op: OpType = "="):
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
        img_path = os.path.join(self.path, image)
        bgimage = pygame.image.load(img_path).convert_alpha()

        self.bgimage = bgimage
        self.background["image"] = image

    def unset_bgimage(self):
        self.background["image"] = None
        self.bgimage = None

    def set_tileset(self, tileset: str, limit: Optional[int] = None):
        self.tileset = tileset

        if limit is not None:
            self.layers = [
                [
                    [tile if tile <= limit else 0 for tile in line] for line in layer
                ] for layer in self.layers
            ]

    def init_layer(self) -> List[List[int]]:
        w, h = self.width, self.height
        return [[0] * w for _ in range(h)]
