# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['youtube_downloader\\main.py'],
    pathex=['youtube_downloader'],
    binaries=[
        ('installer_build\\ffmpeg\\bin\\ffmpeg.exe', '.'),
        ('installer_build\\ffmpeg\\bin\\ffprobe.exe', '.'),
    ],
    datas=[
        ('youtube_downloader\\app\\resource', 'app\\resource'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'qfluentwidgets',
        'yt_dlp',
        'ffmpeg',
        'darkdetect',
        'colorthief',
        'scipy',
        'PIL',
        'app',
        'app.common',
        'app.common.config',
        'app.common.logger',
        'app.common.utils',
        'app.components',
        'app.components.download_worker',
        'app.components.playlist_worker',
        'app.components.concurrent_playlist_worker',
        'app.view',
        'app.view.main_window',
        'app.view.single_download_interface',
        'app.view.playlist_interface',
        'app.view.history_interface',
        'app.view.settings_interface',
        'app.view.about_interface',
        'app.resource',
        'app.resource.resource',
    ],
    excludes=[
        # Heavy ML/Data Science libraries
        'torch', 'tensorflow', 'matplotlib', 'numpy', 'pandas',
        # Unused Qt modules (can save 50-100MB)
        'PySide6.Qt3DAnimation', 'PySide6.Qt3DCore', 'PySide6.Qt3DExtras',
        'PySide6.Qt3DInput', 'PySide6.Qt3DLogic', 'PySide6.Qt3DRender',
        'PySide6.QtBluetooth', 'PySide6.QtCharts', 'PySide6.QtDataVisualization',
        'PySide6.QtDesigner', 'PySide6.QtHelp', 'PySide6.QtLocation',
        'PySide6.QtMultimedia', 'PySide6.QtMultimediaWidgets', 'PySide6.QtNfc',
        'PySide6.QtOpenGL', 'PySide6.QtOpenGLWidgets', 'PySide6.QtPositioning',
        'PySide6.QtPrintSupport', 'PySide6.QtQml', 'PySide6.QtQuick',
        'PySide6.QtQuick3D', 'PySide6.QtQuickControls2', 'PySide6.QtQuickWidgets',
        'PySide6.QtRemoteObjects', 'PySide6.QtScxml', 'PySide6.QtSensors',
        'PySide6.QtSerialPort', 'PySide6.QtSql', 'PySide6.QtStateMachine',
        'PySide6.QtTest', 'PySide6.QtTextToSpeech', 'PySide6.QtUiTools',
        'PySide6.QtWebChannel', 'PySide6.QtWebEngine', 'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineWidgets', 'PySide6.QtWebSockets',
        # Other unused modules (keep zipfile - needed by PyInstaller)
        'tkinter', 'unittest', 'pydoc', 'doctest',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Ytp Downloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,  # Disabled on Windows (strip tool not available)
    upx=True,
    console=False,  # Set to False for GUI app (no console window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='installer_build\\assets\\app_icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,  # Disabled on Windows (strip tool not available)
    upx=True,
    upx_exclude=[
        # Don't compress these (can cause issues)
        'vcruntime140.dll',
        'python*.dll',
    ],
    name='Ytp Downloader',
)
