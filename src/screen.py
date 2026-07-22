from abc import ABC, abstractmethod

import pygame


class Screen(ABC):
    """Base commune a tous les ecrans (menu, sous-menus, pause, game over...).

    Porte la boucle commune (run) et la police adaptative ; chaque ecran
    concret implemente seulement _handle_events() et _draw(). Pattern
    "template method" : run() fixe le squelette, les sous-classes
    remplissent les trous.
    """

    FPS = 60
    BACKGROUND = "black"
    FONT_RATIO = 0.06        # taille de police en % de la hauteur

    def __init__(self) -> None:
        pygame.font.init()
        self.clock = pygame.time.Clock()
        self.running = False
        self.result = ""
        self.font = pygame.font.Font(None, 48)
        self._font_h = 0    # hauteur de fenetre pour laquelle self.font existe

    def run(self, screen: pygame.Surface) -> str:
        """Boucle de l'ecran. Renvoie l'action choisie (ou "" au retour)."""
        self.screen = screen
        self.running = True
        self.result = ""
        while self.running:
            self._handle_events()
            self._draw()
            self.clock.tick(self.FPS)
        return self.result

    def _activate(self, action: str) -> None:
        """Termine l'ecran en renvoyant l'action choisie."""
        self.result = action
        self.running = False

    def _update_font(self, h: int) -> None:
        """Police adaptative : recreee seulement si la hauteur a change."""
        if h != self._font_h:
            self.font = pygame.font.Font(None, int(h * self.FONT_RATIO))
            self._font_h = h

    def _draw_background(self) -> None:
        """Fond commun a tous les ecrans. Surchargeable (ex: la pause
        dessine par-dessus le jeu au lieu de remplir l'ecran)."""
        self.screen.fill(self.BACKGROUND)

    @abstractmethod
    def _handle_events(self) -> None:
        """Traite les evenements de la frame (defini par chaque ecran)."""

    @abstractmethod
    def _draw(self) -> None:
        """Dessine la frame (defini par chaque ecran)."""


class Instructions(Screen):
    """Ecran d'aide : affiche les controles et les regles."""

    FONT_RATIO = 0.04        # plus petit que le menu : beaucoup de lignes
    LINE_GAP = 0.015         # ecart entre lignes en % de la hauteur

    def __init__(self) -> None:
        super().__init__()
        self.lines = [
            "CONTROLES",
            "Fleches ou WASD : se deplacer",
            "Echap : pause",
            "",
            "REGLES",
            "Mange tous les pacgums pour finir le niveau",
            "Evite les fantomes",
            "Un super-pacgum les rend comestibles un moment",
            "",
            "Echap : retour au menu",
        ]

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._activate("quit")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._activate("")      # retour au menu

    def _draw(self) -> None:
        self._draw_background()
        w, h = self.screen.get_size()
        self._update_font(h)

        cx = w / 2
        line_h = self.font.get_height() + int(h * self.LINE_GAP)

        # (i - (n-1)/2) : meme centrage vertical que les boutons du menu
        n = len(self.lines)
        for i, line in enumerate(self.lines):
            y = h / 2 + (i - (n - 1) / 2) * line_h
            text = self.font.render(line, True, "white")
            self.screen.blit(text, text.get_rect(center=(cx, y)))
        pygame.display.flip()
