# -*- coding: utf-8 -*-
"""
Settings Widget - Configure business info, currencies, receipt, and data reset
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox,
    QComboBox, QCheckBox, QFileDialog, QMessageBox, QGroupBox,
    QTabWidget, QTextEdit, QFrame, QDialog, QDialogButtonBox
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
        self.apply_light_theme()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("⚙️ Settings")
        title.setObjectName("page_title")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        layout.addWidget(title)

        # Tabs
        tabs = QTabWidget()
        tabs.setObjectName("settings_tabs")

        # Business Info Tab
        tabs.addTab(self.create_business_tab(), "Business Info")

        # Currency Tab
        tabs.addTab(self.create_currency_tab(), "Currency")

        # Receipt Tab
        tabs.addTab(self.create_receipt_tab(), "Receipt")

        # Data Management Tab
        tabs.addTab(self.create_data_tab(), "Data Management")

        layout.addWidget(tabs)

    def create_business_tab(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(15)

        self.business_name = QLineEdit()
        self.business_name.setPlaceholderText("Business Name (English)")
        layout.addRow("Business Name (EN):", self.business_name)

        self.business_name_ar = QLineEdit()
        self.business_name_ar.setPlaceholderText("اسم المحل")
        self.business_name_ar.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        layout.addRow("Business Name (AR):", self.business_name_ar)

        self.address = QLineEdit()
        self.address.setPlaceholderText("Business Address")
        layout.addRow("Address:", self.address)

        self.phone = QLineEdit()
        self.phone.setPlaceholderText("+961 XX XXX XXX")
        layout.addRow("Phone:", self.phone)

        # Logo selection
        logo_layout = QHBoxLayout()
        self.logo_path = QLineEdit()
        self.logo_path.setReadOnly(True)
        self.logo_path.setPlaceholderText("No logo selected")
        logo_layout.addWidget(self.logo_path)

        logo_btn = QPushButton("📁 Browse")
        logo_btn.clicked.connect(self.choose_logo)
        logo_layout.addWidget(logo_btn)

        layout.addRow("Logo:", logo_layout)

        # Preview
        self.logo_preview = QLabel("No Logo")
        self.logo_preview.setFixedSize(150, 150)
        self.logo_preview.setStyleSheet("border: 2px dashed #ccc; border-radius: 8px;")
        self.logo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addRow("Preview:", self.logo_preview)

        save_btn = QPushButton("💾 Save Business Info")
        save_btn.setObjectName("save_btn")
        save_btn.clicked.connect(self.save_business_settings)
        layout.addRow(save_btn)

        return widget

    def create_currency_tab(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(15)

        self.use_lbp = QCheckBox("Enable Lebanese Pound (LBP)")
        self.use_lbp.setChecked(True)
        layout.addRow(self.use_lbp)

        self.use_usd = QCheckBox("Enable US Dollar (USD)")
        self.use_usd.setChecked(True)
        layout.addRow(self.use_usd)

        self.exchange_rate = QDoubleSpinBox()
        self.exchange_rate.setRange(1000, 500000)
        self.exchange_rate.setDecimals(0)
        self.exchange_rate.setSuffix(" LBP per 1 USD")
        self.exchange_rate.setValue(90000)
        layout.addRow("Exchange Rate:", self.exchange_rate)

        self.default_currency = QComboBox()
        self.default_currency.addItems(["LBP", "USD"])
        layout.addRow("Default Currency:", self.default_currency)

        save_btn = QPushButton("💾 Save Currency Settings")
        save_btn.setObjectName("save_btn")
        save_btn.clicked.connect(self.save_currency_settings)
        layout.addRow(save_btn)

        return widget

    def create_receipt_tab(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(15)

        self.header_text = QTextEdit()
        self.header_text.setMaximumHeight(60)
        self.header_text.setPlaceholderText("Custom header text for receipts")
        layout.addRow("Header Text:", self.header_text)

        self.footer_text = QLineEdit()
        self.footer_text.setPlaceholderText("Thank you for your visit!")
        layout.addRow("Footer Text (EN):", self.footer_text)

        self.footer_text_ar = QLineEdit()
        self.footer_text_ar.setPlaceholderText("شكراً لزيارتكم!")
        self.footer_text_ar.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        layout.addRow("Footer Text (AR):", self.footer_text_ar)

        self.show_logo = QCheckBox("Show Logo on Receipt")
        self.show_logo.setChecked(True)
        layout.addRow(self.show_logo)

        self.show_qr = QCheckBox("Show QR Code on Receipt")
        layout.addRow(self.show_qr)

        self.paper_width = QSpinBox()
        self.paper_width.setRange(58, 80)
        self.paper_width.setSuffix(" mm")
        self.paper_width.setValue(80)
        layout.addRow("Paper Width:", self.paper_width)

        save_btn = QPushButton("💾 Save Receipt Settings")
        save_btn.setObjectName("save_btn")
        save_btn.clicked.connect(self.save_receipt_settings)
        layout.addRow(save_btn)

        return widget

    def create_data_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Warning
        warning = QLabel("⚠️ Danger Zone")
        warning.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        warning.setStyleSheet("color: #E74C3C;")
        layout.addWidget(warning)

        warning_text = QLabel(
            "These actions are irreversible. All data will be permanently deleted. "
            "Make sure to backup any important information before proceeding."
        )
        warning_text.setWordWrap(True)
        warning_text.setStyleSheet("color: #666;")
        layout.addWidget(warning_text)

        layout.addSpacing(20)

        # Reset options
        reset_group = QGroupBox("Reset Data")
        reset_layout = QVBoxLayout(reset_group)

        reset_sales_btn = QPushButton("🗑️ Reset Sales Data Only")
        reset_sales_btn.setObjectName("danger_btn")
        reset_sales_btn.clicked.connect(lambda: self.reset_data("sales"))
        reset_layout.addWidget(reset_sales_btn)

        reset_all_btn = QPushButton("💣 Reset ALL Data (Factory Reset)")
        reset_all_btn.setObjectName("danger_btn")
        reset_all_btn.clicked.connect(lambda: self.reset_data("all"))
        reset_layout.addWidget(reset_all_btn)

        layout.addWidget(reset_group)

        # Backup/Export
        backup_group = QGroupBox("Backup & Export")
        backup_layout = QVBoxLayout(backup_group)

        export_btn = QPushButton("📤 Export Database")
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
            pixmap = QPixmap(file_path).scaled(140, 140, Qt.AspectRatioMode.KeepAspectRatio)
            self.logo_preview.setPixmap(pixmap)

    def load_settings(self):
        # Business settings
        business = self.db.fetchone("SELECT * FROM receipt_settings LIMIT 1")
        if business:
            self.business_name.setText(business.get('business_name', ''))
            self.business_name_ar.setText(business.get('business_name_ar', ''))
            self.address.setText(business.get('address', ''))
            self.phone.setText(business.get('phone', ''))
            if business.get('logo_path') and os.path.exists(business['logo_path']):
                self.logo_path.setText(business['logo_path'])
                pixmap = QPixmap(business['logo_path']).scaled(140, 140, Qt.AspectRatioMode.KeepAspectRatio)
                self.logo_preview.setPixmap(pixmap)

        # Currency settings
        currency = self.db.fetchone("SELECT * FROM currency_settings LIMIT 1")
        if currency:
            self.use_lbp.setChecked(bool(currency.get('use_lbp', 1)))
            self.use_usd.setChecked(bool(currency.get('use_usd', 1)))
            self.exchange_rate.setValue(currency.get('exchange_rate', 90000))
            index = self.default_currency.findText(currency.get('default_currency', 'LBP'))
            if index >= 0:
                self.default_currency.setCurrentIndex(index)

        # Receipt settings
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
                # Factory reset - keep settings but remove all data
                self.db.execute("DELETE FROM orders")
                self.db.execute("DELETE FROM order_items")
                self.db.execute("DELETE FROM menu_items")
                self.db.execute("DELETE FROM categories")
                self.db.execute("DELETE FROM inventory")
                self.db.execute("DELETE FROM daily_sales")
                # Re-insert defaults
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


class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Authentication Required")
        self.setMinimumWidth(300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Enter admin password to proceed:"))

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText("Password")
        layout.addWidget(self.password)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.verify_password)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def verify_password(self):
        password = self.password.text()
        if not password:
            QMessageBox.warning(self, "Error", "Please enter a password!")
            return

        import hashlib
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
