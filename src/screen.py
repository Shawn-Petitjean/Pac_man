from abc import ABC, abstractmethod

import pygame

from src.highscore import Highscores


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


class TextScreen(Screen):
    """Ecran affichant une liste de lignes de texte centrees.

    Gere le rendu des lignes et la navigation (QUIT -> "quit", Echap ->
    retour au menu). Les sous-classes fournissent le contenu via _lines().
    """

    LINE_GAP = 0.015         # ecart entre lignes en % de la hauteur

    @abstractmethod
    def _lines(self) -> list[str]:
        """Les lignes a afficher (defini par chaque ecran)."""

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
        lines = self._lines()
        n = len(lines)
        for i, line in enumerate(lines):
            y = h / 2 + (i - (n - 1) / 2) * line_h
            text = self.font.render(line, True, "white")
            self.screen.blit(text, text.get_rect(center=(cx, y)))
        pygame.display.flip()


class Instructions(TextScreen):
    """Ecran d'aide : affiche les controles et les regles (lignes fixes)."""

    FONT_RATIO = 0.04        # plus petit que le menu : beaucoup de lignes

    def _lines(self) -> list[str]:
        return [
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


class HighscoresScreen(TextScreen):
    """Affiche le top 10 des scores (lignes calculees depuis les donnees)."""

    def __init__(self, highscores: Highscores) -> None:
        super().__init__()
        self.highscores = highscores

    def _lines(self) -> list[str]:
        lines = ["HIGHSCORES", ""]
        entries = self.highscores.entries()
        for rang, entry in enumerate(entries, start=1):
            lines.append(f"{rang}. {entry.name}   {entry.score}")
        if not entries:
            lines.append("Aucun score pour l'instant")
        lines.append("")
        lines.append("Echap : retour")
        return lines


class EndScreen(TextScreen):
    def __init__(self, highscores: Highscores, score: int, title: str) -> None:
        super().__init__()
        self.highscores = highscores
        self.score = score
        self.title = title
        self.name = ""

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._activate("quit")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self._validate()               # valider le nom
                elif event.key == pygame.K_BACKSPACE:
                    self.name = self.name[:-1]     # effacer le dernier
                else:
                    self.name += event.unicode     # ajouter le caractere tape

    def _validate(self) -> None:
        # clean_name est reapplique dans add()
        self.highscores.add(self.name, self.score)
        self.highscores.save()
        self._activate("")                         # retour au menu

    def _lines(self) -> list[str]:
        return [
            self.title,
            "",
            f"Score : {self.score}",
            "",
            f"Ton nom : {self.name}",
            "Entree pour valider",
        ]
