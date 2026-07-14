import pygame


class Button:
    def __init__(self, label: str, action: str) -> None:
        self.label = label
        self.action = action              # "start", "highscores", "quit"...
        self.rect = pygame.Rect(0, 0, 0, 0)   # taille/position posees par Menu
        self.hovered = False
        self.selected = False

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Dessine le bouton (cadre + texte) dans son propre rect."""
        pygame.draw.rect(screen, "white", self.rect,
                         width=3, border_radius=12)
        text_surface = font.render(self.label, True, "white")
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    


class Menu:
    def __init__(self) -> None:
        pygame.font.init()

        self.clock = pygame.time.Clock()
        self.buttons = [
            Button("Start Game", "start"),
            Button("Highscores", "highscores"),
            Button("Instructions", "instructions"),
            Button("Cheat", "cheat"),
            Button("Exit", "quit"),
        ]
        self.font = pygame.font.Font(None, 48)
        self._font_h = 0    # hauteur de fenetre pour laquelle self.font existe

    def run(self, screen: pygame.Surface) -> str:
        self.screen = screen
        self.running = True
        self.result = ""
        while self.running:
            self._handle_events()
            self._draw()
            self.clock.tick(60)
        return self.result

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.result = "quit"
                self.running = False

    def _layout(self) -> None:
        """Dimensionne et positionne les boutons selon la fenetre."""
        w, h = self.screen.get_size()

        # police adaptative : recreee seulement si la hauteur a change
        if h != self._font_h:
            self.font = pygame.font.Font(None, int(h * 0.06)) # taille de police en %
            self._font_h = h

        cx, cy = w / 2, h / 2 # taille de fenetre / 2 pour centrer

        # taille de cadre commune, depuis le libelle le plus large
        max_w = max(self.font.size(b.label)[0] for b in self.buttons)
        box_w = max_w + int(w * 0.03)
        box_h = self.font.get_height() + int(h * 0.05) # taille du cadre en %
        spacing = box_h + int(h * 0.04) # espacement entre bouttons

        n = len(self.buttons)
        for i, button in enumerate(self.buttons):
            y = cy + (i - (n - 1) / 2) * spacing
            button.rect = pygame.Rect(0, 0, box_w, box_h)
            button.rect.center = (int(cx), int(y))

    def _draw(self) -> None:
        self.screen.fill("black")
        self._layout()
        for button in self.buttons:
            button.draw(self.screen, self.font)
        pygame.display.flip()
