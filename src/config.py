from dataclasses import dataclass, field
from typing import Any
import sys


@dataclass
class LevelConfig:
    width: int
    height: int


@dataclass
class GameConfig:
    highscore_filename: str = "highscore"
    levels: list[LevelConfig] = field(default_factory=list)
    seed: int = 1
    level_max_time: int = 90
    lives: int = 3
    points_per_pacgum: int = 50
    points_per_super_pacgum: int = 400
    points_per_ghost: int = 500


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


def get_levels(data: dict[str, Any]) -> list[LevelConfig]:
    """Read and validate the 'levels' list into LevelConfig objects."""
    levels = data.get("levels")

    if not isinstance(levels, list) or not levels:
        print("levels invalid, return to default: width = 20, height = 20",
              file=sys.stderr)
        return [LevelConfig(width=20, height=20) for _ in range(20)]

    res: list[LevelConfig] = []
    for lst in levels:
        if not isinstance(lst, dict):
            continue

        width = get_int(lst, "width", 20, 10)
        height = get_int(lst, "height", 20, 10)

        res.append(LevelConfig(width=width, height=height))

    return res
