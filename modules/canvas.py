from pygame.locals import *
import pygame
from modules import Map, Tileset

class Canvas:

    def __init__(self, position, canvas_size, canvas_tile_size, map_tile_size):
        cw, ch = canvas_size
        width, height = (cw // canvas_tile_size, ch // canvas_tile_size)
        self.width = width
        self.height = height

        screen_w, screen_h = width * canvas_tile_size, height * canvas_tile_size
        rw, rh = cw - screen_w, ch - screen_h
        self.margin_right = (rw, rh)
        self.screen_size = (screen_w, screen_h)

        self.canvas_tile_size = canvas_tile_size
        self.map_tile_size = map_tile_size

        self.position = position
        self.dimensions = dimensions = (width * map_tile_size, height * map_tile_size)
        self.factor = canvas_tile_size / map_tile_size
        self.display = pygame.Surface(dimensions)

        # self.pencil = pygame.cursors.load_xbm(os.path.join("res", "pencil-cursor16.xbm"), os.path.join("res", "pencil-cursor16.xbm"))

    def draw_self(self, screen):
        screen.blit(pygame.transform.scale(self.display, self.screen_size), self.position)
    
    def get_xy(self) -> tuple:
        x, y = pygame.mouse.get_pos()
        d = self.canvas_tile_size
        dx, dy = self.position
        pos = ((x - dx) // d, (y - dy) // d)
        return pos
    
    def get_rect(self):
        rect = (cx, cy, cw, ch) = *self.position, *self.screen_size
        return pygame.Rect(rect)

    def pointer_tile(self, tile, tileset: Tileset):
    # =========== Mostra tile atual na posição do mouse ===========
        pos = x, y = pygame.mouse.get_pos()
        f = self.factor
        dx, dy = self.position
        if self.display.get_rect().collidepoint(pos):
            x -= 14 + dx
            y -= 14 + dy
            x, y = x // f, y // f
            self.display.blit(tileset[tile], (x, y))
            # pygame.mouse.set_cursor(*self.pencil)
    
    def blit_tiles(self, map: Map, layer, tileset: Tileset):
        current = map.layers[layer - 1]
        delta = self.map_tile_size

        for y, line in enumerate(current):
            for x, c in enumerate(line):
                if c != 0:
                    self.display.blit(tileset[c], (x * delta, y * delta))

    def blit_movement(self, map: Map):
        d = self.map_tile_size
        c = d // 2
        r = (d // 8) * 3
        x0 = (d - 1) // 4
        x1 = d - x0

        for y, line in enumerate(map.movement):
            for x, m in enumerate(line):
                if m == 0:
                    pygame.draw.circle(self.display, (255, 255, 255), (x * d + c, y * d + c), r, width = 1)
                elif m == 1:
                    pygame.draw.line(self.display, (255, 255, 255), (x * d + x0,  y * d + c), (x * d + x1,  y * d + c), width = 2)
    
    def draw_map(self, map: Map, show_layers: int, tileset: Tileset, layer: int = 1, movement_layer = False):
        self.display.fill(map.bgcolor)
        if map.bgimage: self.display.blit(map.bgimage, (0, 0))

        if show_layers & 0b0001:
            self.blit_tiles(map, 1, tileset)
        if show_layers & 0b0010:
            self.blit_tiles(map, 2, tileset)
        if show_layers & 0b0100:
            self.blit_tiles(map, 3, tileset)
        if show_layers & 0b1000:
            self.blit_tiles(map, 4, tileset)
        if movement_layer:
            self.blit_movement(map)