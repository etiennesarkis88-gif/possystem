# -*- coding: utf-8 -*-
"""
Cashier Widget - Responsive POS interface
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLayout,
    QPushButton, QLabel, QScrollArea, QFrame, QSpinBox,
    QLineEdit, QComboBox, QMessageBox, QDialog,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QTextEdit, QSizePolicy, QToolButton
)
from PyQt6.QtCore import Qt, QSize, QRect, QPoint, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QColor
import os
import datetime

from database.db_manager import DatabaseManager
from ui.item_customization_dialog import ItemCustomizationDialog
from ui.checkout_popup import CheckoutPopup


class FlowLayout(QLayout):
    """Custom flow layout that wraps items like CSS flex-wrap"""
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self.itemList = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        margin = self.contentsMargins()
        size += QSize(margin.left() + margin.right(), margin.top() + margin.bottom())
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0
        spacing = self.spacing()

        for item in self.itemList:
            wid = item.widget()
            spaceX = spacing + wid.style().layoutSpacing(
                QSizePolicy.ControlType.PushButton,
                QSizePolicy.ControlType.PushButton,
                Qt.Orientation.Horizontal)
            spaceY = spacing + wid.style().layoutSpacing(
                QSizePolicy.ControlType.PushButton,
                QSizePolicy.ControlType.PushButton,
                Qt.Orientation.Vertical)

            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()


class CashierWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.cart = []
        self.current_category = None
        self.currency_settings = self.get_currency_settings()
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        left_panel = self.create_menu_panel()
        main_layout.addWidget(left_panel, 7)

        right_panel = self.create_cart_panel()
        main_layout.addWidget(right_panel, 3)

    def create_menu_panel(self):
        panel = QWidget()
        panel.setStyleSheet("background-color: #f5f6fa;")
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # TOP BAR
        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)

        title = QLabel("Point of Sale")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; background-color: transparent;")
        top_bar.addWidget(title)
        top_bar.addStretch()

        self.currency_indicator = QLabel(self.get_selected_currency())
        self.currency_indicator.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.currency_indicator.setStyleSheet(
            "color: #e67e22; background-color: #fff3e0; padding: 6px 14px; "
            "border-radius: 16px; border: 1px solid #ffe0b2;"
        )
        top_bar.addWidget(self.currency_indicator)

        self.datetime_label = QLabel(datetime.datetime.now().strftime("%a, %b %d, %Y, %I:%M %p"))
        self.datetime_label.setFont(QFont("Segoe UI", 10))
        self.datetime_label.setStyleSheet("color: #666; background-color: transparent;")
        top_bar.addWidget(self.datetime_label)
        layout.addLayout(top_bar)

        # SEARCH BAR
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search items...")
        self.search_input.setStyleSheet(
            "QLineEdit { background-color: #ffffff; border: 2px solid #e0e0e0; "
            "border-radius: 24px; padding: 10px 18px; font-size: 14px; color: #333; }"
            "QLineEdit:focus { border: 2px solid #e67e22; }"
        )
        self.search_input.textChanged.connect(self.search_items)
        layout.addWidget(self.search_input)

        # CATEGORY BUTTONS - scrollable with proper sizing
        cat_container = QWidget()
        cat_container.setStyleSheet("background-color: transparent;")
        cat_layout = QHBoxLayout(cat_container)
        cat_layout.setSpacing(8)
        cat_layout.setContentsMargins(0, 0, 0, 0)

        self.left_arrow = QToolButton()
        self.left_arrow.setText("<")
        self.left_arrow.setFixedSize(32, 40)
        self.left_arrow.setStyleSheet(
            "QToolButton { background-color: #e0e0e0; border: none; border-radius: 6px; "
            "font-size: 14px; font-weight: bold; color: #555; }"
            "QToolButton:hover { background-color: #d0d0d0; }"
        )
        self.left_arrow.clicked.connect(self.scroll_categories_left)
        cat_layout.addWidget(self.left_arrow)

        self.category_scroll = QScrollArea()
        self.category_scroll.setWidgetResizable(True)
        self.category_scroll.setFixedHeight(52)
        self.category_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.category_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.category_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.category_scroll.setStyleSheet("background-color: transparent; border: none;")

        category_widget = QWidget()
        category_widget.setStyleSheet("background-color: transparent;")
        self.category_layout = QHBoxLayout(category_widget)
        self.category_layout.setSpacing(8)
        self.category_layout.setContentsMargins(4, 4, 4, 4)
        self.category_layout.addStretch()

        self.category_scroll.setWidget(category_widget)
        cat_layout.addWidget(self.category_scroll, 1)

        self.right_arrow = QToolButton()
        self.right_arrow.setText(">")
        self.right_arrow.setFixedSize(32, 40)
        self.right_arrow.setStyleSheet(self.left_arrow.styleSheet())
        self.right_arrow.clicked.connect(self.scroll_categories_right)
        cat_layout.addWidget(self.right_arrow)
        layout.addWidget(cat_container)

        # MENU ITEMS - RESPONSIVE FLOW LAYOUT
        self.menu_scroll = QScrollArea()
        self.menu_scroll.setWidgetResizable(True)
        self.menu_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.menu_scroll.setStyleSheet("background-color: transparent; border: none;")
        self.menu_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.menu_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        menu_widget = QWidget()
        menu_widget.setStyleSheet("background-color: transparent;")
        self.menu_flow = FlowLayout(menu_widget, margin=8, spacing=16)

        self.menu_scroll.setWidget(menu_widget)
        layout.addWidget(self.menu_scroll, 1)

        self.load_categories()
        return panel

    def create_cart_panel(self):
        panel = QFrame()
        panel.setStyleSheet("background-color: #ffffff; border-left: 1px solid #e0e0e0;")
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        layout.setContentsMargins(14, 14, 14, 14)

        # CART HEADER
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        order_title = QLabel("Current Order")
        order_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        order_title.setStyleSheet("color: #2c3e50; background-color: transparent;")
        header_layout.addWidget(order_title)

        self.cart_count = QLabel("0")
        self.cart_count.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.cart_count.setStyleSheet(
            "background-color: #e67e22; color: white; border-radius: 10px; padding: 2px 8px;"
        )
        self.cart_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.cart_count)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # EMPTY CART MESSAGE
        self.empty_cart_widget = QWidget()
        self.empty_cart_widget.setStyleSheet("background-color: transparent;")
        empty_layout = QVBoxLayout(self.empty_cart_widget)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.setSpacing(8)

        empty_icon = QLabel("CART")
        empty_icon.setFont(QFont("Segoe UI", 36, QFont.Weight.Bold))
        empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_icon.setStyleSheet("color: #ddd; background-color: transparent;")
        empty_layout.addWidget(empty_icon)

        empty_text = QLabel("Your cart is empty")
        empty_text.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        empty_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_text.setStyleSheet("color: #999; background-color: transparent;")
        empty_layout.addWidget(empty_text)

        empty_sub = QLabel("Add items to get started")
        empty_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_sub.setStyleSheet("color: #bbb; background-color: transparent;")
        empty_layout.addWidget(empty_sub)
        layout.addWidget(self.empty_cart_widget)

        # CART TABLE - RESPONSIVE
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(["Item", "Qty", "Price", "Total", ""])
        self.cart_table.setStyleSheet(
            "QTableWidget { background-color: #ffffff; border: 1px solid #e0e0e0; "
            "border-radius: 8px; gridline-color: #f0f0f0; }"
            "QTableWidget::item { padding: 8px 6px; border-bottom: 1px solid #f0f0f0; color: #2c3e50; }"
            "QHeaderView::section { background-color: #f8f9fa; border: none; padding: 8px; "
            "font-weight: bold; color: #555; border-bottom: 2px solid #e0e0e0; font-size: 11px; }"
        )

        header = self.cart_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)   # Item stretches
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)     # Qty
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)     # Price
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)     # Total
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)     # Remove

        self.cart_table.setColumnWidth(0, 100)
        self.cart_table.setColumnWidth(1, 50)
        self.cart_table.setColumnWidth(2, 65)
        self.cart_table.setColumnWidth(3, 65)
        self.cart_table.setColumnWidth(4, 36)

        self.cart_table.verticalHeader().setVisible(False)
        self.cart_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.cart_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.cart_table.hide()
        layout.addWidget(self.cart_table, 1)

        # ORDER TYPE
        order_type_layout = QHBoxLayout()
        order_type_layout.setSpacing(8)
        order_type_label = QLabel("Order Type:")
        order_type_label.setStyleSheet("color: #555; background-color: transparent;")
        order_type_layout.addWidget(order_type_label)

        self.order_type_combo = QComboBox()
        self.order_type_combo.addItems(["Dine In", "Takeaway", "Delivery"])
        self.order_type_combo.setStyleSheet(
            "QComboBox { background-color: #ffffff; border: 2px solid #e0e0e0; "
            "border-radius: 8px; padding: 8px 12px; color: #333; font-size: 13px; }"
            "QComboBox:focus { border: 2px solid #e67e22; }"
        )
        self.order_type_combo.currentTextChanged.connect(self.on_order_type_changed)
        order_type_layout.addWidget(self.order_type_combo, 1)
        layout.addLayout(order_type_layout)

        # TABLE / DELIVERY INFO
        self.table_input = QLineEdit()
        self.table_input.setPlaceholderText("Table #")
        self.table_input.setStyleSheet(
            "QLineEdit { background-color: #ffffff; border: 2px solid #e0e0e0; "
            "border-radius: 8px; padding: 10px; color: #333; font-size: 13px; }"
            "QLineEdit:focus { border: 2px solid #e67e22; }"
        )
        layout.addWidget(self.table_input)

        self.customer_frame = QFrame()
        self.customer_frame.setStyleSheet("background-color: transparent;")
        customer_layout = QVBoxLayout(self.customer_frame)
        customer_layout.setSpacing(6)
        customer_layout.setContentsMargins(0, 0, 0, 0)

        self.customer_name = QLineEdit()
        self.customer_name.setPlaceholderText("Customer Name")
        self.customer_name.setStyleSheet(self.table_input.styleSheet())
        customer_layout.addWidget(self.customer_name)

        self.customer_phone = QLineEdit()
        self.customer_phone.setPlaceholderText("Phone Number")
        self.customer_phone.setStyleSheet(self.table_input.styleSheet())
        customer_layout.addWidget(self.customer_phone)

        self.delivery_address = QTextEdit()
        self.delivery_address.setPlaceholderText("Delivery Address")
        self.delivery_address.setMaximumHeight(60)
        self.delivery_address.setStyleSheet(
            "QTextEdit { background-color: #ffffff; border: 2px solid #e0e0e0; "
            "border-radius: 8px; padding: 8px; color: #333; font-size: 13px; }"
            "QTextEdit:focus { border: 2px solid #e67e22; }"
        )
        customer_layout.addWidget(self.delivery_address)

        self.customer_frame.hide()
        layout.addWidget(self.customer_frame)

        # TOTALS
        totals_frame = QFrame()
        totals_frame.setStyleSheet("background-color: transparent;")
        totals_layout = QVBoxLayout(totals_frame)
        totals_layout.setSpacing(8)
        totals_layout.setContentsMargins(0, 8, 0, 8)

        subtotal_row = QHBoxLayout()
        subtotal_row.setSpacing(8)
        subtotal_label = QLabel("Subtotal:")
        subtotal_label.setFont(QFont("Segoe UI", 12))
        subtotal_label.setStyleSheet("color: #666; background-color: transparent;")
        subtotal_row.addWidget(subtotal_label)
        subtotal_row.addStretch()
        self.subtotal_value = QLabel("0.00 LBP")
        self.subtotal_value.setFont(QFont("Segoe UI", 12))
        self.subtotal_value.setStyleSheet("color: #2c3e50; background-color: transparent;")
        self.subtotal_value.setAlignment(Qt.AlignmentFlag.AlignRight)
        subtotal_row.addWidget(self.subtotal_value)
        totals_layout.addLayout(subtotal_row)

        total_row = QHBoxLayout()
        total_row.setSpacing(8)
        total_label = QLabel("Total:")
        total_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        total_label.setStyleSheet("color: #2c3e50; background-color: transparent;")
        total_row.addWidget(total_label)
        total_row.addStretch()
        self.total_value = QLabel("0.00 LBP")
        self.total_value.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.total_value.setStyleSheet("color: #2c3e50; background-color: transparent;")
        self.total_value.setAlignment(Qt.AlignmentFlag.AlignRight)
        total_row.addWidget(self.total_value)
        totals_layout.addLayout(total_row)
        layout.addWidget(totals_frame)

        # ACTION BUTTONS
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(10)

        self.charge_btn = QPushButton("Charge")
        self.charge_btn.setStyleSheet(
            "QPushButton { background-color: #27ae60; color: white; border: none; "
            "border-radius: 10px; padding: 16px; font-size: 16px; font-weight: bold; }"
            "QPushButton:hover { background-color: #219a52; }"
            "QPushButton:pressed { background-color: #1e8449; }"
        )
        self.charge_btn.clicked.connect(self.checkout)
        btn_layout.addWidget(self.charge_btn)

        self.clear_btn = QPushButton("Clear Cart")
        self.clear_btn.setStyleSheet(
            "QPushButton { background-color: transparent; color: #e74c3c; "
            "border: 2px solid #e74c3c; border-radius: 10px; padding: 12px; "
            "font-size: 14px; font-weight: bold; }"
            "QPushButton:hover { background-color: #e74c3c; color: white; }"
        )
        self.clear_btn.clicked.connect(self.clear_cart)
        btn_layout.addWidget(self.clear_btn)
        layout.addLayout(btn_layout)

        return panel

    def scroll_categories_left(self):
        self.category_scroll.horizontalScrollBar().setValue(
            self.category_scroll.horizontalScrollBar().value() - 120)

    def scroll_categories_right(self):
        self.category_scroll.horizontalScrollBar().setValue(
            self.category_scroll.horizontalScrollBar().value() + 120)

    def load_categories(self):
        while self.category_layout.count() > 1:
            item = self.category_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        categories = self.db.fetchall(
            "SELECT * FROM categories WHERE is_active = 1 ORDER BY sort_order")

        all_btn = QPushButton("All")
        all_btn.setFixedHeight(38)
        all_btn.setMinimumWidth(60)
        all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        all_btn.setProperty("category_id", -1)
        all_btn.setStyleSheet(
            "QPushButton { background-color: #e67e22; color: white; border: none; "
            "border-radius: 19px; padding: 8px 20px; font-weight: bold; font-size: 12px; }"
            "QPushButton:hover { background-color: #d35400; }"
        )
        all_btn.clicked.connect(lambda: self.load_all_items())
        self.category_layout.insertWidget(0, all_btn)

        for cat in categories:
            btn = QPushButton(cat['name_en'])
            btn.setFixedHeight(38)
            btn.setMinimumWidth(80)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setProperty("category_id", cat['id'])
            btn.clicked.connect(lambda checked, cid=cat['id']: self.load_menu_items(cid))
            btn.setStyleSheet(
                f"QPushButton {{ background-color: #f0f0f0; color: #333; border: 1px solid #ddd; "
                f"border-radius: 19px; padding: 8px 16px; font-weight: 500; font-size: 12px; }}"
                f"QPushButton:hover {{ background-color: {cat['color']}; color: white; "
                f"border-color: {cat['color']}; }}"
            )
            self.category_layout.insertWidget(self.category_layout.count()-1, btn)

        self.load_all_items()

    def load_all_items(self):
        self.current_category = None
        self._clear_menu_flow()
        items = self.db.fetchall(
            "SELECT * FROM menu_items WHERE is_available = 1 ORDER BY sort_order, name_en")
        self._populate_menu_flow(items)

    def load_menu_items(self, category_id):
        self.current_category = category_id
        self._clear_menu_flow()
        items = self.db.fetchall(
            """SELECT * FROM menu_items WHERE category_id = ? AND is_available = 1
            ORDER BY sort_order, name_en""", (category_id,))
        self._populate_menu_flow(items)

    def _clear_menu_flow(self):
        while self.menu_flow.count():
            item = self.menu_flow.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

    def _populate_menu_flow(self, items):
        for item in items:
            card = self.create_item_card(item)
            self.menu_flow.addWidget(card)

    def create_item_card(self, item):
        """Create a responsive item card with proper single-card styling"""
        card = QFrame()
        # Responsive size: min 160px, preferred 180px, max 200px
        card.setMinimumSize(160, 170)
        card.setMaximumSize(200, 200)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        # ONLY style the card frame, NOT internal widgets
        card.setStyleSheet(
            "QFrame { background-color: #ffffff; border: 2px solid #e8e8e8; border-radius: 14px; }"
            "QFrame:hover { border: 2px solid #e67e22; background-color: #fff8f0; }"
        )

        layout = QVBoxLayout(card)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 8, 8, 8)

        # Image/icon area - plain QLabel, no extra frame/border
        img_label = QLabel()
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_label.setFont(QFont("Segoe UI", 28))
        img_label.setStyleSheet("background-color: transparent; border: none;")
        img_label.setFixedHeight(50)

        if item['image_path'] and os.path.exists(item['image_path']):
            pixmap = QPixmap(item['image_path']).scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio)
            img_label.setPixmap(pixmap)
        else:
            img_label.setText(self.get_item_icon(item['name_en']))

        layout.addWidget(img_label)

        # Name - no border, transparent background
        name = QLabel(item['name_en'])
        name.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        name.setStyleSheet("color: #2c3e50; background-color: transparent; border: none;")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name.setWordWrap(True)
        layout.addWidget(name)

        # Price - no border, transparent background
        price_text = self.format_price(item)
        price = QLabel(price_text)
        price.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        price.setStyleSheet("color: #e67e22; background-color: transparent; border: none;")
        price.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(price)

        card.mousePressEvent = lambda e, i=item: self.add_to_cart(i)
        return card

    def get_item_icon(self, name):
        name_lower = name.lower()
        if 'chicken' in name_lower: return 'C'
        if 'burger' in name_lower or 'beef' in name_lower: return 'B'
        if 'falafel' in name_lower: return 'F'
        if 'fries' in name_lower or 'potato' in name_lower: return 'P'
        if 'arguileh' in name_lower or 'shisha' in name_lower: return 'A'
        if 'pepsi' in name_lower or 'coke' in name_lower or 'soda' in name_lower: return 'S'
        if 'water' in name_lower: return 'W'
        if 'sandwich' in name_lower or 'sub' in name_lower: return 'SW'
        if 'plate' in name_lower or 'meal' in name_lower: return 'PL'
        if 'sweet' in name_lower or 'cake' in name_lower or 'dessert' in name_lower: return 'D'
        if 'taouk' in name_lower: return 'T'
        if 'mezza' in name_lower: return 'M'
        return 'I'

    def format_price(self, item):
        price_text = ""
        if self.currency_settings['use_lbp'] and item['price_lbp'] > 0:
            price_text += f"{item['price_lbp']:,.0f} LBP"
        if self.currency_settings['use_usd'] and item['price_usd'] > 0:
            if price_text:
                price_text += " / "
            price_text += f"${item['price_usd']:.2f}"
        return price_text

    def add_to_cart(self, item):
        dialog = ItemCustomizationDialog(item, self.get_selected_currency(),
            self.currency_settings.get('exchange_rate', 90000), self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        customization = dialog.result
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
            # Build display name - single line, truncated if too long
            name_text = item['name_en']
            extras_text = ""
            if item['removed_ingredients']:
                removed = ", ".join(item['removed_ingredients'])
                extras_text += f" (NO: {removed})"
            if item['selected_extras']:
                extras = ", ".join(item['selected_extras'])
                extras_text += f" (+{extras})"
            if item['instructions']:
                extras_text += f" [{item['instructions']}]"

            # Combine into single item, tooltip for full text
            display_text = name_text + extras_text
            name_item = QTableWidgetItem(display_text)
            name_item.setFont(QFont("Segoe UI", 10))
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item.setForeground(QColor("#2c3e50"))
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            name_item.setToolTip(display_text)
            self.cart_table.setItem(i, 0, name_item)

            # Qty spinbox - clean, no buttons
            qty_spin = QSpinBox()
            qty_spin.setRange(1, 99)
            qty_spin.setValue(item['qty'])
            qty_spin.setFixedSize(44, 26)
            qty_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
            qty_spin.setStyleSheet(
                "QSpinBox { background-color: #ffffff; border: 1px solid #ddd; "
                "border-radius: 4px; padding: 2px 4px; color: #333; font-size: 12px; "
                "text-align: center; }"
            )
            qty_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
            qty_spin.valueChanged.connect(lambda val, idx=i: self.update_qty(idx, val))
            self.cart_table.setCellWidget(i, 1, qty_spin)

            currency = self.get_selected_currency()
            if currency == 'LBP':
                unit_price = item['price_lbp'] + item['extras_price_lbp']
                price_text = f"{unit_price:,.0f}"
            else:
                unit_price = item['price_usd'] + item['extras_price_usd']
                price_text = f"${unit_price:.2f}"

            price_item = QTableWidgetItem(price_text)
            price_item.setFont(QFont("Segoe UI", 9))
            price_item.setFlags(price_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            price_item.setForeground(QColor("#2c3e50"))
            self.cart_table.setItem(i, 2, price_item)

            total = unit_price * item['qty']
            if currency == 'LBP':
                total_text = f"{total:,.0f}"
                subtotal_lbp += total
            else:
                total_text = f"${total:.2f}"
                subtotal_usd += total

            total_item = QTableWidgetItem(total_text)
            total_item.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            total_item.setForeground(QColor("#e67e22"))
            self.cart_table.setItem(i, 3, total_item)

            # Remove button
            remove_btn = QPushButton("x")
            remove_btn.setFixedSize(28, 28)
            remove_btn.setStyleSheet(
                "QPushButton { border: none; font-size: 14px; font-weight: bold; "
                "color: #e74c3c; background-color: transparent; border-radius: 14px; }"
                "QPushButton:hover { background-color: #ffebee; }"
            )
            remove_btn.clicked.connect(lambda checked, idx=i: self.remove_from_cart(idx))
            self.cart_table.setCellWidget(i, 4, remove_btn)
            self.cart_table.setRowHeight(i, 40)

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
            self.total_value.setText(f"{subtotal_lbp:,.0f} LBP")
        else:
            self.subtotal_value.setText(f"${subtotal_usd:.2f}")
            self.total_value.setText(f"${subtotal_usd:.2f}")

    def get_selected_currency(self):
        settings = self.get_currency_settings()
        return settings.get('default_currency', 'LBP')

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
        self._clear_menu_flow()
        items = self.db.fetchall(
            """SELECT * FROM menu_items WHERE (name_en LIKE ? OR name_ar LIKE ?)
            AND is_available = 1""", (f"%{text}%", f"%{text}%"))
        self._populate_menu_flow(items)

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

        currency = self.get_selected_currency()
        subtotal_lbp = sum((item['price_lbp'] + item['extras_price_lbp']) * item['qty'] for item in self.cart)
        subtotal_usd = sum((item['price_usd'] + item['extras_price_usd']) * item['qty'] for item in self.cart)

        order_number = f"ORD-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
        order_type = self.order_type_combo.currentText().lower().replace(" ", "_")

        cursor = self.db.execute("""
            INSERT INTO orders (order_number, order_type, table_number, customer_name, customer_phone,
                delivery_address, subtotal_lbp, subtotal_usd, total_lbp, total_usd, currency_used, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (order_number, order_type, self.table_input.text(), self.customer_name.text(),
            self.customer_phone.text(), self.delivery_address.toPlainText(),
            subtotal_lbp, subtotal_usd, subtotal_lbp, subtotal_usd, currency, 'completed'))

        order_id = cursor.lastrowid

        for item in self.cart:
            self.db.execute("""
                INSERT INTO order_items (order_id, menu_item_id, quantity, price_lbp, price_usd,
                    extras_price_lbp, extras_price_usd, removed_ingredients, selected_extras)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (order_id, item['item_id'], item['qty'], item['price_lbp'], item['price_usd'],
                item['extras_price_lbp'], item['extras_price_usd'],
                ','.join(item['removed_ingredients']) if item['removed_ingredients'] else None,
                ','.join(item['selected_extras']) if item['selected_extras'] else None))

        popup = CheckoutPopup(self.db, self.cart, order_id, currency, self)
        popup.exec()
        self.clear_cart()
