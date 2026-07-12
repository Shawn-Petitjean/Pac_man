from mazegenerator import MazeGenerator
import pygame
from .config import N, E, S, W, PAC_F


class Game:
    def __init__(self, size: tuple[int, int], res: tuple[int, int]):
        self.mazegen = MazeGenerator(size)
        pygame.init()
        self.screen = pygame.display.set_mode(res)
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
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
        PAC_F = pygame.image.load("sprite/pac_man/pac_man_f.png").convert()
        PAC_F = pygame.transform.scale(PAC_F,
                                       (self.bloc * 0.6,
                                       self.bloc * 0.6))
        player_pos = pygame.Vector2(self.screen.get_width() / 2, self.screen.get_height() / 2)
        j = 0
        walls = []
        for line in self.mazegen.maze:
            i = 0
            for cell in line:
                walls.extend(self.put_walls(cell, self.padding_h + i, self.padding_v + j))
                i += self.bloc
            j += self.bloc
        while self.running:
            pygame.display.flip()
            self.screen.blit(PAC_F, player_pos)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                player_pos.y -= 300 * self.dt
            if keys[pygame.K_s]:
                player_pos.y += 300 * self.dt
            if keys[pygame.K_a]:
                player_pos.x -= 300 * self.dt
            if keys[pygame.K_d]:
                player_pos.x += 300 * self.dt
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            for wall in walls:
                pygame.draw.rect(self.screen, "blue", wall)
            self.dt = self.clock.tick(60) / 1000
            pygame.display.update()
            pygame.display.flip()
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
        return walls
        # if walls != None:
        #     for wall in walls:
        #         pygame.draw.rect(self.screen, "blue", wall)
        #         pygame.display.update()
