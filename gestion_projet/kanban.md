# Kanban — Pac-Man

Suivi des tâches du projet (chapitre VIII — gestion de projet).

**Légende des propriétaires** : `[G]` = Guillaume · `[S]` = Shawn · `[G+S]` = à deux.

---

## 🔴 À faire

| Tâche | Qui | Note |
|---|---|---|
| README (Config, Highscore, Architecture, Maze, gestion projet) | G | ch. IX |
| Menu pause (`ButtonMenu` par-dessus le jeu, région réduite) | G | dépend du moteur |
| Touches de cheat (invincibilité, skip niveau, freeze, vies, vitesse) | G | dépend des flags moteur |
| IA des fantômes (chase / flee / respawn) | S | |
| Collisions (joueur / murs / fantômes) | S | |
| Scoring temps réel (pacgum, super-pacgum, fantôme) | S | |
| HUD in-game (score / vies / niveau / temps) | S | |
| Progression des niveaux + timer + win/lose | S | |
| Définir le `CheatState` partagé (flags moteur ↔ touches) | G+S | coordination |
| Packaging Itch.io + déploiement | G+S | |

## 🟡 En cours

| Tâche | Qui | Note |
|---|---|---|
| Docs de gestion de projet (ce Kanban + autres) | G | |
| Intégration A-Maze-ing (génération + rendu du labyrinthe) | S | *à confirmer* |
| Déplacement du joueur | S | *à confirmer* |
| Refacto `Game` vers le contrat "fenêtre partagée" | S | reçoit `screen`, `run()` retourne |

## ⏸️ Bloqué / en attente d'intégration

| Tâche | Qui | Débloqué par |
|---|---|---|
| Brancher "Start Game" au vrai jeu (placeholder `EndScreen` actuel) | G | moteur prêt |
| `EndScreen` avec le vrai score + titre win/lose | G | score final du moteur |

## 🟢 Fait

| Tâche | Qui |
|---|---|
| Parsing config (JSON + commentaires, validation, clamp, robuste) | G |
| Orchestration `main` + fenêtre pygame unique partagée | G |
| Menu principal (navigation clavier/souris, boutons responsive) | G |
| Architecture d'écrans (`Screen` / `ButtonMenu` / `TextScreen`) | G |
| Écran Instructions | G |
| Système de highscore (persistance JSON, top 10, validation, robuste) | G |
| Écran Highscores (affichage du top 10) | G |
| Écrans Game Over / Victory + saisie du nom | G |
| Habillage menu : titre PAC-MAN + parade de sprites animés (responsive) | G |
| Contrat d'intégration défini (fenêtre partagée, `run(screen)` → résultat) | G+S |

---

## À compléter (le reste du chapitre VIII)

Le sujet demande aussi, dans ce dossier :
- **Organisation de l'équipe** : qui a fait quoi, comment les décisions ont été prises.
- **Analyse de risques** + mitigations (ex. : moteur pas prêt → parties autonomes d'abord).
- **Plan de test d'acceptation** : features testées, bugs trouvés/corrigés.
- **Points bloquants / conflits** rencontrés (ex. : conflit des deux fenêtres pygame,
  résolu par la fenêtre partagée).
