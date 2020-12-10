from os.path import join
from pygame import image

def path(filename: str) -> str:
    return join("res", filename)

chevron_up = image.load(path("chevron-up.png"))
chevron_down = image.load(path("chevron-down.png"))

__all__ = ["chevron_up", "chevron_down"]