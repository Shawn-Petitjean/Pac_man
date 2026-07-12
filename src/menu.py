import pygame


class Menu:
    def __init__(self) -> None:
        self.clock = pygame.time.Clock()

    def run(self, screen: pygame.Surface) -> str:
        self.screen = screen
        self.running = True
        result = "quit"

        while self.running:
            player_pos = pygame.Vector2(
                screen.get_width() / 2, screen.get_height() / 2)
            cx, cy = player_pos

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    result = "quit"
                    self.running = False

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if pygame.Vector2(event.pos).distance_to((cx, cy)) <= 40:
                        result = "quit"
                        self.running = False

            self.screen.fill("purple")
            pygame.draw.circle(screen, "red", player_pos, 40)
            pygame.display.flip()
            self.clock.tick(60)

        return result
