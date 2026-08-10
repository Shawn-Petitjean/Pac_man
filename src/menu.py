from pathlib import Path

import pygame
from PIL import Image

from src.screen import Screen
from src.config import Cheat

SPRITE_DIR = Path(__file__).resolve().parent.parent / "sprites"


class Button:
    """A menu button: a label, an action, and a rect."""

    BORDER_WIDTH = 3
    BORDER_RADIUS = 12
    SELECTED_SCALE = 1.05
    COLOR_NORMAL = "white"
    COLOR_SELECTED = "gold1"

    def __init__(self, label: str, action: str) -> None:
        self.label = label
        self.action = action
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.selected = False

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the button (frame + text) inside its own rect.

        The selected button is scaled up and a lighter shade.
        """
        color = self.COLOR_SELECTED if self.selected else self.COLOR_NORMAL
        rect = self._display_rect()
        pygame.draw.rect(screen, color, rect,
                         width=self.BORDER_WIDTH,
                         border_radius=self.BORDER_RADIUS)
        text = self._render_label(font, color)
        screen.blit(text, text.get_rect(center=rect.center))

    def _display_rect(self) -> pygame.Rect:
        """Displayed rect, scaled up when selected.

        The clickable area (self.rect) stays put; only the visual grows,
        otherwise hovering would become "sticky".
        """
        if not self.selected:
            return self.rect
        grow = self.SELECTED_SCALE - 1
        return self.rect.inflate(self.rect.w * grow, self.rect.h * grow)

    def _render_label(self, font: pygame.font.Font,
                      color: str) -> pygame.Surface:
        """Render the text, scaled up like the frame when selected."""
        surface = font.render(self.label, True, color)
        if not self.selected:
            return surface
        w, h = surface.get_size()
        return pygame.transform.scale(
            surface,
            (int(w * self.SELECTED_SCALE), int(h * self.SELECTED_SCALE)))

    def is_hovered(self, mouse_pos: tuple[int, int]) -> bool:
        """Return True if the mouse is over the button."""
        return self.rect.collidepoint(mouse_pos)


class ButtonMenu(Screen):
    """Generic screen: a list of buttons navigable by keyboard and mouse.

    Reused by the main menu, pause menu, end screen... Subclasses provide
    the buttons; _region() (overridable) gives the layout area, the whole
    window by default. The design (background, font, button style) is
    inherited/shared, hence identical everywhere.
    """

    BOX_PAD_W = 0.03
    BOX_PAD_H = 0.05
    GAP_RATIO = 0.04

    def __init__(self, buttons: list[Button]) -> None:
        super().__init__()
        self.buttons = buttons
        self.selected = 0

    def _region(self) -> pygame.Rect:
        """Layout area for the buttons. Whole window by default."""
        return self.screen.get_rect()

    def _label_width(self, button: "Button") -> int:
        """Label width used to size the boxes. Overridable (CheatMenu
        measures the widest state so boxes do not shrink on toggle)."""
        return self.font.size(button.label)[0]

    def _handle_events(self) -> None:
        """Dispatch each event to the right handler."""
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
        """Arrows move the selection, Enter/Space activate it."""
        if event.key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(self.buttons)
        elif event.key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(self.buttons)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._activate(self.buttons[self.selected].action)

    def _hover(self, pos: tuple[int, int]) -> None:
        """Hovering moves the selection but activates nothing.

        Handled on MOUSEMOTION (not every frame): otherwise a still mouse
        resting on a button would keep overriding the keyboard selection.
        """
        for i, button in enumerate(self.buttons):
            if button.is_hovered(pos):
                self.selected = i

    def _click(self, pos: tuple[int, int]) -> None:
        """A click activates the button under the cursor."""
        for button in self.buttons:
            if button.is_hovered(pos):
                self._activate(button.action)

    def _layout(self) -> None:
        """Size and position the buttons inside the region."""
        region = self._region()
        self._update_font(region.height)

        cx, cy = region.center

        max_w = max(self._label_width(b) for b in self.buttons)
        box_w = max_w + int(region.width * self.BOX_PAD_W)
        box_h = self.font.get_height() + int(region.height * self.BOX_PAD_H)
        spacing = box_h + int(region.height * self.GAP_RATIO)

        n = len(self.buttons)
        for i, button in enumerate(self.buttons):
            y = cy + (i - (n - 1) / 2) * spacing
            button.rect = pygame.Rect(0, 0, box_w, box_h)
            button.rect.center = (int(cx), int(y))
            button.selected = (i == self.selected)

    def _draw(self) -> None:
        """Draw the frame: background, buttons, then extras (title...)."""
        self._draw_background()
        self._layout()
        for button in self.buttons:
            button.draw(self.screen, self.font)
        self._draw_extra()
        pygame.display.flip()

    def _draw_extra(self) -> None:
        """Extra drawing on top of the buttons. Empty by default,
        overridable (e.g. the main-menu title)."""


class ChaseParade:
    """Attract animation: Pac-Man chased by the ghosts, moving left.

    Loads every frame of each animated GIF (via Pillow) once, scrolls
    right to left in a loop, and cycles the frames to animate them.
    """

    ORDER = ["Pac-Man", "Blinky", "Pinky", "Inky", "Clyde"]
    SIZE_RATIO = 0.03
    SPEED_RATIO = 0.003
    GAP = 1.8
    FRAME_MS = 120

    def __init__(self) -> None:
        self._raw = [self._load_frames(name) for name in self.ORDER]
        self.animations: list[list[pygame.Surface]] = self._raw
        self._scaled_h = 0
        self.x = 0.0
        self._started = False

    def _load_frames(self, name: str) -> list[pygame.Surface]:
        """Extract an animated GIF's frames at native size, with alpha."""
        filename = f"Arcade - Pac-Man - General Sprites - {name} (Left).gif"
        gif = Image.open(SPRITE_DIR / filename)
        frames: list[pygame.Surface] = []
        for i in range(getattr(gif, "n_frames", 1)):
            gif.seek(i)
            rgba = gif.convert("RGBA")
            surf = pygame.image.frombytes(
                rgba.tobytes(), rgba.size, "RGBA").convert_alpha()
            frames.append(surf)
        return frames

    def _rescale(self, h: int) -> None:
        """Rescale the sprites when the window height changes."""
        if h == self._scaled_h:
            return
        self._scaled_h = h
        target = max(1, int(h * self.SIZE_RATIO))
        self.animations = []
        for frames in self._raw:
            factor = target / frames[0].get_height()
            self.animations.append([
                pygame.transform.scale(
                    f, (int(f.get_width() * factor), target))
                for f in frames
            ])

    def draw(self, screen: pygame.Surface, y: int) -> None:
        """Rescale if needed, advance the parade, cycle the frames."""
        w, h = screen.get_size()
        self._rescale(h)

        step = int(self.animations[0][0].get_width() * self.GAP)
        group_w = step * len(self.animations)
        if not self._started or self.x + group_w < 0:
            self.x = float(w)
            self._started = True

        now = pygame.time.get_ticks()
        x = self.x
        for frames in self.animations:
            i = (now // self.FRAME_MS) % len(frames)
            screen.blit(frames[i], (int(x), y))
            x += step
        self.x -= self.SPEED_RATIO * w


class Menu(ButtonMenu):
    """Main menu: big PAC-MAN title plus smaller buttons."""

    FONT_RATIO = 0.045
    TITLE = "PAC-MAN"
    TITLE_RATIO = 0.16
    TITLE_COLOR = "yellow"
    OUTLINE_COLOR = "gold"
    OUTLINE_RATIO = 0.03
    TITLE_Y = 0.16
    PARADE_Y = 0.30
    TOP_MARGIN = 0.42

    def __init__(self) -> None:
        super().__init__([
            Button("Start Game", "start"),
            Button("Highscores", "highscores"),
            Button("Instructions", "instructions"),
            Button("Exit", "quit"),
        ])
        self.title_font = pygame.font.Font(None, 48)
        self._title_h = 0
        self.parade = ChaseParade()

    def _region(self) -> pygame.Rect:
        """Buttons occupy the area below the title (lower part)."""
        r = self.screen.get_rect()
        top = int(r.height * self.TOP_MARGIN)
        return pygame.Rect(0, top, r.width, r.height - top)

    def _draw_extra(self) -> None:
        """Draw the PAC-MAN title with a very light golden outline."""
        w, h = self.screen.get_size()
        if h != self._title_h:
            self.title_font = pygame.font.Font(None, int(h * self.TITLE_RATIO))
            self._title_h = h

        center = (w / 2, h * self.TITLE_Y)
        outline = self.title_font.render(self.TITLE, True, self.OUTLINE_COLOR)
        off = max(1, int(h * self.TITLE_RATIO * self.OUTLINE_RATIO))
        for dx, dy in ((-off, 0), (off, 0), (0, -off), (0, off)):
            rect = outline.get_rect(center=(center[0] + dx, center[1] + dy))
            self.screen.blit(outline, rect)
        title = self.title_font.render(self.TITLE, True, self.TITLE_COLOR)
        self.screen.blit(title, title.get_rect(center=center))
        self.parade.draw(self.screen, int(h * self.PARADE_Y))


class PauseMenu(ButtonMenu):
    """Pause menu: buttons in a centered square, over the frozen game."""

    PANEL_PAD = 40
    PANEL_RADIUS = 16
    REGION_RATIO = 0.5

    def __init__(self, cheats: Cheat) -> None:
        self.cheats = cheats
        super().__init__([
            Button("Resume", "resume"),
            Button("Cheat", "cheat"),
            Button("Main Menu", "menu"),
        ])

    def _region(self) -> pygame.Rect:
        """A centered square, not the whole window."""
        r = self.screen.get_rect()
        size = int(min(r.width, r.height) * self.REGION_RATIO)
        rect = pygame.Rect(0, 0, size, size)
        rect.center = r.center
        return rect

    def _handle_key(self, event: pygame.event.Event) -> None:
        """Escape resumes; otherwise normal navigation."""
        if event.key == pygame.K_ESCAPE:
            self._activate("resume")
        else:
            super()._handle_key(event)

    def _activate(self, action: str) -> None:
        """"cheat" opens the cheat menu then returns; otherwise closes."""
        if action == "cheat":
            CheatMenu(self.cheats).run(self.screen)
        else:
            super()._activate(action)

    def _draw_background(self) -> None:
        """Opaque background: the game is fully hidden behind the menu."""
        self.screen.fill(self.BACKGROUND)

        panel = self._region().inflate(self.PANEL_PAD, self.PANEL_PAD)
        pygame.draw.rect(self.screen, (20, 20, 40), panel,
                         border_radius=self.PANEL_RADIUS)
        pygame.draw.rect(self.screen, "white", panel,
                         width=2, border_radius=self.PANEL_RADIUS)


class CheatMenu(ButtonMenu):
    """Cheat menu: each button toggles a flag of the shared Cheat.

    Unlike a normal menu, activating a toggle does not close the menu:
    it flips the flag and stays. Only "Retour" (or Escape) closes it.
    """

    TOGGLES = [
        ("Invincible", "invincible"),
        ("Vitesse", "speed")
    ]

    def __init__(self, cheats: Cheat) -> None:
        self.cheats = cheats
        self._base = {flag: label for label, flag in self.TOGGLES}
        buttons = [Button("", flag) for _, flag in self.TOGGLES]
        buttons.append(Button("Retour", "back"))
        super().__init__(buttons)

    def _label_width(self, button: Button) -> int:
        """Always measure the widest state ("OFF") for a stable width."""
        if button.action in self._base:
            return self.font.size(f"{self._base[button.action]} : OFF")[0]
        return self.font.size(button.label)[0]

    def _handle_key(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_ESCAPE:
            self._activate("back")
        else:
            super()._handle_key(event)

    def _activate(self, action: str) -> None:
        if action == "back":
            self.running = False
        elif action == "quit":
            self.result = "quit"
            self.running = False
        else:
            setattr(self.cheats, action, not getattr(self.cheats, action))

    def _layout(self) -> None:
        for (label, flag), button in zip(self.TOGGLES, self.buttons):
            state = "ON" if getattr(self.cheats, flag) else "OFF"
            button.label = f"{label} : {state}"
        super()._layout()
