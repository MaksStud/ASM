# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_dynamic_libs, collect_submodules

unicorn_binaries = collect_dynamic_libs('unicorn')
keystone_binaries = collect_dynamic_libs('keystone')

unicorn_imports = collect_submodules('unicorn')
keystone_imports = collect_submodules('keystone')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=unicorn_binaries + keystone_binaries,
    hiddenimports=unicorn_imports + keystone_imports,
    # Додаємо qss файл у збірку
    datas=[('1658763190886.png', '.'), ('style.qss', '.')],
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
    name='ASM runner',
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
    icon='1658763190886.png',
)