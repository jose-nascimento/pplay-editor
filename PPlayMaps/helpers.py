from typing import Tuple
from PPlayMaps import Vector

def clamp(values: Vector, limit: Tuple[int, int]) -> Vector:
    x, y = values
    l0, l1 = limit
    return Vector(max(l0, min(x, l1)), max(l0, min(y, l1)))

def clamp_2(values: Vector, limit_x: Tuple[int, int], limit_y: Tuple[int, int]) -> Vector:
    x, y = values
    lx0, lx1 = limit_x
    ly0, ly1 = limit_y
    return Vector(max(lx0, min(x, lx1)), max(ly0, min(y, ly1)))

def add_v(a: Vector, b: Vector) -> Vector:
    return Vector(a[0] + b[0], a[1] + b[1])

def sub_v(a: Vector, b: Vector) -> Vector:
    return Vector(a[0] - b[0], a[1] - b[1])