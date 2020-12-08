import json
import os
from PIL import Image
import pygame
from modules import Tileset, config as conf
config = conf.config["current"]

class Map:

    def __init__(
            self,
            name,
            layers = None,
            movement = None,
            tileset = config["default_tileset"],
            height = 16,
            width = 30,
            project = None,
            background = {},
            bgimage = None,
            **kwargs
        ):
        self.name = name
        self.height = height
        self.width = width
        self.background = background
        bgcolor = background["background_color"] if "background_color" in background else (0, 0, 0)
        self.bgcolor = (bgcolor[0], bgcolor[1], bgcolor[2])
        self.bgimage = bgimage
        self.tileset = tileset
        self.project = project
        self.movement = movement if movement else self.init_layer()
        self.layers = layers if layers else [self.init_layer(), self.init_layer(), self.init_layer()]

    def save_map(self, project = None):
        if project == None:
            project = config["active_project"]
        filename = f"{self.name}.json"
        path = os.path.join("projects", project, "maps", self.name, filename)
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
    def load_map(cls, name = None, project = None):
        if name == None: name = config["start_map"]
        if project == None: project = config["active_project"]
        filename = f"{name}.json"
        path = os.path.join("projects", project, "maps", name)
        if filename in os.listdir(path):
            with open(os.path.join(path, filename), "r") as json_file:
                data = json.load(json_file)
            if "image" in data["background"]:
                img_path = os.path.join(path, data["background"]["image"])
                bgimage = pygame.image.load(img_path)
            else:
                bgimage = None
            return cls(
                    project = project,
                    width = data["size"]["width"],
                    height = data["size"]["height"],
                    bgimage = bgimage,
                    **data,
                )
        else:
            raise FileNotFoundError

    def get_path(self):
        return os.path.join("projects", self.project, "maps", self.name)

    @property
    def size(self):
        return (self.width, self.height)
    
    def export(self):
        project = self.project
        tileset_name = self.tileset
        tileset = Tileset.load_tiles(project = project, name = tileset_name, mode = "image")
        delta = tileset.tile_size
        map_size = (self.width * delta, self.height * delta)
        canvas = Image.new("RGBA", map_size, self.bgcolor)
        if "image" in self.background:
            bgimage = Image.open(os.path.join(self.get_path(), self.background["image"]))
            canvas.paste(bgimage, (0, 0), bgimage)
        for layer in self.layers:
            for y, line in enumerate(layer):
                for x, tile in enumerate(line):
                    canvas.paste(tileset[tile], (x * delta, y * delta), tileset[tile])
        canvas.save(os.path.join(self.get_path(), f"{self.name}.png"))

    def clear_layer(self, index):
        layer = index - 1
        self.layers[layer] = Map.init_layer()

    def place_tile(self, tile, pos, layer, movement_layer = False):
        x, y = pos
        if movement_layer:
            self.movement[y][x] = tile
        else:
            self.layers[layer - 1][y][x] = tile

    def fill_area(self, tile, start, end, layer, movement_layer = False):
        mp = self.movement if movement_layer else self.layers[layer - 1]
        x0, y0 = start
        x1, y1 = end
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        x1 += 1
        for line in mp[y0:y1]:
            for x, _ in enumerate(line[x0:x1]):
                line[x + x0] = tile
            # for x, _ in enumerate(line):
            #     if x0 <= x < x1:
            #         line[x] = tile
    
    def flood_fill(self, tile, point, layer, movement_layer = False):
        # usa o algoritmo "scanline fill"
        mp = self.movement if movement_layer else self.layers[layer - 1]
        stack = [point]
        ymax = len(mp) - 1
        xmax = len(mp[0]) - 1
        target_tile = mp[point[1]][point[0]]
        if target_tile == tile: return

        while(len(stack)):
            x, y = stack.pop()
            if mp[y][x] == target_tile:
                mp[y][x] = tile
                if x > 0: stack.append((x - 1, y))
                if x < xmax: stack.append((x + 1, y))
                if y > 0: stack.append((x, y - 1))
                if y < ymax: stack.append((x, y + 1))
    
    def get_tile(self, pos, z):
        x, y = pos
        return self.layers[z - 1][y][x]

    def init_layer(self):
        # 30x16
        layer = []
        for i in range(self.height):
            layer.append([0] * self.width)
        return layer