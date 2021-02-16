# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(["..\\mathinspector\\_run.py"],
             pathex=[os.path.abspath("..")],
             binaries=[],
             datas=[("..\\mathinspector\\assets", ".\\assets\\")],
             hiddenimports=["scipy.spatial.transform._rotation_groups", "scipy.special.cython_special"],
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
          name="MathInspector",
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon="..\\mathinspector\\assets\\logo_2.ico")

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name="MathInspector")
