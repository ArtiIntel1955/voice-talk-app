#!/usr/bin/env python
"""PyInstaller build script for Voice Talk GUI application"""

import sys
import os
from pathlib import Path

def create_pyinstaller_spec():
    """Create PyInstaller spec file for building executable"""

    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Voice Talk Application
Build command: pyinstaller voice_talk.spec
"""

import sys
from pathlib import Path

# Determine if running as frozen executable
is_frozen = getattr(sys, 'frozen', False)

block_cipher = None

a = Analysis(
    ['gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/gui/styles/themes.py', 'src/gui/styles'),
        ('data/gui_settings.json', 'data'),
        ('.env.example', '.'),
    ],
    hiddenimports=[
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtCharts',
        'pyttsx3',
        'vosk',
        'requests',
        'numpy',
        'librosa',
        'soundfile',
        'pyaudio',
        'pydantic',
        'sqlalchemy',
        'python_dotenv',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludedimports=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VoiceTalkApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VoiceTalkApp',
)
'''

    spec_path = Path("voice_talk.spec")
    spec_path.write_text(spec_content)
    print(f"✓ Created: {spec_path}")
    return spec_path


def build_executable():
    """Build the executable using PyInstaller"""
    import subprocess

    print("\n" + "="*60)
    print(" Building Voice Talk Application Executable")
    print("="*60)

    try:
        # Check if PyInstaller is installed
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", "pyinstaller"],
            capture_output=True
        )

        if result.returncode != 0:
            print("\n! PyInstaller not installed")
            print("Installing PyInstaller...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "pyinstaller"],
                check=True
            )

        # Create spec file
        print("\nCreating PyInstaller spec file...")
        spec_path = create_pyinstaller_spec()

        # Run PyInstaller
        print(f"\nRunning PyInstaller...")
        result = subprocess.run(
            [sys.executable, "-m", "PyInstaller", str(spec_path), "--windowed"],
            check=False
        )

        if result.returncode == 0:
            print("\n" + "="*60)
            print(" ✓ Build Successful!")
            print("="*60)
            print("\nExecutable location:")
            print("  dist/VoiceTalkApp/VoiceTalkApp.exe")
            print("\nTo run the application:")
            print("  dist/VoiceTalkApp/VoiceTalkApp.exe")
            print("\nTo distribute:")
            print("  Zip the entire 'dist/VoiceTalkApp' folder")
            print("  Users extract and run VoiceTalkApp.exe")
            print("\n" + "="*60)
            return True
        else:
            print("\n✗ Build failed!")
            return False

    except Exception as e:
        print(f"\n✗ Error during build: {e}")
        return False


if __name__ == "__main__":
    success = build_executable()
    sys.exit(0 if success else 1)
