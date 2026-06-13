# -*- coding: utf-8 -*-
"""
Thermal Printer Support - ESC/POS printing
"""

import os
import sys

try:
    import usb.core
    import usb.util
    HAS_USB = True
except ImportError:
    HAS_USB = False

try:
    import serial
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False

class ReceiptPrinter:
    """Thermal receipt printer using ESC/POS commands"""

    # Common USB Vendor IDs
    VENDORS = {
        'epson': 0x04b8,
        'zjiang': 0x0416,
        'xprinter': 0x1fc9,
        'gprinter': 0x6868,
    }

    ESC = b'\x1b'
    GS = b'\x1d'

    def __init__(self, db):
        self.db = db
        self.device = None
        self.paper_width = 80  # mm
        self.load_settings()

    def load_settings(self):
        result = self.db.fetchone("SELECT value FROM settings WHERE key = 'printer_config'")
        if result and result.get('value'):
            import json
            try:
                config = json.loads(result['value'])
                self.paper_width = int(config.get('paper_width', '80').replace('mm', ''))
            except:
                pass

    def find_printer(self):
        """Auto-detect USB thermal printer"""
        if not HAS_USB:
            return None

        for name, vid in self.VENDORS.items():
            device = usb.core.find(idVendor=vid)
            if device:
                return device
        return None

    def print_receipt(self, cart, currency):
        """Print receipt to thermal printer"""
        try:
            device = self.find_printer()
            if not device:
                # Try COM port fallback
                return self._print_via_com(cart, currency)

            # Configure device
            cfg = device.get_active_configuration()
            intf = cfg[(0,0)]
            ep = usb.util.find_descriptor(
                intf,
                custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
            )

            if ep:
                data = self._build_receipt_data(cart, currency)
                ep.write(data)
                return True
        except Exception as e:
            print(f"Print error: {e}")
            return False
        return False

    def _print_via_com(self, cart, currency):
        """Fallback to COM port printing"""
        if not HAS_SERIAL:
            return False
        try:
            for port in ['COM3', 'COM4', 'COM5', 'COM6']:
                try:
                    ser = serial.Serial(port, 9600, timeout=1)
                    data = self._build_receipt_data(cart, currency)
                    ser.write(data)
                    ser.close()
                    return True
                except:
                    continue
        except:
            pass
        return False

    def _build_receipt_data(self, cart, currency):
        """Build ESC/POS receipt data"""
        # Get business info
        settings = self.db.fetchone("SELECT * FROM receipt_settings LIMIT 1") or {}
        business_name = settings.get('business_name', 'Farrouj POS')
        address = settings.get('address', '')
        phone = settings.get('phone', '')

        lines = []
        # Center align
        lines.append(self.ESC + b'a\x01')
        # Bold on
        lines.append(self.ESC + b'E\x01')
        lines.append(business_name.encode('utf-8') + b'\n')
        lines.append(self.ESC + b'E\x00')
        if address:
            lines.append(address.encode('utf-8') + b'\n')
        if phone:
            lines.append(phone.encode('utf-8') + b'\n')
        lines.append(b'-' * 32 + b'\n')

        # Left align
        lines.append(self.ESC + b'a\x00')

        # Items
        total = 0
        for item in cart:
            name = item['name_en']
            qty = item['qty']
            if currency == 'LBP':
                price = item['price_lbp'] + item.get('extras_price_lbp', 0)
                line_total = price * qty
                total += line_total
                lines.append(f"{name} x{qty}  {line_total:,.0f} LBP\n".encode('utf-8'))
            else:
                price = item['price_usd'] + item.get('extras_price_usd', 0)
                line_total = price * qty
                total += line_total
                lines.append(f"{name} x{qty}  ${line_total:.2f}\n".encode('utf-8'))

        lines.append(b'-' * 32 + b'\n')
        # Bold total
        lines.append(self.ESC + b'E\x01')
        if currency == 'LBP':
            lines.append(f"TOTAL: {total:,.0f} LBP\n".encode('utf-8'))
        else:
            lines.append(f"TOTAL: ${total:.2f}\n".encode('utf-8'))
        lines.append(self.ESC + b'E\x00')

        # Footer
        lines.append(b'\n')
        lines.append(self.ESC + b'a\x01')
        footer = settings.get('footer_text', 'Thank you!')
        lines.append(footer.encode('utf-8') + b'\n')
        lines.append(b'\n\n\n')
        # Cut paper
        lines.append(self.GS + b'V\x01')

        return b''.join(lines)

    def test_print(self):
        """Send test print page"""
        try:
            device = self.find_printer()
            if device:
                cfg = device.get_active_configuration()
                intf = cfg[(0,0)]
                ep = usb.util.find_descriptor(
                    intf,
                    custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
                )
                if ep:
                    data = self.ESC + b'a\x01' + b'TEST PRINT\nFarrouj POS\n' + b'\n\n\n' + self.GS + b'V\x01'
                    ep.write(data)
                    return True
        except:
            pass
        return False
