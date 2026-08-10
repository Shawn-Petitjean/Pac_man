from typing import Any

import pygame


class Pac_gum:
    def __init__(self, x: float, y: float, rect: pygame.Rect) -> None:
        self.x = x
        self.y = y
        self.rect = rect
        self.eat = False


class Super_pac_gum(Pac_gum):
    def __init__(self, x: float, y: float, rect: pygame.Rect) -> None:
        super().__init__(x, y, rect)


class Cell:
    def __init__(self, x: float, y: float, value: int,
                 i: int, j: int) -> None:
        self.x = x
        self.y = y
        self.value = value
        self.pac_g: Any = None
        self.pos = [i, j]
