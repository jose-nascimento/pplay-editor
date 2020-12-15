from typing import Optional
import pygame
from PPlayMaps.types import Vec, Color

class Label:
    def __init__(
        self,
        text: str,
        position: Vec,
        font_family: str = "Arial",
        font_size: int = 14,
        color: Color = (255, 255, 255)
    ):
        self.font = font = pygame.font.SysFont(font_family, font_size)

        self.position = position
        self.color = color

        self.surface = font.render(text, 1, color)
        self.surface.fill((0,0,0))
    
    def set_position(self, position: Vec):
        self.position = position

    def set(self, text, color: Optional[Color] = None):
        if color is None:
            color = self.color
        else:
            self.color = color
        self.surface = self.font.render(text, 1, color)
    
    def blit(self, screen) -> None:
        screen.blit(self.surface, self.position)