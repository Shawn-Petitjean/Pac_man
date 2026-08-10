# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller build specification for the Pac-Man game.

Build a self-contained package with:

    pyinstaller pacman.spec --noconfirm

The result lands in ``dist/pacman/`` (a folder to zip and upload), and
additionally as ``dist/Pac-Man.app`` on macOS. PyInstaller builds for the
host operating system, so run this on the platform you want to target.
"""
import sys

from PyInstaller.utils.hooks import collect_all

# Game assets and the default configuration, shipped next to the code.
datas = [
    ("sprites", "sprites"),
    ("config.json", "."),
]

# The maze generator ships as a wheel; pull in all of its files.
mg_datas, mg_binaries, mg_hiddenimports = collect_all("mazegenerator")

a = Analysis(
    ["pacman.py"],
    pathex=[],
    binaries=mg_binaries,
    datas=datas + mg_datas,
    hiddenimports=mg_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="pacman",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="pacman",
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="Pac-Man.app",
        icon=None,
        bundle_identifier="com.42.pacman",
    )
