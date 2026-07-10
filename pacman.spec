# pacman.spec -- PyInstaller build spec (onedir, Linux).
#
# Build with:  make package    (or: pyinstaller --noconfirm --clean pacman.spec)
#
# Produces dist/pacman/ holding the `pacman` executable next to an
# `_internal/` folder with the bundled game data. The build target then copies
# config.json and INSTRUCTIONS.txt beside the executable, so the player can
# read the controls and tune the game without rebuilding it.

import os
import shutil

from PyInstaller.utils.hooks import collect_all

# Only pyglet needs collecting by hand. Do NOT collect_all("arcade"): arcade
# ships its own PyInstaller hook (entry point `pyinstaller40`) which is picked
# up automatically, and which already covers its resources, pymunk's chipmunk
# library and the OpenGL backend hiddenimports. Collecting arcade on top of it
# makes both fight over `arcade/VERSION` -- the hook maps it to a directory,
# collect_all to a file -- and the build dies in COLLECT. PIL and numpy have
# hooks bundled with PyInstaller; mazegenerator is pure Python and is followed
# from the import graph.
datas, binaries, hiddenimports = collect_all("pyglet")

# Game data. The destination of src/resources must mirror Assets.RESOURCES:
# Assets.texture() resolves that same relative path against sys._MEIPASS.
datas += [
    ("src/resources", "src/resources"),
    ("config.json", "."),      # fallback when no config sits next to the exe
]

a = Analysis(
    ["pac-man.py"],
    pathex=["."],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,   # onedir: binaries are gathered by COLLECT below
    name="pacman",
    console=True,            # no extra window on Linux; keeps warnings visible
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name="pacman",
)

# arcade's own hook maps its VERSION *file* to a destination PyInstaller then
# treats as a directory, so the bundle gets `arcade/VERSION/VERSION`. At
# startup arcade reads `arcade/VERSION` as a file, fails with "Is a directory",
# and falls back to reporting version 0.0.0. Flatten it back into a file.
_version = os.path.join(DISTPATH, "pacman", "_internal", "arcade", "VERSION")
if os.path.isdir(_version):
    _staged = _version + ".staged"
    shutil.move(os.path.join(_version, "VERSION"), _staged)
    shutil.rmtree(_version)
    shutil.move(_staged, _version)
