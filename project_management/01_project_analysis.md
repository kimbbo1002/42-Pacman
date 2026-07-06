# 01 — Project Analysis

## Goal

Build a complete and playable Pac-Man in Python: a player navigates a
procedurally generated maze, eats all the Pacgums to clear a level while
avoiding ghosts, with lives, a timer, multiple levels, a persistent highscore
board and a fully configurable ruleset.

## Requirements stapes of implementation

| # | Requirement | Where it lives |
| - | ----------- | -------------- |
| R1 | Read and **validate** a JSON config, never crash on bad input | `src/parsing/parser.py` |
| R2 | Generate a maze from the provided `mazegenerator` wheel | `MenuView`, `Maze` |
| R3 | Player movement constrained by walls | `src/objects/player.py`, `Cell` wall bitmask |
| R4 | Ghosts that chase / wander / flee | `src/objects/ghost.py` |
| R5 | Pacgums, Super Pacgums and super mode | `Maze`, `Player` |
| R6 | Lives, per-level timer, multiple levels | `GameView` |
| R7 | Several screens (menu, pause, win, lose, transition) | `src/visualization/` |
| R8 | Score + persistent top-10 highscores | `src/objects/score.py` |
| R9 | cheat mode | `Player`, `GameView` |
| R10 | Swappable visual themes | `src/objects/assets.py`, `src/resources/` |

## Technical choices & justification

| Decision | Alternatives considered | Why we chose it |
| -------- | ----------------------- | --------------- |
| **Arcade** game engine | Pygame | Higher-level `View`/sprite API, clean event loop, good docs — lets us focus on game logic. |
| **Pydantic** for config | Manual `if` checks | Declarative validation + defaults in one model;  turns a fragile config into a guaranteed-valid object for the rest of the code. |
| **Cell wall bitmask** (4 bits) | Adjacency lists, wall objects | Compact, and both player and ghost movement reduce to a single bit test; matches the maze generator output. |
| **BFS for ghost chase** | A*, greedy distance | Maze is small (≤ 30×30); BFS is simple, always finds the shortest path, and is fast enough per frame. |
| **Theme = folder + palette** | Hard-coded sprites | Adding a theme is dropping a folder + one palette entry; no logic change. |
| **`uv`** for dependencies | pip + venv, poetry | Fast, reproducible lockfile. |
