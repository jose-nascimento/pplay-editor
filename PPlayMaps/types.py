from typing import Tuple, NamedTuple

class Margin(NamedTuple):
    top: int
    right: int
    bottom: int
    left: int

class Vector(NamedTuple):
    x: int
    y: int

Color = Tuple[int, int, int]