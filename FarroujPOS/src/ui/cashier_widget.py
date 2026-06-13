# -*- coding: utf-8 -*-
"""
Cashier Widget - Main POS interface with light theme
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QScrollArea, QFrame, QSpinBox,
    QLineEdit, QComboBox, QMessageBox, QDialog,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QTextEdit, QSplitter, QGroupBox, QDoubleSpinBox,
    QRadioButton, QButtonGroup, QFileDialog, QSizePolicy,
    QCheckBox, QDialogButtonBox, QToolButton
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QColor
import os
import datetime

from database.db_manager import DatabaseManager
from ui.item_customization_dialog import ItemCustomizationDialog
from ui.checkout_popup import CheckoutPopup

class CashierWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.cart = []
        self.current_category = None
        self.currency_settings = self.get_currency_settings()
        self.init_ui()
        self.load_categories()
        self.setStyleSheet(self.get_stylesheet())

    def get_stylesheet(self):
        return """
            CashierWidget {
                background-color: #f5f6fa;
            }
            #menu_panel {
                background-color: #f5f6fa;
                border: none;
            }
            #cart_panel {
                background-color: #ffffff;
                border-left: 1px solid #e0e0e0;
            }
            #pos_title {
                color: #2c3e50;
                font-size: 22px;
                font-weight: bold;
            }
            #currency_indicator {
                color: #e67e22;
                background-color: #fff3e0;
                padding: 5px 15px;
                border-radius: 15px;
            }
            #datetime_label {
                color: #666;
            }
            #search_input {
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 25px;
                padding: 10px 20px;
                font-size: 14px;
                color: #333;
            }
            #search_input:focus {
                border: 2px solid #e67e22;
            }
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
            #category_scroll {
                background-color: transparent;
                border: none;
            }
            #menu_scroll {
                background-color: transparent;
                border: none;
            }
            #item_card {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
            }
            #item_card:hover {
                border: 2px solid #e67e22;
                background-color: #fff8f0;
            }
            #cart_table {
                background-color: transparent;
                border: none;
            }
            #cart_table::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QHeaderView::section {
                background-color: transparent;
                border: none;
                padding: 8px;
                font-weight: bold;
                color: #666;
            }
            #charge_btn {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            #charge_btn:hover {
                background-color: #219a52;
            }
            #clear_btn {
                background-color: transparent;
                color: #e74c3c;
                border: 2px solid #e74c3c;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
            }
            #clear_btn:hover {
                background-color: #e74c3c;
                color: white;
            }
            #order_type {
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 8px;
            }
            #table_input {
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 10px;
                color: #333;
            }
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 8px;
                color: #333;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #333;
            }
        """

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Left panel - Menu (70%)
        left_panel = self.create_menu_panel()
        layout.addWidget(left_panel, 7)

        # Right panel - Cart (30%)
        right_panel = self.create_cart_panel()
        layout.addWidget(right_panel, 3)

    def create_menu_panel(self):
        panel = QFrame()
        panel.setObjectName("menu_panel")
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Top bar with title and currency
        top_bar = QHBoxLayout()
        title = QLabel("Point of Sale")
        title.setObjectName("pos_title")
        title.setStyleSheet("color: #2c3e50;")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        top_bar.addWidget(title)

        top_bar.addStretch()

        # Currency indicator
        self.currency_indicator = QLabel("LBP")
        self.currency_indicator.setObjectName("currency_indicator")
        self.currency_indicator.setStyleSheet("color: #e67e22; background-color: #fff3e0; padding: 5px 15px; border-radius: 15px;")
        self.currency_indicator.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        top_bar.addWidget(self.currency_indicator)

        # Date/time
        self.datetime_label = QLabel(datetime.datetime.now().strftime("%a, %b %d, %Y, %I:%M %p"))
        self.datetime_label.setObjectName("datetime_label")
        self.datetime_label.setStyleSheet("color: #666;")
        self.datetime_label.setFont(QFont("Segoe UI", 11))
        top_bar.addWidget(self.datetime_label)

        layout.addLayout(top_bar)

        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search items...")
        self.search_input.setObjectName("search_input")
        self.search_input.textChanged.connect(self.search_items)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Category buttons with scroll arrows
        cat_container = QWidget()
        cat_container.setStyleSheet("background-color: transparent;")
        cat_layout = QHBoxLayout(cat_container)
        cat_layout.setSpacing(0)
        cat_layout.setContentsMargins(0, 0, 0, 0)

        # Left arrow
        self.left_arrow = QToolButton()
        self.left_arrow.setText("◀")
        self.left_arrow.setFixedSize(30, 40)
        self.left_arrow.setStyleSheet("""
            QToolButton {
                background-color: #e0e0e0;
                border: none;
                border-radius: 4px;
                font-size: 12px;
                color: #666;
            }
            QToolButton:hover {
                background-color: #d0d0d0;
            }
        """)
        self.left_arrow.clicked.connect(self.scroll_categories_left)
        cat_layout.addWidget(self.left_arrow)

        # Category scroll area
        self.category_scroll = QScrollArea()
        self.category_scroll.setWidgetResizable(True)
        self.category_scroll.setFixedHeight(50)
        self.category_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.category_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.category_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.category_scroll.setStyleSheet("background-color: transparent; border: none;")

        category_widget = QWidget()
        category_widget.setStyleSheet("background-color: transparent;")
        self.category_layout = QHBoxLayout(category_widget)
        self.category_layout.setSpacing(10)
        self.category_layout.setContentsMargins(5, 5, 5, 5)
        self.category_layout.addStretch()

        self.category_scroll.setWidget(category_widget)
        cat_layout.addWidget(self.category_scroll, 1)

        # Right arrow
        self.right_arrow = QToolButton()
        self.right_arrow.setText("▶")
        self.right_arrow.setFixedSize(30, 40)
        self.right_arrow.setStyleSheet("""
            QToolButton {
                background-color: #e0e0e0;
                border: none;
                border-radius: 4px;
                font-size: 12px;
                color: #666;
            }
            QToolButton:hover {
                background-color: #d0d0d0;
            }
        """)
        self.right_arrow.clicked.connect(self.scroll_categories_right)
        cat_layout.addWidget(self.right_arrow)

        layout.addWidget(cat_container)

        # Menu items grid
        self.menu_scroll = QScrollArea()
        self.menu_scroll.setWidgetResizable(True)
        self.menu_scroll.setObjectName("menu_scroll")
        self.menu_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.menu_scroll.setStyleSheet("background-color: transparent; border: none;")

        menu_widget = QWidget()
        menu_widget.setStyleSheet("background-color: transparent;")
        self.menu_grid = QGridLayout(menu_widget)
        self.menu_grid.setSpacing(15)
        self.menu_grid.setContentsMargins(10, 10, 10, 10)

        self.menu_scroll.setWidget(menu_widget)
        layout.addWidget(self.menu_scroll)

        return panel

    def create_cart_panel(self):
        panel = QFrame()
        panel.setObjectName("cart_panel")
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Current Order header
        header_layout = QHBoxLayout()
        cart_icon = QLabel("🛒")
        cart_icon.setFont(QFont("Segoe UI", 20))
        header_layout.addWidget(cart_icon)

        order_title = QLabel("Current Order")
        order_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        order_title.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(order_title)

        self.cart_count = QLabel("0")
        self.cart_count.setObjectName("cart_count_badge")
        self.cart_count.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.cart_count.setStyleSheet("""
            background-color: #e67e22; 
            color: white; 
            border-radius: 10px; 
            padding: 2px 8px;
        """)
        header_layout.addWidget(self.cart_count)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Empty cart message
        self.empty_cart_widget = QWidget()
        self.empty_cart_widget.setStyleSheet("background-color: transparent;")
        empty_layout = QVBoxLayout(self.empty_cart_widget)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        empty_icon = QLabel("🧺")
        empty_icon.setFont(QFont("Segoe UI", 48))
        empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_icon)

        empty_text = QLabel("Your cart is empty")
        empty_text.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        empty_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_text.setStyleSheet("color: #666;")
        empty_layout.addWidget(empty_text)

        empty_sub = QLabel("Add items to get started")
        empty_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_sub.setStyleSheet("color: #999;")
        empty_layout.addWidget(empty_sub)

        layout.addWidget(self.empty_cart_widget)

        # Cart table (hidden when empty)
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(4)
        self.cart_table.setHorizontalHeaderLabels(["Item", "Qty", "Price", ""])
        self.cart_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.cart_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.cart_table.setColumnWidth(3, 40)
        self.cart_table.setObjectName("cart_table")
        self.cart_table.hide()
        layout.addWidget(self.cart_table)

        # Order type
        order_type_layout = QHBoxLayout()
        self.order_type_combo = QComboBox()
        self.order_type_combo.addItems(["Dine In", "Takeaway", "Delivery"])
        self.order_type_combo.setObjectName("order_type")
        self.order_type_combo.currentTextChanged.connect(self.on_order_type_changed)
        order_type_layout.addWidget(QLabel("Order Type:"))
        order_type_layout.addWidget(self.order_type_combo)
        layout.addLayout(order_type_layout)

        # Table/Delivery info
        self.table_input = QLineEdit()
        self.table_input.setPlaceholderText("Table #")
        self.table_input.setObjectName("table_input")
        layout.addWidget(self.table_input)

        # Customer info (hidden by default, shown for delivery)
        self.customer_frame = QFrame()
        self.customer_frame.setStyleSheet("background-color: transparent;")
        customer_layout = QVBoxLayout(self.customer_frame)
        self.customer_name = QLineEdit()
        self.customer_name.setPlaceholderText("Customer Name")
        self.customer_phone = QLineEdit()
        self.customer_phone.setPlaceholderText("Phone Number")
        self.delivery_address = QTextEdit()
        self.delivery_address.setPlaceholderText("Delivery Address")
        self.delivery_address.setMaximumHeight(60)
        customer_layout.addWidget(self.customer_name)
        customer_layout.addWidget(self.customer_phone)
        customer_layout.addWidget(self.delivery_address)
        self.customer_frame.hide()
        layout.addWidget(self.customer_frame)

        layout.addStretch()

        # Totals section
        totals_frame = QFrame()
        totals_frame.setStyleSheet("background-color: transparent;")
        totals_layout = QVBoxLayout(totals_frame)
        totals_layout.setSpacing(10)

        self.subtotal_label = QLabel("Subtotal")
        self.subtotal_label.setFont(QFont("Segoe UI", 12))
        self.subtotal_label.setStyleSheet("color: #666;")
        self.subtotal_value = QLabel("0.00 LBP")
        self.subtotal_value.setFont(QFont("Segoe UI", 12))
        self.subtotal_value.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.subtotal_value.setStyleSheet("color: #2c3e50;")

        subtotal_row = QHBoxLayout()
        subtotal_row.addWidget(self.subtotal_label)
        subtotal_row.addWidget(self.subtotal_value)
        totals_layout.addLayout(subtotal_row)

        # Total row
        total_row = QHBoxLayout()
        self.total_label = QLabel("Total")
        self.total_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.total_label.setStyleSheet("color: #2c3e50;")
        self.total_value = QLabel("0.00 LBP")
        self.total_value.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.total_value.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.total_value.setStyleSheet("color: #2c3e50;")
        total_row.addWidget(self.total_label)
        total_row.addWidget(self.total_value)
        totals_layout.addLayout(total_row)

        layout.addWidget(totals_frame)

        # Action buttons
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(10)

        self.charge_btn = QPushButton("💳 Charge")
        self.charge_btn.setObjectName("charge_btn")
        self.charge_btn.clicked.connect(self.checkout)

        self.clear_btn = QPushButton("🗑️ Clear Cart")
        self.clear_btn.setObjectName("clear_btn")
        self.clear_btn.clicked.connect(self.clear_cart)

        btn_layout.addWidget(self.charge_btn)
        btn_layout.addWidget(self.clear_btn)
        layout.addLayout(btn_layout)

        return panel

    def scroll_categories_left(self):
        self.category_scroll.horizontalScrollBar().setValue(
            self.category_scroll.horizontalScrollBar().value() - 100
        )

    def scroll_categories_right(self):
        self.category_scroll.horizontalScrollBar().setValue(
            self.category_scroll.horizontalScrollBar().value() + 100
        )

    def load_categories(self):
        # Clear existing
        while self.category_layout.count() > 1:
            item = self.category_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        categories = self.db.fetchall(
            "SELECT * FROM categories WHERE is_active = 1 ORDER BY sort_order"
        )

        # Add "All" button first
        all_btn = QPushButton("📋 All")
        all_btn.setFixedHeight(40)
        all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        all_btn.setProperty("category_id", -1)
        all_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 20px;
                padding: 8px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        all_btn.clicked.connect(lambda: self.load_all_items())
        self.category_layout.insertWidget(0, all_btn)

        for cat in categories:
            btn = QPushButton(self.get_category_icon(cat['name_en']) + " " + cat['name_en'])
            btn.setFixedHeight(40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setProperty("category_id", cat['id'])
            btn.setProperty("color", cat['color'])
            btn.clicked.connect(lambda checked, cid=cat['id']: self.load_menu_items(cid))

            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #f0f0f0;
                    color: #333;
                    border: 1px solid #ddd;
                    border-radius: 20px;
                    padding: 8px 20px;
                    font-weight: 500;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: {cat['color']};
                    color: white;
                    border-color: {cat['color']};
                }}
            """)

            self.category_layout.insertWidget(self.category_layout.count()-1, btn)

        # Load all items by default
        self.load_all_items()

    def get_category_icon(self, name):
        icons = {
            'Farrouj': '🍗', 'Arguileh': '🚬', 'Sandwiches': '🥪',
            'Daily Meals': '🍽️', 'Sweets': '🍰', 'Drinks': '🥤',
            'Plates': '🍛', 'Taouk': '🍢', 'Mezza': '🥗', 'Snacks': '🍟'
        }
        return icons.get(name, '🍽️')

    def load_all_items(self):
        self.current_category = None

        while self.menu_grid.count():
            item = self.menu_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        items = self.db.fetchall(
            "SELECT * FROM menu_items WHERE is_available = 1 ORDER BY sort_order, name_en"
        )

        row, col = 0, 0
        for item in items:
            card = self.create_item_card(item)
            self.menu_grid.addWidget(card, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

    def load_menu_items(self, category_id):
        self.current_category = category_id

        while self.menu_grid.count():
            item = self.menu_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        items = self.db.fetchall(
            """SELECT * FROM menu_items 
               WHERE category_id = ? AND is_available = 1 
               ORDER BY sort_order, name_en""",
            (category_id,)
        )

        row, col = 0, 0
        for item in items:
            card = self.create_item_card(item)
            self.menu_grid.addWidget(card, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

    def create_item_card(self, item):
        card = QFrame()
        card.setObjectName("item_card")
        card.setFixedSize(220, 200)
        card.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(card)
        layout.setSpacing(6)
        layout.setContentsMargins(12, 12, 12, 12)

        # Image/icon area
        img_container = QFrame()
        img_container.setFixedHeight(80)
        img_container.setStyleSheet("background-color: #f8f9fa; border-radius: 8px;")
        img_layout = QVBoxLayout(img_container)
        img_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        img_label = QLabel()
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_label.setFont(QFont("Segoe UI", 28))

        if item['image_path'] and os.path.exists(item['image_path']):
            pixmap = QPixmap(item['image_path']).scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio)
            img_label.setPixmap(pixmap)
        else:
            img_label.setText(self.get_item_icon(item['name_en']))

        img_layout.addWidget(img_label)
        layout.addWidget(img_container)

        # Name
        name = QLabel(item['name_en'])
        name.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        name.setStyleSheet("color: #2c3e50;")
        layout.addWidget(name)

        # Price
        price_text = ""
        if self.currency_settings['use_lbp'] and item['price_lbp'] > 0:
            price_text += f"{item['price_lbp']:,.0f} LBP"
        if self.currency_settings['use_usd'] and item['price_usd'] > 0:
            if price_text:
                price_text += " / "
            price_text += f"${item['price_usd']:.2f}"

        price = QLabel(price_text)
        price.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        price.setStyleSheet("color: #e67e22;")
        layout.addWidget(price)

        # Description
        if item.get('description_en'):
            desc = QLabel(item['description_en'][:40] + "..." if len(item['description_en']) > 40 else item['description_en'])
            desc.setFont(QFont("Segoe UI", 9))
            desc.setStyleSheet("color: #888;")
            layout.addWidget(desc)

        # Click to add
        card.mousePressEvent = lambda e, i=item: self.add_to_cart(i)

        return card

    def get_item_icon(self, name):
        name_lower = name.lower()
        if 'chicken' in name_lower: return '🍗'
        if 'burger' in name_lower or 'beef' in name_lower: return '🍔'
        if 'falafel' in name_lower: return '🧆'
        if 'fries' in name_lower or 'potato' in name_lower: return '🍟'
        if 'arguileh' in name_lower or 'shisha' in name_lower: return '🚬'
        if 'pepsi' in name_lower or 'coke' in name_lower or 'soda' in name_lower: return '🥤'
        if 'water' in name_lower: return '💧'
        if 'sandwich' in name_lower or 'sub' in name_lower: return '🥪'
        if 'plate' in name_lower or 'meal' in name_lower: return '🍽️'
        if 'sweet' in name_lower or 'cake' in name_lower or 'dessert' in name_lower: return '🍰'
        if 'taouk' in name_lower: return '🍢'
        if 'mezza' in name_lower: return '🥗'
        return '🍽️'

    def add_to_cart(self, item):
        """Show customization dialog, then add to cart"""
        dialog = ItemCustomizationDialog(item, self.get_selected_currency(), 
                                         self.currency_settings.get('exchange_rate', 90000), self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        customization = dialog.result

        # Calculate price with extras
        base_price_lbp = item['price_lbp'] or 0
        base_price_usd = item['price_usd'] or 0

        cart_item = {
            'item_id': item['id'],
            'name_en': item['name_en'],
            'name_ar': item['name_ar'] or '',
            'price_lbp': base_price_lbp,
            'price_usd': base_price_usd,
            'qty': 1,
            'removed_ingredients': customization['removed_ingredients'],
            'selected_extras': customization['selected_extras'],
            'extras_price_lbp': customization['extras_price_lbp'],
            'extras_price_usd': customization['extras_price_usd'],
            'instructions': customization['instructions']
        }

        self.cart.append(cart_item)
        self.update_cart_display()

    def update_cart_display(self):
        if not self.cart:
            self.empty_cart_widget.show()
            self.cart_table.hide()
            self.cart_count.setText("0")
            self.update_totals(0, 0)
            return

        self.empty_cart_widget.hide()
        self.cart_table.show()
        self.cart_table.setRowCount(len(self.cart))
        self.cart_count.setText(str(len(self.cart)))

        subtotal_lbp = 0
        subtotal_usd = 0

        for i, item in enumerate(self.cart):
            # Build display name with modifications
            name_text = item['name_en']

            # Show removed ingredients
            if item['removed_ingredients']:
                removed = ", ".join(item['removed_ingredients'])
                name_text = name_text + "\n  ❌ NO: " + removed

            # Show extras
            if item['selected_extras']:
                extras = ", ".join(item['selected_extras'])
                name_text = name_text + "\n  ➕ " + extras

            # Show instructions
            if item['instructions']:
                name_text = name_text + "\n  📝 " + item['instructions']

            name_item = QTableWidgetItem(name_text)
            name_item.setFont(QFont("Segoe UI", 10))
            self.cart_table.setItem(i, 0, name_item)

            # Qty
            qty_spin = QSpinBox()
            qty_spin.setRange(1, 99)
            qty_spin.setValue(item['qty'])
            qty_spin.valueChanged.connect(lambda val, idx=i: self.update_qty(idx, val))
            self.cart_table.setCellWidget(i, 1, qty_spin)

            # Price (base + extras)
            currency = self.get_selected_currency()
            if currency == 'LBP':
                unit_price = item['price_lbp'] + item['extras_price_lbp']
                price_text = f"{unit_price:,.0f}"
            else:
                unit_price = item['price_usd'] + item['extras_price_usd']
                price_text = f"${unit_price:.2f}"

            self.cart_table.setItem(i, 2, QTableWidgetItem(price_text))

            # Total
            total = unit_price * item['qty']
            if currency == 'LBP':
                total_text = f"{total:,.0f}"
                subtotal_lbp += total
            else:
                total_text = f"${total:.2f}"
                subtotal_usd += total

            self.cart_table.setItem(i, 3, QTableWidgetItem(total_text))

            # Remove button
            remove_btn = QPushButton("🗑️")
            remove_btn.setFixedSize(30, 30)
            remove_btn.setStyleSheet("border: none; font-size: 14px;")
            remove_btn.clicked.connect(lambda checked, idx=i: self.remove_from_cart(idx))
            self.cart_table.setCellWidget(i, 4, remove_btn)

        self.update_totals(subtotal_lbp, subtotal_usd)

    def update_qty(self, index, qty):
        self.cart[index]['qty'] = qty
        self.update_cart_display()

    def remove_from_cart(self, index):
        self.cart.pop(index)
        self.update_cart_display()

    def update_totals(self, subtotal_lbp, subtotal_usd):
        currency = self.get_selected_currency()

        if currency == 'LBP':
            self.subtotal_value.setText(f"{subtotal_lbp:,.0f} LBP")
            total = subtotal_lbp
            self.total_value.setText(f"{total:,.0f} LBP")
        else:
            self.subtotal_value.setText(f"${subtotal_usd:.2f}")
            total = subtotal_usd
            self.total_value.setText(f"${total:.2f}")

    def get_selected_currency(self):
        return 'LBP'

    def get_currency_settings(self):
        result = self.db.fetchone("SELECT * FROM currency_settings LIMIT 1")
        return result or {'use_lbp': 1, 'use_usd': 1, 'exchange_rate': 90000, 'default_currency': 'LBP'}

    def search_items(self, text):
        if not text:
            if self.current_category:
                self.load_menu_items(self.current_category)
            else:
                self.load_all_items()
            return

        while self.menu_grid.count():
            item = self.menu_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        items = self.db.fetchall(
            """SELECT * FROM menu_items 
               WHERE (name_en LIKE ? OR name_ar LIKE ?) 
               AND is_available = 1""",
            (f"%{text}%", f"%{text}%")
        )

        row, col = 0, 0
        for item in items:
            card = self.create_item_card(item)
            self.menu_grid.addWidget(card, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

    def on_order_type_changed(self, text):
        if text == "Delivery":
            self.customer_frame.show()
            self.table_input.hide()
        else:
            self.customer_frame.hide()
            self.table_input.show()

    def clear_cart(self):
        self.cart = []
        self.update_cart_display()

    def checkout(self):
        if not self.cart:
            QMessageBox.warning(self, "Empty Cart", "Please add items to the cart first.")
            return

        # Calculate totals
        currency = self.get_selected_currency()
        subtotal_lbp = sum((item['price_lbp'] + item['extras_price_lbp']) * item['qty'] for item in self.cart)
        subtotal_usd = sum((item['price_usd'] + item['extras_price_usd']) * item['qty'] for item in self.cart)

        # Save order
        order_type = self.order_type_combo.currentText().lower().replace(" ", "_")

        cursor = self.db.execute("""
            INSERT INTO orders (order_type, table_number, customer_name, customer_phone,
                delivery_address, subtotal_lbp, subtotal_usd,
                total_lbp, total_usd, currency_used, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order_type, self.table_input.text(), self.customer_name.text(),
            self.customer_phone.text(), self.delivery_address.toPlainText(),
            subtotal_lbp, subtotal_usd,
            subtotal_lbp, subtotal_usd, currency, 'completed'
        ))

        order_id = cursor.lastrowid

        # Save order items with ingredients/extras
        for item in self.cart:
            self.db.execute("""
                INSERT INTO order_items (order_id, menu_item_id, quantity, price_lbp, price_usd,
                    extras_price_lbp, extras_price_usd, removed_ingredients, selected_extras)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (order_id, item['item_id'], item['qty'], item['price_lbp'], item['price_usd'],
                   item['extras_price_lbp'], item['extras_price_usd'],
                   ','.join(item['removed_ingredients']) if item['removed_ingredients'] else None,
                   ','.join(item['selected_extras']) if item['selected_extras'] else None))

        # Show checkout popup
        popup = CheckoutPopup(self.db, self.cart, order_id, currency, self)
        popup.exec()

        # Clear cart after popup closes
        self.clear_cart()
