# -*- coding: utf-8 -*-
"""
PDF Receipt Export using ReportLab
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os

class PDFGenerator:
    def __init__(self, db):
        self.db = db

    def generate_receipt(self, cart, file_path, currency):
        """Generate a PDF receipt"""
        settings = self.db.fetchone("SELECT * FROM receipt_settings LIMIT 1") or {}
        business_name = settings.get('business_name', 'Farrouj POS')
        address = settings.get('address', '')
        phone = settings.get('phone', '')
        footer = settings.get('footer_text', 'Thank you for your visit!')

        doc = SimpleDocTemplate(
            file_path,
            pagesize=(80*mm, 297*mm) if settings.get('paper_width', 80) == 80 else (58*mm, 297*mm),
            rightMargin=5*mm,
            leftMargin=5*mm,
            topMargin=5*mm,
            bottomMargin=5*mm
        )

        styles = getSampleStyleSheet()
        elements = []

        # Business name
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=6,
            textColor=colors.HexColor('#2c3e50')
        )
        elements.append(Paragraph(business_name, title_style))

        if address:
            addr_style = ParagraphStyle('Addr', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER)
            elements.append(Paragraph(address, addr_style))
        if phone:
            elements.append(Paragraph(phone, addr_style))

        elements.append(Spacer(1, 6))
        elements.append(Table([['']], colWidths=[70*mm], style=TableStyle([
            ('LINEBELOW', (0,0), (-1,0), 1, colors.black),
        ])))
        elements.append(Spacer(1, 6))

        # Items table
        data = [['Item', 'Qty', 'Total']]
        total = 0
        for item in cart:
            qty = item['qty']
            if currency == 'LBP':
                price = item['price_lbp'] + item.get('extras_price_lbp', 0)
                line_total = price * qty
                total += line_total
                data.append([item['name_en'], str(qty), f"{line_total:,.0f}"])
            else:
                price = item['price_usd'] + item.get('extras_price_usd', 0)
                line_total = price * qty
                total += line_total
                data.append([item['name_en'], str(qty), f"${line_total:.2f}"])

        # Total row
        if currency == 'LBP':
            data.append(['', 'TOTAL', f"{total:,.0f} LBP"])
        else:
            data.append(['', 'TOTAL', f"${total:.2f}"])

        table = Table(data, colWidths=[40*mm, 10*mm, 20*mm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('ALIGN', (0,0), (0,-1), 'LEFT'),
            ('ALIGN', (1,0), (1,-1), 'CENTER'),
            ('ALIGN', (2,0), (2,-1), 'RIGHT'),
            ('LINEBELOW', (0,0), (-1,0), 1, colors.black),
            ('LINEABOVE', (0,-1), (-1,-1), 1, colors.black),
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,-1), (-1,-1), 10),
        ]))
        elements.append(table)

        elements.append(Spacer(1, 12))
        footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER)
        elements.append(Paragraph(footer, footer_style))
        elements.append(Paragraph(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M')}", footer_style))

        doc.build(elements)
        return True
