"""Filesystem paths that stay correct once the game is frozen by PyInstaller.

Two kinds of paths, and they must not be confused:

- Read-only game data (textures, the default config) ships *inside* the
  bundle. PyInstaller extracts it to ``sys._MEIPASS``, which is neither the
  working directory nor the folder holding the executable.
- Files the player owns (their config, their highscores) must be editable and
  must survive across runs, so they live *next to the executable*.

During development both resolve to the project root.
"""
import os
import sys


def is_frozen() -> bool:
    """Return True when running from a PyInstaller bundle."""
    return getattr(sys, "frozen", False)


def _project_root() -> str:
    """Return the repository root, i.e. the parent of the `src` package."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def bundle_path(*parts: str) -> str:
    """Build the path to a read-only resource shipped with the game.

    Relative paths would resolve against the working directory, which is
    wherever the player happened to launch the game from."""
    base = getattr(sys, "_MEIPASS", None) if is_frozen() else None
    return os.path.join(base or _project_root(), *parts)


def app_path(*parts: str) -> str:
    """Build the path to a file living next to the executable.

    The bundle directory is a temporary extraction folder, so anything the
    player edits or that must persist belongs here instead."""
    base = os.path.dirname(os.path.abspath(sys.executable)) if is_frozen() \
        else _project_root()
    return os.path.join(base, *parts)


def writable_path(filename: str) -> str:
    """Resolve a file the game writes to, such as the highscores.

    An absolute path from the config is honoured as-is; a bare name lands
    next to the executable rather than in the working directory."""
    if os.path.isabs(filename):
        return filename
    return app_path(filename)


def default_config_path(filename: str = "config.json") -> str:
    """Locate the config to load when none was given on the command line.

    The copy next to the executable wins, so a player can tune the game
    without rebuilding it; the bundled copy is the fallback."""
    beside_exe = app_path(filename)
    if os.path.exists(beside_exe):
        return beside_exe
    return bundle_path(filename)
