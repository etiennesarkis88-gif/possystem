# -*- coding: utf-8 -*-
"""
Delivery Widget - Manage delivery orders and drivers
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QLabel, QLineEdit, QComboBox, QMessageBox,
    QDialog, QFormLayout, QTextEdit, QDateEdit, QFrame
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor

class DeliveryWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.load_deliveries()
        self.apply_light_theme()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("🚚 Delivery Management")
        title.setObjectName("page_title")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        layout.addWidget(title)

        # Filters
        filter_layout = QHBoxLayout()
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Pending", "Out for Delivery", "Delivered", "Cancelled"])
        self.status_filter.currentTextChanged.connect(self.load_deliveries)
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.status_filter)

        self.date_filter = QDateEdit()
        self.date_filter.setCalendarPopup(True)
        self.date_filter.setDate(QDate.currentDate())
        self.date_filter.dateChanged.connect(self.load_deliveries)
        filter_layout.addWidget(QLabel("Date:"))
        filter_layout.addWidget(self.date_filter)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Deliveries table
        self.delivery_table = QTableWidget()
        self.delivery_table.setColumnCount(8)
        self.delivery_table.setHorizontalHeaderLabels([
            "Order #", "Customer", "Phone", "Address", "Items", "Total", "Status", "Actions"
        ])
        self.delivery_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.delivery_table.setObjectName("data_table")
        layout.addWidget(self.delivery_table)

    def load_deliveries(self):
        status = self.status_filter.currentText()
        date = self.date_filter.date().toString("yyyy-MM-dd")

        query = """
            SELECT o.*, 
                   (SELECT COUNT(*) FROM order_items oi WHERE oi.order_id = o.id) as item_count
            FROM orders o
            WHERE o.order_type = 'delivery'
            AND date(o.created_at) = ?
        """
        params = [date]

        if status != "All":
            query += " AND o.status = ?"
            params.append(status.lower().replace(" ", "_"))

        query += " ORDER BY o.created_at DESC"

        deliveries = self.db.fetchall(query, tuple(params))

        self.delivery_table.setRowCount(len(deliveries))
        for i, d in enumerate(deliveries):
            self.delivery_table.setItem(i, 0, QTableWidgetItem(str(d['id'])))
            self.delivery_table.setItem(i, 1, QTableWidgetItem(d['customer_name'] or ''))
            self.delivery_table.setItem(i, 2, QTableWidgetItem(d['customer_phone'] or ''))
            self.delivery_table.setItem(i, 3, QTableWidgetItem(d['delivery_address'] or ''))
            self.delivery_table.setItem(i, 4, QTableWidgetItem(str(d['item_count'])))

            currency = d['currency_used'] or 'LBP'
            if currency == 'LBP':
                total_text = f"{d['total_lbp']:,.0f} LBP"
            else:
                total_text = f"${d['total_usd']:.2f}"
            self.delivery_table.setItem(i, 5, QTableWidgetItem(total_text))

            status_colors = {
                'pending': ('⏳ Pending', '#F39C12'),
                'out_for_delivery': ('🛵 Out for Delivery', '#3498DB'),
                'delivered': ('✅ Delivered', '#27AE60'),
                'cancelled': ('❌ Cancelled', '#E74C3C')
            }
            status_text, color = status_colors.get(d['status'], (d['status'], '#666'))
            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(QColor(color))
            self.delivery_table.setItem(i, 6, status_item)

            # Actions
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(5, 0, 5, 0)

            if d['status'] == 'pending':
                out_btn = QPushButton("🛵")
                out_btn.setFixedSize(30, 25)
                out_btn.setToolTip("Mark as Out for Delivery")
                out_btn.clicked.connect(lambda checked, oid=d['id']: self.update_status(oid, 'out_for_delivery'))
                actions_layout.addWidget(out_btn)

            if d['status'] in ['pending', 'out_for_delivery']:
                done_btn = QPushButton("✅")
                done_btn.setFixedSize(30, 25)
                done_btn.setToolTip("Mark as Delivered")
                done_btn.clicked.connect(lambda checked, oid=d['id']: self.update_status(oid, 'delivered'))
                actions_layout.addWidget(done_btn)

            actions_layout.addStretch()
            self.delivery_table.setCellWidget(i, 7, actions)

    def update_status(self, order_id, status):
        self.db.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        self.load_deliveries()

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
