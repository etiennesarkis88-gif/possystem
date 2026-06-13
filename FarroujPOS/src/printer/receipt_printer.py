# -*- coding: utf-8 -*-
"""
Receipt Printer - Thermal printer support using ESC/POS
"""

import os
import sys
from datetime import datetime

try:
    from escpos.printer import Usb, Serial, Network
    from escpos.exceptions import Error as ESCPOSError
    ESCPOS_AVAILABLE = True
except ImportError:
    ESCPOS_AVAILABLE = False

from PyQt6.QtWidgets import QMessageBox

class ReceiptPrinter:
    def __init__(self, db):
        self.db = db
        self.settings = self.load_settings()

    def load_settings(self):
        result = self.db.fetchone("SELECT * FROM receipt_settings LIMIT 1")
        return result or {}

    def get_printer(self):
        """Initialize printer connection using saved settings or auto-detect."""
        if not ESCPOS_AVAILABLE:
            return None

        # Load saved config
        import json
        config = self.load_printer_config()

        try:
            conn_type = config.get('conn_type', 'Auto Detect (USB)')

            if conn_type == 'Auto Detect (USB)' or conn_type == 'USB (Manual)':
                # Use saved VID/PID or defaults
                vid = int(config.get('vid', '0416'), 16) if config.get('vid') else 0x0416
                pid = int(config.get('pid', '5011'), 16) if config.get('pid') else 0x5011
                printer = Usb(vid, pid, 0)
                return printer

            elif conn_type == 'Serial (COM)':
                port = config.get('com_port', 'COM3')
                printer = Serial(port)
                return printer

            elif conn_type == 'Network (IP)':
                ip = config.get('ip', '192.168.1.100')
                printer = Network(ip)
                return printer

        except Exception as e:
            # Fallback to auto-detect
            try:
                printer = Usb(0x0416, 0x5011, 0)
                return printer
            except:
                try:
                    printer = Serial('COM3')
                    return printer
                except:
                    return None

        return None

    def load_printer_config(self):
        """Load saved printer configuration"""
        try:
            result = self.db.fetchone("SELECT value FROM settings WHERE key = 'printer_config'")
            if result and result.get('value'):
                import json
                return json.loads(result['value'])
        except:
            pass
        return {}

    def print_receipt(self, cart, currency='LBP', order_info=None):
        """Print receipt to thermal printer"""
        printer = self.get_printer()

        if not printer:
            QMessageBox.warning(None, "Printer Error",
                "Could not connect to printer.\nPlease check connections and try again.")
            return False

        try:
            printer.set(align='center')

            # Logo
            if self.settings.get('show_logo') and self.settings.get('logo_path'):
                if os.path.exists(self.settings['logo_path']):
                    printer.image(self.settings['logo_path'])

            # Business name
            printer.set(text_type='B', height=2, width=2)
            printer.text(self.settings.get('business_name', 'لقمة أبو جورج') + '\n')
            if self.settings.get('business_name_ar'):
                printer.text(self.settings['business_name_ar'] + '\n')

            printer.set(text_type='NORMAL', height=1, width=1)
            printer.text('─' * 32 + '\n')

            # Order info
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            printer.text(f"Date: {now}\n")
            if order_info:
                printer.text(f"Order: {order_info.get('order_number', 'N/A')}\n")
                if order_info.get('table_number'):
                    printer.text(f"Table: {order_info['table_number']}\n")
            printer.text('─' * 32 + '\n')

            # Items
            printer.set(align='left')
            for item in cart:
                name = item['name_en']
                if item.get('name_ar'):
                    name += f" ({item['name_ar']})"

                qty = item['qty']
                if currency == 'LBP':
                    price = item['price_lbp'] + item.get('extras_price_lbp', 0)
                    line = f"{name[:20]:<20} x{qty} {price*qty:>8,.0f}\n"
                else:
                    price = item['price_usd'] + item.get('extras_price_usd', 0)
                    line = f"{name[:20]:<20} x{qty} ${price*qty:>7.2f}\n"

                printer.text(line)

                # Show removed ingredients
                if item.get('removed_ingredients'):
                    removed = ", ".join(item['removed_ingredients'])
                    printer.text(f"  [-] NO: {removed}\n")

                # Show extras
                if item.get('selected_extras'):
                    extras = ", ".join(item['selected_extras'])
                    printer.text(f"  [+] Extras: {extras}\n")

                # Show instructions
                if item.get('instructions'):
                    printer.text(f"  >> {item['instructions']}\n")

            printer.set(align='center')
            printer.text('─' * 32 + '\n')

            # Totals
            subtotal = sum(item['price_lbp' if currency == 'LBP' else 'price_usd'] * item['qty']
                          for item in cart)
            total = subtotal

            printer.set(align='right')
            if currency == 'LBP':
                printer.text(f"Subtotal: {subtotal:,.0f} LBP\n")
                printer.set(text_type='B', height=2, width=1)
                printer.text(f"TOTAL: {total:,.0f} LBP\n")
            else:
                printer.text(f"Subtotal: ${subtotal:.2f}\n")
                printer.set(text_type='B', height=2, width=1)
                printer.text(f"TOTAL: ${total:.2f}\n")

            printer.set(text_type='NORMAL', height=1, width=1)
            printer.set(align='center')
            printer.text('─' * 32 + '\n')

            # Footer
            if self.settings.get('footer_text'):
                printer.text(self.settings['footer_text'] + '\n')
            if self.settings.get('footer_text_ar'):
                printer.text(self.settings['footer_text_ar'] + '\n')

            # QR Code
            if self.settings.get('show_qr_code'):
                printer.qr("Farrouj POS - Thank you for your visit!")

            printer.cut()
            # FIXED: Wrap close() in try/except
            try:
                printer.close()
            except:
                pass

            QMessageBox.information(None, "Success", "Receipt printed successfully!")
            return True

        except Exception as e:
            QMessageBox.critical(None, "Print Error", f"Failed to print: {str(e)}")
            return False
