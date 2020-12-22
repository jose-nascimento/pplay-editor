from typing import Tuple, NamedTuple, Union
try:
    from typing import Literal
    has_literal = True
except:
    has_literal = False

if has_literal:
    ArrowType = Literal["up", "down", "left", "right"]
    OpType = Literal["=", "+", "-"]
else:
    ArrowType = str
    OpType = str

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