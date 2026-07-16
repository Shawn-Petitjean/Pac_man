import pygame


class Button:
    """Un bouton de menu : un libelle, une action, un rect."""

    BORDER_WIDTH = 3
    BORDER_RADIUS = 12
    SELECTED_SCALE = 1.05          # upscale de 5% du bouton selectionne
    COLOR_NORMAL = "white"
    COLOR_SELECTED = "brown3"

    def __init__(self, label: str, action: str) -> None:
        self.label = label
        self.action = action              # "start", "highscores", "quit"...
        self.rect = pygame.Rect(0, 0, 0, 0)   # taille/position posees par Menu
        self.selected = False

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Dessine le bouton (cadre + texte) dans son propre rect.

        Le bouton selectionne est agrandi et d'une teinte plus claire.
        """
        color = self.COLOR_SELECTED if self.selected else self.COLOR_NORMAL
        rect = self._display_rect()
        pygame.draw.rect(screen, color, rect,
                         width=self.BORDER_WIDTH,
                         border_radius=self.BORDER_RADIUS)
        text = self._render_label(font, color)
        screen.blit(text, text.get_rect(center=rect.center))

    def _display_rect(self) -> pygame.Rect:
        """Rect affiche : agrandi si selectionne.

        La zone cliquable (self.rect) ne bouge pas, elle : seul le visuel
        grossit, sinon le survol deviendrait "collant".
        """
        if not self.selected:
            return self.rect
        grow = self.SELECTED_SCALE - 1
        return self.rect.inflate(self.rect.w * grow, self.rect.h * grow)

    def _render_label(self, font: pygame.font.Font,
                      color: str) -> pygame.Surface:
        """Rend le texte, avec le meme upscale que le cadre si selectionne."""
        surface = font.render(self.label, True, color)
        if not self.selected:
            return surface
        w, h = surface.get_size()
        return pygame.transform.scale(
            surface,
            (int(w * self.SELECTED_SCALE), int(h * self.SELECTED_SCALE)))

    def is_hovered(self, mouse_pos: tuple[int, int]) -> bool:
        """Renvoie True si la souris est au-dessus du bouton."""
        return self.rect.collidepoint(mouse_pos)


class Menu:
    """Menu principal : navigue au clavier/souris, renvoie l'action choisie."""

    FPS = 60
    BACKGROUND = "black"
    FONT_RATIO = 0.06        # taille de police en % de la hauteur
    BOX_PAD_W = 0.03         # padding du cadre en % de la largeur
    BOX_PAD_H = 0.05         # padding du cadre en % de la hauteur
    GAP_RATIO = 0.04         # ecart entre boutons en % de la hauteur

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
        self.selected = 0
        self.running = False
        self.result = ""

    def run(self, screen: pygame.Surface) -> str:
        """Boucle du menu. Renvoie l'action choisie par le joueur."""
        self.screen = screen
        self.running = True
        self.result = ""
        while self.running:
            self._handle_events()
            self._draw()
            self.clock.tick(self.FPS)
        return self.result

    # ---------------------------------------------------------------- events

    def _handle_events(self) -> None:
        """Aiguille chaque evenement vers le bon handler."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._activate("quit")
            elif event.type == pygame.KEYDOWN:
                self._handle_key(event)
            elif event.type == pygame.MOUSEMOTION:
                self._hover(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._click(event.pos)

    def _handle_key(self, event: pygame.event.Event) -> None:
        """Fleches = deplacer la selection, Entree/Espace = activer."""
        # modulo = rotation : depuis le dernier, 5 % 5 = 0 donc retour au
        # premier ; depuis le premier, -1 % 5 = 4 donc retour au dernier
        if event.key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(self.buttons)
        elif event.key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(self.buttons)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._activate(self.buttons[self.selected].action)

    def _hover(self, pos: tuple[int, int]) -> None:
        """Le survol deplace la selection, mais n'active rien.

        Sur MOUSEMOTION (pas a chaque frame) : sinon une souris immobile
        posee sur un bouton ecraserait en boucle la selection au clavier.
        """
        for i, button in enumerate(self.buttons):
            if button.is_hovered(pos):
                self.selected = i

    def _click(self, pos: tuple[int, int]) -> None:
        """Le clic active le bouton sous le curseur."""
        for button in self.buttons:
            if button.is_hovered(pos):
                self._activate(button.action)

    def _activate(self, action: str) -> None:
        """Termine le menu en renvoyant l'action choisie."""
        self.result = action
        self.running = False

    # ---------------------------------------------------------- layout/dessin

    def _update_font(self, h: int) -> None:
        """Police adaptative : recreee seulement si la hauteur a change."""
        if h != self._font_h:
            self.font = pygame.font.Font(None, int(h * self.FONT_RATIO))
            self._font_h = h

    def _layout(self) -> None:
        """Dimensionne et positionne les boutons selon la fenetre."""
        w, h = self.screen.get_size()
        self._update_font(h)

        cx, cy = w / 2, h / 2      # centre de la fenetre

        # taille de cadre commune, depuis le libelle le plus large
        max_w = max(self.font.size(b.label)[0] for b in self.buttons)
        box_w = max_w + int(w * self.BOX_PAD_W)
        box_h = self.font.get_height() + int(h * self.BOX_PAD_H)
        spacing = box_h + int(h * self.GAP_RATIO)

        # (i - (n-1)/2) etale les boutons autour de cy : le bloc reste centre
        n = len(self.buttons)
        for i, button in enumerate(self.buttons):
            y = cy + (i - (n - 1) / 2) * spacing
            button.rect = pygame.Rect(0, 0, box_w, box_h)
            button.rect.center = (int(cx), int(y))
            button.selected = (i == self.selected)

    def _draw(self) -> None:
        """Dessine la frame : fond, puis chaque bouton."""
        self.screen.fill(self.BACKGROUND)
        self._layout()
        for button in self.buttons:
            button.draw(self.screen, self.font)
        pygame.display.flip()
