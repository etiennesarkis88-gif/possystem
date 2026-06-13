# -*- coding: utf-8 -*-
"""
Helper utilities for Farrouj POS
"""

import os
import hashlib

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def format_currency_lbp(amount):
    """Format LBP amount with commas"""
    return f"{amount:,.0f} LBP"

def format_currency_usd(amount):
    """Format USD amount with 2 decimals"""
    return f"${amount:.2f}"

def ensure_dir(path):
    """Ensure directory exists"""
    os.makedirs(path, exist_ok=True)
    return path
