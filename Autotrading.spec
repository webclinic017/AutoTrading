# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['gui.py'],
             pathex=['D:\\Programming\\Algo Trading\\algo trading project', 'D:\\Programming\\Algo Trading\\algo trading project\\news_reactor', 'D:\\Programming\\Algo Trading\\algo trading project\\strategy', 'D:\\Programming\\Algo Trading\\algo trading project\\risk_management', 'D:\\Programming\\Algo Trading\\algo trading project'],
             binaries=[],
             datas=[],
             hiddenimports=['sklearn.utils._cython_blas', 'sklearn.neighbors.typedefs', 'sklearn.neighbors.quad_tree', 'sklearn.tree._utils', 'currency_converter.CurrencyConverter'],
             hookspath=[],
             runtime_hooks=[],
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
          name='Autotrading',
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
               name='Autotrading')
