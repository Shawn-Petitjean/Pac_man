from .game import Game


def main() -> None:
    """it only serve the purpose of running the CLI."""
    try:
        game = Game((30, 30), (1600, 1500))
        game.run()
    except Exception as e:
        print(f"an error occurred {e.__class__.__name__}\n{e}")


if __name__ == "__main__":
    main()
