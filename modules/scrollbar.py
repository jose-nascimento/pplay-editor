import pygame
from PPlayMaps.types import Vec, Color, Vector

class ScrollBar:

    def __init__(
        self,
        orientation: str,
        position: Vec,
        screen_length: int,
        visible_length: int,
        total_length: int,
        width: int,
        fill_color: Color = (242, 242, 242),
        bar_color: Color = (64, 64, 64),
    ):
        self.length = length = screen_length
        # self.ratio = max(1, total_length / visible_length)
        self.sector_length = sector_length = length // total_length
        self.remainder = remainder = length - (sector_length * total_length)
        self.scroll_length = visible_length * sector_length + remainder
        if orientation == "y":
            dimensions = Vector(width, length)
        else:
            dimensions = Vector(length, width)

        self.orientation = orientation
        self.position = position
        self.dimensions = dimensions
        self.width = width
        self.fill_color = fill_color
        self.bar_color = bar_color

        
        self.display = pygame.Surface(dimensions)
        self.display.fill(fill_color)
    
    def update(self, scroll: int):
        sector_length = self.sector_length
        self.scroll_length

        offset = scroll * sector_length

        self.display.fill(self.fill_color)
        if self.orientation == "y":
            pygame.draw.rect(self.display, self.bar_color, (0, offset, self.width, self.scroll_length))
        else:
            pygame.draw.rect(self.display, self.bar_color, (offset, 0, self.scroll_length, self.width))            

    def draw(self, screen: pygame.Surface):
        screen.blit(self.display, self.position)