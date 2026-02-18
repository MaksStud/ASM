# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_dynamic_libs, collect_submodules

# 1. Збираємо динамічні бібліотеки (.dll)
unicorn_binaries = collect_dynamic_libs('unicorn')
keystone_binaries = collect_dynamic_libs('keystone')

# 2. Збираємо приховані імпорти (всі архітектурні підмодулі)
unicorn_imports = collect_submodules('unicorn')
keystone_imports = collect_submodules('keystone')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=unicorn_binaries + keystone_binaries,
    # Додаємо зібрані підмодулі сюди:
    hiddenimports=unicorn_imports + keystone_imports,
    datas=[('1658763190886.png', '.')],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['1658763190886.png'],
)