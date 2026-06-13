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
        self.apply_light_theme()

    def init_ui(self):
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("background-color: #f5f6fa; border: none;")

        content = QWidget()
        layout = QVBoxLayout(content)
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

        # Inventory table - FIXED: better column widths and row heights
        self.inv_table = QTableWidget()
        self.inv_table.setColumnCount(7)
        self.inv_table.setHorizontalHeaderLabels([
            "Item", "Category", "Quantity", "Unit", "Min Stock", "Status", "Actions"
        ])

        # FIXED: Set proper column widths
        self.inv_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.inv_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.inv_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.inv_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.inv_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.inv_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.inv_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)

        self.inv_table.setColumnWidth(2, 100)
        self.inv_table.setColumnWidth(3, 80)
        self.inv_table.setColumnWidth(4, 100)
        self.inv_table.setColumnWidth(5, 120)
        self.inv_table.setColumnWidth(6, 100)

        # FIXED: Set minimum row height for better visibility
        self.inv_table.verticalHeader().setDefaultSectionSize(50)
        self.inv_table.setObjectName("data_table")
        layout.addWidget(self.inv_table)

        layout.addStretch()
        scroll.setWidget(content)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
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
            # FIXED: Ensure text is visible with proper styling
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

            min_stock_item = QTableWidgetItem(str(item['min_stock'] or 10))
            min_stock_item.setFlags(min_stock_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            min_stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            min_stock_item.setForeground(QColor("#2c3e50"))
            self.inv_table.setItem(i, 4, min_stock_item)

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
            status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            status_item.setForeground(QColor(color))
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.inv_table.setItem(i, 5, status_item)

            # Actions - FIXED: Proper sized button
            adjust_btn = QPushButton("⚖️ Adjust")
            adjust_btn.setFixedSize(90, 36)
            adjust_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            adjust_btn.clicked.connect(lambda checked, iid=item['id']: self.adjust_stock(iid))
            self.inv_table.setCellWidget(i, 6, adjust_btn)

            # FIXED: Set row height
            self.inv_table.setRowHeight(i, 50)

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

            min_item = QTableWidgetItem(str(item['min_stock'] or 10))
            min_item.setFlags(min_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            min_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            min_item.setForeground(QColor("#2c3e50"))
            self.inv_table.setItem(i, 4, min_item)

            status = "❌ Out of Stock" if (item['quantity'] or 0) <= 0 else "⚠️ Low Stock"
            color = "#E74C3C" if (item['quantity'] or 0) <= 0 else "#F39C12"
            status_item = QTableWidgetItem(status)
            status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            status_item.setForeground(QColor(color))
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.inv_table.setItem(i, 5, status_item)

            # FIXED: Proper sized button
            adjust_btn = QPushButton("⚖️ Adjust")
            adjust_btn.setFixedSize(90, 36)
            adjust_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            adjust_btn.clicked.connect(lambda checked, iid=item['id']: self.adjust_stock(iid))
            self.inv_table.setCellWidget(i, 6, adjust_btn)

            self.inv_table.setRowHeight(i, 50)

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

        /* Inputs - FIXED: visible borders */
        QLineEdit {
            background-color: #ffffff;
            color: #333333;
            border: 2px solid #cccccc;
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
            border: 2px solid #cccccc;
            border-radius: 8px;
            padding: 8px;
            font-size: 13px;
        }
        QTextEdit:focus {
            border: 2px solid #e67e22;
        }

        /* Dropdowns */
        QComboBox {
            background-color: #ffffff;
            color: #333333;
            border: 2px solid #cccccc;
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
            border: 2px solid #cccccc;
            border-radius: 6px;
            padding: 5px;
        }

        /* Checkboxes - FIXED: visible */
        QCheckBox {
            color: #2c3e50;
            font-size: 13px;
            spacing: 8px;
            background-color: transparent;
        }
        QCheckBox::indicator {
            width: 20px;
            height: 20px;
            border: 2px solid #cccccc;
            border-radius: 4px;
            background-color: #ffffff;
        }
        QCheckBox::indicator:checked {
            background-color: #e67e22;
            border: 2px solid #e67e22;
            image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNCIgaGVpZ2h0PSIxNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjMiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBvbHlsaW5lIHBvaW50cz0iMjAgNiA5IDE3IDQgMTIiPjwvcG9seWxpbmU+PC9zdmc+);
        }
        QCheckBox::indicator:hover {
            border: 2px solid #e67e22;
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

        /* Tables - FIXED: better row height and visibility */
        QTableWidget {
            background-color: #ffffff;
            color: #333333;
            border: 1px solid #dddddd;
            border-radius: 8px;
            gridline-color: #eeeeee;
            alternate-background-color: #fafafa;
        }
        QTableWidget::item {
            padding: 12px;
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
        QTableView {
            gridline-color: #e0e0e0;
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
            border: 2px solid #cccccc;
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
        self.setMinimumWidth(350)
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(15)

        self.item_name = QLabel()
        self.item_name.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addRow("Item:", self.item_name)

        self.current_qty = QLabel()
        layout.addRow("Current Qty:", self.current_qty)

        self.new_qty = QSpinBox()
        self.new_qty.setRange(0, 999999)
        self.new_qty.setStyleSheet("""
            QSpinBox {
                background-color: #ffffff;
                color: #333333;
                border: 2px solid #cccccc;
                border-radius: 6px;
                padding: 5px;
                min-height: 20px;
            }
            QSpinBox:focus {
                border: 2px solid #e67e22;
            }
        """)
        layout.addRow("New Quantity:", self.new_qty)

        self.unit = QLineEdit()
        self.unit.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                color: #333333;
                border: 2px solid #cccccc;
                border-radius: 8px;
                padding: 10px;
            }
            QLineEdit:focus {
                border: 2px solid #e67e22;
            }
        """)
        layout.addRow("Unit:", self.unit)

        self.min_stock = QSpinBox()
        self.min_stock.setRange(0, 9999)
        self.min_stock.setStyleSheet("""
            QSpinBox {
                background-color: #ffffff;
                color: #333333;
                border: 2px solid #cccccc;
                border-radius: 6px;
                padding: 5px;
                min-height: 20px;
            }
            QSpinBox:focus {
                border: 2px solid #e67e22;
            }
        """)
        layout.addRow("Min Stock Alert:", self.min_stock)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Save")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
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
