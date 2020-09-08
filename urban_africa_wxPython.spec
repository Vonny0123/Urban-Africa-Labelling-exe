# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import os
from PyInstaller.utils.hooks import collect_data_files # this is very helpful

paths = [
	'C:\\Users\\ewand\\.spyder-py3\\Urban_Africa'
]

binaries = []

hidden_imports = [
	'pyproj.datadir', 
	'pyproj._datadir',
	'fiona._shim', 
	'fiona.schema'
]

runtime_hooks=['hook.py']

a = Analysis(['urban_africa_wxPython.py'],
             pathex=paths,
             binaries=binaries,
             datas=collect_data_files('geopandas', subdir='datasets'),
             hiddenimports=hidden_imports,
             hookspath=[],
             runtime_hooks=runtime_hooks,
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Urban Africa Labelling',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Urban Africa Labelling')
