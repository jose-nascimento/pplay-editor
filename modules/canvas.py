from typing import Optional, Union
from pygame.locals import *
import pygame
from PPlayMaps import Scenario, Map, Tileset
from PPlayMaps.types import Vec, Vector
from modules import ScrollBar

class Canvas(Scenario):

    def __init__(
            self,
            position: Vec,
            size: Vec,
            screen_size: Vec,
            *args,
            limit_margin: bool = True,
            # own arguments:
            scroll_width: int = 16,
            **kwargs
        ):
        super().__init__(
            position,
            size,
            screen_size,
            *args,
            limit_margin = limit_margin,
            **kwargs
        )
        self.scroll_width = scroll_width
        self.has_scrollbar = False

        self.scroll_bar_y = None
        self.scroll_bar_x = None

    def set_scrollbar(self):
        sw, sh = self.screen_size
        sx, sy = self.curr_scroll
        vw, vh = self.size
        mw, mh = self.get_map_size()
        scroll_width = self.scroll_width

        self.has_scrollbar = True
        scroll_y_position = Vector(sw - scroll_width, 0)
        scroll_x_position = Vector(0, sh - scroll_width)

        self.scroll_bar_y = ScrollBar("y", scroll_y_position, sh, vh, mh, scroll_width)
        self.scroll_bar_x = ScrollBar("x", scroll_x_position, sw, vw, mw, scroll_width)

        self.scroll_bar_y.update(sy)
        self.scroll_bar_x.update(sx)

    def set_map(self, map: Map, tileset: Tileset):
        super().set_map(map, tileset)

        w, h = self.size
        mw, mh = map.size
        if (mh - h) > 0 or (mw - w) > 0:
            self.set_scrollbar()

    def on_resize(
        self,
        position: Optional[Vec] = None,
        screen_size: Optional[Vec] = None,
        tile_size: Optional[Vec] = None
    ):
        super().on_resize(position, screen_size, tile_size)

        if self.map_size is not None:
            self.set_scrollbar()

    def scroll(self, delta: Union[Vec, int], dy: Optional[int] = None) -> Vector:
        super().scroll(delta, dy)
        
        if self.has_scrollbar:
            x, y = self.curr_scroll
            self.scroll_bar_y.update(y)
            self.scroll_bar_x.update(x)

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
        xmin, ymin = self.curr_scroll
        xmax, ymax = self.width + xmin, self.height + ymin

        d = self.map_tile_size
        c = d // 2
        r = (d // 8) * 3
        x0 = (d - 1) // 4
        x1 = d - x0

        for y, line in enumerate(movement[ymin:ymax]):
            for x, m in enumerate(line[xmin:xmax]):
                if m == 0:
                    pygame.draw.circle(self.display, (255, 255, 255), (x * d + c, y * d + c), r, width = 1)
                elif m == 1:
                    pygame.draw.line(self.display, (255, 255, 255), (x * d + x0,  y * d + c), (x * d + x1,  y * d + c), width = 2)

    def draw(self, screen: pygame.Surface):
        display_size = self.map_size or self.display_size
        bar_x, bar_y = self.scroll_bar_x, self.scroll_bar_y

        self.screen.blit(pygame.transform.scale(self.display, display_size), self.margin)
        if bar_y: bar_y.draw(self.screen)
        if bar_x: bar_x.draw(self.screen)
        screen.blit(self.screen, self.position)