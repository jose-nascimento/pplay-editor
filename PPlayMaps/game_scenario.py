from typing import Optional, Tuple
from PPlayMaps import Scenario
from PPlayMaps.types import Vector, Vec, ArrowType
from PPlayMaps.helpers import sub_v
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
        scroll_x, scroll_y = self.curr_scroll
        cx, cy = x - scroll_x, y - scroll_y
        sx, sy = self.screen_tile_size
        px, py = self.position
        mx, my = self.margin
        dx, dy = px + mx, py + my
        return Vector(cx * sx + dx, cy * sy + dy)

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

    def hero_can_move(self, movement: ArrowType) -> bool:
        hx, hy = self.hero_position
        width, height = self.get_map_size()
        if movement == "up":
            hy -= 1
        elif movement == "down":
            hy += 1
        elif movement == "left":
            hx -= 1
        elif movement == "right":
            hx += 1
        if (0 <= hx < width) and (0 <= hy < height):
            return self.map.movement[hy][hx] == 0
        else:
            return False

    def can_move_to(self, position: Vec) -> bool:
        x, y = position
        width, height = self.get_map_size()
        if (0 <= x < width) and (0 <= y < height):
            return self.map.movement[y][x] == 0
        else:
            return False

    def move_hero_to(self, position: Vec):
        x, y = position
        width, height = self.get_map_size()
        if (0 <= x < width) and (0 <= y < height):
            p0 = self.hero_position

            self.hero_position = Vector(*position)

            mx, my = self.max_scroll
            if max(mx, my) > 0:
                sx, sy = self.curr_scroll
                width, height = self.size
                map_width, map_height = self.get_map_size()
                half_w, half_h = width // 2, height // 2
                rw, rh = width % 2, height % 2
                dx, dy = sub_v(p0, position)
                to_x, to_y = 0, 0

                if dx > 0 and sx > 0 and (map_width - x) > half_w:
                    # indo para a esquerda, posição atual está a > meia tela da borda direita
                    to_x = -dx
                elif dx < 0 and sx <= mx and x > half_w + rw:
                    # indo para a direita, posição atual está a > meia tela da borda esquerda
                    to_x = -dx

                if dy > 0 and sy > 0 and (map_height - y) > half_h:
                    # subindo, posição atual está a > meia tela do fundo
                    to_y = -dy
                elif dy < 0 and sy <= my and y > half_h + rh:
                    # descendo, posição atual está a > meia tela do topo
                    to_y = -dy

                self.scroll((to_x, to_y))
            
            hx, hy = self.get_hero_screen_position()
            self.hero.set_position(hx, hy)


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