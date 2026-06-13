# -*- coding: utf-8 -*-
"""
PDF Generator - Export receipts to PDF format
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
import os

class PDFGenerator:
    def __init__(self, db):
        self.db = db
        self.settings = self.load_settings()
        self.styles = getSampleStyleSheet()
        self.setup_styles()

    def load_settings(self):
        result = self.db.fetchone("SELECT * FROM receipt_settings LIMIT 1")
        return result or {}

    def setup_styles(self):
        """Setup custom styles for the PDF"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#E74C3C'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        self.header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=6,
            alignment=TA_CENTER
        )

        self.item_style = ParagraphStyle(
            'ItemStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=3
        )

        self.total_style = ParagraphStyle(
            'TotalStyle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#E74C3C'),
            spaceAfter=6,
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold'
        )

    def generate_receipt(self, cart, file_path, currency='LBP', order_info=None):
        """Generate a PDF receipt"""
        doc = SimpleDocTemplate(
            file_path,
            pagesize=(80*mm, 297*mm),  # Thermal paper width
            rightMargin=5*mm,
            leftMargin=5*mm,
            topMargin=10*mm,
            bottomMargin=10*mm
        )

        elements = []

        # Logo
        if self.settings.get('logo_path') and os.path.exists(self.settings['logo_path']):
            try:
                img = Image(self.settings['logo_path'], width=60*mm, height=30*mm)
                elements.append(img)
                elements.append(Spacer(1, 5*mm))
            except:
                pass

        # Business Name
        business_name = self.settings.get('business_name', 'لقمة أبو جورج')
        elements.append(Paragraph(business_name, self.title_style))

        if self.settings.get('business_name_ar'):
            elements.append(Paragraph(self.settings['business_name_ar'], self.header_style))

        # Address and Phone
        if self.settings.get('address'):
            elements.append(Paragraph(self.settings['address'], self.header_style))
        if self.settings.get('phone'):
            elements.append(Paragraph(f"Tel: {self.settings['phone']}", self.header_style))

        elements.append(Spacer(1, 5*mm))

        # Date and Order Info
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elements.append(Paragraph(f"Date: {now}", self.header_style))

        if order_info:
            if order_info.get('order_number'):
                elements.append(Paragraph(f"Order #: {order_info['order_number']}", self.header_style))
            if order_info.get('table_number'):
                elements.append(Paragraph(f"Table: {order_info['table_number']}", self.header_style))

        elements.append(Spacer(1, 5*mm))

        # Items table
        table_data = [['Item', 'Qty', 'Price', 'Total']]

        subtotal = 0
        for item in cart:
            name = item['name_en']

            # Add modifications to name
            if item.get('removed_ingredients'):
                removed = ", ".join(item['removed_ingredients'])
                name += f"\n[-NO: {removed}]"

            if item.get('selected_extras'):
                extras = ", ".join(item['selected_extras'])
                name += f"\n[+{extras}]"

            if item.get('instructions'):
                name += f"\n>> {item['instructions']}"

            qty = item['qty']

            if currency == 'LBP':
                price = item['price_lbp'] + item.get('extras_price_lbp', 0)
                total = price * qty
                subtotal += total
                price_str = f"{price:,.0f}"
                total_str = f"{total:,.0f}"
            else:
                price = item['price_usd'] + item.get('extras_price_usd', 0)
                total = price * qty
                subtotal += total
                price_str = f"${price:.2f}"
                total_str = f"${total:.2f}"

            table_data.append([name, str(qty), price_str, total_str])

        # Create table
        table = Table(table_data, colWidths=[35*mm, 10*mm, 15*mm, 15*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E74C3C')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 5*mm))

        # Totals

        total = subtotal

        if currency == 'LBP':
            elements.append(Paragraph(f"Subtotal: {subtotal:,.0f} LBP", self.total_style))

            elements.append(Paragraph(f"<b>TOTAL: {total:,.0f} LBP</b>", self.total_style))
        else:
            elements.append(Paragraph(f"Subtotal: ${subtotal:.2f}", self.total_style))

            elements.append(Paragraph(f"<b>TOTAL: ${total:.2f}</b>", self.total_style))

        elements.append(Spacer(1, 10*mm))

        # Footer
        footer = self.settings.get('footer_text', 'Thank you for your visit!')
        elements.append(Paragraph(footer, self.header_style))

        if self.settings.get('footer_text_ar'):
            elements.append(Paragraph(self.settings['footer_text_ar'], self.header_style))

        # Build PDF
        doc.build(elements)
        return True
