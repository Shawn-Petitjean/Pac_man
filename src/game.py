from mazegenerator import MazeGenerator
import pygame
from .config import N, E, S, W


class Game:
    def __init__(self, size: tuple[int, int], res: tuple[int, int]):
        self.mazegen = MazeGenerator(size)
        pygame.init()
        self.screen = pygame.display.set_mode(res)
        self.clock = pygame.time.Clock()
        self.running = True
        if res[0] > res[1]:
            # upsacle le pattern
            # self.padding_h = (max(res) - min(res)) / 2
            self.padding_v = (res[1] * 0.1)
            self.m_bloc = res[1] * 0.01
            self.bloc = (((res[1] * 0.8) - (len(self.mazegen.maze) - 1))
                         / len(self.mazegen.maze))
            self.padding_h = (res[0] - (self.bloc) * (len(self.mazegen.maze))) / 2
        else:
            self.padding_h = (res[0] * 0.1)
            self.m_bloc = res[0] * 0.01
            self.bloc = (((res[0] * 0.8) - (self.m_bloc * (len(self.mazegen.maze) - 1)))
                         / len(self.mazegen.maze))
            self.padding_v = (res[1] - (self.bloc + self.m_bloc) * (len(self.mazegen.maze))) / 2

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            j = 0
            for line in self.mazegen.maze:
                i = 0
                for cell in line:
                    self.put_walls(cell, self.padding_h + i, self.padding_v + j)
                    i += self.bloc
                j += self.bloc
        pygame.quit()
    
    def put_walls(self, cell: int, x: int, y: int):
        walls = []
        if cell & N:
            walls.append(pygame.Rect(
                                 x,
                                 y,
                                 self.bloc,
                                 self.m_bloc
                                ))
        if cell & W:
            walls.append(pygame.Rect(
                                 x,
                                 y,
                                 self.m_bloc,
                                 self.bloc
                                ))
        if cell & S:
            walls.append(pygame.Rect(
                                 x,
                                 y + self.bloc,
                                 self.bloc,
                                 self.m_bloc
                                ))
        if cell & E:
            walls.append(pygame.Rect(
                                 x + self.bloc,
                                 y,
                                 self.m_bloc,
                                 self.bloc + self.m_bloc
                                ))
        if walls != None:
            for wall in walls:
                pygame.draw.rect(self.screen, "blue", wall)
                pygame.display.update()
