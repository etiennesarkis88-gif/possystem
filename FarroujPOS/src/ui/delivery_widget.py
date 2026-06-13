# -*- coding: utf-8 -*-
"""
Delivery Widget - Manage delivery orders
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QLabel, QLineEdit, QComboBox, QMessageBox,
    QDialog, QFormLayout, QTextEdit, QDateEdit, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor

class DeliveryWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.load_deliveries()

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

        title = QLabel("Delivery Management")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; background-color: transparent;")
        layout.addWidget(title)

        # Filters
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Pending", "Out for Delivery", "Delivered", "Cancelled"])
        self.status_filter.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                color: #333;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
            }
        """)
        self.status_filter.currentTextChanged.connect(self.load_deliveries)
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.status_filter)

        self.date_filter = QDateEdit()
        self.date_filter.setCalendarPopup(True)
        self.date_filter.setDate(QDate.currentDate())
        self.date_filter.setStyleSheet("""
            QDateEdit {
                background-color: #ffffff;
                color: #333;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
            }
        """)
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
        self.delivery_table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                gridline-color: #f0f0f0;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #f0f0f0;
                color: #333;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                border: none;
                padding: 10px;
                font-weight: bold;
                color: #555;
                border-bottom: 2px solid #e0e0e0;
            }
        """)
        layout.addWidget(self.delivery_table)
        layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

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
                'pending': ('Pending', '#F39C12'),
                'out_for_delivery': ('Out for Delivery', '#3498DB'),
                'delivered': ('Delivered', '#27AE60'),
                'cancelled': ('Cancelled', '#E74C3C')
            }
            status_text, color = status_colors.get(d['status'], (d['status'], '#666'))
            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(QColor(color))
            self.delivery_table.setItem(i, 6, status_item)

            # Actions
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(4, 0, 4, 0)
            actions_layout.setSpacing(4)

            if d['status'] == 'pending':
                out_btn = QPushButton("Out")
                out_btn.setFixedSize(50, 26)
                out_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-size: 10px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                out_btn.setToolTip("Mark as Out for Delivery")
                out_btn.clicked.connect(lambda checked, oid=d['id']: self.update_status(oid, 'out_for_delivery'))
                actions_layout.addWidget(out_btn)

            if d['status'] in ['pending', 'out_for_delivery']:
                done_btn = QPushButton("Done")
                done_btn.setFixedSize(50, 26)
                done_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #27ae60;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-size: 10px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #219a52;
                    }
                """)
                done_btn.setToolTip("Mark as Delivered")
                done_btn.clicked.connect(lambda checked, oid=d['id']: self.update_status(oid, 'delivered'))
                actions_layout.addWidget(done_btn)

            actions_layout.addStretch()
            self.delivery_table.setCellWidget(i, 7, actions)
            self.delivery_table.setRowHeight(i, 44)

    def update_status(self, order_id, status):
        self.db.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        self.load_deliveries()
