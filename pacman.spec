import os
import shutil

from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all("pyglet")

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

_version = os.path.join(DISTPATH, "pacman", "_internal", "arcade", "VERSION")
if os.path.isdir(_version):
    _staged = _version + ".staged"
    shutil.move(os.path.join(_version, "VERSION"), _staged)
    shutil.rmtree(_version)
    shutil.move(_staged, _version)
