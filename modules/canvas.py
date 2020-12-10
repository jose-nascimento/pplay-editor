from pygame.locals import *
import pygame
from PPlayMaps import Scenario

class Canvas(Scenario):

    def __init__(self, *args, limit_margin: bool = True, **kwargs):
        super().__init__(*args, limit_margin, **kwargs)

    # =========== Mostra tile atual na posição do mouse ===========
    def pointer_tile(self, tile):
        tileset = self.tileset
        pos = x, y = pygame.mouse.get_pos()
        fx, fy = self.factor
        dx, dy = self.position
        if self.display.get_rect().collidepoint(pos):
            x -= 14 + dx
            y -= 14 + dy
            x, y = x // fx, y // fy
            self.display.blit(tileset[tile], (x, y))

    def blit_movement(self):
        movement = self.map.movement
        d = self.map_tile_size
        c = d // 2
        r = (d // 8) * 3
        x0 = (d - 1) // 4
        x1 = d - x0

        for y, line in enumerate(movement):
            for x, m in enumerate(line):
                if m == 0:
                    pygame.draw.circle(self.display, (255, 255, 255), (x * d + c, y * d + c), r, width = 1)
                elif m == 1:
                    pygame.draw.line(self.display, (255, 255, 255), (x * d + x0,  y * d + c), (x * d + x1,  y * d + c), width = 2)