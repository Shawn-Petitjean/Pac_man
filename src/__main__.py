import sys

import pygame

from src.parsing import build_config
from src.menu import Menu
from src.screen import Instructions, HighscoresScreen
from src.highscore import Highscores
from src.game import Game
from src.config import Cheat, SEED


def main() -> None:
    """Point d'entree : charge la config, puis pilote le flot des ecrans."""
    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py <config.json>", file=sys.stderr)
        return

    # try:
    config_path = sys.argv[1]
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
        print(result)
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
            if game.run() == "quit":
                running = False
            score = game.pacman.score
    # except Exception as e:
    #     print(f"An error occurred '{e.__class__.__name__}'\n'{e}'")
    # finally:
    #     pygame.quit()


if __name__ == "__main__":
    main()
