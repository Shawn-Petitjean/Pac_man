from pathlib import Path

import pygame
from PIL import Image

from src.screen import Screen

SPRITE_DIR = Path(__file__).resolve().parent.parent / "sprites"


class Button:
    """Un bouton de menu : un libelle, une action, un rect."""

    BORDER_WIDTH = 3
    BORDER_RADIUS = 12
    SELECTED_SCALE = 1.05          # upscale de 5% du bouton selectionne
    COLOR_NORMAL = "white"
    COLOR_SELECTED = "gold1"

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
        """Dessine la frame : fond, boutons, puis extras (titre...)."""
        self._draw_background()
        self._layout()
        for button in self.buttons:
            button.draw(self.screen, self.font)
        self._draw_extra()
        pygame.display.flip()

    def _draw_extra(self) -> None:
        """Dessin par-dessus les boutons (titre...). Vide par defaut,
        surchargeable (ex: le titre du menu principal)."""


class ChaseParade:
    """Animation d'attract : Pac-Man poursuivi par les fantomes vers la gauche.

    Charge toutes les frames de chaque GIF anime (via Pillow) une seule
    fois, defile de droite a gauche en boucle, et cycle les frames pour
    animer (waka-waka de Pac-Man, dandinement des fantomes).
    """

    ORDER = ["Pac-Man", "Blinky", "Pinky", "Inky", "Clyde"]  # Pac-Man devant
    SIZE_RATIO = 0.03     # hauteur d'un sprite en % de la hauteur de fenetre
    SPEED_RATIO = 0.003   # deplacement/frame en % de la largeur de fenetre
    GAP = 1.8             # espacement entre sprites (x largeur d'un sprite)
    FRAME_MS = 120        # duree d'affichage d'une frame d'animation (ms)

    def __init__(self) -> None:
        # frames a taille native, chargees une seule fois
        self._raw = [self._load_frames(name) for name in self.ORDER]
        # versions redimensionnees selon la fenetre (remplies au 1er draw)
        self.animations: list[list[pygame.Surface]] = self._raw
        self._scaled_h = 0    # hauteur de fenetre pour laquelle scale est fait
        self.x = 0.0
        self._started = False

    def _load_frames(self, name: str) -> list[pygame.Surface]:
        """Extrait les frames d'un GIF anime, taille native, avec alpha."""
        filename = f"Arcade - Pac-Man - General Sprites - {name} (Left).gif"
        gif = Image.open(SPRITE_DIR / filename)
        frames: list[pygame.Surface] = []
        for i in range(getattr(gif, "n_frames", 1)):
            gif.seek(i)
            rgba = gif.convert("RGBA")   # PIL gere la transparence -> alpha
            surf = pygame.image.frombytes(
                rgba.tobytes(), rgba.size, "RGBA").convert_alpha()
            frames.append(surf)
        return frames

    def _rescale(self, h: int) -> None:
        """Redimensionne les sprites si la hauteur de fenetre a change."""
        if h == self._scaled_h:
            return
        self._scaled_h = h
        target = max(1, int(h * self.SIZE_RATIO))   # hauteur cible d'un sprite
        self.animations = []
        for frames in self._raw:
            factor = target / frames[0].get_height()
            self.animations.append([
                pygame.transform.scale(
                    f, (int(f.get_width() * factor), target))
                for f in frames
            ])

    def draw(self, screen: pygame.Surface, y: int) -> None:
        """Redimensionne au besoin, avance la parade, cycle les frames."""
        w, h = screen.get_size()
        self._rescale(h)

        step = int(self.animations[0][0].get_width() * self.GAP)
        group_w = step * len(self.animations)
        if not self._started or self.x + group_w < 0:
            self.x = float(w)     # (re)part du bord droit
            self._started = True

        now = pygame.time.get_ticks()
        x = self.x
        for frames in self.animations:
            i = (now // self.FRAME_MS) % len(frames)   # frame courante
            screen.blit(frames[i], (int(x), y))
            x += step
        self.x -= self.SPEED_RATIO * w    # vitesse proportionnelle a w


class Menu(ButtonMenu):
    """Menu principal : titre PAC-MAN (gros) + boutons (plus petits)."""

    FONT_RATIO = 0.045       # boutons plus petits que le titre
    TITLE = "PAC-MAN"
    TITLE_RATIO = 0.16       # titre bien plus gros que les boutons
    TITLE_COLOR = "yellow"   # couleur Pac-Man
    OUTLINE_COLOR = "gold"   # contour doré, tres leger
    OUTLINE_RATIO = 0.03     # epaisseur du contour en % de la taille du titre
    TITLE_Y = 0.16           # centre vertical du titre (% de la hauteur)
    PARADE_Y = 0.30          # haut des sprites de la parade (% de la hauteur)
    TOP_MARGIN = 0.42        # place reservee en haut (titre + parade)

    def __init__(self) -> None:
        super().__init__([
            Button("Start Game", "start"),
            Button("Highscores", "highscores"),
            Button("Instructions", "instructions"),
            Button("Exit", "quit"),
        ])
        self.title_font = pygame.font.Font(None, 48)
        self._title_h = 0    # hauteur pour laquelle title_font existe
        self.parade = ChaseParade()

    def _region(self) -> pygame.Rect:
        """Les boutons occupent la zone SOUS le titre (partie basse)."""
        r = self.screen.get_rect()
        top = int(r.height * self.TOP_MARGIN)
        return pygame.Rect(0, top, r.width, r.height - top)

    def _draw_extra(self) -> None:
        """Dessine le titre PAC-MAN, avec un contour dore tres leger."""
        w, h = self.screen.get_size()
        if h != self._title_h:       # police du titre recreee au resize
            self.title_font = pygame.font.Font(None, int(h * self.TITLE_RATIO))
            self._title_h = h

        center = (w / 2, h * self.TITLE_Y)
        # contour : le titre en dore, decale de quelques px dans 4 directions
        outline = self.title_font.render(self.TITLE, True, self.OUTLINE_COLOR)
        off = max(1, int(h * self.TITLE_RATIO * self.OUTLINE_RATIO))
        for dx, dy in ((-off, 0), (off, 0), (0, -off), (0, off)):
            rect = outline.get_rect(center=(center[0] + dx, center[1] + dy))
            self.screen.blit(outline, rect)
        # le titre jaune par-dessus
        title = self.title_font.render(self.TITLE, True, self.TITLE_COLOR)
        self.screen.blit(title, title.get_rect(center=center))
        # la parade de sprites defile sous le titre
        self.parade.draw(self.screen, int(h * self.PARADE_Y))
