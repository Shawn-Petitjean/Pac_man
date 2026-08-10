from abc import ABC, abstractmethod

import pygame

from src.highscore import Highscores


class Screen(ABC):
    """Base class shared by every screen (menu, sub-menus, pause, end...).

    Owns the common loop (run) and the responsive font; each concrete
    screen only implements _handle_events() and _draw(). Template-method
    pattern: run() sets the skeleton, subclasses fill the gaps.
    """

    FPS = 60
    BACKGROUND = "black"
    FONT_RATIO = 0.06

    def __init__(self) -> None:
        pygame.font.init()
        self.clock = pygame.time.Clock()
        self.running = False
        self.result = ""
        self.font = pygame.font.Font(None, 48)
        self._font_h = 0

    def run(self, screen: pygame.Surface) -> str:
        """Run the screen loop and return the chosen action."""
        self.screen = screen
        self.running = True
        self.result = ""
        while self.running:
            self._handle_events()
            self._draw()
            self.clock.tick(self.FPS)
        return self.result

    def _activate(self, action: str) -> None:
        """End the screen, returning the chosen action."""
        self.result = action
        self.running = False

    def _update_font(self, h: int) -> None:
        """Responsive font: rebuilt only when the window height changes."""
        if h != self._font_h:
            self.font = pygame.font.Font(None, int(h * self.FONT_RATIO))
            self._font_h = h

    def _draw_background(self) -> None:
        """Common background. Overridable (e.g. pause draws over the game)."""
        self.screen.fill(self.BACKGROUND)

    @abstractmethod
    def _handle_events(self) -> None:
        """Handle this frame's events (defined by each screen)."""

    @abstractmethod
    def _draw(self) -> None:
        """Draw this frame (defined by each screen)."""


class TextScreen(Screen):
    """Screen showing a list of centered text lines.

    Handles line rendering and navigation (QUIT -> "quit", Escape ->
    back to menu). Subclasses provide the content via _lines().
    """

    LINE_GAP = 0.015

    @abstractmethod
    def _lines(self) -> list[str]:
        """The lines to display (defined by each screen)."""

    def _line_color(self, index: int, line: str) -> str:
        """Colour of a line (white by default), overridable per line."""
        return "white"

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._activate("quit")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._activate("")

    def _draw(self) -> None:
        self._draw_background()
        w, h = self.screen.get_size()
        self._update_font(h)

        cx = w / 2
        line_h = self.font.get_height() + int(h * self.LINE_GAP)

        lines = self._lines()
        n = len(lines)
        for i, line in enumerate(lines):
            y = h / 2 + (i - (n - 1) / 2) * line_h
            text = self.font.render(line, True, self._line_color(i, line))
            self.screen.blit(text, text.get_rect(center=(cx, y)))
        pygame.display.flip()


class Instructions(TextScreen):
    """Help screen: shows the controls and rules (fixed lines)."""

    FONT_RATIO = 0.04

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
    """Show the top 10 scores (lines computed from the data)."""

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
    """End screen: victory or defeat, score, then name entry.

    A single screen for both cases; `won` changes the title and its colour.
    """

    WON_COLOR = "yellow"
    LOST_COLOR = "red"

    def __init__(self, highscores: Highscores, score: int,
                 won: bool) -> None:
        super().__init__()
        self.highscores = highscores
        self.score = score
        self.won = won
        self.name = ""

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._activate("quit")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self._validate()
                elif event.key == pygame.K_BACKSPACE:
                    self.name = self.name[:-1]
                else:
                    self.name += event.unicode

    def _validate(self) -> None:
        self.highscores.add(self.name, self.score)
        self.highscores.save()
        self._activate("")

    def _lines(self) -> list[str]:
        head = "VICTORY !" if self.won else "GAME OVER"
        return [
            head,
            "",
            f"Score : {self.score}",
            "",
            f"Ton nom : {self.name}",
            "Entree pour valider",
        ]

    def _line_color(self, index: int, line: str) -> str:
        """Title (line 0) coloured: yellow on victory, red on defeat."""
        if index == 0:
            return self.WON_COLOR if self.won else self.LOST_COLOR
        return "white"
