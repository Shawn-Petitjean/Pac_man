import json
from typing import Any

from src.config import GameConfig, LevelConfig, get_int, get_str
from src.config import read_config_file, strip_comments


def parse_config(text: str) -> dict[str, Any]:
    """Parse comment-free JSON text into a dictionary.

    Empty content (or comments only) yields an empty dict, so the
    configuration still loads with every default value.
    """
    if not text.strip():
        return {}
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("the config file must contain a JSON object")
    return data


def build_config(config_path: str) -> GameConfig:
    """Read, parse and validate a config file into a safe GameConfig."""
    text = read_config_file(config_path)
    text = strip_comments(text)
    data = parse_config(text)

    highscore_filename = get_str(data, "highscore_filename",
                                 "highscores.json")
    lives = get_int(data, "lives", 3, minimum=1)
    size_data = data.get("size", {})
    if not isinstance(size_data, dict):
        size_data = {}
    width = get_int(size_data, "width", 20, minimum=15)
    height = get_int(size_data, "height", 20, minimum=15)
    level_max_time = get_int(data, "level_max_time", 90, minimum=1)
    points_per_pacgum = get_int(data, "points_per_pacgum", 10, minimum=0)
    points_per_super_pacgum = get_int(
        data, "points_per_super_pacgum", 50, minimum=0)
    points_per_ghost = get_int(data, "points_per_ghost", 200, minimum=0)
    seed = get_int(data, "seed", 42, minimum=1)

    return GameConfig(
        highscore_filename=highscore_filename,
        size=LevelConfig(width=width, height=height),
        seed=seed,
        level_max_time=level_max_time,
        lives=lives,
        points_per_pacgum=points_per_pacgum,
        points_per_super_pacgum=points_per_super_pacgum,
        points_per_ghost=points_per_ghost,
    )
