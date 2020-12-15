from typing import Tuple, NamedTuple, Union

class Margin(NamedTuple):
    top: int
    right: int
    bottom: int
    left: int

class Vector(NamedTuple):
    x: int
    y: int

Vec = Union[Tuple[int, int], Vector]

Color = Tuple[int, int, int]