import pygame
from .config import GHOST_R


class Pac_man:
    def __init__(self, current: Cell, x: int, y: int, center: list[int, int], bloc: int):
        self.current = current
        self.x = x
        self.y = y
        self.center = center
        self.d = None
        self.n_gum = 0
        self.alive = True
        self.sprite = pygame.image.load("sprites/pac_man/pac_man_f.png").convert()
        self.sprite = pygame.transform.scale(self.sprite,
                                            (
                                             bloc * 0.6,
                                             bloc * 0.6
                                            ))


class Ghost:
    def __init__(self, current: Cell, x: int, y: int):
        self.current = current
        self.x = x
        self.y = y
        self.alive = True
        self


class Red_Ghost(Ghost):
    def __init__(self, current: Cell, x: int, y: int, bloc: int):
        super().__init__(current, x, y)
        self.sprite = pygame.image.load(GHOST_R).convert()
        self.sprite = pygame.transform.scale(self.sprite,
                                            (
                                             bloc * 0.6,
                                             bloc * 0.6
                                            ))

    # def pathfinding(self, pac_m: Pac_man, cells: list[Cell]):
