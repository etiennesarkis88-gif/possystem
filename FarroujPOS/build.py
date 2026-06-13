#!/usr/bin/env python3
"""
Build script to create Windows executable using PyInstaller
Run this after installing requirements: pip install -r requirements.txt
"""

import subprocess
import sys
import os

def build():
    # Ensure PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=FarroujPOS",
        "--windowed",
        "--onefile",
        "--icon=NONE",
        "--add-data=src/assets;assets",
        "--clean",
        "main.py"
    ]

    print("Building FarroujPOS executable...")
    print("This may take a few minutes...")
    subprocess.check_call(cmd)

    print("\n" + "="*50)
    print("BUILD COMPLETE!")
    print("="*50)
    print("Your executable is in the 'dist' folder:")
    print("  dist/FarroujPOS.exe")
    print("\nTo create an installer, use Inno Setup with installer/installer.iss")

if __name__ == "__main__":
    build()
