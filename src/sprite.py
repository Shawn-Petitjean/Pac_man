import pygame
from .config import GHOST_R
from mazegenerator import MazeGenerator
from .maze import Cell
import time


class Sprite:
    def __init__(self, current: Cell, x: int, y: int, center: list[int, int], bloc: int, maze: MazeGenerator):
        self.current = current
        self.x = x
        self.y = y
        self.center = center
        self.d = None
        self.dead = False
        self.spawn = current.pos
        self.bloc = bloc
        self.maze = maze

    def pathfinding(self, pos: tuple[int, int]):
        self.maze._entryx = self.current.pos[0]
        self.maze._entryy = self.current.pos[1]
        self.maze._exitx = pos[0]
        self.maze._exity = pos[1]
        self.maze._find_short_path()
        if len(self.maze._shortest_path) > 0:
            self.d = self.maze._shortest_path[0]
        else:
            self.d = None


class Pac_man(Sprite):
    def __init__(self, current: Cell, x: int, y: int, center: list[int, int], bloc: int, maze: MazeGenerator):
        super().__init__(current, x, y, center, bloc, maze)
        self.n_gum = 0
        self.d_time = 0
        self.sprite = pygame.image.load("sprites/pac_man/pac_man_f.png").convert()
        self.sprite = pygame.transform.scale(self.sprite,
                                            (
                                             bloc * 0.6,
                                             bloc * 0.6
                                            ))
        self.invul = False


class Ghost(Sprite):
    def __init__(self, current: Cell, x: int, y: int, center: list[int, int], bloc, maze: MazeGenerator):
        super().__init__(current, x, y, center, bloc, maze)
        self.d_time = 0


class Red_Ghost(Ghost):
    def __init__(self, current: Cell, x: int, y: int, center: list[int, int], bloc: int, maze: MazeGenerator, size: tuple[int, int]):
        super().__init__(current, x, y, center, bloc, maze)
        self.sprite = pygame.image.load(GHOST_R).convert()
        self.sprite = pygame.transform.scale(self.sprite,
                                            (
                                             bloc * 0.6,
                                             bloc * 0.6
                                            ))
        self.current = current
        self.maze = maze
        self.size = size
        self.d = None
        self.dead = False

    
    def collide(self, pac_m: Pac_man):
        if ((self.center[0] - (self.bloc / 2)) <= pac_m.center[0]
            and (self.center[0] + (self.bloc / 2)) >= pac_m.center[0] and
            ((self.center[1] - (self.bloc / 2)) <= pac_m.center[1]
            and (self.center[1] + (self.bloc / 2)) >= pac_m.center[1])):
            if pac_m.invul == False:
                pac_m.d_time = time.time()
                pac_m.dead = True
            else:
                pass
                