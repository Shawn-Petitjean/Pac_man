from src.parsing import build_config
from src.menu import Menu
import pygame
import sys


def main() -> None:
    """it only serve the purpose of running the CLI."""
    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py <config.json>", file=sys.stderr)
        return

    try:
        config_path = sys.argv[1]
        config = build_config(config_path)
        menu = Menu()
        running = True

        pygame.init()
        screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)

        while running:
            result = menu.run(screen)
            if result == "quit":
                running = False

    except Exception as e:
        print(f"an error occurred {e.__class__.__name__}\n{e}")
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
