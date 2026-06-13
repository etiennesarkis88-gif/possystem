# -*- coding: utf-8 -*-
"""
Item Customization Dialog - Shows ingredients and extras when adding item to cart
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, 
    QPushButton, QScrollArea, QWidget, QFrame, QTextEdit,
    QSpinBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class ItemCustomizationDialog(QDialog):
    def __init__(self, item, currency='LBP', exchange_rate=90000, parent=None):
        super().__init__(parent)
        self.item = item
        self.currency = currency
        self.exchange_rate = exchange_rate
        self.setWindowTitle(f"Customize - {item['name_en']}")
        self.setMinimumWidth(450)
        self.setMaximumHeight(700)

        self.ingredient_checks = {}
        self.extra_checks = {}
        self.result = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Item header
        header = QLabel(f"🍽️ {self.item['name_en']}")
        header.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(header)

        if self.item.get('name_ar'):
            header_ar = QLabel(self.item['name_ar'])
            header_ar.setFont(QFont("Segoe UI", 12))
            header_ar.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            header_ar.setAlignment(Qt.AlignmentFlag.AlignRight)
            layout.addWidget(header_ar)

        # Price display
        if self.currency == 'LBP':
            price_text = f"{self.item['price_lbp']:,.0f} LBP"
        else:
            price_text = f"${self.item['price_usd']:.2f}"

        price_label = QLabel(f"Base Price: {price_text}")
        price_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        price_label.setStyleSheet("color: #e67e22;")
        layout.addWidget(price_label)

        layout.addSpacing(10)

        # Scroll area for ingredients and extras
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(15)

        # Ingredients Section
        if self.item.get('ingredients'):
            ing_frame = QFrame()
            ing_frame.setObjectName("section_frame")
            ing_layout = QVBoxLayout(ing_frame)
            ing_layout.setSpacing(8)

            ing_title = QLabel("🥗 Ingredients (Uncheck to remove)")
            ing_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            ing_layout.addWidget(ing_title)

            ingredients = [i.strip() for i in self.item['ingredients'].split(',') if i.strip()]
            for ing in ingredients:
                chk = QCheckBox(ing)
                chk.setChecked(True)
                chk.setFont(QFont("Segoe UI", 11))
                self.ingredient_checks[ing] = chk
                ing_layout.addWidget(chk)

            scroll_layout.addWidget(ing_frame)

        # Extras Section
        if self.item.get('extras'):
            ext_frame = QFrame()
            ext_frame.setObjectName("section_frame")
            ext_layout = QVBoxLayout(ext_frame)
            ext_layout.setSpacing(8)

            ext_title = QLabel("➕ Extras (Check to add)")
            ext_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            ext_layout.addWidget(ext_title)

            extras = self.parse_extras(self.item['extras'])
            for extra_name, extra_price_lbp, extra_price_usd in extras:
                if self.currency == 'LBP':
                    price_str = f"+{extra_price_lbp:,.0f} LBP"
                else:
                    price_str = f"+${extra_price_usd:.2f}"

                chk = QCheckBox(f"{extra_name}  ({price_str})")
                chk.setFont(QFont("Segoe UI", 11))
                chk.setProperty("extra_name", extra_name)
                chk.setProperty("price_lbp", extra_price_lbp)
                chk.setProperty("price_usd", extra_price_usd)
                self.extra_checks[extra_name] = chk
                ext_layout.addWidget(chk)

            scroll_layout.addWidget(ext_frame)

        # Special Instructions
        inst_frame = QFrame()
        inst_frame.setObjectName("section_frame")
        inst_layout = QVBoxLayout(inst_frame)

        inst_title = QLabel("📝 Special Instructions")
        inst_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        inst_layout.addWidget(inst_title)

        self.instructions = QTextEdit()
        self.instructions.setPlaceholderText("Any special requests...")
        self.instructions.setMaximumHeight(60)
        inst_layout.addWidget(self.instructions)

        scroll_layout.addWidget(inst_frame)
        scroll_layout.addStretch()

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Total price display
        self.total_label = QLabel("Total: " + price_text)
        self.total_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.total_label.setStyleSheet("color: #27ae60;")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.total_label)

        # Update total when extras change
        for chk in self.extra_checks.values():
            chk.stateChanged.connect(self.update_total)

        # Buttons
        btn_layout = QHBoxLayout()

        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setObjectName("cancel_btn")
        cancel_btn.clicked.connect(self.reject)

        add_btn = QPushButton("✅ Add to Order")
        add_btn.setObjectName("add_btn")
        add_btn.setDefault(True)
        add_btn.clicked.connect(self.confirm)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(add_btn)
        layout.addLayout(btn_layout)

        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLabel {
                color: #2c3e50;
                background-color: transparent;
            }
            #section_frame {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 10px;
            }
            QCheckBox {
                font-size: 12px;
                padding: 5px;
                color: #2c3e50;
                background-color: transparent;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                color: #333;
                background-color: #ffffff;
            }
            #add_btn {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            #add_btn:hover {
                background-color: #219a52;
            }
            #cancel_btn {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
            }
            #cancel_btn:hover {
                background-color: #c0392b;
            }
        """)

    def parse_extras(self, extras_str):
        """Parse extras string: 'Extra Cheese:50000:0.55, Extra Sauce:25000:0.28'"""
        extras = []
        if not extras_str:
            return extras

        for part in extras_str.split(','):
            part = part.strip()
            if not part:
                continue

            # Format: "Name:price_lbp" or "Name:price_lbp:price_usd"
            parts = part.split(':')
            if len(parts) >= 2:
                name = parts[0].strip()
                try:
                    price_lbp = float(parts[1].strip())
                except:
                    price_lbp = 0

                price_usd = price_lbp / self.exchange_rate if self.exchange_rate else 0
                if len(parts) >= 3:
                    try:
                        price_usd = float(parts[2].strip())
                    except:
                        pass

                extras.append((name, price_lbp, price_usd))

        return extras

    def update_total(self):
        base_price = self.item['price_lbp'] if self.currency == 'LBP' else self.item['price_usd']
        extras_total = 0

        for chk in self.extra_checks.values():
            if chk.isChecked():
                if self.currency == 'LBP':
                    extras_total += chk.property("price_lbp")
                else:
                    extras_total += chk.property("price_usd")

        total = base_price + extras_total

        if self.currency == 'LBP':
            self.total_label.setText(f"Total: {total:,.0f} LBP")
        else:
            self.total_label.setText(f"Total: ${total:.2f}")

    def confirm(self):
        # Get removed ingredients
        removed = []
        for ing, chk in self.ingredient_checks.items():
            if not chk.isChecked():
                removed.append(ing)

        # Get selected extras
        selected_extras = []
        extras_price_lbp = 0
        extras_price_usd = 0

        for extra_name, chk in self.extra_checks.items():
            if chk.isChecked():
                selected_extras.append(extra_name)
                extras_price_lbp += chk.property("price_lbp")
                extras_price_usd += chk.property("price_usd")

        self.result = {
            'removed_ingredients': removed,
            'selected_extras': selected_extras,
            'extras_price_lbp': extras_price_lbp,
            'extras_price_usd': extras_price_usd,
            'instructions': self.instructions.toPlainText().strip()
        }

        self.accept()
