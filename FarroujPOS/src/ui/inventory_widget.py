# -*- coding: utf-8 -*-
"""
Inventory Widget - Track stock levels and low inventory alerts
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QLabel, QSpinBox, QMessageBox, QDialog,
    QFormLayout, QComboBox, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

class InventoryWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.load_inventory()
        self.apply_light_theme()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("📦 Inventory Management")
        title.setObjectName("page_title")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        layout.addWidget(title)

        # Toolbar
        toolbar = QHBoxLayout()
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.load_inventory)
        toolbar.addWidget(self.refresh_btn)

        self.low_stock_btn = QPushButton("⚠️ Low Stock Items")
        self.low_stock_btn.clicked.connect(self.show_low_stock)
        toolbar.addWidget(self.low_stock_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Stats
        self.stats_label = QLabel()
        self.stats_label.setObjectName("stats_label")
        layout.addWidget(self.stats_label)

        # Inventory table
        self.inv_table = QTableWidget()
        self.inv_table.setColumnCount(7)
        self.inv_table.setHorizontalHeaderLabels([
            "Item", "Category", "Quantity", "Unit", "Min Stock", "Status", "Actions"
        ])
        self.inv_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.inv_table.setObjectName("data_table")
        layout.addWidget(self.inv_table)

    def load_inventory(self):
        items = self.db.fetchall("""
            SELECT mi.*, c.name_en as category_name, i.quantity, i.unit, i.min_stock
            FROM menu_items mi
            LEFT JOIN categories c ON mi.category_id = c.id
            LEFT JOIN inventory i ON mi.id = i.item_id
            ORDER BY mi.name_en
        """)

        self.inv_table.setRowCount(len(items))
        low_count = 0

        for i, item in enumerate(items):
            self.inv_table.setItem(i, 0, QTableWidgetItem(item['name_en']))
            self.inv_table.setItem(i, 1, QTableWidgetItem(item['category_name'] or ''))

            qty = item['quantity'] or 0
            qty_item = QTableWidgetItem(str(qty))
            self.inv_table.setItem(i, 2, qty_item)

            self.inv_table.setItem(i, 3, QTableWidgetItem(item['unit'] or 'piece'))
            self.inv_table.setItem(i, 4, QTableWidgetItem(str(item['min_stock'] or 10)))

            # Status
            min_stock = item['min_stock'] or 10
            if qty <= 0:
                status = "❌ Out of Stock"
                color = "#E74C3C"
                low_count += 1
            elif qty <= min_stock:
                status = "⚠️ Low Stock"
                color = "#F39C12"
                low_count += 1
            else:
                status = "✅ In Stock"
                color = "#27AE60"

            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor(color))
            self.inv_table.setItem(i, 5, status_item)

            # Actions
            adjust_btn = QPushButton("⚖️ Adjust")
            adjust_btn.clicked.connect(lambda checked, iid=item['id']: self.adjust_stock(iid))
            self.inv_table.setCellWidget(i, 6, adjust_btn)

        self.stats_label.setText(f"Total Items: {len(items)} | Low/Out of Stock: {low_count}")

    def show_low_stock(self):
        items = self.db.fetchall("""
            SELECT mi.*, c.name_en as category_name, i.quantity, i.unit, i.min_stock
            FROM menu_items mi
            LEFT JOIN categories c ON mi.category_id = c.id
            LEFT JOIN inventory i ON mi.id = i.item_id
            WHERE i.quantity IS NULL OR i.quantity <= i.min_stock
            ORDER BY mi.name_en
        """)

        self.inv_table.setRowCount(len(items))
        for i, item in enumerate(items):
            self.inv_table.setItem(i, 0, QTableWidgetItem(item['name_en']))
            self.inv_table.setItem(i, 1, QTableWidgetItem(item['category_name'] or ''))
            self.inv_table.setItem(i, 2, QTableWidgetItem(str(item['quantity'] or 0)))
            self.inv_table.setItem(i, 3, QTableWidgetItem(item['unit'] or 'piece'))
            self.inv_table.setItem(i, 4, QTableWidgetItem(str(item['min_stock'] or 10)))

            status = "❌ Out of Stock" if (item['quantity'] or 0) <= 0 else "⚠️ Low Stock"
            color = "#E74C3C" if (item['quantity'] or 0) <= 0 else "#F39C12"
            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor(color))
            self.inv_table.setItem(i, 5, status_item)

    def adjust_stock(self, item_id):
        dialog = StockDialog(self.db, item_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_inventory()



    def apply_light_theme(self):
        """Apply consistent light theme"""
        self.setStyleSheet("""
            /* Base */
            QWidget {
                background-color: #f5f6fa;
                color: #2c3e50;
            }

            /* Labels */
            QLabel {
                color: #2c3e50;
                background-color: transparent;
            }
            QLabel#page_title {
                color: #2c3e50;
                font-size: 22px;
                font-weight: bold;
            }

            /* Inputs */
            QLineEdit {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #dddddd;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #e67e22;
            }

            QTextEdit {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #dddddd;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
            }

            /* Dropdowns */
            QComboBox {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #dddddd;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #ddd;
                selection-background-color: #e67e22;
            }

            /* Spin boxes */
            QSpinBox, QDoubleSpinBox {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #dddddd;
                border-radius: 6px;
                padding: 5px;
            }

            /* Buttons */
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
            QPushButton:pressed {
                background-color: #a04000;
            }

            /* Tables */
            QTableWidget {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #dddddd;
                border-radius: 8px;
                gridline-color: #eeeeee;
                alternate-background-color: #fafafa;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eeeeee;
                color: #333333;
            }
            QTableWidget::item:selected {
                background-color: #fff3e0;
                color: #333333;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                color: #333333;
                border: none;
                padding: 12px;
                font-weight: bold;
                font-size: 12px;
            }

            /* Tabs */
            QTabWidget::pane {
                background-color: #ffffff;
                border: 1px solid #dddddd;
                border-radius: 8px;
                top: -1px;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                color: #666666;
                padding: 12px 24px;
                border: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background-color: #e67e22;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #e0e0e0;
            }

            /* Scroll areas */
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }

            /* Group boxes */
            QGroupBox {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #dddddd;
                border-radius: 8px;
                padding: 20px;
                margin-top: 15px;
                font-weight: bold;
            }
            QGroupBox::title {
                color: #333333;
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
            }

            /* Frames */
            QFrame {
                background-color: transparent;
                border: none;
            }

            /* Date edits */
            QDateEdit {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #dddddd;
                border-radius: 8px;
                padding: 8px;
            }
            QDateEdit::drop-down {
                border: none;
                width: 30px;
            }

            /* Dialogs */
            QDialog {
                background-color: #f5f6fa;
            }
            QDialog QLabel {
                color: #2c3e50;
            }
        """)


class StockDialog(QDialog):
    def __init__(self, db, item_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.item_id = item_id
        self.setWindowTitle("Adjust Stock")
        self.setMinimumWidth(300)
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QFormLayout(self)

        self.item_name = QLabel()
        self.item_name.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addRow("Item:", self.item_name)

        self.current_qty = QLabel()
        layout.addRow("Current Qty:", self.current_qty)

        self.new_qty = QSpinBox()
        self.new_qty.setRange(0, 999999)
        layout.addRow("New Quantity:", self.new_qty)

        self.unit = QLineEdit()
        layout.addRow("Unit:", self.unit)

        self.min_stock = QSpinBox()
        self.min_stock.setRange(0, 9999)
        layout.addRow("Min Stock Alert:", self.min_stock)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

    def load_data(self):
        item = self.db.fetchone("""
            SELECT mi.name_en, i.quantity, i.unit, i.min_stock
            FROM menu_items mi
            LEFT JOIN inventory i ON mi.id = i.item_id
            WHERE mi.id = ?
        """, (self.item_id,))

        if item:
            self.item_name.setText(item['name_en'])
            self.current_qty.setText(str(item['quantity'] or 0))
            self.new_qty.setValue(item['quantity'] or 0)
            self.unit.setText(item['unit'] or 'piece')
            self.min_stock.setValue(item['min_stock'] or 10)

    def save(self):
        # Check if inventory record exists
        existing = self.db.fetchone(
            "SELECT id FROM inventory WHERE item_id = ?", (self.item_id,)
        )

        if existing:
            self.db.execute("""
                UPDATE inventory SET quantity=?, unit=?, min_stock=?, last_updated=CURRENT_TIMESTAMP
                WHERE item_id=?
            """, (self.new_qty.value(), self.unit.text(), self.min_stock.value(), self.item_id))
        else:
            self.db.execute("""
                INSERT INTO inventory (item_id, quantity, unit, min_stock)
                VALUES (?, ?, ?, ?)
            """, (self.item_id, self.new_qty.value(), self.unit.text(), self.min_stock.value()))

        self.accept()
