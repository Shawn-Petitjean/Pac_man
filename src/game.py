from mazegenerator import MazeGenerator
import pygame
from .config import N, E, S, W

class Pac_gum:
    def __init__(self, x: int, y: int, rect):
        self.x = x
        self.y = y
        self.rect = rect
        self.eat = False

class Cell:
    def __init__(self, x: int, y: int, value: int):
        self.x = x
        self.y = y
        self.value = value
        self.pac_g = None


class Pac_man:
    def __init__(self, current: Cell, x: int, y: int, center: list[int, int]):
        self.current = current
        self.x = x
        self.y = y
        self.center = center
        self.d = None
        self.n_gum = 0


class Game:
    def __init__(self, size: tuple[int, int], res: tuple[int, int]):
        self.mazegen = MazeGenerator(size)
        pygame.init()
        self.screen = pygame.display.set_mode(res)
        self.clock = pygame.time.Clock()
        self.running = True
        self.rows = len(self.mazegen.maze)
        self.cols = len(self.mazegen.maze[0])
        self.len = self.cols
        self.dt = 0
        self.cell: list[Cell] = []
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
        for cell in self.cell:
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

    def processed_keys(self, key_pressed, pac_m):
        center_x = pac_m.current.x + (self.bloc / 2)
        center_y = pac_m.current.y + (self.bloc / 2)
        aligned_x = abs(pac_m.center[0] - center_x) <= 1
        aligned_y = abs(pac_m.center[1] - center_y) <= 1

        if aligned_x:
            if key_pressed[pygame.K_w] and not pac_m.current.value & N:
                pac_m.d = "w"
            elif key_pressed[pygame.K_s] and not pac_m.current.value & S:
                pac_m.d = "s"
        if aligned_y:
            if key_pressed[pygame.K_a] and not pac_m.current.value & W:
                pac_m.d = "a"
            elif key_pressed[pygame.K_d] and not pac_m.current.value & E:
                pac_m.d = "d"
        return None

    def move(self, pac_m):
        if pac_m.d:
            current_index = self.cell.index(pac_m.current)
            if pac_m.d == "w":
                if pac_m.current.value & N and pac_m.center[1] - 100 * self.dt <= pac_m.current.y + self.bloc / 2:
                    pac_m.y = (pac_m.current.y + self.bloc / 2) - self.m_bloc
                    pac_m.center[1] = pac_m.current.y + self.bloc / 2
                    return
                pac_m.y -= 100 * self.dt
                pac_m.center[1] -= 100 * self.dt
                if current_index >= self.cols:
                    above = self.cell[current_index - self.cols]
                    if pac_m.center[1] <= above.y + self.bloc:
                        pac_m.current = above
            elif pac_m.d == "s":
                if pac_m.current.value & S and pac_m.center[1] + 100 * self.dt >= pac_m.current.y + self.bloc / 2:
                    pac_m.y = (pac_m.current.y + self.bloc / 2) - self.m_bloc
                    pac_m.center[1] = pac_m.current.y + self.bloc / 2
                    return
                pac_m.y += 100 * self.dt
                pac_m.center[1] += 100 * self.dt
                if current_index + self.cols < len(self.cell):
                    below = self.cell[current_index + self.cols]
                    if pac_m.center[1] >= below.y:
                        pac_m.current = below
            elif pac_m.d == "a":
                if pac_m.current.value & W and pac_m.center[0] - 100 * self.dt <= pac_m.current.x + self.bloc / 2:
                    pac_m.x = (pac_m.current.x + self.bloc / 2) - self.m_bloc
                    pac_m.center[0] = pac_m.current.x + self.bloc / 2
                    return
                pac_m.x -= 100 * self.dt
                pac_m.center[0] -= 100 * self.dt
                if current_index % self.cols != 0:
                    left = self.cell[current_index - 1]
                    if pac_m.center[0] <= left.x + self.bloc:
                        pac_m.current = left
            elif pac_m.d == "d":
                if pac_m.current.value & E and pac_m.center[0] + 100 * self.dt >= pac_m.current.x + self.bloc / 2:
                    pac_m.x = (pac_m.current.x + self.bloc / 2) - self.m_bloc
                    pac_m.center[0] = pac_m.current.x + self.bloc / 2
                    return
                pac_m.x += 100 * self.dt
                pac_m.center[0] += 100 * self.dt
                if (current_index + 1) % self.cols != 0:
                    right = self.cell[current_index + 1]
                    if pac_m.center[0] >= right.x:
                        pac_m.current = right

        # cordinate.index(new_cell) -> 3

    def run(self):
        PAC_F = pygame.image.load("sprite/pac_man/pac_man_f.png").convert()
        PAC_F = pygame.transform.scale(PAC_F,
                                       (
                                        self.bloc * 0.6,
                                        self.bloc * 0.6
                                       ))
        j = 0
        k = 0
        walls = []
        count_l = 0
        keys = None
        for line in self.mazegen.maze:
            i = 0
            count_c = 0
            for cell in line:
                walls.extend(self.put_walls(cell, self.padding_h + i, self.padding_v + j))
                if count_c == round((len(self.mazegen.maze[0]) / 2) - 1) and count_l == round((len(self.mazegen.maze) / 2) - 1):
                    pac_spawn = Cell(self.padding_h + i, self.padding_v + j, cell)
                    k = 1
                if not k == 1:
                    self.cell.append(Cell(self.padding_h + i, self.padding_v + j, cell))
                else:
                    self.cell.append(pac_spawn)
                    k = 0
                count_c += 1
                i += self.bloc + self.m_bloc
            j += self.bloc + self.m_bloc
            count_l += 1
        self.init_pac_gum()
        pac_m = Pac_man(
                        pac_spawn,
                        pac_spawn.x + ((self.bloc - (self.m_bloc / 2)) - PAC_F.get_width()) / 2,
                        pac_spawn.y + ((self.bloc) - PAC_F.get_height()) / 2,
                        [pac_spawn.x + (self.bloc / 2), pac_spawn.y + (self.bloc / 2)]
                        )
        while self.running:
            self.screen.fill("black")
            self.screen.blit(PAC_F, (pac_m.x, pac_m.y))
            self.processed_keys(pygame.key.get_pressed(), pac_m)
            self.move(pac_m)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            self.dt = self.clock.tick(60) / 1000
            for wall in walls:
                pygame.draw.rect(self.screen, "blue", wall)
            if ((pac_m.current.pac_g.eat == False and
                (pac_m.current.x + (self.bloc / 2)) - 5 <= pac_m.center[0]
                and (pac_m.current.x + (self.bloc / 2)) + 5 >= pac_m.center[0]) and
                ((pac_m.current.y + (self.bloc / 2)) - 5 <= pac_m.center[1]
                and (pac_m.current.y + (self.bloc / 2)) + 5 >= pac_m.center[1])):
                pac_m.current.pac_g.eat = True
                pac_m.n_gum += 1
            print(pac_m.n_gum)
            for cell in self.cell:
                if cell.pac_g and not cell.pac_g.eat:
                    pygame.draw.rect(self.screen, "yellow", cell.pac_g.rect)
            pygame.display.update()
            pygame.display.flip()
        pygame.quit()
