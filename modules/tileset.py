import pickle
import os
import pygame
from glob import glob
from modules import config as conf
config = conf.config["current"]

class Tileset:

    def __init__(self, name, tiles, position):
        self.name = name
        self.tiles = tiles
        self.display = pygame.Surface((16, 16 * 16))
        self.position = position

    def blit(self, selected_tile = None, mode = 0):
        self.display.fill((255, 255, 255))
        for y, tile in enumerate(self.tiles[1:15]):
            self.display.blit(tile, (0, y * 16))
        if selected_tile:
            tile_y = (selected_tile - 1) * 16
            pygame.draw.rect(self.display, (24, 144, 255), (0, tile_y, 16, 16), width = 1)
    
    def draw_self(self, screen):
        screen.blit(pygame.transform.scale(self.display, (48, 48 * 16)), self.position)

    def __getitem__(self, key):
        return self.tiles[key]

    def __setitem__(self, key, value):
        self.tiles[key] = value

    def __len__(self):
        return len(self.tiles)

    @classmethod
    def load_tiles(cls, position, name = None, project = None):
        if name == None:
            name = config["default_tileset"]
        if project == None:
            project = config["active_project"]
        path = os.path.join("projects", project, "tilesets", name)
        tile_list = sorted([x for x in glob(os.path.join(path, "*.png"))])
        tiles = [pygame.image.load(x) for x in tile_list]
        tileset = cls(name, tiles, position)
        return tileset
