from mazegenerator import MazeGenerator
import pygame
import time
from .sprite import Pac_man, Ghost
from .config import N, E, S, W, Cheat, GameConfig, GHOST_R, GHOST_O, GHOST_P, GHOST_B
from .menu import PauseMenu
from .maze import Pac_gum, Cell, Super_pac_gum


class Game:
    def __init__(self, screen: pygame.Surface, size: tuple[int, int],
                 cheats: Cheat, seed: int, config: GameConfig):
        self.seed = seed
        self.time = 0
        self.win = False
        self.timer = time.time()
        self.config = config
        self.add_time = 0
        self.n_gum = 0
        self.death_speed = 300
        self.size = size
        self. font = pygame.font.Font(None, 36)
        self.pacman = None
        self.ghost = []
        self.level = 0
        self.walls = []
        self.s_gum_score = config.points_per_super_pacgum
        self.gum_score = config.points_per_pacgum
        self.ghost_score = config.points_per_ghost
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
        self.max_t = config.level_max_time
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

    def init_game(self):
        ls_sprite = [GHOST_R, GHOST_O, GHOST_P, GHOST_B]
        g_pos = [0, self.rows - 1, (self.cols * self.rows) - self.rows, (self.cols * self.rows) - 1]
        r1 = 0 if len(self.mazegen.maze[0]) % 2 == 0 else 1
        r2 = 0 if len(self.mazegen.maze) % 2 == 0 else 1
        j = 0
        k = False
        count_l = 0
        for line in self.mazegen.maze:
            i = 0
            count_c = 0
            for cell in line:
                self.walls.extend(self.put_walls(cell, self.padding_h + i, self.padding_v + j))
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
        self.init_s_pac_gum()
        self.init_pac_gum()
        if self.level == 0:
            self.pacman = Pac_man(
                            pac_spawn,
                            pac_spawn.x + ((self.bloc - self.bloc * 0.6) / 2),
                            pac_spawn.y + ((self.bloc - self.bloc * 0.6) / 2),
                            [pac_spawn.x + (self.bloc / 2), pac_spawn.y + (self.bloc / 2)],
                            self.bloc,
                            self.mazegen,
                            self.config.lives
                            )
            for i in range(0, 4):
                self.ghost.append(Ghost(
                                    self.cells[g_pos[i]],
                                    self.cells[g_pos[i]].x + ((self.bloc - self.bloc * 0.6) / 2),
                                    self.cells[g_pos[i]].y + ((self.bloc - self.bloc * 0.6) / 2),
                                    [self.cells[g_pos[i]].x + (self.bloc / 2), self.cells[g_pos[i]].y + (self.bloc / 2)],
                                    self.bloc,
                                    self.mazegen,
                                    self.size,
                                    ls_sprite[i]
                                    ))
        else:
            self.pacman.current = pac_spawn
            self.pacman.pos = [pac_spawn.x + (self.bloc / 2), pac_spawn.y + (self.bloc / 2)]
            self.pacman.x = pac_spawn.x + ((self.bloc - self.bloc * 0.6) / 2)
            self.pacman.y = pac_spawn.y + ((self.bloc - self.bloc * 0.6) / 2)
            self.pacman.maze = self.mazegen
            for i in range(0, 4):
                self.ghost[i].current = self.cells[g_pos[i]]
                self.ghost[i].x = self.cells[g_pos[i]].x + ((self.bloc - self.bloc * 0.6) / 2)
                self.ghost[i].y = self.cells[g_pos[i]].y + ((self.bloc - self.bloc * 0.6) / 2)
                self.ghost[i].pos = [self.cells[g_pos[i]].x + (self.bloc / 2), self.cells[g_pos[i]].y + (self.bloc / 2)]
                self.ghost[i].maze = self.mazegen
        self.ghost[0].pathfinding(self.pacman.current.pos)
        self.time = time.time()

    def screen_refresh(self):
            score = (self.pacman.n_gum * self.gum_score) + (self.pacman.n_sgum * self.s_gum_score) + (self.pacman.n_ghost * self.ghost_score)
            score_text = self.font.render(f"Score : {score}" + f" Timer : {self.max_t - round(time.time() - self.timer + self.add_time)}  Lives : {self.pacman.live}", True, (255, 255, 255))
            pygame.display.flip()
            self.screen.fill("black")
            for wall in self.walls:
                pygame.draw.rect(self.screen, "blue", wall)
            for cell in self.cells:
                if cell.pac_g and not cell.pac_g.eat:
                    pygame.draw.rect(self.screen, "yellow", cell.pac_g.rect)
            self.screen.blit(self.pacman.sprite, (self.pacman.x, self.pacman.y))
            for ghost in self.ghost:
                self.screen.blit(ghost.sprite, (ghost.x, ghost.y))
            self.screen.blit(score_text, (10, 10))
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
            if not cell.value == 15 and not cell.pac_g:
                self.n_gum += 1
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

    def init_s_pac_gum(self):
        ls = [self.rows + 1, (self.rows * 2) - 2, ((self.rows) * (self.cols)) - self.rows - 2, ((self.rows - 1) * (self.cols - 1))]
        for pos in ls:
            self.n_gum += 1
            self.cells[pos].pac_g = Super_pac_gum(
                                                    self.cells[pos].x - (self.bloc - (self.bloc * 0.1)),
                                                    self.cells[pos].y + self.bloc - (self.bloc * 0.1),
                                                    pygame.Rect(
                                                                self.cells[pos].x + (self.bloc / 2) - (self.bloc * 0.1),
                                                                self.cells[pos].y + (self.bloc / 2) - (self.bloc * 0.1),
                                                                self.bloc * 0.4,
                                                                self.bloc * 0.4
                                                                )
                                                 )
        
    def processed_move(self):
            if self.pacman.dead == True:
                for ghost in self.ghost:
                    ghost.pathfinding(ghost.spawn)
                    if ghost.d:
                        temp = ghost.speed
                        ghost.speed = self.death_speed
                        self.move(ghost)
                        ghost.speed = temp
                self.pacman.pathfinding(self.pacman.spawn)
                if self.pacman.d:
                    temp = self.pacman.speed
                    self.pacman.speed = self.death_speed
                    self.move(self.pacman)
                    self.pacman.speed = temp
                return
            for ghost in self.ghost:
                if ghost.dead == True:
                    ghost.pathfinding(ghost.spawn)
                    temp = ghost.speed
                    ghost.speed = self.death_speed
                    if ghost.d:
                        self.move(ghost)
                    ghost.speed = temp

                elif self.pacman.invul or self.cheats.invincible:
                    ghost.pathfinding(self.pacman.escape())
                    if ghost.d:
                        self.move(ghost)
                    self.pacman.collide(ghost)

                else:
                    ghost.pathfinding(self.pacman.current.pos)
                    if ghost.d:
                        self.move(ghost)
                    ghost.collide(self.pacman)

            self.processed_keys(pygame.key.get_pressed())
            self.move(self.pacman)

    def processed_keys(self, key_pressed):
        center_x = self.pacman.current.x + (self.bloc / 2)
        center_y = self.pacman.current.y + (self.bloc / 2)
        aligned_x = abs(self.pacman.center[0] - center_x) <= 1
        aligned_y = abs(self.pacman.center[1] - center_y) <= 1

        if aligned_x:
            if key_pressed[pygame.K_w] and not self.pacman.current.value & N:
                self.pacman.d = "N"
            elif key_pressed[pygame.K_s] and not self.pacman.current.value & S:
                self.pacman.d = "S"
        if aligned_y:
            if key_pressed[pygame.K_a] and not self.pacman.current.value & W:
                self.pacman.d = "W"
            elif key_pressed[pygame.K_d] and not self.pacman.current.value & E:
                self.pacman.d = "E"
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
                if sprite.current.value & N and sprite.center[1] - sprite.speed * self.dt <= sprite.current.y + self.bloc / 2:
                    self.snap_sprite_to_current(sprite)
                    return
                sprite.y -= sprite.speed * self.dt
                sprite.center[1] -= sprite.speed * self.dt
                if current_index >= self.cols:
                    above = self.cells[current_index - self.cols]
                    if sprite.center[1] <= above.y + self.bloc / 2:
                        sprite.current = above
            elif sprite.d == "S":
                if sprite.current.value & S and sprite.center[1] + sprite.speed * self.dt >= sprite.current.y + self.bloc / 2:
                    self.snap_sprite_to_current(sprite)
                    return
                sprite.y += sprite.speed * self.dt
                sprite.center[1] += sprite.speed * self.dt
                if current_index + self.cols < len(self.cells):
                    below = self.cells[current_index + self.cols]
                    if sprite.center[1] >= below.y + self.bloc / 2:
                        sprite.current = below
            elif sprite.d == "W":
                if sprite.current.value & W and sprite.center[0] - sprite.speed * self.dt <= sprite.current.x + self.bloc / 2:
                    self.snap_sprite_to_current(sprite)
                    return
                sprite.x -= sprite.speed * self.dt
                sprite.center[0] -= sprite.speed * self.dt
                if current_index % self.cols != 0:
                    left = self.cells[current_index - 1]
                    if sprite.center[0] <= left.x + self.bloc / 2:
                        sprite.current = left
            elif sprite.d == "E":
                if sprite.current.value & E and sprite.center[0] + sprite.speed * self.dt >= sprite.current.x + self.bloc / 2:
                    self.snap_sprite_to_current(sprite)
                    return
                sprite.x += sprite.speed * self.dt
                sprite.center[0] += sprite.speed * self.dt
                if (current_index + 1) % self.cols != 0:
                    right = self.cells[current_index + 1]
                    if sprite.center[0] >= right.x + self.bloc / 2:
                        sprite.current = right
            if sprite.current is not old_current:
                self.snap_sprite_to_current(sprite)

    def status(self, k: int):
        if self.cheats.speed:
            self.pacman.speed = 180
        else:
            self.pacman.speed = 120
        if self.pacman.dead == True:
            self.add_time = self.pacman.d_time - time.time()
            k = 1
        if self.pacman.d_time + 5 <= time.time():
            self.pacman.dead = False
        if self.pacman.invul_time + 5 <= time.time():
            self.pacman.invul = False
        for ghost in self.ghost:
            if ghost.d_time + 5 <= time.time():
                ghost.dead = False
        if ((self.pacman.current.pac_g.eat == False and self.pacman.dead == False and
            (self.pacman.current.x + (self.bloc / 2)) - 5 <= self.pacman.center[0]
            and (self.pacman.current.x + (self.bloc / 2)) + 5 >= self.pacman.center[0]) and
            ((self.pacman.current.y + (self.bloc / 2)) - 5 <= self.pacman.center[1]
            and (self.pacman.current.y + (self.bloc / 2)) + 5 >= self.pacman.center[1])):
            self.pacman.current.pac_g.eat = True
            if self.pacman.current.pac_g.__class__.__name__ == "Super_pac_gum":
                self.pacman.n_sgum += 1
                self.pacman.invul = True
                self.pacman.invul_time = time.time()
            else:
                self.pacman.n_gum += 1
        if self.pacman.dead == False and k == 1:
            self.timer += time.time() - self.pacman.d_time
            self.add_time = 0
            k = 0
        if self.pacman.live == 0:
            self.running = False
        if self.max_t - round(time.time() - self.timer + self.add_time) <= 0:
            self.running = False
        if self.level == 5:
            self.win = True
            self.running = False
        if self.pacman.n_gum + self.pacman.n_sgum == self.n_gum - 300:
            self.level += 1
            self.walls = []
            self.cells = []
            self.mazegen.generate()
            self.init_game()

    def run(self) -> str:
        self.init_game()
        k = 0
        j = 0
        start_menu = 0
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.result = "quit"
                    self.running = False
                elif (event.type == pygame.KEYDOWN
                        and event.key == pygame.K_ESCAPE):
                    start_menu = time.time()
                    j = 1
                    choice = PauseMenu(self.cheats).run(self.screen)
                    if choice == "menu":
                        self.running = False
                    elif choice == "quit":
                        self.result = "quit"
                        self.running = False
                    self.clock.tick()
            if j == 1:
                self.timer += time.time() - start_menu
                start_menu = 0
                j = 0
            self.dt = self.clock.tick(60) / 1000
            self.processed_move()
            self.status(k)
            self.screen_refresh()
        return self.result
