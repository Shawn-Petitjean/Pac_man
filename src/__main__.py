import sys

import pygame

from src.parsing import build_config
from src.menu import Menu
from src.screen import Instructions


def main() -> None:
    """Point d'entree : charge la config, puis pilote le flot des ecrans."""
    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py <config.json>", file=sys.stderr)
        return

    try:
        config_path = sys.argv[1]
        build_config(config_path)      # valide la config au lancement
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
    except Exception as e:
        print(f"an error occurred {e.__class__.__name__}\n{e}")
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
