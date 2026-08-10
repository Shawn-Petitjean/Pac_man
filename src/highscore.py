"""Persistent highscore system.

Loads the top 10 at startup and saves them at the end of a game.
"""

import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

MAX_ENTRIES = 10
MAX_NAME_LEN = 10


def highscore_dir() -> Path:
    """Return a writable directory for the highscore file.

    In a PyInstaller build the sources live in a read-only bundle, so the
    scores are stored under the user's home directory instead of next to
    the code.
    """
    if getattr(sys, "frozen", False):
        directory = Path.home() / ".pacman"
        directory.mkdir(parents=True, exist_ok=True)
        return directory
    return Path(__file__).resolve().parent.parent


@dataclass
class HighscoreEntry:
    """A single highscore entry: a name and a score."""

    name: str
    score: int


class Highscores:
    """Manage the persistent list of best scores.

    Responsibilities: load/save to a JSON file, keep the MAX_ENTRIES best
    sorted by descending score, validate names (<= MAX_NAME_LEN,
    alphanumeric and spaces) and scores (non-negative integers), and stay
    robust: a missing or corrupted file yields an empty list without ever
    raising.
    """

    def __init__(self, filename: str) -> None:
        """Prepare the manager for a given file (does not load yet)."""
        self.path = highscore_dir() / filename
        self._entries: list[HighscoreEntry] = []

    def load(self) -> None:
        """Load entries from the file.

        A missing, unreadable or invalid-JSON file starts from an empty
        list without raising.
        """
        self._entries = []
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return
        if not isinstance(data, list):
            return
        for item in data:
            if isinstance(item, dict):
                name = item.get("name")
                score = item.get("score")
                if isinstance(name, str) and isinstance(score, int):
                    self.add(name, score)

    def save(self) -> None:
        """Write the current entries to the JSON file."""
        data = [asdict(e) for e in self.entries()]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def add(self, name: str, score: int) -> None:
        """Add a score: clean the name, clamp the score, store the entry."""
        name = self.clean_name(name)
        if score <= 0:
            self._entries.append(HighscoreEntry(name, 0))
        else:
            self._entries.append(HighscoreEntry(name, score))

    def entries(self) -> list[HighscoreEntry]:
        """Return the entries sorted with the best score first."""
        res = sorted(self._entries,
                     key=lambda e: e.score, reverse=True)
        return res[:MAX_ENTRIES]

    @staticmethod
    def clean_name(name: str) -> str:
        """Reduce a name to <= MAX_NAME_LEN alphanumeric-or-space chars."""
        kept = [c for c in name if c.isalnum() or c == " "]
        return "".join(kept)[:MAX_NAME_LEN]
