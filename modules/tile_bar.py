from typing import Literal, Optional, Tuple, Union
import pygame
from PPlayMaps import Tileset, Vector

class TileBar:

    def calc_size(
        self,
        position: Vector,
        screen_size: Vector,
        screen_tile_size: Vector
    ) -> Tuple[int, int]:
        sw, sh = screen_size
        tx, ty = screen_tile_size

        height = sh - position[1]
        length = height // ty
        inner_height = length * ty
        margin = (height - inner_height) // 2

        self.height = height
        self.inner_height = inner_height
        self.length = length
        self.margin = margin

        self.screen_size = screen_size
        self.screen_tile_size = screen_tile_size
        self.width = ty
        self.position = position

        return height, length

    def __init__(
        self,
        tileset: Tileset,
        position: Tuple[int, int],
        screen_size: Tuple[int, int],
        screen_tile_size: Tuple[int, int],
    ) -> None:
        height, length = self.calc_size(position, screen_size, screen_tile_size)

        width = screen_tile_size[0]

        self.tileset = tileset

        tile_size = tileset.tile_size
        self.tile_size = tile_size
        self.size = size = len(tileset)
        self.max_scroll = max(0, size + 1 - length)
        self.curr_scroll = 0
        self.selected_tile = 0

        self.screen = pygame.Surface((width, height))
        self.display = pygame.Surface((tile_size, length * tile_size))
        self.screen.fill((255, 255, 255))

    def set_tileset(self, tileset: Tileset) -> Literal[0]:
        self.tileset = tileset
        length = self.length

        tile_size = tileset.tile_size
        self.tile_size = tile_size
        self.size = size = len(tileset)
        self.max_scroll = max(0, size + 1 - length)
        self.curr_scroll = 0
        self.selected_tile = 0

        self.display = pygame.Surface((tile_size, length * tile_size))

        return 0

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
            self.scroll_to("max")
        elif selected_tile > size:
            selected_tile = 0
            self.scroll_to(0)
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

        height, length = self.calc_size(position, screen_size, screen_tile_size)

        width = screen_tile_size[0]

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

    def scroll_to(self, scroll: Union[str, int]):
        max_scroll = self.max_scroll
        if scroll == "max":
            self.curr_scroll = max_scroll
            return
        self.curr_scroll = min(max_scroll, max(0, scroll))

    def draw_arrow(self, direction: str) -> pygame.Surface:
        scroll = self.curr_scroll
        height = self.margin
        width = self.width
        
        if direction == "up":
            y0, y1 = (height, 0)
            limit = 0
        else:
            y0, y1 = (0, height)
            limit = self.max_scroll

        color =  (192, 192, 192) if scroll == limit else (64, 64, 64)
        middle = width // 2

        rect = pygame.Surface((width, height))
        rect.fill((255, 255, 255))
        pygame.draw.lines(rect, color, False, [(0, y0), (middle, y1), (width, y0)], width = 4)

        return rect

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
        inner_height = self.inner_height
        margin = self.margin
        self.screen.blit(pygame.transform.scale(self.display, (self.width, inner_height)), (0, margin))
        self.screen.blit(self.draw_arrow("up"), (0, 0))
        self.screen.blit(self.draw_arrow("down"), (0, inner_height + margin))
        screen.blit(self.screen, self.position)