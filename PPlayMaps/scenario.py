from typing import Literal, Tuple, Optional, Union
from pygame import image
from pygame.locals import *
import pygame
from PPlayMaps import Map, Tileset
from PPlayMaps.types import Vector, Vec
from .helpers import clamp_2, add_v

class Scenario:

    def calc_size(
        self,
        size: Vec,
        screen_size: Vec,
        tile_size: Optional[Vec] = None,
        position: Optional[Vec] = None,
        *,
        limit_margin: bool = False
    ) -> Tuple[Vector, Vector, Vector]:
        sw, sh = screen_size
        width, height = size

        if tile_size == None:
            tile_size = (sw // width, sh // height)
            if limit_margin:
                min_tile = min(tile_size)
                tile_size = Vector(min_tile, min_tile)
        else:
            tile_size = Vector(*tile_size)
        
        tx, ty = tile_size
        (vw, vh) = display_size = Vector(width * tx, height * ty)
        margin = Vector((sw - vw) // 2, (sh - vh) // 2)

        if limit_margin is None:
            limit_margin = self.limit_margin
        else:
            self.limit_margin = limit_margin

        self.width = width
        self.height = height
        self.margin = margin
        self.screen_tile_size = tile_size
        self.display_size = display_size
        self.screen_size = screen_size
        if position is not None: self.position = Vector(*position)

        return display_size, margin, tile_size

    def __init__(
        self,
        position: Vec,
        size: Vec,
        screen_size: Vec,
        tile_size: Optional[Vec] = None,
        *,
        fill_color: Color = (192, 192, 192),
        limit_margin: bool = False
    ) -> None:
        self.calc_size(
            size,
            screen_size,
            tile_size,
            position,
            limit_margin = limit_margin
        )

        self.fill_color = fill_color
        self.curr_scroll = Vector(0, 0)
        self.max_scroll = Vector(0, 0)
        self.map_size = None
        self.bgimage_override = None

        self.screen = pygame.Surface(screen_size)
        self.screen.fill(fill_color)

    @property
    def size(self):
        return (self.width, self.height)

    def on_resize(
        self,
        position: Optional[Vec] = None,
        screen_size: Optional[Vec] = None,
        tile_size: Optional[Vec] = None
    ) -> None:
        if position is None: position = self.position
        if screen_size is None: screen_size = self.screen_size
        if tile_size is None: tile_size = self.screen_tile_size

        width, height = self.width, self.height
        size = (width, height)
        self.calc_size(size, screen_size, tile_size)

        if self.map_size is not None:
            self.calc_map_display()
        
        self.screen = pygame.Surface(screen_size)
        fill_color = self.fill_color
        self.screen.fill(fill_color)

    def map_hw(self) -> Vector:
        map = self.map
        map_w, map_h = map.width, map.height
        display_w, display_h = self.width, self.height
        return Vector(min(map_w, display_w), min(map_h, display_h))

    def calc_map_display(self):
        sx, sy = self.screen_tile_size
        map_tile_size = self.map_tile_size
        factor = (sx / map_tile_size, sy / map_tile_size)

        width, height = self.map_hw()
        map_size = Vector(width * sx, height * sy)

        self.factor = factor
        self.map_size = map_size

    def calc_map_size(self) -> Vector:
        width, height = self.map_hw()
        map_tile_size = self.map_tile_size
        map = self.map

        sw, sh = self.width, self.height
        mw, mh = map.width, map.height
        max_scroll = Vector(max(mw - sw, 0), max(mh - sh, 0))

        dimensions = Vector(width * map_tile_size, height * map_tile_size)
        self.dimensions = dimensions
        self.max_scroll = max_scroll
        self.calc_map_display()

        return dimensions

    def set_map(self, map: Map, tileset: Tileset):
        self.map = map
        self.tileset = tileset

        self.show_layers = 0b1111
        self.map_tile_size = tileset.tile_size
        self.curr_scroll = Vector(0, 0)

        dimensions = self.calc_map_size()

        self.display = pygame.Surface(dimensions)

    def load_map(
        self,
        name: Optional[str] = None,
        project: Optional[str] = None,
        path: Optional[str] = None
    ):
        if path:
            map = Map.load_from(path)
        else:
            map = Map.load(name, project = project)
            
        tileset_name = map.tileset
        tileset = Tileset.load(tileset_name, project = project)

        self.set_map(map, tileset)

    # ------------ Map manipulation ------------

    def get_map_params(self) -> dict:
        return self.map.get_params()

    def export_image(self, path: str):
        self.map.export_image(path)

    def clear_layer(self, layer: int):
        self.map.clear_layer(layer)

    def clear_movement(self):
        self.map.clear_movement()

    def place_tile(self, tile: int, pos: Vec, layer: int, movement_layer: bool = False):
        self.map.place_tile(tile, pos, layer, movement_layer = movement_layer)

    def fill_area(
        self,
        tile: int,
        start: Vec,
        end: Vec,
        layer: int,
        movement_layer: bool = False
    ):
        self.map.fill_area(tile, start, end, layer, movement_layer = movement_layer)
    
    def flood_fill(self, tile: int, point: Vec, layer: int, movement_layer: bool = False):
        self.map.flood_fill(tile, point, layer, movement_layer = movement_layer)

    def get_tile(self, pos: Vec, layer: int) -> int:
        return self.map.get_tile(pos, layer)

    def resize(self, value: Vec, *, op: Literal["=", "+", "-"] = "="):
        return self.map.resize(value, op = op)

    def set_bgcolor(self, color: Color = (0, 0, 0)):
        self.map.set_bgcolor(color)

    def set_bgimage(self, name: Optional[str] = None, path: Optional[str] = None):
        if name is not None:
            self.map.set_bgimage(name)
        elif path is not None:
            image = pygame.image.load(path).convert_alpha()
            self.bgimage_override = image

    def set_tileset(self, tileset_name: str) -> Tileset:
        tileset = Tileset.load(tileset_name)
        limit = len(tileset)

        self.tileset = tileset
        self.map_tile_size = tileset.tile_size

        self.map.set_tileset(tileset_name, limit)
        dimensions = self.calc_map_size()

        self.display = pygame.Surface(dimensions)

        return tileset

    # ---------- End map manipulation ----------

    def scroll(self, delta: Union[Vec, int], dy: Optional[int] = None) -> Vector:
        if type(delta) == int:
            if dy is not None:
                delta = Vector(delta, dy)
            else:
                raise TypeError("scroll takes two integers or one tuple/vector")
        xmax, ymax = max_scroll = self.max_scroll
        if max(max_scroll) == 0:
            return Vector(0, 0)
        curr_scroll = self.curr_scroll
        new_scroll = clamp_2(add_v(curr_scroll, delta), (0, xmax), (0, ymax))

        self.curr_scroll = new_scroll
        return new_scroll


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
        display_size = self.map_size or self.display_size
        self.screen.blit(pygame.transform.scale(self.display, display_size), self.margin)
        screen.blit(self.screen, self.position)

    def get_xy(self) -> Vector:
        x, y = pygame.mouse.get_pos()
        sx, sy = self.screen_tile_size
        px, py = self.position
        mx, my = self.margin
        dx, dy = (px + mx, py + my)
        return Vector((x - dx) // sx, (y - dy) // sy)
    
    def get_map_xy(self) -> Vector:
        x, y = pygame.mouse.get_pos()
        sx, sy = self.screen_tile_size
        px, py = self.position
        mx, my = self.margin
        dx, dy = (px + mx, py + my)
        pos_x, pos_y =  (x - dx) // sx, (y - dy) // sy
        if min(pos_x, pos_y) < 0:
            return Vector(-1, -1)
        scroll_x, scroll_y = self.curr_scroll
        return Vector(pos_x + scroll_x, pos_y + scroll_y)
    
    def get_rect(self) -> pygame.Rect:
        cx, cy = self.position
        cw, ch = self.screen_size
        rect = (cx, cy, cw, ch)
        return pygame.Rect(rect)

    def is_mouseouver(self) -> int:
        pos = pygame.mouse.get_pos()
        r = self.get_rect()
        return r.collidepoint(pos)
    
    def blit_tiles(self, layer):
        tileset = self.tileset
        current = self.map.layers[layer - 1]
        d = self.map_tile_size
        xmin, ymin = self.curr_scroll
        xmax, ymax = self.width + xmin, self.height + ymin

        for y, line in enumerate(current[ymin:ymax]):
            for x, c in enumerate(line[xmin:xmax]):
                if c != 0:
                    self.display.blit(tileset[c], (x * d, y * d))
    
    def draw_map(self):
        map = self.map
        show_layers = self.show_layers
        self.display.fill(map.bgcolor)
        if self.bgimage_override:
            self.display.blit(self.bgimage_override, (0, 0))
        elif map.bgimage:
            self.display.blit(map.bgimage, (0, 0))

        if show_layers & 0b0001:
            self.blit_tiles(1)
        if show_layers & 0b0010:
            self.blit_tiles(2)
        if show_layers & 0b0100:
            self.blit_tiles(3)
        if show_layers & 0b1000:
            self.blit_tiles(4)