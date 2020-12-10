from typing import Optional, Tuple
import pygame
from PPlayMaps import Tileset, Vector

class TileBar:

    @staticmethod
    def calc_size(
        position: Vector,
        screen_size: Vector,
        screen_tile_size: Vector
    ) -> Tuple[int, int, int, int]:
        sw, sh = screen_size
        tx, ty = screen_tile_size

        height = sh - position[1]
        length = height // ty
        inner_height = length * ty
        margin = (height - inner_height) // 2

        return height, inner_height, length, margin

    def __init__(
        self,
        tileset: Tileset,
        position: Tuple[int, int],
        screen_size: Tuple[int, int],
        screen_tile_size: Tuple[int, int],
    ) -> None:
        height, inner_height, length, margin = self.calc_size(position, screen_size, screen_tile_size)

        self.height = height
        self.inner_height = inner_height
        self.__length__ = self.length = length
        self.margin = margin
        self.width = width = screen_tile_size[0]

        self.tileset = tileset
        self.screen_size = screen_size
        self.screen_tile_size = screen_tile_size
        self.position = position

        tile_size = tileset.tile_size
        self.tile_size = tile_size
        self.size = size = len(tileset) + 1
        self.max_scroll = max(0, size - length)
        self.curr_scroll = 0

        self.selected_tile = 0
        self.screen = pygame.Surface((width, height))
        self.display = pygame.Surface((tile_size, length * tile_size))
        self.screen.fill((255, 255, 255))

    def __getitem__(self, key):
        return self.tileset[key]

    def change_tile(self, d: int) -> int:
        selected_tile = self.selected_tile + d
        size = self.size
        lenght = self.length
        scroll = self.curr_scroll
        max_scroll = self.max_scroll
        half = lenght // 2
        r = lenght % 2

        if selected_tile < 0:
            selected_tile = size
        elif selected_tile > size:
            selected_tile = 0
        if d < 0 and scroll > 0 and (size - selected_tile) > half + r:
            # subindo, tile atual está < meia tela do fundo
            self.scroll(d)
        elif d > 0 and scroll < max_scroll and selected_tile > half:
            # descendo, tile atual está < meia tela do topo
            self.scroll(d)
        self.selected_tile = selected_tile
        return selected_tile
    
    def set_tile(self, tile: int) -> int:
        size = self.size
        if tile < 0:
            tile = size
        if tile > size:
            tile = 0
        self.selected_tile = tile
        return tile

    def get_rect(self) -> pygame.Rect:
        cx, cy = self.position
        rect = (cx, cy, self.width, self.height)
        return pygame.Rect(rect)

    def is_mouseouver(self) -> int:
        pos = pygame.mouse.get_pos()
        r = self.get_rect()
        return r.collidepoint(pos)
    
    def click(self) -> int:
        x, y = pygame.mouse.get_pos()
        sx, sy = self.screen_tile_size
        px, py = self.position
        scroll = self.curr_scroll
        size = self.size
        my = self.margin
        dy = py + my
        index = (y - dy) // sy + scroll
        if 0 <= index <= size:
            self.selected_tile = index
            return index
        return self.selected_tile

    def on_resize(
        self,
        position: Optional[Vector] = None,
        screen_size: Optional[Vector] = None,
        screen_tile_size: Optional[Vector] = None
    ):
        if position is None: position = self.position
        if screen_size is None: screen_size = self.screen_size
        if screen_tile_size is None: screen_tile_size = self.screen_tile_size

        height, inner_height, length, margin = self.calc_size(position, screen_size, screen_tile_size)

        self.height = height
        self.inner_height = inner_height
        self.__length__ = self.length = length
        self.margin = margin
        self.width = width = screen_tile_size[0]

        self.screen_size = screen_size
        self.screen_tile_size = screen_tile_size
        self.position = position

        # tile_size = self.tile_size
        # self.display = pygame.Surface((tile_size, length * tile_size))
        self.screen = pygame.Surface((width, height))
        self.screen.fill((255, 255, 255))

    def scroll(self, d: int):
        max_scroll = self.max_scroll
        if max_scroll == 0:
            return 0
        new_scroll = min(max_scroll, max(0, self.curr_scroll + d))

        self.curr_scroll = new_scroll
        return new_scroll

    def blit(self):
        d = self.tileset.tile_size
        tiles = [0] + self.tileset.tiles
        curr_scroll = self.curr_scroll
        selected_tile = self.selected_tile
        length = self.length

        ymin, ymax = 0 + curr_scroll, length + curr_scroll
        self.display.fill((255, 255, 255))

        for y, tile in enumerate(tiles[ymin:ymax]):
            if y == ymin == 0:
                pass
            else:
                self.display.blit(tile, (0, y * d))
        if selected_tile is None:
            pass
        elif ymin <= selected_tile <= ymax:
            tile_y = (selected_tile - curr_scroll) * d
            pygame.draw.rect(self.display, (24, 144, 255), (0, tile_y, d, d), width = 1)
    
    def draw_self(self, screen):
        self.screen.blit(pygame.transform.scale(self.display, (self.width, self.inner_height)), (0, self.margin))
        screen.blit(self.screen, self.position)