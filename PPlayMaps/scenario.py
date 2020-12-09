from typing import Tuple
from pygame.locals import *
import pygame
from PPlayMaps import Map, Tileset

class Scenario:

    def __init__(self, position: Tuple[int, int], size: Tuple[int, int], screen_size: Tuple[int, int]):
        cw, ch = screen_size
        width, height = size
        screen_tile_size = (cw // width, ch // height)
        rw, rh = cw % width, cw % height

        self.width = width
        self.height = height
        self.margin = (rw, rh)
        self.screen_tile_size = screen_tile_size
        self.position = position
        self.screen_size = screen_size

        self.screen = pygame.Surface(screen_size)

    def set_map(self, map: Map, tileset: Tileset):
        sx, sy = self.screen_tile_size
        map_tile_size = tileset.tile_size
        factor = (sx / map_tile_size, sy / map_tile_size)
        dimensions = (self.width * map_tile_size, self.height * map_tile_size)

        self.map = map
        self.factor = factor
        self.dimensions = dimensions
        self.map_tile_size = map_tile_size
        self.tileset = tileset
        self.show_layers = 0b1111

        self.display = pygame.Surface(dimensions)

    def load_map(self, name):
        map = Map.load_map(name)
        tileset_name = map.tileset
        tileset = Tileset.load_tiles(tileset_name)

        self.set_map(map, tileset)

    def set_layer_visibility(self, layer, mode = None):
        if mode is None:
            self.show_layers ^= 1 << (layer - 1)
        elif mode == 0:
            mask = 1 << (layer - 1)
            self.show_layers = self.show_layers & ~mask
        elif mode == 1:
            mask = 1 << (layer - 1)
            self.show_layers = self.show_layers | mask

    def toggle_layer(self, layer):
        toggle = 1 << (layer - 1)
        if self.show_layers == toggle:
            self.show_layers = 0b1111
        else:
            self.show_layers = toggle

    def draw_self(self, screen):
        self.screen.blit(pygame.transform.scale(self.display, self.screen_size), (0, 0))
        screen.blit(self.screen, self.position)
    
    def get_xy(self) -> tuple:
        x, y = pygame.mouse.get_pos()
        sx, sy = self.screen_tile_size
        dx, dy = self.position
        pos = ((x - dx) // sx, (y - dy) // sy)
        return pos
    
    def get_rect(self):
        cx, cy = self.position
        cw, ch = self.screen_size
        rect = (cx, cy, cw, ch)
        return pygame.Rect(rect)
    
    def blit_tiles(self, layer):
        tileset = self.tileset
        current = self.map.layers[layer - 1]
        d = self.map_tile_size

        for y, line in enumerate(current):
            for x, c in enumerate(line):
                if c != 0:
                    self.display.blit(tileset[c], (x * d, y * d))
    
    def draw_map(self):
        map = self.map
        show_layers = self.show_layers
        self.display.fill(map.bgcolor)
        if map.bgimage: self.display.blit(map.bgimage, (0, 0))

        if show_layers & 0b0001:
            self.blit_tiles(1)
        if show_layers & 0b0010:
            self.blit_tiles(2)
        if show_layers & 0b0100:
            self.blit_tiles(3)
        if show_layers & 0b1000:
            self.blit_tiles(4)