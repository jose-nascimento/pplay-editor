from typing import Tuple
from PPlayMaps.types import Vector, Vec

def clamp(values: Vec, limit: Vec) -> Vector:
    x, y = values
    l0, l1 = limit
    return Vector(max(l0, min(x, l1)), max(l0, min(y, l1)))

def clamp_2(values: Vec, limit_x: Vec, limit_y: Vec) -> Vector:
    x, y = values
    lx0, lx1 = limit_x
    ly0, ly1 = limit_y
    return Vector(max(lx0, min(x, lx1)), max(ly0, min(y, ly1)))

def add_v(a: Vec, b: Vec) -> Vector:
    return Vector(a[0] + b[0], a[1] + b[1])

def sub_v(a: Vec, b: Vec) -> Vector:
    return Vector(a[0] - b[0], a[1] - b[1])