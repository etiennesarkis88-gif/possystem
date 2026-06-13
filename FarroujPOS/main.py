#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Farrouj POS - Lebanese Restaurant Point of Sale System
Fully Offline Desktop Application
Supports: English + Arabic typing | LBP + USD | Thermal Printing | PDF Export
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontDatabase
from ui.main_window import MainWindow
from database.db_manager import DatabaseManager

def main():
    # Enable high DPI support BEFORE creating QApplication
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Farrouj POS")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("FarroujPOS")

    # Load custom fonts
    font_path = os.path.join(os.path.dirname(__file__), 'src', 'assets', 'fonts')
    if os.path.exists(font_path):
        for font_file in os.listdir(font_path):
            if font_file.endswith(('.ttf', '.otf')):
                QFontDatabase.addApplicationFont(os.path.join(font_path, font_file))

    # Initialize database
    db = DatabaseManager()
    db.initialize_database()

    # Create and show main window
    window = MainWindow()
    window.showMaximized()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
