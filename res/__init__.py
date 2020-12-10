from os.path import join
from pygame import image

def path(filename: str) -> str:
    return join("res", filename)

chevron_up = image.load(path("chevron-up.png")).convert()
chevron_down = image.load(path("chevron-down.png")).convert()

__all__ = ["chevron_up", "chevron_down"]