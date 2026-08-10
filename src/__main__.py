import os
import sys

import pygame

from src.parsing import build_config
from src.menu import Menu
from src.screen import Instructions, HighscoresScreen, EndScreen
from src.highscore import Highscores
from src.game import Game
from src.config import Cheat, SEED


def _resource_root() -> None:
    """Anchor the working directory to the bundled assets when frozen.

    A PyInstaller build extracts its data (sprites, config) next to the
    executable; moving there lets the relative asset paths keep working.
    """
    base = getattr(sys, "_MEIPASS", None)
    if getattr(sys, "frozen", False) and base:
        os.chdir(base)


def main() -> None:
    """Entry point: load the config, then drive the flow of screens."""
    _resource_root()
    config_path = sys.argv[1] if len(sys.argv) >= 2 else "config.json"

    try:
        config = build_config(config_path)
        highscores = Highscores(config.highscore_filename)
        highscores.load()
        cheats = Cheat()
        pygame.init()
        screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
        menu = Menu()

        running = True
        while running:
            result = menu.run(screen)
            if result == "quit":
                running = False
            elif result == "instructions":
                if Instructions().run(screen) == "quit":
                    running = False
            elif result == "highscores":
                if HighscoresScreen(highscores).run(screen) == "quit":
                    running = False
            elif result == "start":
                size = (config.size.width, config.size.height)
                game = Game(screen, size, cheats, SEED, config)
                outcome = game.run()
                if outcome == "quit":
                    running = False
                elif outcome in ("won", "lost"):
                    end = EndScreen(highscores, game.score, outcome == "won")
                    if end.run(screen) == "quit":
                        running = False
    except Exception as e:
        print(f"An error occurred '{e.__class__.__name__}'\n'{e}'")
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
