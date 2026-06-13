# -*- coding: utf-8 -*-
"""
Main Window - Primary application interface (Light Theme)
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QStackedWidget, QFrame,
    QMessageBox, QDialog, QLineEdit, QGraphicsDropShadowEffect,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QIcon, QFont, QColor, QPixmap
import os
import datetime

from ui.cashier_widget import CashierWidget
from ui.menu_widget import MenuWidget
from ui.inventory_widget import InventoryWidget
from ui.settings_widget import SettingsWidget
from ui.reports_widget import ReportsWidget
from ui.delivery_widget import DeliveryWidget
from database.db_manager import DatabaseManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.current_user = None
        self.init_ui()
        self.load_styles()
        self.start_clock()

    def init_ui(self):
        self.setWindowTitle("لقمة أبو جورج - POS")
        self.setMinimumSize(1400, 900)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)

        # Content area
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, 1)

        # Initialize all pages
        self.cashier_widget = CashierWidget(self.db)
        self.menu_widget = MenuWidget(self.db)
        self.inventory_widget = InventoryWidget(self.db)
        self.delivery_widget = DeliveryWidget(self.db)
        self.reports_widget = ReportsWidget(self.db)
        self.settings_widget = SettingsWidget(self.db)

        self.content_stack.addWidget(self.cashier_widget)  # Index 0
        self.content_stack.addWidget(self.menu_widget)      # Index 1
        self.content_stack.addWidget(self.inventory_widget) # Index 2
        self.content_stack.addWidget(self.delivery_widget)  # Index 3
        self.content_stack.addWidget(self.reports_widget)   # Index 4
        self.content_stack.addWidget(self.settings_widget)  # Index 5

        # Show cashier by default
        self.show_page(0)

    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)
        sidebar.setFrameShape(QFrame.Shape.NoFrame)

        layout = QVBoxLayout(sidebar)
        layout.setSpacing(5)
        layout.setContentsMargins(15, 20, 15, 20)

        # Logo area
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.setSpacing(8)

        # Logo icon
        logo_icon = QLabel("🍴")
        logo_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_icon.setFont(QFont("Segoe UI", 32))
        logo_layout.addWidget(logo_icon)

        # Business name
        logo_label = QLabel("لقمة أبو جورج")
        logo_label.setObjectName("logo")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        logo_layout.addWidget(logo_label)

        # Currency label
        currency_label = QLabel("LBP")
        currency_label.setObjectName("currency_label")
        currency_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        currency_label.setFont(QFont("Segoe UI", 10))
        logo_layout.addWidget(currency_label)

        layout.addWidget(logo_container)
        layout.addSpacing(20)

        # Navigation buttons
        nav_buttons = [
            ("🛒", "Point of Sale", 0),
            ("🧾", "Receipts", 1),
            ("📦", "Inventory", 2),
            ("📊", "Reports", 3),
            ("🏷️", "Categories", 4),
            ("🍽️", "Menu Items", 5),
            ("⚙️", "Settings", 6),
        ]

        self.nav_buttons = []
        for icon, text, index in nav_buttons:
            btn = QPushButton(f"{icon}  {text}")
            btn.setObjectName("nav_button")
            btn.setFixedHeight(48)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setProperty("page_index", index)
            btn.clicked.connect(lambda checked, idx=index: self.show_page(idx))
            self.nav_buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        # Bottom info
        bottom_frame = QFrame()
        bottom_layout = QVBoxLayout(bottom_frame)
        bottom_layout.setSpacing(5)

        date_label = QLabel(datetime.datetime.now().strftime("%a, %b %d, %Y"))
        date_label.setObjectName("date_label")
        date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bottom_layout.addWidget(date_label)

        version = QLabel("POS System v1.0")
        version.setObjectName("version")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bottom_layout.addWidget(version)

        layout.addWidget(bottom_frame)

        return sidebar

    def show_page(self, index):
        # Map sidebar index to content stack index
        # Sidebar: 0=POS, 1=Receipts, 2=Inventory, 3=Reports, 4=Categories, 5=Menu Items, 6=Settings
        # Content: 0=Cashier, 1=Menu, 2=Inventory, 3=Delivery, 4=Reports, 5=Settings

        mapping = {
            0: 0,  # Point of Sale -> Cashier
            1: 0,  # Receipts -> Cashier (we'll handle receipts differently)
            2: 2,  # Inventory -> Inventory
            3: 4,  # Reports -> Reports
            4: 1,  # Categories -> Menu (Categories tab)
            5: 1,  # Menu Items -> Menu (Items tab)
            6: 5,  # Settings -> Settings
        }

        content_index = mapping.get(index, 0)
        self.content_stack.setCurrentIndex(content_index)

        # If Categories or Menu Items, switch to correct tab
        if index == 4:  # Categories
            self.menu_widget.switch_to_categories()
        elif index == 5:  # Menu Items
            self.menu_widget.switch_to_items()

        # Update button styles
        for i, btn in enumerate(self.nav_buttons):
            if i == index:
                btn.setObjectName("nav_button_active")
            else:
                btn.setObjectName("nav_button")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def start_clock(self):
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)  # Update every second

    def update_clock(self):
        # Update date label in sidebar
        for child in self.sidebar.findChildren(QLabel):
            if child.objectName() == "date_label":
                child.setText(datetime.datetime.now().strftime("%a, %b %d, %Y"))

    def load_styles(self):
        # Only style the sidebar - content widgets handle their own styles
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            #sidebar {
                background-color: #1a1a2e;
                border: none;
            }
            #logo {
                color: #ffffff;
                padding: 5px;
            }
            #currency_label {
                color: #a0a0a0;
                font-size: 11px;
            }
            #nav_button {
                background-color: transparent;
                color: #a0a0a0;
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 13px;
                font-weight: 500;
                text-align: left;
            }
            #nav_button:hover {
                background-color: #2d2d44;
                color: white;
            }
            #nav_button_active {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 13px;
                font-weight: 600;
                text-align: left;
            }
            #date_label {
                color: #888;
                font-size: 11px;
                padding: 5px;
            }
            #version {
                color: #666;
                font-size: 10px;
            }
        """)
