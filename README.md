*This project has been created as part
of the 42 curriculum by bokim, evarache.*

# Description

This project is a complete and playable Pac-Man, inspired by the real and historical arcade game.

The player moves through a procedurally generated maze, eating every Pacgum to clear the level while avoiding the ghosts that roam the corridors. Super Pacgums temporarily turn the tables, letting Pac-Man eat the ghosts for bonus points. The game features multiple levels, a lives and timer system, a persistent highscore board, three swappable visual themes (`pacman`, `stardew_valley`, `minecraft`) and a fully configurable ruleset loaded from a JSON file.

It is written in Python using the [Arcade](https://api.arcade.academy/) game engine, with maze layouts produced by the school's `mazegenerator` package.

# Instructions

Requirements:
- Python **3.10+**
- [`uv`](https://docs.astral.sh/uv/) for dependency management
- The `mazegenerator` wheel (see [Maze generation](#maze-generation for more explanations))

Install the dependencies and run the game with the Makefile:

```sh
make install   # uv sync — creates the virtual environment and installs deps
make run       # launches the game with config.json
```

Other useful targets:

| Target             | Description                                            |
| ------------------ | ----------------------------------------------------- |
| `make debug`       | Run the game under the `pdb` debugger                 |
| `make lint`        | Run `flake8` and `mypy`                               |
| `make lint-strict` | Run `flake8` and `mypy --strict`                      |
| `make clean`       | Remove `__pycache__`, `.pyc` files and the mypy cache |
| `make fclean`      | `clean` + remove `uv.lock` and the `.venv`            |

You can also run it directly : `uv run python3 pac-man.py config.json`.

## Configuration

The game reads all its settings from a JSON config file passed as the only command-line argument. Every field is validated at load time. If a field is missing, out of range or invalid, a warning is printed and the field falls back to its default value below (the game never crashes on a malformed config).

| Field                     | Description                | Constraints                             | Default            |
| ------------------------- | -------------------------- | --------------------------------------- | ------------------ |
| `highscore_filename`      | File where highscores live | must end in `.json`                     | `highscore.json`   |
| `level`                   | Number of levels to play   | 1–20                                    | 10                 |
| `width` / `height`        | Maze dimensions            | 10–30                                   | 15                 |
| `lives`                   | Starting number of lives   | 1–10                                    | 3                  |
| `points_per_pacgum`       | Points for a Pacgum        | 1–250                                   | 10                 |
| `points_per_super_pacgum` | Points for a Super Pacgum  | 1–500                                   | 50                 |
| `points_per_ghost`        | Points for eating a ghost  | 1–1000                                  | 200                |
| `seed`                    | Seed for maze generation   | positive integer                        | 42                 |
| `level_max_time`          | Time limit per level (s)   | ≤ 150                                   | 90                 |
| `theme`                   | Visual theme               | `pacman`, `stardew_valley`, `minecraft` | `pacman`           |

Point values must also respect the hierarchy `pacgum * 2 ≤ super_pacgum` and `super_pacgum * 2 ≤ ghost`. If they don't, the three point values are reset to their defaults (`10` / `50` / `200`). If the whole config file is missing or corrupted, all settings fall back to their defaults.

## Controls

| Key        | Action                                   |
| ---------- | ---------------------------------------- |
| `SPACE`    | Start the game (from the menu)           |
| Arrow keys | Move Pac-Man (hold to keep moving)       |
| `P`        | Pause / resume                           |
| `ESCAPE`   | Quit the game                            |

### Cheat mode

| Key        | Action                                   |
| ---------- | ---------------------------------------- |
| `C`        | Start cheat mode                        |
| `G`        | Freeze the ghosts (cheat mode only)      |
| `N`        | Skip to the next level (cheat mode only) |

### Rules

Eat all the Pacgums in the limit time to win the level.
If a ghost catches you, you lose a life, respawn after 3 seconds, and you have 3 seconds of invincibility. 
If you eat a super-pacgum, you are invincible and able to eat the ghosts for a short time (fixed on 8 seconds). If you eat a ghost, he will respawn at his corner after 5 seconds.
Game Over when you run out of lives or time.
If you complete the level, you move on to the next level.
When all the levels are completed, you win the game.  

You can save your score and enter your name even if you don´t finish the game.

# Maze generation

Download the .whl from the intranet page of the project and put it on the root of the repository, rename it `mazegenerator-2.0.2-py3-none-any.whl`.
Then you can use the Makefile to run the program.

The `MazeGenerator`, is invoked with the configured `width`, `height` and `seed` to build a non-perfect maze (with loops) at the start of each game, so a given seed always produces the same maze. For the first level, the maze is always generated with the seed given in the configuration file. For all others levels, the seed used is random.


# Highscore

Highscores are persisted between games in the JSON file named by `highscore_filename` in the config (defaults to `highscore.json`). Each entry holds a player name (alphanumeric and spaces, max 10 characters) and a score. When a game ends, the player types a name — left empty, it is saved as `Anonymous` — and the score is added to the board. The list is sorted from highest to lowest and only the **10 highscores** are kept; the rest are dropped. This leaderboard is loaded and displayed on the main menu.

# Implementation

The game is built on the [Arcade](https://api.arcade.academy/) engine and structured as a set of *Views*, one per screen (menu, gameplay, pause, level transition, win, lose).  
The active view drives the game loop: `on_update()` advances the state each frame while `on_draw()` renders it, and keyboard input is handled in `on_key_press` / `on_key_release`.

The maze is modeled as a grid of `Cell` objects. Each cell stores its walls as a 4-bit bitmask (top / right / bottom / left) and flags for what sits on it (Pacgum, Super Pacgum, player, ghost).

Ghost behaviour is a small state machine evaluated every tick in `move_ghosts()`:
- **Chase** — the ghost closest to the player runs a **BFS** shortest-path search and takes one step toward Pac-Man.
- **Wander** — the other ghosts move randomly to a free neighbour, avoiding their last few cells so they don't oscillate.
- **Flee** — while the player is in super mode (after eating a Super Pacgum), every ghost runs away toward the cell farthest from the player and can be eaten for points.
- **Respawn** — an eaten ghost disappears and comes back at its spawn after a fixed delay.

Eating a Super Pacgum flips the player into super mode; cheat mode makes the player invincible and able to cross walls, and can freeze the ghosts or skip levels. Visuals are theme-driven: an `Assets` helper resolves sprite paths from the `theme` field so the same code renders any of the three themes. Configuration is parsed and validated up front with [Pydantic](https://docs.pydantic.dev/) models, guaranteeing the rest of the game always receives sane values.

# General Software Architecture

The code is organized into three packages under `src/`, each with a clear responsibility, plus a thin entry point:

```
src/
├── parsing/            # Config loading & validation
│   └── parser.py       # Config (Pydantic model) + load_config()
|
├── objects/            # Game state & rules
│   ├── maze.py         # Maze, Cell
│   ├── player.py       # Player
│   ├── ghost.py        # Ghost + move_ghosts()
│   ├── score.py        # Score, InputName
│   └── assets.py       # Assets (theme → sprite paths & palette)
|
├── visualization/      # Arcade Views (rendering + input)
|   |
│   ├── menu_view.py, game_view.py, pause_view.py,
│   |   transition_view.py, win_view.py, lose_view.py
|   |
│   └── scaler.py       # ui_scale() responsive helper
|
└── resources/          # Theme assets (pacman / stardew_valley / minecraft)
```


The three packages form a one-way dependency chain: `visualization` depends on `objects`, and `objects` depends on `parsing`. Nothing flows back the other way, which keeps the game rules independent from how they are drawn.

- **`parsing`** turns the raw JSON file into a validated `Config` object. Every other module receives this `Config` and trusts its values, so validation lives in exactly one place.

- **`objects`** holds the game state and all the rules, independent of Arcade's rendering. `Maze` owns the grid of `Cell` objects and places the `Player` and the four `Ghost`s on it; each `Cell` carries its wall bitmask and what occupies it. `Player` and `Ghost` query the maze to move, `move_ghosts()` drives the ghost AI, `Score` handles points and highscore persistence, and `Assets` maps the configured theme to sprite paths and a colour palette.

- **`visualization`** contains the Arcade `View` classes, one per screen, that render the state and handle input. `GameView` is the hub: it owns the `Maze`, `Player`, `Ghost`s and `Score`, runs the per-frame loop, and hands control to `PauseView`, `TransitionView`, `WinView` or `LoseView` as the game progresses. `MenuView` is the entry screen that builds the maze and launches a `GameView`.


# Project Management

The project was driven with a structured approach: a Trello Kanban board for
day-to-day tracking, Git feature branches with peer review, and a continuous
lint gate (`flake8` + `mypy`). All the supporting documents — project analysis,
timeline & Gantt, progress tracking, risk analysis, team organization,
acceptance test plan and retrospective — are in the
[`project_management/`](project_management/) directory.

# Ressources

Arcade : https://api.arcade.academy/en/stable/  
Geeksforgeeks : https://www.geeksforgeeks.org/python/arcade-library-in-python/


AI was used to better understand the functioning of the arcade module.