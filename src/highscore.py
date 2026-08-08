"""Systeme de highscore persistant

Charge le top 10 au demarrage, save en fin de partie.
"""

from dataclasses import dataclass, asdict
from pathlib import Path
import json

# src/highscore.py -> src -> racine du projet
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MAX_ENTRIES = 10        # on garde le top 10
MAX_NAME_LEN = 10       # noms <= 10 caracteres (sujet)


@dataclass
class HighscoreEntry:
    """Une entree de highscore : un nom et un score."""

    name: str
    score: int


class Highscores:
    """Gere la liste persistante des meilleurs scores.

    Responsabilites :
      - charger / sauver dans un fichier JSON ;
      - garder les MAX_ENTRIES meilleurs, tries par score decroissant ;
      - valider les noms (<= MAX_NAME_LEN, alphanumerique + espaces) ;
      - valider les scores (entiers >= 0) ;
      - rester robuste : fichier manquant ou corrompu -> liste vide,
        jamais d'exception qui remonte.
    """

    def __init__(self, filename: str) -> None:
        """Prepare le gestionnaire pour un fichier donne (ne charge pas)."""
        self.path = PROJECT_ROOT / filename
        self._entries: list[HighscoreEntry] = []

    def load(self) -> None:
        """Charge les entrees depuis le fichier.

        Fichier absent, illisible ou JSON invalide -> on repart d'une
        liste vide sans lever d'exception.
        """
        self._entries = []
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return                          # absent ou corrompu -> liste vide
        if not isinstance(data, list):
            return
        for item in data:
            if isinstance(item, dict):
                name = item.get("name")
                score = item.get("score")
                if isinstance(name, str) and isinstance(score, int):
                    self.add(name, score)

    def save(self) -> None:
        """Ecrit les entrees courantes dans le fichier JSON."""
        data = [asdict(e) for e in self.entries()]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def add(self, name: str, score: int) -> None:
        """Ajoute un score : nettoie le nom, valide le score, garde le top."""
        name = self.clean_name(name)
        if score <= 0:
            self._entries.append(HighscoreEntry(name, 0))
        else:
            self._entries.append(HighscoreEntry(name, score))

    def entries(self) -> list[HighscoreEntry]:
        """Renvoie les entrees triees, meilleur score en premier."""
        res = sorted(self._entries,
                     key=lambda e: e.score, reverse=True)
        return res[:MAX_ENTRIES]

    @staticmethod
    def clean_name(name: str) -> str:
        """Reduit un nom a <= MAX_NAME_LEN caracteres alphanum + espaces."""
        kept = [c for c in name if c.isalnum() or c == " "]
        return "".join(kept)[:MAX_NAME_LEN]
