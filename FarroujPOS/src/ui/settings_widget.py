# -*- coding: utf-8 -*-
"""
Settings Widget - Configure business info, currencies, receipt, and data reset
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox,
    QComboBox, QCheckBox, QFileDialog, QMessageBox, QGroupBox,
    QTabWidget, QTextEdit, QFrame, QDialog, QDialogButtonBox,
    QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
import hashlib
import os


class SettingsWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("background-color: #f5f6fa; border: none;")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Settings")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; background-color: transparent;")
        layout.addWidget(title)

        tabs = QTabWidget()
        tabs.setStyleSheet(
            "QTabWidget::pane { background-color: #ffffff; border: 1px solid #e0e0e0; "
            "border-radius: 10px; top: -1px; }"
            "QTabBar::tab { background-color: #f0f0f0; color: #666; padding: 12px 24px; "
            "border: none; border-top-left-radius: 10px; border-top-right-radius: 10px; "
            "font-weight: 500; font-size: 13px; }"
            "QTabBar::tab:selected { background-color: #e67e22; color: white; }"
            "QTabBar::tab:hover:!selected { background-color: #e0e0e0; }"
        )

        tabs.addTab(self.create_business_tab(), "Business Info")
        tabs.addTab(self.create_currency_tab(), "Currency")
        tabs.addTab(self.create_receipt_tab(), "Receipt")
        tabs.addTab(self.create_data_tab(), "Data Management")

        layout.addWidget(tabs)
        layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def create_business_tab(self):
        widget = QWidget()
        widget.setStyleSheet("background-color: #ffffff;")
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        input_style = (
            "QLineEdit { background-color: #ffffff; color: #333; border: 2px solid #e0e0e0; "
            "border-radius: 8px; padding: 10px 12px; font-size: 13px; min-height: 18px; }"
            "QLineEdit:focus { border: 2px solid #e67e22; }"
        )

        self.business_name = QLineEdit()
        self.business_name.setPlaceholderText("Business Name (English)")
        self.business_name.setStyleSheet(input_style)
        form.addRow("Business Name (EN):", self.business_name)

        self.business_name_ar = QLineEdit()
        self.business_name_ar.setPlaceholderText("Business Name (Arabic)")
        self.business_name_ar.setStyleSheet(input_style)
        form.addRow("Business Name (AR):", self.business_name_ar)

        self.address = QLineEdit()
        self.address.setPlaceholderText("Business Address")
        self.address.setStyleSheet(input_style)
        form.addRow("Address:", self.address)

        self.phone = QLineEdit()
        self.phone.setPlaceholderText("+961 XX XXX XXX")
        self.phone.setStyleSheet(input_style)
        form.addRow("Phone:", self.phone)

        layout.addLayout(form)

        # Logo selection
        logo_group = QGroupBox("Logo")
        logo_group.setStyleSheet(
            "QGroupBox { background-color: #f8f9fa; border: 1px solid #e0e0e0; "
            "border-radius: 10px; padding: 16px; margin-top: 10px; "
            "font-weight: bold; color: #2c3e50; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 8px; }"
        )
        logo_layout = QVBoxLayout(logo_group)
        logo_layout.setSpacing(10)

        logo_row = QHBoxLayout()
        logo_row.setSpacing(8)

        self.logo_path = QLineEdit()
        self.logo_path.setReadOnly(True)
        self.logo_path.setPlaceholderText("No logo selected")
        self.logo_path.setStyleSheet(input_style)
        logo_row.addWidget(self.logo_path, 1)

        logo_btn = QPushButton("Browse")
        logo_btn.setFixedWidth(90)
        logo_btn.setStyleSheet(
            "QPushButton { background-color: #3498db; color: white; border: none; "
            "border-radius: 8px; padding: 10px; font-weight: bold; font-size: 12px; }"
            "QPushButton:hover { background-color: #2980b9; }"
        )
        logo_btn.clicked.connect(self.choose_logo)
        logo_row.addWidget(logo_btn)
        logo_layout.addLayout(logo_row)

        preview_row = QHBoxLayout()
        preview_row.setSpacing(8)
        preview_label = QLabel("Preview:")
        preview_label.setStyleSheet("color: #555; background-color: transparent;")
        preview_row.addWidget(preview_label)

        self.logo_preview = QLabel("No Logo")
        self.logo_preview.setFixedSize(140, 140)
        self.logo_preview.setStyleSheet(
            "border: 2px dashed #ccc; border-radius: 10px; color: #999; "
            "background-color: #f0f0f0;"
        )
        self.logo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_row.addWidget(self.logo_preview)
        preview_row.addStretch()
        logo_layout.addLayout(preview_row)

        layout.addWidget(logo_group)

        save_btn = QPushButton("Save Business Info")
        save_btn.setStyleSheet(
            "QPushButton { background-color: #27ae60; color: white; border: none; "
            "border-radius: 8px; padding: 12px 24px; font-size: 14px; font-weight: bold; }"
            "QPushButton:hover { background-color: #219a52; }"
        )
        save_btn.clicked.connect(self.save_business_settings)
        layout.addWidget(save_btn)
        layout.addStretch()

        return widget

    def create_currency_tab(self):
        widget = QWidget()
        widget.setStyleSheet("background-color: #ffffff;")
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        checkbox_style = (
            "QCheckBox { color: #2c3e50; font-size: 13px; spacing: 8px; "
            "background-color: transparent; }"
            "QCheckBox::indicator { width: 20px; height: 20px; border: 2px solid #ccc; "
            "border-radius: 4px; background-color: #fff; }"
            "QCheckBox::indicator:checked { background-color: #e67e22; "
            "border: 2px solid #e67e22; }"
        )

        self.use_lbp = QCheckBox("Enable Lebanese Pound (LBP)")
        self.use_lbp.setChecked(True)
        self.use_lbp.setStyleSheet(checkbox_style)
        form.addRow(self.use_lbp)

        self.use_usd = QCheckBox("Enable US Dollar (USD)")
        self.use_usd.setChecked(True)
        self.use_usd.setStyleSheet(checkbox_style)
        form.addRow(self.use_usd)

        spinbox_style = (
            "QDoubleSpinBox { background-color: #ffffff; color: #333; "
            "border: 2px solid #e0e0e0; border-radius: 8px; padding: 8px; "
            "font-size: 13px; min-height: 18px; }"
            "QDoubleSpinBox:focus { border: 2px solid #e67e22; }"
        )

        self.exchange_rate = QDoubleSpinBox()
        self.exchange_rate.setRange(1000, 500000)
        self.exchange_rate.setDecimals(0)
        self.exchange_rate.setSuffix(" LBP per 1 USD")
        self.exchange_rate.setValue(90000)
        self.exchange_rate.setStyleSheet(spinbox_style)
        form.addRow("Exchange Rate:", self.exchange_rate)

        # FIXED: combo style with explicit text color and proper popup
        combo_style = (
            "QComboBox { background-color: #ffffff; color: #333333; "
            "border: 2px solid #e0e0e0; border-radius: 8px; padding: 8px 12px; "
            "font-size: 13px; min-height: 18px; }"
            "QComboBox:focus { border: 2px solid #e67e22; }"
            "QComboBox::drop-down { border: none; width: 30px; }"
            "QComboBox::down-arrow { image: none; border-left: 5px solid transparent; "
            "border-right: 5px solid transparent; border-top: 6px solid #666; }"
            "QComboBox QAbstractItemView { background-color: #ffffff; color: #333333; "
            "border: 1px solid #e0e0e0; selection-background-color: #e67e22; "
            "selection-color: white; }"
        )

        self.default_currency = QComboBox()
        self.default_currency.addItems(["LBP", "USD"])
        self.default_currency.setStyleSheet(combo_style)
        form.addRow("Default Currency:", self.default_currency)

        layout.addLayout(form)

        save_btn = QPushButton("Save Currency Settings")
        save_btn.setStyleSheet(
            "QPushButton { background-color: #27ae60; color: white; border: none; "
            "border-radius: 8px; padding: 12px 24px; font-size: 14px; font-weight: bold; }"
            "QPushButton:hover { background-color: #219a52; }"
        )
        save_btn.clicked.connect(self.save_currency_settings)
        layout.addWidget(save_btn)
        layout.addStretch()

        return widget

    def create_receipt_tab(self):
        widget = QWidget()
        widget.setStyleSheet("background-color: #ffffff;")
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        input_style = (
            "QLineEdit { background-color: #ffffff; color: #333; border: 2px solid #e0e0e0; "
            "border-radius: 8px; padding: 10px 12px; font-size: 13px; min-height: 18px; }"
            "QLineEdit:focus { border: 2px solid #e67e22; }"
        )

        textedit_style = (
            "QTextEdit { background-color: #ffffff; color: #333; border: 2px solid #e0e0e0; "
            "border-radius: 8px; padding: 8px; font-size: 13px; }"
            "QTextEdit:focus { border: 2px solid #e67e22; }"
        )

        self.header_text = QTextEdit()
        self.header_text.setMaximumHeight(60)
        self.header_text.setPlaceholderText("Custom header text for receipts")
        self.header_text.setStyleSheet(textedit_style)
        form.addRow("Header Text:", self.header_text)

        self.footer_text = QLineEdit()
        self.footer_text.setPlaceholderText("Thank you for your visit!")
        self.footer_text.setStyleSheet(input_style)
        form.addRow("Footer Text (EN):", self.footer_text)

        self.footer_text_ar = QLineEdit()
        self.footer_text_ar.setPlaceholderText("Thank you for your visit!")
        self.footer_text_ar.setStyleSheet(input_style)
        form.addRow("Footer Text (AR):", self.footer_text_ar)

        checkbox_style = (
            "QCheckBox { color: #2c3e50; font-size: 13px; spacing: 8px; "
            "background-color: transparent; }"
            "QCheckBox::indicator { width: 20px; height: 20px; border: 2px solid #ccc; "
            "border-radius: 4px; background-color: #fff; }"
            "QCheckBox::indicator:checked { background-color: #e67e22; "
            "border: 2px solid #e67e22; }"
        )

        self.show_logo = QCheckBox("Show Logo on Receipt")
        self.show_logo.setChecked(True)
        self.show_logo.setStyleSheet(checkbox_style)
        form.addRow(self.show_logo)

        self.show_qr = QCheckBox("Show QR Code on Receipt")
        self.show_qr.setStyleSheet(checkbox_style)
        form.addRow(self.show_qr)

        spinbox_style = (
            "QSpinBox { background-color: #ffffff; color: #333; border: 2px solid #e0e0e0; "
            "border-radius: 8px; padding: 8px; font-size: 13px; min-height: 18px; }"
            "QSpinBox:focus { border: 2px solid #e67e22; }"
        )

        self.paper_width = QSpinBox()
        self.paper_width.setRange(58, 80)
        self.paper_width.setSuffix(" mm")
        self.paper_width.setValue(80)
        self.paper_width.setStyleSheet(spinbox_style)
        form.addRow("Paper Width:", self.paper_width)

        layout.addLayout(form)

        save_btn = QPushButton("Save Receipt Settings")
        save_btn.setStyleSheet(
            "QPushButton { background-color: #27ae60; color: white; border: none; "
            "border-radius: 8px; padding: 12px 24px; font-size: 14px; font-weight: bold; }"
            "QPushButton:hover { background-color: #219a52; }"
        )
        save_btn.clicked.connect(self.save_receipt_settings)
        layout.addWidget(save_btn)
        layout.addStretch()

        return widget

    def create_data_tab(self):
        widget = QWidget()
        widget.setStyleSheet("background-color: #ffffff;")
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        warning = QLabel("Danger Zone")
        warning.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        warning.setStyleSheet("color: #E74C3C; background-color: transparent;")
        layout.addWidget(warning)

        warning_text = QLabel(
            "These actions are irreversible. All data will be permanently deleted. "
            "Make sure to backup any important information before proceeding."
        )
        warning_text.setWordWrap(True)
        warning_text.setStyleSheet("color: #666; background-color: transparent;")
        layout.addWidget(warning_text)
        layout.addSpacing(20)

        reset_group = QGroupBox("Reset Data")
        reset_group.setStyleSheet(
            "QGroupBox { background-color: #f8f9fa; border: 1px solid #e0e0e0; "
            "border-radius: 10px; padding: 16px; margin-top: 10px; "
            "font-weight: bold; color: #2c3e50; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 8px; }"
        )
        reset_layout = QVBoxLayout(reset_group)
        reset_layout.setSpacing(10)

        reset_sales_btn = QPushButton("Reset Sales Data Only")
        reset_sales_btn.setStyleSheet(
            "QPushButton { background-color: #e74c3c; color: white; border: none; "
            "border-radius: 8px; padding: 12px 20px; font-size: 13px; font-weight: bold; }"
            "QPushButton:hover { background-color: #c0392b; }"
        )
        reset_sales_btn.clicked.connect(lambda: self.reset_data("sales"))
        reset_layout.addWidget(reset_sales_btn)

        reset_all_btn = QPushButton("Reset ALL Data (Factory Reset)")
        reset_all_btn.setStyleSheet(
            "QPushButton { background-color: #c0392b; color: white; border: none; "
            "border-radius: 8px; padding: 12px 20px; font-size: 13px; font-weight: bold; }"
            "QPushButton:hover { background-color: #a93226; }"
        )
        reset_all_btn.clicked.connect(lambda: self.reset_data("all"))
        reset_layout.addWidget(reset_all_btn)

        layout.addWidget(reset_group)

        backup_group = QGroupBox("Backup & Export")
        backup_group.setStyleSheet(reset_group.styleSheet())
        backup_layout = QVBoxLayout(backup_group)
        backup_layout.setSpacing(10)

        export_btn = QPushButton("Export Database")
        export_btn.setStyleSheet(
            "QPushButton { background-color: #3498db; color: white; border: none; "
            "border-radius: 8px; padding: 12px 20px; font-size: 13px; font-weight: bold; }"
            "QPushButton:hover { background-color: #2980b9; }"
        )
        export_btn.clicked.connect(self.export_database)
        backup_layout.addWidget(export_btn)

        layout.addWidget(backup_group)
        layout.addStretch()

        return widget

    def choose_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Logo", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.svg *.webp)"
        )
        if file_path:
            self.logo_path.setText(file_path)
            pixmap = QPixmap(file_path).scaled(130, 130, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_preview.setPixmap(pixmap)
            self.logo_preview.setText("")

    def load_settings(self):
        business = self.db.fetchone("SELECT * FROM receipt_settings LIMIT 1")
        if business:
            self.business_name.setText(business.get('business_name', ''))
            self.business_name_ar.setText(business.get('business_name_ar', ''))
            self.address.setText(business.get('address', ''))
            self.phone.setText(business.get('phone', ''))
            if business.get('logo_path') and os.path.exists(business['logo_path']):
                self.logo_path.setText(business['logo_path'])
                pixmap = QPixmap(business['logo_path']).scaled(130, 130, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.logo_preview.setPixmap(pixmap)
                self.logo_preview.setText("")

        currency = self.db.fetchone("SELECT * FROM currency_settings LIMIT 1")
        if currency:
            self.use_lbp.setChecked(bool(currency.get('use_lbp', 1)))
            self.use_usd.setChecked(bool(currency.get('use_usd', 1)))
            self.exchange_rate.setValue(currency.get('exchange_rate', 90000))
            index = self.default_currency.findText(currency.get('default_currency', 'LBP'))
            if index >= 0:
                self.default_currency.setCurrentIndex(index)

        if business:
            self.header_text.setPlainText(business.get('header_text', ''))
            self.footer_text.setText(business.get('footer_text', ''))
            self.footer_text_ar.setText(business.get('footer_text_ar', ''))
            self.show_logo.setChecked(bool(business.get('show_logo', 1)))
            self.show_qr.setChecked(bool(business.get('show_qr_code', 0)))
            self.paper_width.setValue(business.get('paper_width', 80))

    def save_business_settings(self):
        self.db.execute("""
            UPDATE receipt_settings SET
                business_name=?, business_name_ar=?, address=?, phone=?, logo_path=?
            WHERE id=1
        """, (
            self.business_name.text(),
            self.business_name_ar.text(),
            self.address.text(),
            self.phone.text(),
            self.logo_path.text()
        ))
        QMessageBox.information(self, "Success", "Business information saved!")

    def save_currency_settings(self):
        if not self.use_lbp.isChecked() and not self.use_usd.isChecked():
            QMessageBox.warning(self, "Error", "At least one currency must be enabled!")
            return

        self.db.execute("""
            UPDATE currency_settings SET
                use_lbp=?, use_usd=?, exchange_rate=?, default_currency=?
            WHERE id=1
        """, (
            1 if self.use_lbp.isChecked() else 0,
            1 if self.use_usd.isChecked() else 0,
            self.exchange_rate.value(),
            self.default_currency.currentText()
        ))
        QMessageBox.information(self, "Success", "Currency settings saved!")

    def save_receipt_settings(self):
        self.db.execute("""
            UPDATE receipt_settings SET
                header_text=?, footer_text=?, footer_text_ar=?,
                show_logo=?, show_qr_code=?, paper_width=?
            WHERE id=1
        """, (
            self.header_text.toPlainText(),
            self.footer_text.text(),
            self.footer_text_ar.text(),
            1 if self.show_logo.isChecked() else 0,
            1 if self.show_qr.isChecked() else 0,
            self.paper_width.value()
        ))
        QMessageBox.information(self, "Success", "Receipt settings saved!")

    def reset_data(self, mode):
        dialog = PasswordDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        reply = QMessageBox.warning(
            self, f"Confirm Reset ({mode.upper()})",
            f"Are you absolutely sure you want to reset {mode} data?\n\n"
            "This action CANNOT be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if mode == "sales":
                self.db.execute("DELETE FROM orders")
                self.db.execute("DELETE FROM order_items")
                self.db.execute("DELETE FROM daily_sales")
            else:
                self.db.execute("DELETE FROM orders")
                self.db.execute("DELETE FROM order_items")
                self.db.execute("DELETE FROM menu_items")
                self.db.execute("DELETE FROM categories")
                self.db.execute("DELETE FROM inventory")
                self.db.execute("DELETE FROM daily_sales")
                self.db.initialize_database()

            QMessageBox.information(self, "Success", f"{mode.upper()} data has been reset!")

    def export_database(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Database", "farrouj_backup.db", "SQLite DB (*.db)"
        )
        if file_path:
            import shutil
            db_path = self.db.db_path
            shutil.copy2(db_path, file_path)
            QMessageBox.information(self, "Success", f"Database exported to {file_path}")


class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Authentication Required")
        self.setMinimumWidth(350)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(
            "QDialog { background-color: #f5f6fa; }"
            "QLabel { color: #2c3e50; background-color: transparent; }"
        )
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Enter Admin Password")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; background-color: transparent;")
        layout.addWidget(title)

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText("Password")
        self.password.setStyleSheet(
            "QLineEdit { background-color: #ffffff; color: #333; border: 2px solid #e0e0e0; "
            "border-radius: 8px; padding: 10px 12px; font-size: 13px; }"
            "QLineEdit:focus { border: 2px solid #e67e22; }"
        )
        layout.addWidget(self.password)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(
            "QPushButton { background-color: #95a5a6; color: white; border: none; "
            "border-radius: 8px; padding: 10px 20px; font-weight: bold; }"
            "QPushButton:hover { background-color: #7f8c8d; }"
        )
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("OK")
        ok_btn.setDefault(True)
        ok_btn.setStyleSheet(
            "QPushButton { background-color: #e67e22; color: white; border: none; "
            "border-radius: 8px; padding: 10px 20px; font-weight: bold; }"
            "QPushButton:hover { background-color: #d35400; }"
        )
        ok_btn.clicked.connect(self.verify_password)
        btn_layout.addWidget(ok_btn)

        layout.addLayout(btn_layout)

    def verify_password(self):
        password = self.password.text()
        if not password:
            QMessageBox.warning(self, "Error", "Please enter a password!")
            return

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        user = self.parent().db.fetchone(
            "SELECT * FROM users WHERE username = ? AND password_hash = ?",
            ("admin", password_hash)
        )

        if user:
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Incorrect password!")
            self.password.clear()
