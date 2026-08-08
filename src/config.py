from dataclasses import dataclass, field
from typing import Any
import sys
import pygame

PAC_F = pygame.image.load("sprites/pac_man_f.png")
GHOST_R = "sprites/ghost/red_ghost.png"
W = 8
S = 4
E = 2
N = 1


@dataclass
class LevelConfig:
    width: int
    height: int


@dataclass
class GameConfig:
    highscore_filename: str = "highscore"
    size: LevelConfig = field(default_factory=lambda: LevelConfig(20, 20))
    seed: int = 1
    level_max_time: int = 90
    lives: int = 3
    points_per_pacgum: int = 50
    points_per_super_pacgum: int = 400
    points_per_ghost: int = 500


@dataclass
class Cheat:
    invincible: bool = False
    speed: bool = False
    next_level: bool = False


def read_config_file(path: str) -> str:
    """Read the raw text of the config file (comments included)."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def strip_comments(text: str) -> str:
    """Remove full-line '#' comments from the raw config text."""
    kept = []
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            continue
        kept.append(line)

    return "\n".join(kept)


# ********HELPER*********


def get_int(data: dict[str, Any], key: str,
            default: int, minimum: int) -> int:
    """Read an int field from `data`, clamping to `default` if the
    value is missing, not an int, or below `minimum`."""
    val = data.get(key)

    if not isinstance(val, int) or isinstance(val, bool) or val < minimum:
        print(f"Key: {key} invalid, return to default: {default}",
              file=sys.stderr)
        return default

    return val


def get_str(data: dict[str, Any], key: str, default: str) -> str:
    """Read a str field, clamping to `default` if missing or invalid."""
    val = data.get(key)

    if not isinstance(val, str) or not val:
        print(f"Key: {key} invalid, return to default: {default}",
              file=sys.stderr)
        return default

    return val
