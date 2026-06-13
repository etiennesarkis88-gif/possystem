# -*- coding: utf-8 -*-
"""
Main Window - Application entry point with sidebar navigation
"""

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame, QScrollArea,
    QSizePolicy, QToolButton
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap
import sys
import os

from database.db_manager import DatabaseManager
from ui.cashier_widget import CashierWidget
from ui.menu_widget import MenuWidget
from ui.inventory_widget import InventoryWidget
from ui.reports_widget import ReportsWidget
from ui.delivery_widget import DeliveryWidget
from ui.settings_widget import SettingsWidget

# Global stylesheet for the entire application
APP_STYLESHEET = """
QMainWindow {
    background-color: #f5f6fa;
}

/* Sidebar */
QFrame#sidebar {
    background-color: #2c3e50;
    border: none;
}

/* Navigation buttons */
QPushButton#nav_btn {
    background-color: transparent;
    color: #bdc3c7;
    border: none;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 14px;
    font-weight: 500;
    text-align: left;
    min-height: 44px;
}
QPushButton#nav_btn:hover {
    background-color: #34495e;
    color: white;
}
QPushButton#nav_btn_active {
    background-color: #e67e22;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 14px;
    font-weight: 500;
    text-align: left;
    min-height: 44px;
}
QPushButton#nav_btn_active:hover {
    background-color: #d35400;
}

/* Scrollbars */
QScrollBar:vertical {
    background-color: #f0f0f0;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background-color: #c0c0c0;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background-color: #a0a0a0;
}
QScrollBar:horizontal {
    background-color: #f0f0f0;
    height: 10px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal {
    background-color: #c0c0c0;
    border-radius: 5px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover {
    background-color: #a0a0a0;
}

/* Content area */
QScrollArea {
    background-color: #f5f6fa;
    border: none;
}
QScrollArea > QWidget > QWidget {
    background-color: #f5f6fa;
}
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()
        self.setStyleSheet(APP_STYLESHEET)
        self.start_clock()

    def init_ui(self):
        self.setWindowTitle("Farrouj POS")
        self.setMinimumSize(1280, 800)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)

        # Content area
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #f5f6fa;")

        # Initialize pages
        self.pages = {
            0: CashierWidget(self.db),
            1: MenuWidget(self.db),
            2: InventoryWidget(self.db),
            3: ReportsWidget(self.db),
            4: DeliveryWidget(self.db),
            5: SettingsWidget(self.db),
        }

        for idx, page in self.pages.items():
            self.content_stack.addWidget(page)

        main_layout.addWidget(self.content_stack, 1)

        # Set initial page
        self.content_stack.setCurrentIndex(0)
        self.update_sidebar_active(0)

    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        layout = QVBoxLayout(sidebar)
        layout.setSpacing(6)
        layout.setContentsMargins(12, 20, 12, 20)

        # Logo area
        logo_frame = QFrame()
        logo_frame.setStyleSheet("background-color: transparent;")
        logo_layout = QVBoxLayout(logo_frame)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.setSpacing(4)

        logo_icon = QLabel("F")
        logo_icon.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        logo_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_icon.setStyleSheet("color: #e67e22; background-color: transparent;")
        logo_layout.addWidget(logo_icon)

        logo_text = QLabel("Farrouj POS")
        logo_text.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        logo_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_text.setStyleSheet("color: #e67e22; background-color: transparent;")
        logo_layout.addWidget(logo_text)

        logo_sub = QLabel("Restaurant POS")
        logo_sub.setFont(QFont("Segoe UI", 10))
        logo_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_sub.setStyleSheet("color: #7f8c8d; background-color: transparent;")
        logo_layout.addWidget(logo_sub)

        layout.addWidget(logo_frame)
        layout.addSpacing(25)

        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("Cashier", 0),
            ("Menu", 1),
            ("Inventory", 2),
            ("Reports", 3),
            ("Delivery", 4),
            ("Settings", 5),
        ]

        for text, page_idx in nav_items:
            btn = QPushButton(f"  {text}")
            btn.setObjectName("nav_btn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setProperty("page_index", page_idx)
            btn.clicked.connect(lambda checked, idx=page_idx: self.switch_page(idx))
            self.nav_buttons[page_idx] = btn
            layout.addWidget(btn)

        layout.addStretch()

        # Bottom info
        info_frame = QFrame()
        info_frame.setStyleSheet("background-color: transparent;")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(4)

        self.date_label = QLabel()
        self.date_label.setFont(QFont("Segoe UI", 10))
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setStyleSheet("color: #7f8c8d; background-color: transparent;")
        info_layout.addWidget(self.date_label)

        version = QLabel("v1.0.0")
        version.setFont(QFont("Segoe UI", 9))
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet("color: #7f8c8d; background-color: transparent;")
        info_layout.addWidget(version)

        layout.addWidget(info_frame)

        return sidebar

    def switch_page(self, index):
        self.content_stack.setCurrentIndex(index)
        self.update_sidebar_active(index)

    def update_sidebar_active(self, active_idx):
        for idx, btn in self.nav_buttons.items():
            if idx == active_idx:
                btn.setObjectName("nav_btn_active")
                btn.setStyleSheet("")  # Force refresh
                btn.style().unpolish(btn)
                btn.style().polish(btn)
            else:
                btn.setObjectName("nav_btn")
                btn.setStyleSheet("")
                btn.style().unpolish(btn)
                btn.style().polish(btn)

    def start_clock(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        self.update_clock()

    def update_clock(self):
        from datetime import datetime
        now = datetime.now()
        self.date_label.setText(now.strftime("%I:%M %p"))


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Farrouj POS")
    app.setApplicationDisplayName("Farrouj POS")

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
