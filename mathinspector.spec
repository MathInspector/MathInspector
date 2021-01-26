# -*- mode: python -*-

import os

block_cipher = None

added_files = [
  ('assets', 'assets')
]

a = Analysis(['mathinspector/__main__.py'],
             pathex=[os.path.join(os.path.abspath('.'), 'mathinspector')],
             binaries=[],
             hiddenimports=['pywt._extensions._cwt'],
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
          a.binaries,
          [],
          exclude_binaries=True,
          name='mathinspector',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='mathinspector')

app = BUNDLE(coll,
            name='mathinspector.app',
            icon='assets/icons_3.icns',
            bundle_identifier='com.math.inspector',
            info_plist={
              'CFBundleName': 'Math Inspector',
              'NSPrincipleClass': 'NSApplication',
              'NSAppleScriptEnabled': False,
              'NSHighResolutionCapable': 'True',
              'CFBundleDocumentTypes': [
                {
                    'CFBundleTypeName': 'MathInspector',
                    'CFBundleTypeIconFile': 'icons_3',
                    'LSItemContentTypes': ['com.math.inspector'],
                    'CFBundleTypeExtensions': ['math'],
                    'LSHandlerRank': 'Owner'
                    }
                ]                                
            }
)
