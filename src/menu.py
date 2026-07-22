import pygame

from src.screen import Screen


class Button:
    """Un bouton de menu : un libelle, une action, un rect."""

    BORDER_WIDTH = 3
    BORDER_RADIUS = 12
    SELECTED_SCALE = 1.05          # upscale de 5% du bouton selectionne
    COLOR_NORMAL = "white"
    COLOR_SELECTED = "brown3"      # plus clair que brown4

    def __init__(self, label: str, action: str) -> None:
        self.label = label
        self.action = action              # "start", "highscores", "quit"...
        self.rect = pygame.Rect(0, 0, 0, 0)   # posee par le layout
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


class ButtonMenu(Screen):
    """Ecran generique : une liste de boutons navigables clavier/souris.

    Reutilisable par le menu principal, le menu pause, game over... La
    sous-classe fournit les boutons ; _region() (surchargeable) donne la
    zone de placement, par defaut toute la fenetre. Le design (fond,
    police, style des boutons) est herite/partage, donc identique partout.
    """

    BOX_PAD_W = 0.03         # padding du cadre en % de la largeur (region)
    BOX_PAD_H = 0.05         # padding du cadre en % de la hauteur (region)
    GAP_RATIO = 0.04         # ecart entre boutons en % de la hauteur (region)

    def __init__(self, buttons: list[Button]) -> None:
        super().__init__()
        self.buttons = buttons
        self.selected = 0

    def _region(self) -> pygame.Rect:
        """Zone de placement des boutons. Defaut : toute la fenetre."""
        return self.screen.get_rect()

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
        # modulo = rotation : depuis le dernier, n % n = 0 donc retour au
        # premier ; depuis le premier, -1 % n = n-1 donc retour au dernier
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

    # ---------------------------------------------------------- layout/dessin

    def _layout(self) -> None:
        """Dimensionne et positionne les boutons dans la region."""
        region = self._region()
        self._update_font(region.height)

        cx, cy = region.center

        # taille de cadre commune, depuis le libelle le plus large
        max_w = max(self.font.size(b.label)[0] for b in self.buttons)
        box_w = max_w + int(region.width * self.BOX_PAD_W)
        box_h = self.font.get_height() + int(region.height * self.BOX_PAD_H)
        spacing = box_h + int(region.height * self.GAP_RATIO)

        # (i - (n-1)/2) etale les boutons autour du centre de la region
        n = len(self.buttons)
        for i, button in enumerate(self.buttons):
            y = cy + (i - (n - 1) / 2) * spacing
            button.rect = pygame.Rect(0, 0, box_w, box_h)
            button.rect.center = (int(cx), int(y))
            button.selected = (i == self.selected)

    def _draw(self) -> None:
        """Dessine la frame : fond, puis chaque bouton."""
        self._draw_background()
        self._layout()
        for button in self.buttons:
            button.draw(self.screen, self.font)
        pygame.display.flip()


class Menu(ButtonMenu):
    """Menu principal : les boutons du jeu, plein ecran."""

    def __init__(self) -> None:
        super().__init__([
            Button("Start Game", "start"),
            Button("Highscores", "highscores"),
            Button("Instructions", "instructions"),
            Button("Exit", "quit"),
        ])
