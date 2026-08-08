from mazegenerator import MazeGenerator
import pygame
import time
from .sprite import Pac_man, Red_Ghost
from .config import N, E, S, W, Cheat
from .menu import PauseMenu
from .maze import Pac_gum, Cell



class Game:
    def __init__(self, screen: pygame.Surface, size: tuple[int, int],
                 cheats: Cheat, seed: int):
        self.seed = seed
        self.time = 0
        self.size = size
        self.mazegen = MazeGenerator(size, seed=self.seed)
        self.screen = screen
        self.cheats = cheats
        res = screen.get_size()
        self.clock = pygame.time.Clock()
        self.running = True
        self.result = ""
        self.rows = len(self.mazegen.maze)
        self.cols = len(self.mazegen.maze[0])
        self.len = self.cols
        self.dt = 0
        self.cells: list[Cell] = []
        if res[0] > res[1]:
            # upsacle le pattern
            # self.padding_h = (max(res) - min(res)) / 2
            # self.padding_v = (res[0] - res[1]) * 0.75
            self.padding_v = res[1] * 0.1
            self.m_bloc = ((res[1] - self.padding_v * 2) / (len(self.mazegen.maze) + 1)) * 0.2
            self.bloc = ((res[1] - self.padding_v * 2) / len(self.mazegen.maze)) * 0.8
            self.padding_h = (self.m_bloc * (len(self.mazegen.maze) + 1)) + (self.bloc * len(self.mazegen.maze))
            self.padding_h = (res[0] - self.padding_h) / 2
        else:
            self.padding_h = res[1] * 0.1
            self.m_bloc = ((res[0] - self.padding_h * 2) / (len(self.mazegen.maze) + 1)) * 0.2
            self.bloc = ((res[0] - self.padding_h * 2) / len(self.mazegen.maze)) * 0.8
            self.padding_v = (self.m_bloc * len(self.mazegen.maze) + 1) + (self.bloc * len(self.mazegen.maze))
            self.padding_v = (res[1] - self.padding_v) / 2
        # def initialise(self):

    def screen_refresh(self, pac_m, ghost_r, walls):
            self.screen.fill("black")
            for wall in walls:
                pygame.draw.rect(self.screen, "blue", wall)
            for cell in self.cells:
                if cell.pac_g and not cell.pac_g.eat:
                    pygame.draw.rect(self.screen, "yellow", cell.pac_g.rect)
            self.screen.blit(pac_m.sprite, (pac_m.x, pac_m.y))
            self.screen.blit(ghost_r.sprite, (ghost_r.x, ghost_r.y))
            pygame.display.flip()

    def put_walls(self, cell: int, x: int, y: int):
        walls = []
        if cell & N:
            walls.append(pygame.Rect(
                                    x - self.m_bloc,
                                    y - self.m_bloc,
                                    self.bloc + self.m_bloc * 2,
                                    self.m_bloc
                                    ))
        if cell & W:
            walls.append(pygame.Rect(
                                x - self.m_bloc,
                                y,
                                self.m_bloc,
                                self.bloc + self.m_bloc
                                ))
        if cell & S:
            walls.append(pygame.Rect(
                                x,
                                y + self.bloc,
                                self.bloc + self.m_bloc,
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

    def init_pac_gum(self):
        for cell in self.cells:
            if not cell.value == 15:
                cell.pac_g = Pac_gum(
                                     cell.x - (self.bloc - (self.bloc * 0.1)),
                                     cell.y + self.bloc - (self.bloc * 0.1),
                                     pygame.Rect(
                                                 cell.x + (self.bloc / 2) - (self.bloc * 0.1),
                                                 cell.y + (self.bloc / 2) - (self.bloc * 0.1),
                                                 self.bloc * 0.2,
                                                 self.bloc * 0.2
                                                )
                                    )

    def processed_move(self, pac_m, ghost_r):
            if pac_m.dead == False:
                self.processed_keys(pygame.key.get_pressed(), pac_m)
            else:
                self.move(ghost_r)
            ghost_r.pathfinding(pac_m.current.pos)
            ghost_r.collide(pac_m)
            if ghost_r.d:
                self.move(ghost_r)
            self.move(pac_m)

    def processed_keys(self, key_pressed, pac_m):
        center_x = pac_m.current.x + (self.bloc / 2)
        center_y = pac_m.current.y + (self.bloc / 2)
        aligned_x = abs(pac_m.center[0] - center_x) <= 1
        aligned_y = abs(pac_m.center[1] - center_y) <= 1

        if aligned_x:
            if key_pressed[pygame.K_w] and not pac_m.current.value & N:
                pac_m.d = "N"
            elif key_pressed[pygame.K_s] and not pac_m.current.value & S:
                pac_m.d = "S"
        if aligned_y:
            if key_pressed[pygame.K_a] and not pac_m.current.value & W:
                pac_m.d = "W"
            elif key_pressed[pygame.K_d] and not pac_m.current.value & E:
                pac_m.d = "E"
        return None

    def snap_sprite_to_current(self, sprite):
        sprite.center[0] = sprite.current.x + (self.bloc / 2)
        sprite.center[1] = sprite.current.y + (self.bloc / 2)
        sprite.x = sprite.current.x + (self.bloc - sprite.sprite.get_width()) / 2
        sprite.y = sprite.current.y + (self.bloc - sprite.sprite.get_height()) / 2

    def move(self, sprite):
        if sprite.d:
            current_index = self.cells.index(sprite.current)
            old_current = sprite.current
            if sprite.d == "N":
                if sprite.current.value & N and sprite.center[1] - 100 * self.dt <= sprite.current.y + self.bloc / 2:
                    self.snap_sprite_to_current(sprite)
                    return
                sprite.y -= 100 * self.dt
                sprite.center[1] -= 100 * self.dt
                if current_index >= self.cols:
                    above = self.cells[current_index - self.cols]
                    if sprite.center[1] <= above.y + self.bloc / 2:
                        sprite.current = above
            elif sprite.d == "S":
                if sprite.current.value & S and sprite.center[1] + 100 * self.dt >= sprite.current.y + self.bloc / 2:
                    self.snap_sprite_to_current(sprite)
                    return
                sprite.y += 100 * self.dt
                sprite.center[1] += 100 * self.dt
                if current_index + self.cols < len(self.cells):
                    below = self.cells[current_index + self.cols]
                    if sprite.center[1] >= below.y + self.bloc / 2:
                        sprite.current = below
            elif sprite.d == "W":
                if sprite.current.value & W and sprite.center[0] - 100 * self.dt <= sprite.current.x + self.bloc / 2:
                    self.snap_sprite_to_current(sprite)
                    return
                sprite.x -= 100 * self.dt
                sprite.center[0] -= 100 * self.dt
                if current_index % self.cols != 0:
                    left = self.cells[current_index - 1]
                    if sprite.center[0] <= left.x + self.bloc / 2:
                        sprite.current = left
            elif sprite.d == "E":
                if sprite.current.value & E and sprite.center[0] + 100 * self.dt >= sprite.current.x + self.bloc / 2:
                    self.snap_sprite_to_current(sprite)
                    return
                sprite.x += 100 * self.dt
                sprite.center[0] += 100 * self.dt
                if (current_index + 1) % self.cols != 0:
                    right = self.cells[current_index + 1]
                    if sprite.center[0] >= right.x + self.bloc / 2:
                        sprite.current = right
            if sprite.current is not old_current:
                self.snap_sprite_to_current(sprite)


    def run(self) -> str:
        r1 = 0 if len(self.mazegen.maze[0]) % 2 == 0 else 1
        r2 = 0 if len(self.mazegen.maze) % 2 == 0 else 1
        j = 0
        k = False
        walls = []
        count_l = 0
        for line in self.mazegen.maze:
            i = 0
            count_c = 0
            for cell in line:
                walls.extend(self.put_walls(cell, self.padding_h + i, self.padding_v + j))
                if (count_c == round((len(self.mazegen.maze[0]) / 2) - 1) + r1 
                    and count_l == round((len(self.mazegen.maze) / 2) - 1) + r2):
                    pac_spawn = Cell(self.padding_h + i, self.padding_v + j, cell, count_c, count_l)
                    k = True
                if not k:
                    self.cells.append(Cell(self.padding_h + i, self.padding_v + j, cell, count_c, count_l))
                else:
                    self.cells.append(pac_spawn)
                    k = False
                count_c += 1
                i += self.bloc + self.m_bloc
            j += self.bloc + self.m_bloc
            count_l += 1
        self.init_pac_gum()
        pac_m = Pac_man(
                        pac_spawn,
                        pac_spawn.x + ((self.bloc - self.bloc * 0.6) / 2),
                        pac_spawn.y + ((self.bloc - self.bloc * 0.6) / 2),
                        [pac_spawn.x + (self.bloc / 2), pac_spawn.y + (self.bloc / 2)],
                        self.bloc,
                        self.mazegen
                        )
        ghost_r = Red_Ghost(
                            self.cells[0],
                            self.cells[0].x + ((self.bloc - self.bloc * 0.6) / 2),
                            self.cells[0].y + ((self.bloc - self.bloc * 0.6) / 2),
                            [self.cells[0].x + (self.bloc / 2), self.cells[0].y + (self.bloc / 2)],
                            self.bloc,
                            self.mazegen,
                            self.size
                            )
        ghost_r.pathfinding(pac_m.current.pos)
        self.time = time.time()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.result = "quit"
                    self.running = False
                elif (event.type == pygame.KEYDOWN
                        and event.key == pygame.K_ESCAPE):
                    choice = PauseMenu(self.cheats).run(self.screen)
                    if choice == "menu":
                        self.running = False
                    elif choice == "quit":
                        self.result = "quit"
                        self.running = False
                    self.clock.tick()
            self.dt = self.clock.tick(60) / 1000
            self.processed_move(pac_m, ghost_r)
            if ((pac_m.current.pac_g.eat == False and
                (pac_m.current.x + (self.bloc / 2)) - 5 <= pac_m.center[0]
                and (pac_m.current.x + (self.bloc / 2)) + 5 >= pac_m.center[0]) and
                ((pac_m.current.y + (self.bloc / 2)) - 5 <= pac_m.center[1]
                and (pac_m.current.y + (self.bloc / 2)) + 5 >= pac_m.center[1])):
                pac_m.current.pac_g.eat = True
                pac_m.n_gum += 1
            self.screen_refresh(pac_m, ghost_r, walls)
        return self.result
