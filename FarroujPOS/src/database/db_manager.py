# -*- coding: utf-8 -*-
"""
Database Manager - SQLite backend for offline operation
"""

import sqlite3
import os
import json
from datetime import datetime
from pathlib import Path

class DatabaseManager:
    def __init__(self):
        self.db_path = os.path.join(
            os.path.expanduser("~"), 
            "FarroujPOS", 
            "data", 
            "farrouj_pos.db"
        )
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = None
        self.connect()

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")

    def initialize_database(self):
        """Create all tables if they don't exist"""
        cursor = self.conn.cursor()

        # Settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_en TEXT NOT NULL,
                name_ar TEXT,
                icon_path TEXT,
                color TEXT DEFAULT '#FF6B35',
                sort_order INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Menu items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                name_en TEXT NOT NULL,
                name_ar TEXT,
                description_en TEXT,
                description_ar TEXT,
                price_lbp REAL DEFAULT 0,
                price_usd REAL DEFAULT 0,
                cost_lbp REAL DEFAULT 0,
                cost_usd REAL DEFAULT 0,
                ingredients TEXT,
                extras TEXT,
                image_path TEXT,
                is_available INTEGER DEFAULT 1,
                is_popular INTEGER DEFAULT 0,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        """)

        # Inventory table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER,
                quantity REAL DEFAULT 0,
                unit TEXT DEFAULT 'piece',
                min_stock REAL DEFAULT 10,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES menu_items(id)
            )
        """)

        # Orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT UNIQUE,
                order_type TEXT DEFAULT 'dine_in',
                table_number TEXT,
                customer_name TEXT,
                customer_phone TEXT,
                delivery_address TEXT,
                delivery_fee_lbp REAL DEFAULT 0,
                delivery_fee_usd REAL DEFAULT 0,
                subtotal_lbp REAL DEFAULT 0,
                subtotal_usd REAL DEFAULT 0,
                discount_lbp REAL DEFAULT 0,
                discount_usd REAL DEFAULT 0,
                total_lbp REAL DEFAULT 0,
                total_usd REAL DEFAULT 0,
                currency_used TEXT DEFAULT 'LBP',
                payment_method TEXT DEFAULT 'cash',
                status TEXT DEFAULT 'pending',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)

        # Order items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                menu_item_id INTEGER,
                quantity INTEGER DEFAULT 1,
                price_lbp REAL,
                price_usd REAL,
                extras_price_lbp REAL DEFAULT 0,
                extras_price_usd REAL DEFAULT 0,
                removed_ingredients TEXT,
                selected_extras TEXT,
                special_instructions TEXT,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
            )
        """)

        # Daily sales summary
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE,
                total_orders INTEGER DEFAULT 0,
                total_sales_lbp REAL DEFAULT 0,
                total_sales_usd REAL DEFAULT 0,
                total_discount_lbp REAL DEFAULT 0,
                total_discount_usd REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Receipt settings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS receipt_settings (
                id INTEGER PRIMARY KEY,
                business_name TEXT DEFAULT 'لقمة أبو جورج',
                business_name_ar TEXT DEFAULT 'لقمة أبو جورج',
                address TEXT,
                phone TEXT,
                logo_path TEXT,
                header_text TEXT,
                footer_text TEXT DEFAULT 'Thank you for your visit!',
                footer_text_ar TEXT DEFAULT 'شكراً لزيارتكم!',
                show_logo INTEGER DEFAULT 1,
                show_qr_code INTEGER DEFAULT 0,
                paper_width INTEGER DEFAULT 80,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Users table for password protection
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password_hash TEXT,
                role TEXT DEFAULT 'cashier',
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Currency settings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS currency_settings (
                id INTEGER PRIMARY KEY,
                use_lbp INTEGER DEFAULT 1,
                use_usd INTEGER DEFAULT 1,
                exchange_rate REAL DEFAULT 90000,
                default_currency TEXT DEFAULT 'LBP',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()
        self._insert_default_data()

    def _insert_default_data(self):
        cursor = self.conn.cursor()

        # Default categories with Lebanese food themes
        categories = [
            ("Farrouj", "فروج", "farrouj.png", "#E74C3C", 1),
            ("Arguileh", "أرجيلة", "arguileh.png", "#9B59B6", 2),
            ("Sandwiches", "ساندويش", "sandwich.png", "#F39C12", 3),
            ("Daily Meals", "وجبات يومية", "daily.png", "#27AE60", 4),
            ("Sweets", "حلويات", "sweets.png", "#E91E63", 5),
            ("Drinks", "مشروبات", "drinks.png", "#3498DB", 6),
            ("Plates", "صحون", "plates.png", "#E67E22", 7),
            ("Taouk", "تاووق", "taouk.png", "#1ABC9C", 8),
            ("Mezza", "مقبلات", "mezza.png", "#795548", 9),
        ]

        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("""
                INSERT INTO categories (name_en, name_ar, icon_path, color, sort_order)
                VALUES (?, ?, ?, ?, ?)
            """, categories)

        # Default receipt settings
        cursor.execute("SELECT COUNT(*) FROM receipt_settings")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO receipt_settings (id, business_name, business_name_ar, 
                    address, phone, footer_text, footer_text_ar)
                VALUES (1, 'لقمة أبو جورج', 'لقمة أبو جورج', 
                    'Beirut, Lebanon', '+961 1 234 567', 
                    'Thank you for your visit!', 'شكراً لزيارتكم!')
            """)

        # Default currency settings
        cursor.execute("SELECT COUNT(*) FROM currency_settings")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO currency_settings (id, use_lbp, use_usd, exchange_rate, default_currency)
                VALUES (1, 1, 1, 90000, 'LBP')
            """)

        # Default admin user (password: admin123)
        import hashlib
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            password_hash = hashlib.sha256("admin123".encode()).hexdigest()
            cursor.execute("""
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            """, ("admin", password_hash, "admin"))

        self.conn.commit()

    def execute(self, query, params=()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor

    def fetchall(self, query, params=()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def fetchone(self, query, params=()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    def close(self):
        if self.conn:
            self.conn.close()
