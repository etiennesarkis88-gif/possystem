# -*- coding: utf-8 -*-
"""
Checkout Popup - Shows after checkout with Print, Export PDF, and Close options
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QMessageBox, QFileDialog, QLineEdit, QComboBox,
    QFormLayout, QSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import os

from utils.printer import ReceiptPrinter
from utils.pdf_exporter import PDFGenerator


class CheckoutPopup(QDialog):
    def __init__(self, db, cart, order_id, currency, parent=None):
        super().__init__(parent)
        self.db = db
        self.cart = cart
        self.order_id = order_id
        self.currency = currency
        self.setWindowTitle("Order Complete")
        self.setMinimumWidth(380)
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("background-color: #ffffff;")
        layout = QVBoxLayout(self)
        layout.setSpacing(18)
        layout.setContentsMargins(28, 28, 28, 28)

        success_text = QLabel("Order Completed!")
        success_text.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        success_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        success_text.setStyleSheet("color: #27ae60; background-color: transparent;")
        layout.addWidget(success_text)

        order_num = QLabel(f"Order #{self.order_id}")
        order_num.setFont(QFont("Segoe UI", 13))
        order_num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        order_num.setStyleSheet("color: #666; background-color: transparent;")
        layout.addWidget(order_num)
        layout.addSpacing(16)

        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(10)

        print_row = QHBoxLayout()
        print_row.setSpacing(8)

        self.print_btn = QPushButton("Print Receipt")
        self.print_btn.setFixedHeight(48)
        self.print_btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.print_btn.setStyleSheet(
            "QPushButton { background-color: #3498db; color: white; border: none; "
            "border-radius: 10px; padding: 12px; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background-color: #2980b9; }"
        )
        self.print_btn.clicked.connect(self.print_receipt)
        print_row.addWidget(self.print_btn, 1)

        self.gear_btn = QPushButton("Settings")
        self.gear_btn.setFixedSize(90, 48)
        self.gear_btn.setFont(QFont("Segoe UI", 11))
        self.gear_btn.setToolTip("Printer Settings")
        self.gear_btn.setStyleSheet(
            "QPushButton { background-color: #ecf0f1; color: #333; border: 1px solid #bdc3c7; "
            "border-radius: 10px; font-weight: bold; font-size: 11px; }"
            "QPushButton:hover { background-color: #d5dbdb; }"
        )
        self.gear_btn.clicked.connect(self.open_printer_settings)
        print_row.addWidget(self.gear_btn)

        btn_layout.addLayout(print_row)

        self.pdf_btn = QPushButton("Export Receipt to PDF")
        self.pdf_btn.setFixedHeight(48)
        self.pdf_btn.setFont(QFont("Segoe UI", 13))
        self.pdf_btn.setStyleSheet(
            "QPushButton { background-color: #9b59b6; color: white; border: none; "
            "border-radius: 10px; padding: 12px; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background-color: #8e44ad; }"
        )
        self.pdf_btn.clicked.connect(self.export_pdf)
        btn_layout.addWidget(self.pdf_btn)

        self.close_btn = QPushButton("Close")
        self.close_btn.setFixedHeight(48)
        self.close_btn.setFont(QFont("Segoe UI", 13))
        self.close_btn.setStyleSheet(
            "QPushButton { background-color: #e74c3c; color: white; border: none; "
            "border-radius: 10px; padding: 12px; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background-color: #c0392b; }"
        )
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.close_btn)

        layout.addLayout(btn_layout)

    def print_receipt(self):
        printer = ReceiptPrinter(self.db)
        success = printer.print_receipt(self.cart, self.currency)
        if success:
            QMessageBox.information(self, "Success", "Receipt printed successfully!")

    def export_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Receipt PDF", f"receipt_order_{self.order_id}.pdf", "PDF Files (*.pdf)"
        )
        if file_path:
            generator = PDFGenerator(self.db)
            generator.generate_receipt(self.cart, file_path, self.currency)
            QMessageBox.information(self, "Success", f"Receipt saved to {file_path}")

    def open_printer_settings(self):
        dialog = PrinterSettingsDialog(self.db, self)
        dialog.exec()


class PrinterSettingsDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Printer Settings")
        self.setMinimumWidth(380)
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        self.setStyleSheet("background-color: #f5f6fa;")
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Printer Configuration")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; background-color: transparent;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        input_style = (
            "QLineEdit { background-color: #ffffff; color: #333; border: 2px solid #e0e0e0; "
            "border-radius: 8px; padding: 10px 12px; font-size: 13px; min-height: 18px; }"
            "QLineEdit:focus { border: 2px solid #e67e22; }"
        )

        combo_style = (
            "QComboBox { background-color: #ffffff; color: #333; border: 2px solid #e0e0e0; "
            "border-radius: 8px; padding: 8px 12px; font-size: 13px; min-height: 18px; }"
            "QComboBox:focus { border: 2px solid #e67e22; }"
        )

        self.conn_type = QComboBox()
        self.conn_type.addItems(["Auto Detect (USB)", "USB (Manual)", "Serial (COM)", "Network (IP)"])
        self.conn_type.setStyleSheet(combo_style)
        form.addRow("Connection:", self.conn_type)

        self.usb_vid = QLineEdit()
        self.usb_vid.setPlaceholderText("e.g., 0416")
        self.usb_vid.setStyleSheet(input_style)
        form.addRow("USB Vendor ID:", self.usb_vid)

        self.usb_pid = QLineEdit()
        self.usb_pid.setPlaceholderText("e.g., 5011")
        self.usb_pid.setStyleSheet(input_style)
        form.addRow("USB Product ID:", self.usb_pid)

        self.com_port = QComboBox()
        self.com_port.addItems(["COM1", "COM2", "COM3", "COM4", "COM5", "COM6"])
        self.com_port.setStyleSheet(combo_style)
        form.addRow("COM Port:", self.com_port)

        self.ip_address = QLineEdit()
        self.ip_address.setPlaceholderText("e.g., 192.168.1.100")
        self.ip_address.setStyleSheet(input_style)
        form.addRow("Printer IP:", self.ip_address)

        self.paper_width = QComboBox()
        self.paper_width.addItems(["58mm", "80mm"])
        self.paper_width.setStyleSheet(combo_style)
        form.addRow("Paper Width:", self.paper_width)

        layout.addLayout(form)

        test_btn = QPushButton("Test Print")
        test_btn.setStyleSheet(
            "QPushButton { background-color: #3498db; color: white; border: none; "
            "border-radius: 8px; padding: 12px; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background-color: #2980b9; }"
        )
        test_btn.clicked.connect(self.test_print)
        layout.addWidget(test_btn)

        save_btn = QPushButton("Save Settings")
        save_btn.setStyleSheet(
            "QPushButton { background-color: #27ae60; color: white; border: none; "
            "border-radius: 8px; padding: 12px; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background-color: #219a52; }"
        )
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

    def load_settings(self):
        result = self.db.fetchone("SELECT value FROM settings WHERE key = 'printer_config'")
        if result and result.get('value'):
            import json
            try:
                config = json.loads(result['value'])
                self.conn_type.setCurrentText(config.get('conn_type', 'Auto Detect (USB)'))
                self.usb_vid.setText(config.get('vid', ''))
                self.usb_pid.setText(config.get('pid', ''))
                self.com_port.setCurrentText(config.get('com_port', 'COM3'))
                self.ip_address.setText(config.get('ip', ''))
                self.paper_width.setCurrentText(config.get('paper_width', '80mm'))
            except:
                pass

    def save_settings(self):
        import json
        config = {
            'conn_type': self.conn_type.currentText(),
            'vid': self.usb_vid.text(),
            'pid': self.usb_pid.text(),
            'com_port': self.com_port.currentText(),
            'ip': self.ip_address.text(),
            'paper_width': self.paper_width.currentText()
        }
        self.db.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            ('printer_config', json.dumps(config))
        )
        QMessageBox.information(self, "Saved", "Printer settings saved!")
        self.accept()

    def test_print(self):
        QMessageBox.information(self, "Test", "Sending test print...")
