# -*- coding: utf-8 -*-
"""
Inventory Widget - Track stock levels and low inventory alerts
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QLabel, QSpinBox, QMessageBox, QDialog,
    QFormLayout, QComboBox, QLineEdit, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor


class InventoryWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.load_inventory()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: #f5f6fa; border: none;")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Inventory Management")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; background-color: transparent;")
        layout.addWidget(title)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setStyleSheet(
            "QPushButton { background-color: #3498db; color: white; border: none; "
            "border-radius: 8px; padding: 10px 20px; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background-color: #2980b9; }"
        )
        self.refresh_btn.clicked.connect(self.load_inventory)
        toolbar.addWidget(self.refresh_btn)

        self.low_stock_btn = QPushButton("Low Stock Items")
        self.low_stock_btn.setStyleSheet(
            "QPushButton { background-color: #f39c12; color: white; border: none; "
            "border-radius: 8px; padding: 10px 20px; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background-color: #d68910; }"
        )
        self.low_stock_btn.clicked.connect(self.show_low_stock)
        toolbar.addWidget(self.low_stock_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.stats_label = QLabel()
        self.stats_label.setFont(QFont("Segoe UI", 11))
        self.stats_label.setStyleSheet("color: #555; background-color: transparent;")
        layout.addWidget(self.stats_label)

        self.inv_table = QTableWidget()
        self.inv_table.setColumnCount(7)
        self.inv_table.setHorizontalHeaderLabels([
            "Item", "Category", "Quantity", "Unit", "Min Stock", "Status", "Actions"
        ])
        self.inv_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.inv_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.inv_table.setStyleSheet(
            "QTableWidget { background-color: #ffffff; border: 1px solid #e0e0e0; "
            "border-radius: 8px; gridline-color: #f0f0f0; }"
            "QTableWidget::item { padding: 10px; border-bottom: 1px solid #f0f0f0; color: #333; }"
            "QHeaderView::section { background-color: #f8f9fa; border: none; padding: 10px; "
            "font-weight: bold; color: #555; border-bottom: 2px solid #e0e0e0; }"
        )
        self.inv_table.verticalHeader().setDefaultSectionSize(48)
        layout.addWidget(self.inv_table)
        layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

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
            name_item = QTableWidgetItem(item['name_en'])
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item.setForeground(QColor("#2c3e50"))
            self.inv_table.setItem(i, 0, name_item)

            cat_item = QTableWidgetItem(item['category_name'] or '')
            cat_item.setFlags(cat_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            cat_item.setForeground(QColor("#2c3e50"))
            self.inv_table.setItem(i, 1, cat_item)

            qty = item['quantity'] or 0
            qty_item = QTableWidgetItem(str(qty))
            qty_item.setFlags(qty_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            qty_item.setForeground(QColor("#2c3e50"))
            self.inv_table.setItem(i, 2, qty_item)

            unit_item = QTableWidgetItem(item['unit'] or 'piece')
            unit_item.setFlags(unit_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            unit_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            unit_item.setForeground(QColor("#2c3e50"))
            self.inv_table.setItem(i, 3, unit_item)

            min_stock_val = int(item['min_stock'] or 10)
            min_stock_item = QTableWidgetItem(str(min_stock_val))
            min_stock_item.setFlags(min_stock_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            min_stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            min_stock_item.setForeground(QColor("#2c3e50"))
            self.inv_table.setItem(i, 4, min_stock_item)

            if qty <= 0:
                status = "Out of Stock"
                color = "#E74C3C"
                low_count += 1
            elif qty <= min_stock_val:
                status = "Low Stock"
                color = "#F39C12"
                low_count += 1
            else:
                status = "In Stock"
                color = "#27AE60"

            status_item = QTableWidgetItem(status)
            status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            status_item.setForeground(QColor(color))
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.inv_table.setItem(i, 5, status_item)

            adjust_btn = QPushButton("Adjust")
            adjust_btn.setFixedSize(80, 32)
            adjust_btn.setStyleSheet(
                "QPushButton { background-color: #3498db; color: white; border: none; "
                "border-radius: 6px; font-size: 11px; font-weight: bold; }"
                "QPushButton:hover { background-color: #2980b9; }"
            )
            adjust_btn.clicked.connect(lambda checked, iid=item['id']: self.adjust_stock(iid))
            self.inv_table.setCellWidget(i, 6, adjust_btn)
            self.inv_table.setRowHeight(i, 48)

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
            name_item = QTableWidgetItem(item['name_en'])
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item.setForeground(QColor("#2c3e50"))
            self.inv_table.setItem(i, 0, name_item)

            cat_item = QTableWidgetItem(item['category_name'] or '')
            cat_item.setFlags(cat_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            cat_item.setForeground(QColor("#2c3e50"))
            self.inv_table.setItem(i, 1, cat_item)

            qty_item = QTableWidgetItem(str(item['quantity'] or 0))
            qty_item.setFlags(qty_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            qty_item.setForeground(QColor("#2c3e50"))
            self.inv_table.setItem(i, 2, qty_item)

            unit_item = QTableWidgetItem(item['unit'] or 'piece')
            unit_item.setFlags(unit_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            unit_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            unit_item.setForeground(QColor("#2c3e50"))
            self.inv_table.setItem(i, 3, unit_item)

            min_val = int(item['min_stock'] or 10)
            min_item = QTableWidgetItem(str(min_val))
            min_item.setFlags(min_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            min_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            min_item.setForeground(QColor("#2c3e50"))
            self.inv_table.setItem(i, 4, min_item)

            status = "Out of Stock" if (item['quantity'] or 0) <= 0 else "Low Stock"
            color = "#E74C3C" if (item['quantity'] or 0) <= 0 else "#F39C12"
            status_item = QTableWidgetItem(status)
            status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            status_item.setForeground(QColor(color))
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.inv_table.setItem(i, 5, status_item)

            adjust_btn = QPushButton("Adjust")
            adjust_btn.setFixedSize(80, 32)
            adjust_btn.setStyleSheet(
                "QPushButton { background-color: #3498db; color: white; border: none; "
                "border-radius: 6px; font-size: 11px; font-weight: bold; }"
                "QPushButton:hover { background-color: #2980b9; }"
            )
            adjust_btn.clicked.connect(lambda checked, iid=item['id']: self.adjust_stock(iid))
            self.inv_table.setCellWidget(i, 6, adjust_btn)
            self.inv_table.setRowHeight(i, 48)

        self.stats_label.setText(f"Showing: {len(items)} low stock items")

    def adjust_stock(self, item_id):
        dialog = StockDialog(self.db, item_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_inventory()


class StockDialog(QDialog):
    def __init__(self, db, item_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.item_id = item_id
        self.setWindowTitle("Adjust Stock")
        self.setMinimumWidth(400)
        self.init_ui()
        self.load_data()

    def init_ui(self):
        # FIXED: explicit label color so they show on light background
        self.setStyleSheet(
            "QDialog { background-color: #f5f6fa; }"
            "QLabel { color: #2c3e50; background-color: transparent; font-size: 13px; }"
        )
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        # Item name display (bold)
        self.item_name = QLabel()
        self.item_name.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.item_name.setStyleSheet("color: #2c3e50; background-color: transparent;")
        form.addRow("Item:", self.item_name)

        self.current_qty = QLabel()
        self.current_qty.setFont(QFont("Segoe UI", 12))
        self.current_qty.setStyleSheet("color: #555; background-color: transparent;")
        form.addRow("Current Qty:", self.current_qty)

        spinbox_style = (
            "QSpinBox { background-color: #ffffff; color: #333; border: 2px solid #e0e0e0; "
            "border-radius: 8px; padding: 8px; font-size: 13px; min-height: 18px; }"
            "QSpinBox:focus { border: 2px solid #e67e22; }"
        )

        self.new_qty = QSpinBox()
        self.new_qty.setRange(0, 999999)
        self.new_qty.setStyleSheet(spinbox_style)
        form.addRow("New Quantity:", self.new_qty)

        input_style = (
            "QLineEdit { background-color: #ffffff; color: #333; border: 2px solid #e0e0e0; "
            "border-radius: 8px; padding: 10px 12px; font-size: 13px; }"
            "QLineEdit:focus { border: 2px solid #e67e22; }"
        )

        self.unit = QLineEdit()
        self.unit.setStyleSheet(input_style)
        form.addRow("Unit:", self.unit)

        self.min_stock = QSpinBox()
        self.min_stock.setRange(0, 9999)
        self.min_stock.setStyleSheet(spinbox_style)
        form.addRow("Min Stock Alert:", self.min_stock)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        save_btn = QPushButton("Save")
        save_btn.setStyleSheet(
            "QPushButton { background-color: #27ae60; color: white; border: none; "
            "border-radius: 8px; padding: 10px 24px; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background-color: #219a52; }"
        )
        save_btn.clicked.connect(self.save)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(
            "QPushButton { background-color: #95a5a6; color: white; border: none; "
            "border-radius: 8px; padding: 10px 24px; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background-color: #7f8c8d; }"
        )
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

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
            self.new_qty.setValue(int(item['quantity'] or 0))
            self.unit.setText(item['unit'] or 'piece')
            self.min_stock.setValue(int(item['min_stock'] or 10))

    def save(self):
        existing = self.db.fetchone(
            "SELECT id FROM inventory WHERE item_id = ?", (self.item_id,))

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
