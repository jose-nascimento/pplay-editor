from typing import Tuple
import pygame
from PPlayMaps import Tileset

class TileBar:

    def __init__(
            self,
            tileset: Tileset,
            position: Tuple[int, int],
            screen_tile_size: Tuple[int, int],
            height: int = 16,
        ) -> None:
        self.height = height
        self.tileset = tileset
        self.screen_tile_size = screen_tile_size
        self.position = position

        tile_size = tileset.tile_size
        self.display = pygame.Surface((tile_size, tile_size * height))

    def blit(self, selected_tile = None):
        d = self.tileset.tile_size
        tiles = self.tileset.tiles
        xmax = self.height
        self.display.fill((255, 255, 255))

        for y, tile in enumerate(tiles[0:xmax]):
            self.display.blit(tile, (0, y * d))
        if selected_tile:
            tile_y = (selected_tile - 1) * d
            pygame.draw.rect(self.display, (24, 144, 255), (0, tile_y, d, d), width = 1)
    
    def draw_self(self, screen):
        sx, sy = self.screen_tile_size
        screen.blit(pygame.transform.scale(self.display, (sx, sy * self.height)), self.position)