# 03 — Team Organization

We divided up the large parts into us but each of member worked on the differents parts.


## Roles of each member

| Area | Files | Owner |
| ---- | ----- | ----- |
| Config parsing & validation | `src/parsing/parser.py` | **bokim** |
| Maze & cells | `src/objects/maze.py` | **evarache** |
| Player logic | `src/objects/player.py` | **evarache** |
| Ghost AI | `src/objects/ghost.py` | **bokim** |
| Arcade views (menu/game/pause/win/lose/transition) | `src/visualization/*.py` | **evarache** |
| Theme system & assets | `src/objects/assets.py`, `src/resources/` | **bokim** |
| Score & highscore UI | `src/objects/score.py` | **evarache** |
| UI scaling | `src/visualization/scaler.py` | **bokim** |
| Shared: game loop integration | `src/visualization/game_view.py` | **evarache** |
| Tooling, Makefile, docs | `Makefile`, `README.md`, this folder | **bokim** |


## How we worked

- **Cards on Trello.** Every task was a Trello card.
  The card moved Backlog → To Do → Done.  
  The board was checked at the start of each working session. We also warned the other member on discord when we finished a task.

- **Git flow.** Work happened on short-lived feature branches, merged into
  `main` after a quick review. Commits follow a `type(scope): message`
  convention (e.g. `fix: fixed module path`).
