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

        title = QLabel("📊 Reports & Analytics")
        title.setObjectName("page_title")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        layout.addWidget(title)

        # Filters
        filter_layout = QHBoxLayout()

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        filter_layout.addWidget(QLabel("From:"))
        filter_layout.addWidget(self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        filter_layout.addWidget(QLabel("To:"))
        filter_layout.addWidget(self.end_date)

        self.report_type = QComboBox()
        self.report_type.addItems(["Sales Summary", "Daily Breakdown", "Top Items", "Category Performance"])
        filter_layout.addWidget(QLabel("Report:"))
        filter_layout.addWidget(self.report_type)

        generate_btn = QPushButton("📊 Generate")
        generate_btn.setObjectName("action_btn")
        generate_btn.clicked.connect(self.load_report)
        filter_layout.addWidget(generate_btn)

        export_btn = QPushButton("📤 Export CSV")
        export_btn.setObjectName("action_btn")
        export_btn.clicked.connect(self.export_csv)
        filter_layout.addWidget(export_btn)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Summary cards
        cards_layout = QHBoxLayout()
        self.total_sales_card = self.create_card("Total Sales", "0 LBP")
        self.order_count_card = self.create_card("Orders", "0")
        self.avg_order_card = self.create_card("Avg Order", "0 LBP")

        cards_layout.addWidget(self.total_sales_card)
        cards_layout.addWidget(self.order_count_card)
        cards_layout.addWidget(self.avg_order_card)
        layout.addLayout(cards_layout)

        # Report table
        self.report_table = QTableWidget()
        self.report_table.setObjectName("data_table")
        layout.addWidget(self.report_table)
        layout.addStretch()

        scroll.setWidget(content)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def create_card(self, title, value):
        card = QFrame()
        card.setObjectName("stat_card")
        card.setFixedHeight(100)
        layout = QVBoxLayout(card)

        title_label = QLabel(title)
        title_label.setObjectName("card_title")
        title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setObjectName("card_value")
        value_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
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
