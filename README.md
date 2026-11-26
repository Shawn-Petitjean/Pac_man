*This project has been created by Guillaume-Lacolley and Shawn-Petitjean.*

# Pac-Man

A Pac-Man clone written in Python with [pygame-ce](https://pyga.me/), built
for the 42 curriculum. Animated menu, in-game pause, cheat toggles, a JSON
configuration loader (comments allowed, invalid values fall back to safe
defaults) and a persistent top-10 highscore table.

## Controls

| Action | Keys |
| --- | --- |
| Move | `W` `A` `S` `D` (or arrow keys) |
| Pause | `Escape` |
| Menus | Mouse or arrow keys, `Enter` to validate |

Eat every pac-gum to clear the level, avoid the ghosts, and grab a super
pac-gum to turn them edible for a while. The in-game **Instructions** screen
(from the main menu) shows the full controls and rules.

## Requirements

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) for environment and dependency management

## Install

```bash
make install
```

This creates a `.venv`, installs the dependencies and the bundled
`mazegenerator` wheel.

## Run from source

```bash
make run              # uses config.json
# or
uv run python -m src config.json
```

`config.json` is optional: launched without it, the game starts on defaults.

## Configuration

`config.json` supports `#` comments. Any missing or out-of-range value is
replaced by a safe default, so the game always starts.

| Key | Meaning |
| --- | --- |
| `highscore_filename` | highscore file name |
| `size.width` / `size.height` | maze dimensions |
| `seed` | maze generation seed |
| `level_max_time` | per-level time limit (seconds) |
| `lives` | starting lives |
| `points_per_pacgum` / `points_per_super_pacgum` / `points_per_ghost` | scoring |

Highscores persist to `~/.pacman/highscores.json` in a packaged build, or
next to the sources when run from source.

## Lint

```bash
make lint             # flake8 + mypy --strict
```

## Build the package

```bash
make package
```

PyInstaller (driven by [`pacman.spec`](pacman.spec)) produces a
self-contained build in `dist/`:

- `dist/pacman/` — a standalone folder (the cross-platform artifact). Zip it
  and upload it as-is.
- `dist/Pac-Man.app` — a macOS application bundle (ad-hoc signed; on first
  launch, right-click → **Open** to bypass the unidentified-developer prompt).

PyInstaller builds for the host OS only, so run `make package` on each
platform you want to target. The build bundles the sprites, the default
`config.json` and the `mazegenerator` dependency, so the package is fully
self-contained.

## Deploy to itch.io

1. `make package`
2. Zip the artifact:
   - cross-platform: `cd dist && zip -r pacman.zip pacman`
   - macOS app: `cd dist && ditto -c -k --keepParent Pac-Man.app Pac-Man.zip`
3. On itch.io, create a project, set the kind to **Downloadable**, upload the
   zip, tick the matching platform, and set the visibility to
   **unlisted/private** for a free build.
