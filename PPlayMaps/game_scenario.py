import pygame
from PPlayMaps.helpers import add_v
from typing import Optional, Tuple
from PPlayMaps import Scenario, helpers
from PPlayMaps.types import Vector, Vec, ArrowType
from PPlay.window import Window
from PPlay.sprite import Sprite
from PPlay.gameimage import GameImage

class GameScenario(Scenario):

    def __init__(
        self,
        position: Vec,
        size: Vec,
        screen_size: Vec,
        tile_size: Optional[Vec] = None,
        *args,
        **kwargs
    ):
        super().__init__(
            position,
            size,
            screen_size,
            tile_size = tile_size,
            *args,
            **kwargs
        )

        self.window = Window.get_screen()
        self.hero = None
        self.hero_position = None

    def update(self):
        self.draw_map()
        self.hero.update()

    def get_display_position(self, x: int, y: int) -> Vector:
        tile_size = self.map_tile_size
        return Vector(x * tile_size, y * tile_size)

    def get_screen_position(self, x: int, y: int) -> Vector:
        sx, sy = self.screen_tile_size
        px, py = self.position
        mx, my = self.margin
        dx, dy = px + mx, py + my
        return Vector(x * sx + dx, y * sy + dy)

    def get_hero_screen_position(self) -> Vector:
        return self.get_screen_position(*self.hero_position)

    def draw(self):
        super().draw(self.window)
        self.draw_sprite(self.hero, self.hero_position)

    def draw_sprite(self, sprite: GameImage, position: Vec):
        sx, sy = self.get_screen_position(*position)
        sprite.set_position(sx, sy)
        sprite.draw()

    def place_hero(self, hero: Sprite, position: Vec = (0, 0)):
        self.hero = hero
        self.hero_position = Vector(*position)

    def stepping_on(self, tile: int):
        x, y = self.hero_position
        for i, layer in enumerate(self.map.layers):
            if layer[y][x] == tile:
                return i + 1
    
    def tile_at(self, layer: int, position: Vec):
        x, y = position
        return self.map.layers[layer - 1][y][x]

    def hero_can_move(self, movement: ArrowType):
        hx, hy = self.hero_position
        if movement == "up":
            hy -= 1
        elif movement == "down":
            hy += 1
        elif movement == "left":
            hx -= 1
        elif movement == "right":
            hx += 1
        return self.map.movement[hy][hx] == 0

    def can_move_to(self, position: Vec) -> bool:
        x, y = position
        return self.map.movement[y][x] == 0

    def move_hero_to(self, position: Vec):
        self.hero_position = Vector(*position)
        x, y = self.get_hero_screen_position()
        self.hero.set_position(x, y)

    def move_hero(self, movement: ArrowType) -> bool:
        if self.hero_can_move(movement):
            hx, hy = self.hero_position
            if movement == "up":
                hy -= 1
            elif movement == "down":
                hy += 1
            elif movement == "left":
                hx -= 1
            elif movement == "right":
                hx += 1
            self.move_hero_to((hx, hy))
            return True
        return False

    def move_hero_ignore_terrain(self, movement: ArrowType):
        hx, hy = self.hero_position
        if movement == "up":
            hy -= 1
        elif movement == "down":
            hy += 1
        elif movement == "left":
            hx -= 1
        elif movement == "right":
            hx += 1
        self.move_hero_to((hx, hy))

    def move_hero_keys(self) -> Tuple[bool, bool]:
        keyboard = Window.get_keyboard()
        hx, hy = self.hero_position
        h, v = False, False
        if keyboard.key_pressed("up"):
            hy -= 1
            v = not v
        if(keyboard.key_pressed("down")):
            hy += 1
            v = not v
        if keyboard.key_pressed("left"):
            hx -= 1
            h = not h
        if(keyboard.key_pressed("right")):
            hx += 1
            h = not h
        hero_position = Vector(hx, hy)
        if (h or v) and self.can_move_to(hero_position):
            self.move_hero_to(hero_position)
            return h, v
        else:
            return False, False
    
    def move_hero_key_x(self) -> bool:
        keyboard = Window.get_keyboard()
        hx, hy = self.hero_position
        moved = False
        if keyboard.key_pressed("left"):
            hx -= 1
            moved = not moved
        if(keyboard.key_pressed("right")):
            hx += 1
            moved = not moved
        hero_position = Vector(hx, hy)
        if moved and self.can_move_to(hero_position):
            self.move_hero_to(hero_position)
            return moved
        return False

    def move_hero_key_y(self) -> bool:
        keyboard = Window.get_keyboard()
        hx, hy = self.hero_position
        moved = False
        if keyboard.key_pressed("up"):
            hy -= 1
            moved = not moved
        if(keyboard.key_pressed("down")):
            hy += 1
            moved = not moved
        hero_position = Vector(hx, hy)
        if moved and self.can_move_to(hero_position):
            self.move_hero_to(hero_position)
            return moved
        return False