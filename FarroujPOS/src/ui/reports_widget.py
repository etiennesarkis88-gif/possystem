# -*- coding: utf-8 -*-
"""
Reports Widget - Sales reports and analytics
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QLabel, QDateEdit, QComboBox, QFrame,
    QMessageBox, QFileDialog, QScrollArea
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor
import csv
from datetime import datetime, timedelta

class ReportsWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.load_report()

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

        title = QLabel("Reports & Analytics")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; background-color: transparent;")
        layout.addWidget(title)

        # Filters
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.start_date.setStyleSheet("""
            QDateEdit {
                background-color: #ffffff;
                color: #333;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
            }
        """)
        filter_layout.addWidget(QLabel("From:"))
        filter_layout.addWidget(self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setStyleSheet(self.start_date.styleSheet())
        filter_layout.addWidget(QLabel("To:"))
        filter_layout.addWidget(self.end_date)

        self.report_type = QComboBox()
        self.report_type.addItems(["Sales Summary", "Daily Breakdown", "Top Items", "Category Performance"])
        self.report_type.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                color: #333;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
            }
        """)
        filter_layout.addWidget(QLabel("Report:"))
        filter_layout.addWidget(self.report_type)

        generate_btn = QPushButton("Generate")
        generate_btn.setStyleSheet("""
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
        """)
        generate_btn.clicked.connect(self.load_report)
        filter_layout.addWidget(generate_btn)

        export_btn = QPushButton("Export CSV")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        export_btn.clicked.connect(self.export_csv)
        filter_layout.addWidget(export_btn)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Summary cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)
        self.total_sales_card = self.create_card("Total Sales", "0 LBP")
        self.order_count_card = self.create_card("Orders", "0")
        self.avg_order_card = self.create_card("Avg Order", "0 LBP")
        cards_layout.addWidget(self.total_sales_card)
        cards_layout.addWidget(self.order_count_card)
        cards_layout.addWidget(self.avg_order_card)
        layout.addLayout(cards_layout)

        # Report table
        self.report_table = QTableWidget()
        self.report_table.setStyleSheet("""
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
        layout.addWidget(self.report_table)
        layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def create_card(self, title, value):
        card = QFrame()
        card.setFixedHeight(90)
        card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setSpacing(4)
        layout.setContentsMargins(16, 12, 16, 12)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #7f8c8d; background-color: transparent;")
        layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        value_label.setStyleSheet("color: #2c3e50; background-color: transparent;")
        layout.addWidget(value_label)

        return card

    def load_report(self):
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        report_type = self.report_type.currentText()

        if report_type == "Sales Summary":
            self.load_sales_summary(start, end)
        elif report_type == "Daily Breakdown":
            self.load_daily_breakdown(start, end)
        elif report_type == "Top Items":
            self.load_top_items(start, end)
        elif report_type == "Category Performance":
            self.load_category_performance(start, end)

    def load_sales_summary(self, start, end):
        result = self.db.fetchone("""
            SELECT COUNT(*) as count,
                COALESCE(SUM(total_lbp), 0) as total_lbp,
                COALESCE(SUM(total_usd), 0) as total_usd
            FROM orders
            WHERE date(created_at) BETWEEN ? AND ? AND status = 'completed'
        """, (start, end))

        count = result['count'] if result else 0
        total_lbp = result['total_lbp'] if result else 0
        total_usd = result['total_usd'] if result else 0

        self.order_count_card.findChildren(QLabel)[1].setText(str(count))
        self.total_sales_card.findChildren(QLabel)[1].setText(f"{total_lbp:,.0f} LBP")
        avg = total_lbp / count if count > 0 else 0
        self.avg_order_card.findChildren(QLabel)[1].setText(f"{avg:,.0f} LBP")

        orders = self.db.fetchall("""
            SELECT * FROM orders
            WHERE date(created_at) BETWEEN ? AND ? AND status = 'completed'
            ORDER BY created_at DESC
        """, (start, end))

        self.report_table.setColumnCount(6)
        self.report_table.setHorizontalHeaderLabels([
            "Order #", "Date", "Type", "Items", "Subtotal", "Total"
        ])
        self.report_table.setRowCount(len(orders))

        for i, o in enumerate(orders):
            self.report_table.setItem(i, 0, QTableWidgetItem(str(o['id'])))
            self.report_table.setItem(i, 1, QTableWidgetItem(o['created_at'][:16]))
            self.report_table.setItem(i, 2, QTableWidgetItem(o['order_type']))

            items = self.db.fetchone("SELECT COUNT(*) as c FROM order_items WHERE order_id = ?", (o['id'],))
            self.report_table.setItem(i, 3, QTableWidgetItem(str(items['c'])))

            currency = o['currency_used'] or 'LBP'
            if currency == 'LBP':
                self.report_table.setItem(i, 4, QTableWidgetItem(f"{o['subtotal_lbp']:,.0f}"))
                self.report_table.setItem(i, 5, QTableWidgetItem(f"{o['total_lbp']:,.0f}"))
            else:
                self.report_table.setItem(i, 4, QTableWidgetItem(f"${o['subtotal_usd']:.2f}"))
                self.report_table.setItem(i, 5, QTableWidgetItem(f"${o['total_usd']:.2f}"))

    def load_daily_breakdown(self, start, end):
        data = self.db.fetchall("""
            SELECT date(created_at) as date,
                COUNT(*) as orders,
                COALESCE(SUM(total_lbp), 0) as total_lbp,
                COALESCE(SUM(total_usd), 0) as total_usd
            FROM orders
            WHERE date(created_at) BETWEEN ? AND ? AND status = 'completed'
            GROUP BY date(created_at)
            ORDER BY date
        """, (start, end))

        self.report_table.setColumnCount(4)
        self.report_table.setHorizontalHeaderLabels(["Date", "Orders", "Total (LBP)", "Total (USD)"])
        self.report_table.setRowCount(len(data))

        total_lbp = 0
        for i, d in enumerate(data):
            self.report_table.setItem(i, 0, QTableWidgetItem(d['date']))
            self.report_table.setItem(i, 1, QTableWidgetItem(str(d['orders'])))
            self.report_table.setItem(i, 2, QTableWidgetItem(f"{d['total_lbp']:,.0f}"))
            self.report_table.setItem(i, 3, QTableWidgetItem(f"${d['total_usd']:.2f}"))
            total_lbp += d['total_lbp']

        self.total_sales_card.findChildren(QLabel)[1].setText(f"{total_lbp:,.0f} LBP")
        self.order_count_card.findChildren(QLabel)[1].setText(str(sum(d['orders'] for d in data)))

    def load_top_items(self, start, end):
        data = self.db.fetchall("""
            SELECT mi.name_en, mi.name_ar, SUM(oi.quantity) as total_qty,
                SUM(oi.price_lbp * oi.quantity) as total_lbp,
                SUM(oi.price_usd * oi.quantity) as total_usd
            FROM order_items oi
            JOIN menu_items mi ON oi.menu_item_id = mi.id
            JOIN orders o ON oi.order_id = o.id
            WHERE date(o.created_at) BETWEEN ? AND ? AND o.status = 'completed'
            GROUP BY mi.id
            ORDER BY total_qty DESC
            LIMIT 20
        """, (start, end))

        self.report_table.setColumnCount(5)
        self.report_table.setHorizontalHeaderLabels(["Item", "Arabic", "Qty Sold", "Revenue (LBP)", "Revenue (USD)"])
        self.report_table.setRowCount(len(data))

        for i, d in enumerate(data):
            self.report_table.setItem(i, 0, QTableWidgetItem(d['name_en']))
            self.report_table.setItem(i, 1, QTableWidgetItem(d['name_ar'] or ''))
            self.report_table.setItem(i, 2, QTableWidgetItem(str(d['total_qty'])))
            self.report_table.setItem(i, 3, QTableWidgetItem(f"{d['total_lbp']:,.0f}"))
            self.report_table.setItem(i, 4, QTableWidgetItem(f"${d['total_usd']:.2f}"))

    def load_category_performance(self, start, end):
        data = self.db.fetchall("""
            SELECT c.name_en, c.name_ar, COUNT(DISTINCT o.id) as orders,
                SUM(oi.quantity) as items_sold,
                SUM(oi.price_lbp * oi.quantity) as revenue_lbp
            FROM order_items oi
            JOIN menu_items mi ON oi.menu_item_id = mi.id
            JOIN categories c ON mi.category_id = c.id
            JOIN orders o ON oi.order_id = o.id
            WHERE date(o.created_at) BETWEEN ? AND ? AND o.status = 'completed'
            GROUP BY c.id
            ORDER BY revenue_lbp DESC
        """, (start, end))

        self.report_table.setColumnCount(5)
        self.report_table.setHorizontalHeaderLabels(["Category", "Arabic", "Orders", "Items Sold", "Revenue"])
        self.report_table.setRowCount(len(data))

        for i, d in enumerate(data):
            self.report_table.setItem(i, 0, QTableWidgetItem(d['name_en']))
            self.report_table.setItem(i, 1, QTableWidgetItem(d['name_ar'] or ''))
            self.report_table.setItem(i, 2, QTableWidgetItem(str(d['orders'])))
            self.report_table.setItem(i, 3, QTableWidgetItem(str(d['items_sold'])))
            self.report_table.setItem(i, 4, QTableWidgetItem(f"{d['revenue_lbp']:,.0f} LBP"))

    def export_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Report", f"report_{datetime.now().strftime('%Y%m%d')}.csv",
            "CSV Files (*.csv)"
        )
        if not file_path:
            return

        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            headers = []
            for i in range(self.report_table.columnCount()):
                headers.append(self.report_table.horizontalHeaderItem(i).text())
            writer.writerow(headers)

            for row in range(self.report_table.rowCount()):
                row_data = []
                for col in range(self.report_table.columnCount()):
                    item = self.report_table.item(row, col)
                    row_data.append(item.text() if item else '')
                writer.writerow(row_data)

        QMessageBox.information(self, "Success", f"Report exported to {file_path}")
