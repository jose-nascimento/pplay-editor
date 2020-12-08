import os
import json
from PIL import Image
import pygame
from glob import glob
from modules import config as conf
config = conf.config["current"]

class Tileset:

    def __init__(self, name, tiles, position, tile_size = 16, height = 16, canvas_tile_size = 48, mode = "pygame"):
        self.name = name
        self.tile_size = tile_size
        self.canvas_tile_size = canvas_tile_size
        self.height = height
        self.tiles = tiles
        # self.tiles = [pygame.image.fromstring(i.tobytes(), i.size, i.mode) for i in tiles]
        if mode == "pygame": self.display = pygame.Surface((tile_size, tile_size * height))
        self.position = position

    def blit(self, selected_tile = None, mode = 0):
        d = self.tile_size
        self.display.fill((255, 255, 255))

        for y, tile in enumerate(self.tiles[1:15]):
            self.display.blit(tile, (0, y * d))
        if selected_tile:
            tile_y = (selected_tile - 1) * d
            pygame.draw.rect(self.display, (24, 144, 255), (0, tile_y, d, d), width = 1)
    
    def draw_self(self, screen):
        ts = self.canvas_tile_size
        screen.blit(pygame.transform.scale(self.display, (ts, ts * self.height)), self.position)

    def __getitem__(self, key):
        return self.tiles[key]

    def __setitem__(self, key, value):
        self.tiles[key] = value

    def __len__(self):
        return len(self.tiles)

    @classmethod
    def load_tiles(cls, position = None, canvas_tile_size = None, name = None, project = None, mode = "pygame"):
        if name == None:
            name = config["default_tileset"]
        if project == None:
            project = config["active_project"]
        path = os.path.join("projects", project, "tilesets", name)
        with open(os.path.join(path, "tileset.json"), "r") as file:
            options = json.load(file)
        tile_size = options["tile_size"]
        tile_list = sorted([x for x in glob(os.path.join(path, "*.png"))])
        if mode == "pygame":
            tiles = [pygame.image.load(x) for x in tile_list]
        else:
            tiles = [Image.open(x).convert("RGBA") for x in tile_list]
        tileset = cls(name, tiles, position, tile_size= tile_size, mode = mode, canvas_tile_size = canvas_tile_size)
        return tileset
