# -*- coding: utf-8 -*-
"""
Menu Widget - Manage categories and menu items
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QDialog, QFormLayout, QTextEdit, QFileDialog,
    QTabWidget, QFrame, QScrollArea, QColorDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPixmap
import os
import re


def normalize_extras_text(raw_text):
    extras = []
    for line in raw_text.replace("\n", ",").split(","):
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(":") if p.strip()]
        if len(parts) >= 3:
            name, lbp, usd = parts[0], parts[1], parts[2]
        elif len(parts) == 2:
            name, lbp = parts[0], parts[1]
            try:
                usd = str(round(float(lbp) / 90000, 2))
            except:
                usd = "0"
        else:
            m = re.match(r"^(.*?)(\d+(?:\.\d+)?)$", line)
            if not m:
                continue
            name = m.group(1).strip()
            lbp = m.group(2).strip()
            try:
                usd = str(round(float(lbp) / 90000, 2))
            except:
                usd = "0"
        extras.append(f"{name}:{lbp}:{usd}")
    return ", ".join(extras)


class MenuWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.load_data()

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

        title = QLabel("Menu Management")
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

        tabs.addTab(self.create_categories_tab(), "Categories")
        tabs.addTab(self.create_items_tab(), "Menu Items")

        layout.addWidget(tabs)
        layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def create_categories_tab(self):
        widget = QWidget()
        widget.setStyleSheet("background-color: #ffffff;")
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        toolbar = QHBoxLayout()
        self.add_cat_btn = QPushButton("Add Category")
        self.add_cat_btn.setStyleSheet(
            "QPushButton { background-color: #e67e22; color: white; border: none; "
            "border-radius: 8px; padding: 10px 20px; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background-color: #d35400; }"
        )
        self.add_cat_btn.clicked.connect(self.add_category)
        toolbar.addWidget(self.add_cat_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.cat_table = QTableWidget()
        self.cat_table.setColumnCount(6)
        self.cat_table.setHorizontalHeaderLabels([
            "Name (EN)", "Name (AR)", "Color", "Order", "Active", "Actions"
        ])
        # FIXED: better column sizing
        header = self.cat_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.cat_table.setColumnWidth(2, 60)
        self.cat_table.setColumnWidth(3, 60)
        self.cat_table.setColumnWidth(4, 60)
        self.cat_table.setColumnWidth(5, 120)
        self.cat_table.setStyleSheet(
            "QTableWidget { background-color: #ffffff; border: 1px solid #e0e0e0; "
            "border-radius: 8px; gridline-color: #f0f0f0; }"
            "QTableWidget::item { padding: 10px; border-bottom: 1px solid #f0f0f0; color: #333; }"
            "QHeaderView::section { background-color: #f8f9fa; border: none; padding: 10px; "
            "font-weight: bold; color: #555; border-bottom: 2px solid #e0e0e0; }"
        )
        layout.addWidget(self.cat_table)
        layout.addStretch()

        return widget

    def create_items_tab(self):
        widget = QWidget()
        widget.setStyleSheet("background-color: #ffffff;")
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        self.category_filter = QComboBox()
        self.category_filter.setStyleSheet(
            "QComboBox { background-color: #ffffff; color: #333; border: 2px solid #e0e0e0; "
            "border-radius: 8px; padding: 8px 12px; font-size: 13px; }"
        )
        self.category_filter.addItem("All Categories")
        self.category_filter.currentIndexChanged.connect(self.filter_items)
        toolbar.addWidget(QLabel("Filter:"))
        toolbar.addWidget(self.category_filter)

        self.add_item_btn = QPushButton("Add Item")
        self.add_item_btn.setStyleSheet(
            "QPushButton { background-color: #e67e22; color: white; border: none; "
            "border-radius: 8px; padding: 10px 20px; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background-color: #d35400; }"
        )
        self.add_item_btn.clicked.connect(self.add_item)
        toolbar.addWidget(self.add_item_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(8)
        self.items_table.setHorizontalHeaderLabels([
            "Name (EN)", "Name (AR)", "Category", "Price (LBP)",
            "Price (USD)", "Available", "Popular", "Actions"
        ])
        # FIXED: better column sizing
        header = self.items_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        self.items_table.setColumnWidth(3, 90)
        self.items_table.setColumnWidth(4, 90)
        self.items_table.setColumnWidth(5, 80)
        self.items_table.setColumnWidth(6, 70)
        self.items_table.setColumnWidth(7, 120)
        self.items_table.setStyleSheet(
            "QTableWidget { background-color: #ffffff; border: 1px solid #e0e0e0; "
            "border-radius: 8px; gridline-color: #f0f0f0; }"
            "QTableWidget::item { padding: 10px; border-bottom: 1px solid #f0f0f0; color: #333; }"
            "QHeaderView::section { background-color: #f8f9fa; border: none; padding: 10px; "
            "font-weight: bold; color: #555; border-bottom: 2px solid #e0e0e0; }"
        )
        layout.addWidget(self.items_table)
        layout.addStretch()

        return widget

    def load_data(self):
        self.load_categories()
        self.load_items()

    def load_categories(self):
        categories = self.db.fetchall(
            "SELECT * FROM categories ORDER BY sort_order"
        )

        self.cat_table.setRowCount(len(categories))
        self.category_filter.clear()
        self.category_filter.addItem("All Categories")

        for i, cat in enumerate(categories):
            self.cat_table.setItem(i, 0, QTableWidgetItem(cat['name_en']))
            self.cat_table.setItem(i, 1, QTableWidgetItem(cat['name_ar'] or ''))

            color_btn = QPushButton()
            color_btn.setFixedSize(30, 20)
            color_btn.setStyleSheet(f"background-color: {cat['color']}; border: none; border-radius: 4px;")
            self.cat_table.setCellWidget(i, 2, color_btn)

            self.cat_table.setItem(i, 3, QTableWidgetItem(str(cat['sort_order'])))
            self.cat_table.setItem(i, 4, QTableWidgetItem("Yes" if cat['is_active'] else "No"))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 0, 4, 0)
            actions_layout.setSpacing(6)

            edit_btn = QPushButton("Edit")
            edit_btn.setFixedSize(50, 28)
            edit_btn.setStyleSheet(
                "QPushButton { background-color: #3498db; color: white; border: none; "
                "border-radius: 4px; font-size: 11px; font-weight: bold; }"
                "QPushButton:hover { background-color: #2980b9; }"
            )
            edit_btn.clicked.connect(lambda checked, cid=cat['id']: self.edit_category(cid))

            delete_btn = QPushButton("Del")
            delete_btn.setFixedSize(50, 28)
            delete_btn.setStyleSheet(
                "QPushButton { background-color: #e74c3c; color: white; border: none; "
                "border-radius: 4px; font-size: 11px; font-weight: bold; }"
                "QPushButton:hover { background-color: #c0392b; }"
            )
            delete_btn.clicked.connect(lambda checked, cid=cat['id']: self.delete_category(cid))

            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            self.cat_table.setCellWidget(i, 5, actions_widget)
            self.cat_table.setRowHeight(i, 44)

            self.category_filter.addItem(cat['name_en'], cat['id'])

    def load_items(self):
        items = self.db.fetchall("""
            SELECT mi.*, c.name_en as category_name
            FROM menu_items mi
            LEFT JOIN categories c ON mi.category_id = c.id
            ORDER BY mi.category_id, mi.sort_order
        """)

        self.items_table.setRowCount(len(items))

        for i, item in enumerate(items):
            self.items_table.setItem(i, 0, QTableWidgetItem(item['name_en']))
            self.items_table.setItem(i, 1, QTableWidgetItem(item['name_ar'] or ''))
            self.items_table.setItem(i, 2, QTableWidgetItem(item['category_name'] or ''))
            self.items_table.setItem(i, 3, QTableWidgetItem(f"{item['price_lbp']:,.0f}"))
            self.items_table.setItem(i, 4, QTableWidgetItem(f"${item['price_usd']:.2f}"))
            self.items_table.setItem(i, 5, QTableWidgetItem("Yes" if item['is_available'] else "No"))
            self.items_table.setItem(i, 6, QTableWidgetItem("Yes" if item['is_popular'] else "No"))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 0, 4, 0)
            actions_layout.setSpacing(6)

            edit_btn = QPushButton("Edit")
            edit_btn.setFixedSize(50, 28)
            edit_btn.setStyleSheet(
                "QPushButton { background-color: #3498db; color: white; border: none; "
                "border-radius: 4px; font-size: 11px; font-weight: bold; }"
                "QPushButton:hover { background-color: #2980b9; }"
            )
            edit_btn.clicked.connect(lambda checked, iid=item['id']: self.edit_item(iid))

            delete_btn = QPushButton("Del")
            delete_btn.setFixedSize(50, 28)
            delete_btn.setStyleSheet(
                "QPushButton { background-color: #e74c3c; color: white; border: none; "
                "border-radius: 4px; font-size: 11px; font-weight: bold; }"
                "QPushButton:hover { background-color: #c0392b; }"
            )
            delete_btn.clicked.connect(lambda checked, iid=item['id']: self.delete_item(iid))

            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            self.items_table.setCellWidget(i, 7, actions_widget)
            self.items_table.setRowHeight(i, 44)

    def filter_items(self):
        cat_id = self.category_filter.currentData()
        if cat_id:
            items = self.db.fetchall("""
                SELECT mi.*, c.name_en as category_name
                FROM menu_items mi
                LEFT JOIN categories c ON mi.category_id = c.id
                WHERE mi.category_id = ?
                ORDER BY mi.sort_order
            """, (cat_id,))
        else:
            items = self.db.fetchall("""
                SELECT mi.*, c.name_en as category_name
                FROM menu_items mi
                LEFT JOIN categories c ON mi.category_id = c.id
                ORDER BY mi.category_id, mi.sort_order
            """)

        self.items_table.setRowCount(len(items))
        for i, item in enumerate(items):
            self.items_table.setItem(i, 0, QTableWidgetItem(item['name_en']))
            self.items_table.setItem(i, 1, QTableWidgetItem(item['name_ar'] or ''))
            self.items_table.setItem(i, 2, QTableWidgetItem(item['category_name'] or ''))
            self.items_table.setItem(i, 3, QTableWidgetItem(f"{item['price_lbp']:,.0f}"))
            self.items_table.setItem(i, 4, QTableWidgetItem(f"${item['price_usd']:.2f}"))
            self.items_table.setItem(i, 5, QTableWidgetItem("Yes" if item['is_available'] else "No"))
            self.items_table.setItem(i, 6, QTableWidgetItem("Yes" if item['is_popular'] else "No"))

    def add_category(self):
        dialog = CategoryDialog(self.db, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_categories()
            self.load_items()

    def edit_category(self, cat_id):
        dialog = CategoryDialog(self.db, cat_id, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_categories()

    def delete_category(self, cat_id):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Delete this category? All items in it will also be deleted.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.execute("DELETE FROM inventory WHERE item_id IN (SELECT id FROM menu_items WHERE category_id = ?)", (cat_id,))
                self.db.execute("DELETE FROM menu_items WHERE category_id = ?", (cat_id,))
                self.db.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
                QMessageBox.information(self, "Success", "Category deleted!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed: {str(e)}")
            self.load_categories()
            self.load_items()

    def add_item(self):
        dialog = ItemDialog(self.db, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_items()

    def edit_item(self, item_id):
        dialog = ItemDialog(self.db, item_id, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_items()

    def delete_item(self, item_id):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Delete this item?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.execute("DELETE FROM inventory WHERE item_id = ?", (item_id,))
                self.db.execute("DELETE FROM menu_items WHERE id = ?", (item_id,))
                QMessageBox.information(self, "Success", "Item deleted!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed: {str(e)}")
            self.load_items()


class CategoryDialog(QDialog):
    def __init__(self, db, cat_id=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.cat_id = cat_id
        self.setWindowTitle("Add Category" if not cat_id else "Edit Category")
        self.setMinimumWidth(400)
        self.init_ui()
        if cat_id:
            self.load_data()

    def init_ui(self):
        self.setStyleSheet("background-color: #f5f6fa;")
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        input_style = (
            "QLineEdit { background-color: #ffffff; color: #333; border: 2px solid #e0e0e0; "
            "border-radius: 8px; padding: 10px 12px; font-size: 13px; }"
            "QLineEdit:focus { border: 2px solid #e67e22; }"
        )

        self.name_en = QLineEdit()
        self.name_en.setPlaceholderText("English name (e.g., Farrouj)")
        self.name_en.setStyleSheet(input_style)
        form.addRow("Name (EN):", self.name_en)

        self.name_ar = QLineEdit()
        self.name_ar.setPlaceholderText("Arabic name")
        self.name_ar.setStyleSheet(input_style)
        form.addRow("Name (AR):", self.name_ar)

        self.color_btn = QPushButton("Choose Color")
        self.color_btn.clicked.connect(self.choose_color)
        self.selected_color = "#E74C3C"
        self.color_btn.setStyleSheet(
            f"background-color: {self.selected_color}; color: white; border: none; "
            "border-radius: 8px; padding: 10px;"
        )
        form.addRow("Color:", self.color_btn)

        spinbox_style = (
            "QSpinBox { background-color: #ffffff; color: #333; border: 2px solid #e0e0e0; "
            "border-radius: 8px; padding: 8px; font-size: 13px; }"
            "QSpinBox:focus { border: 2px solid #e67e22; }"
        )

        self.sort_order = QSpinBox()
        self.sort_order.setRange(0, 999)
        self.sort_order.setStyleSheet(spinbox_style)
        form.addRow("Sort Order:", self.sort_order)

        self.is_active = QComboBox()
        self.is_active.addItems(["Active", "Inactive"])
        self.is_active.setStyleSheet(
            "QComboBox { background-color: #ffffff; color: #333; border: 2px solid #e0e0e0; "
            "border-radius: 8px; padding: 8px 12px; font-size: 13px; }"
        )
        form.addRow("Status:", self.is_active)

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

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = color.name()
            self.color_btn.setStyleSheet(
                f"background-color: {self.selected_color}; color: white; border: none; "
                "border-radius: 8px; padding: 10px;"
            )

    def load_data(self):
        cat = self.db.fetchone("SELECT * FROM categories WHERE id = ?", (self.cat_id,))
        if cat:
            self.name_en.setText(cat['name_en'])
            self.name_ar.setText(cat['name_ar'] or '')
            self.selected_color = cat['color']
            self.color_btn.setStyleSheet(
                f"background-color: {self.selected_color}; color: white; border: none; "
                "border-radius: 8px; padding: 10px;"
            )
            self.sort_order.setValue(cat['sort_order'])
            self.is_active.setCurrentIndex(0 if cat['is_active'] else 1)

    def save(self):
        name_en = self.name_en.text().strip()
        if not name_en:
            QMessageBox.warning(self, "Error", "English name is required!")
            return

        data = {
            'name_en': name_en,
            'name_ar': self.name_ar.text().strip(),
            'color': self.selected_color,
            'sort_order': self.sort_order.value(),
            'is_active': 1 if self.is_active.currentIndex() == 0 else 0
        }

        if self.cat_id:
            self.db.execute("""
                UPDATE categories SET name_en=?, name_ar=?, color=?, sort_order=?, is_active=?
                WHERE id=?
            """, (data['name_en'], data['name_ar'], data['color'],
                data['sort_order'], data['is_active'], self.cat_id))
        else:
            self.db.execute("""
                INSERT INTO categories (name_en, name_ar, color, sort_order, is_active)
                VALUES (?, ?, ?, ?, ?)
            """, (data['name_en'], data['name_ar'], data['color'],
                data['sort_order'], data['is_active']))

        self.accept()


class ItemDialog(QDialog):
    def __init__(self, db, item_id=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.item_id = item_id
        self.image_path = None
        self.setWindowTitle("Add Menu Item" if not item_id else "Edit Menu Item")
        self.setMinimumWidth(450)
        self.init_ui()
        if item_id:
            self.load_data()

    def init_ui(self):
        self.setStyleSheet("background-color: #f5f6fa;")
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: #f5f6fa; border: none;")

        content = QWidget()
        layout = QFormLayout(content)
        layout.setSpacing(12)
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

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

        spinbox_style = (
            "QSpinBox, QDoubleSpinBox { background-color: #ffffff; color: #333; "
            "border: 2px solid #e0e0e0; border-radius: 8px; padding: 8px; font-size: 13px; "
            "min-height: 18px; }"
            "QSpinBox:focus, QDoubleSpinBox:focus { border: 2px solid #e67e22; }"
        )

        combo_style = (
            "QComboBox { background-color: #ffffff; color: #333; border: 2px solid #e0e0e0; "
            "border-radius: 8px; padding: 8px 12px; font-size: 13px; min-height: 18px; }"
            "QComboBox:focus { border: 2px solid #e67e22; }"
        )

        self.name_en = QLineEdit()
        self.name_en.setPlaceholderText("English name")
        self.name_en.setStyleSheet(input_style)
        layout.addRow("Name (EN):", self.name_en)

        self.name_ar = QLineEdit()
        self.name_ar.setPlaceholderText("Arabic name")
        self.name_ar.setStyleSheet(input_style)
        layout.addRow("Name (AR):", self.name_ar)

        self.desc_en = QTextEdit()
        self.desc_en.setMaximumHeight(60)
        self.desc_en.setPlaceholderText("English description")
        self.desc_en.setStyleSheet(textedit_style)
        layout.addRow("Description (EN):", self.desc_en)

        self.desc_ar = QTextEdit()
        self.desc_ar.setMaximumHeight(60)
        self.desc_ar.setPlaceholderText("Arabic description")
        self.desc_ar.setStyleSheet(textedit_style)
        layout.addRow("Description (AR):", self.desc_ar)

        self.ingredients = QTextEdit()
        self.ingredients.setMaximumHeight(60)
        self.ingredients.setPlaceholderText("Comma-separated: Chicken, Garlic Sauce, Pickles, Lettuce")
        self.ingredients.setStyleSheet(textedit_style)
        layout.addRow("Ingredients:", self.ingredients)

        self.extras = QTextEdit()
        self.extras.setMaximumHeight(60)
        self.extras.setPlaceholderText("Format: Name:LBP:USD\nExample: cheese:90000:1.0, extra fries:45000:0.5")
        self.extras.setStyleSheet(textedit_style)
        layout.addRow("Extras (Name:LBP:USD):", self.extras)

        self.category = QComboBox()
        categories = self.db.fetchall("SELECT id, name_en FROM categories WHERE is_active = 1")
        for cat in categories:
            self.category.addItem(cat['name_en'], cat['id'])
        self.category.setStyleSheet(combo_style)
        layout.addRow("Category:", self.category)

        self.price_lbp = QDoubleSpinBox()
        self.price_lbp.setRange(0, 999999999)
        self.price_lbp.setDecimals(0)
        self.price_lbp.setSuffix(" LBP")
        self.price_lbp.setStyleSheet(spinbox_style)
        layout.addRow("Price (LBP):", self.price_lbp)

        self.price_usd = QDoubleSpinBox()
        self.price_usd.setRange(0, 99999)
        self.price_usd.setDecimals(2)
        self.price_usd.setSuffix(" USD")
        self.price_usd.setStyleSheet(spinbox_style)
        layout.addRow("Price (USD):", self.price_usd)

        self.cost_lbp = QDoubleSpinBox()
        self.cost_lbp.setRange(0, 999999999)
        self.cost_lbp.setDecimals(0)
        self.cost_lbp.setStyleSheet(spinbox_style)
        layout.addRow("Cost (LBP):", self.cost_lbp)

        self.image_btn = QPushButton("Choose Image")
        self.image_btn.setStyleSheet(
            "QPushButton { background-color: #3498db; color: white; border: none; "
            "border-radius: 8px; padding: 10px 20px; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background-color: #2980b9; }"
        )
        self.image_btn.clicked.connect(self.choose_image)
        layout.addRow("Image:", self.image_btn)

        self.is_available = QComboBox()
        self.is_available.addItems(["Available", "Not Available"])
        self.is_available.setStyleSheet(combo_style)
        layout.addRow("Availability:", self.is_available)

        self.is_popular = QComboBox()
        self.is_popular.addItems(["Regular", "Popular"])
        self.is_popular.setStyleSheet(combo_style)
        layout.addRow("Popularity:", self.is_popular)

        self.sort_order = QSpinBox()
        self.sort_order.setRange(0, 999)
        self.sort_order.setStyleSheet(spinbox_style)
        layout.addRow("Sort Order:", self.sort_order)

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
        layout.addRow(btn_layout)

        scroll.setWidget(content)
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(scroll)

    def choose_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.image_path = file_path
            self.image_btn.setText(os.path.basename(file_path))

    def load_data(self):
        item = self.db.fetchone("SELECT * FROM menu_items WHERE id = ?", (self.item_id,))
        if item:
            self.name_en.setText(item['name_en'])
            self.name_ar.setText(item['name_ar'] or '')
            self.desc_en.setPlainText(item['description_en'] or '')
            self.desc_ar.setPlainText(item['description_ar'] or '')
            self.ingredients.setPlainText(item['ingredients'] or '')
            self.extras.setPlainText(item['extras'] or '')

            index = self.category.findData(item['category_id'])
            if index >= 0:
                self.category.setCurrentIndex(index)

            self.price_lbp.setValue(item['price_lbp'] or 0)
            self.price_usd.setValue(item['price_usd'] or 0)
            self.cost_lbp.setValue(item['cost_lbp'] or 0)
            self.image_path = item['image_path']
            if self.image_path:
                self.image_btn.setText(os.path.basename(self.image_path))

            self.is_available.setCurrentIndex(0 if item['is_available'] else 1)
            self.is_popular.setCurrentIndex(1 if item['is_popular'] else 0)
            self.sort_order.setValue(item['sort_order'])

    def save(self):
        name_en = self.name_en.text().strip()
        if not name_en:
            QMessageBox.warning(self, "Error", "English name is required!")
            return

        data = {
            'name_en': name_en,
            'name_ar': self.name_ar.text().strip(),
            'description_en': self.desc_en.toPlainText().strip(),
            'description_ar': self.desc_ar.toPlainText().strip(),
            'ingredients': self.ingredients.toPlainText().strip(),
            'extras': normalize_extras_text(self.extras.toPlainText().strip()),
            'category_id': self.category.currentData(),
            'price_lbp': self.price_lbp.value(),
            'price_usd': self.price_usd.value(),
            'cost_lbp': self.cost_lbp.value(),
            'image_path': self.image_path,
            'is_available': 1 if self.is_available.currentIndex() == 0 else 0,
            'is_popular': 1 if self.is_popular.currentIndex() == 1 else 0,
            'sort_order': self.sort_order.value()
        }

        if self.item_id:
            self.db.execute("""
                UPDATE menu_items SET
                    name_en=?, name_ar=?, description_en=?, description_ar=?,
                    ingredients=?, extras=?, category_id=?, price_lbp=?, price_usd=?,
                    cost_lbp=?, image_path=?, is_available=?, is_popular=?, sort_order=?
                WHERE id=?
            """, (data['name_en'], data['name_ar'], data['description_en'], data['description_ar'],
                data['ingredients'], data['extras'], data['category_id'], data['price_lbp'],
                data['price_usd'], data['cost_lbp'], data['image_path'], data['is_available'],
                data['is_popular'], data['sort_order'], self.item_id))
        else:
            cursor = self.db.execute("""
                INSERT INTO menu_items (name_en, name_ar, description_en, description_ar,
                    ingredients, extras, category_id, price_lbp, price_usd, cost_lbp,
                    image_path, is_available, is_popular, sort_order)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (data['name_en'], data['name_ar'], data['description_en'], data['description_ar'],
                data['ingredients'], data['extras'], data['category_id'], data['price_lbp'],
                data['price_usd'], data['cost_lbp'], data['image_path'], data['is_available'],
                data['is_popular'], data['sort_order']))

            new_id = cursor.lastrowid
            self.db.execute("""
                INSERT INTO inventory (item_id, quantity, unit, min_stock)
                VALUES (?, 0, 'piece', 10)
            """, (new_id,))

        self.accept()
