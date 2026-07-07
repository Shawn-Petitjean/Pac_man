from mazegenerator import MazeGenerator
import pygame
from .config import LINE


class Game:
    def __init__(self, size: tuple[int, int], res: tuple[int, int]):
        self.mazegen = MazeGenerator(size)
        pygame.init()
        self.screen = pygame.display.set_mode(res)
        self.clock = pygame.time.Clock()
        self.running = True
        if res[0] > res[1]:
            self.padding_h = (max(res) - min(res)) / 2
            self.padding_v = (res[1] * 0.1)
            self.bloc = abs((res[1] - self.padding_v * 2) / len(self.mazegen.maze))
        else:
            self.padding_v = (max(res) - min(res)) / 2
            self.padding_h = (res[1] * 0.1)
            self.bloc = abs(res[0] - self.padding_v * 2) / len(self.mazegen.maze[0])

    def run(self):
        print(self.bloc)
        print(len(self.mazegen.maze[0]))
        print(len(self.mazegen.maze))
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            j = 0
            for line in self.mazegen.maze:
                i = 0
                for cell in line:
                    r = pygame.Rect(self.padding_h + i, self.padding_v + j, self.bloc, self.bloc)
                    i += self.bloc + 5
                    pygame.draw.rect(self.screen, "blue", r)
                    pygame.display.update()
                j += self.bloc + 5
        pygame.quit()
