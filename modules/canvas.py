import os
from pygame.locals import *
import pygame
from modules import Map, Tileset

class Canvas:

    def __init__(self, width, height, position):
        self.width = width
        self.height = height
        self.position = position
        self.dimensions = dimensions = (width * 16, height * 16)
        self.display = pygame.Surface(dimensions)
        # self.pencil = pygame.cursors.load_xbm(os.path.join("res", "pencil-cursor16.xbm"), os.path.join("res", "pencil-cursor16.xbm"))

    @property
    def onscreen_size(self):
        return (self.width * 48, self.height * 48)

    def draw_self(self, screen):
        screen.blit(pygame.transform.scale(self.display, self.onscreen_size), self.position)
    
    def get_xy(self) -> tuple:
        x, y = pygame.mouse.get_pos()
        dx, dy = self.position
        pos = ((x - dx) // 48, (y - dy) // 48)
        return pos
    
    def get_rect(self):
        rect = (cx, cy, cw, ch) = *self.position, *self.onscreen_size
        return pygame.Rect(rect)

    def pointer_tile(self, tile, tileset: Tileset):
    # =========== Mostra tile atual na posição do mouse ===========
        pos = x, y = pygame.mouse.get_pos()
        dx, dy = self.position
        if self.display.get_rect().collidepoint(pos):
            x -= 14 + dx
            y -= 14 + dy
            x, y = x // 3, y // 3
            self.display.blit(tileset[tile], (x, y))
            # pygame.mouse.set_cursor(*self.pencil)
    
    def blit_tiles(self, map: Map, layer, tileset: Tileset):
        current = map.layers[layer - 1]

        for y, line in enumerate(current):
            for x, c in enumerate(line):
                if c != 0:
                    self.display.blit(tileset[c], (x * 16, y * 16))
    
    def draw_map(self, map: Map, show_layers: int, tileset: Tileset):
        self.display.fill(map.bgcolor)

        if show_layers & 0b0001:
            self.blit_tiles(map, 1, tileset)
        if show_layers & 0b0010:
            self.blit_tiles(map, 2, tileset)
        if show_layers & 0b0100:
            self.blit_tiles(map, 3, tileset)
        if show_layers & 0b1000:
            self.blit_tiles(map, 4, tileset)