# 🍗 Farrouj POS - Lebanese Restaurant Point of Sale System

A fully offline, customizable Windows desktop POS system designed specifically for Lebanese snack shops and restaurants.

## ✨ Features

- **💰 Cashier Interface** - Fast, intuitive order taking with category-based menu
- **📋 Menu Management** - Add/edit/remove items and categories with bilingual support
- **📦 Inventory Tracking** - Stock levels with low-stock alerts
- **🚚 Delivery Management** - Track delivery orders with customer details
- **🖨️ Thermal Printing** - Native ESC/POS thermal printer support (USB)
- **📄 PDF Export** - Export receipts to PDF format
- **💱 Dual Currency** - Support for LBP and USD with customizable exchange rate
- **🌐 Bilingual** - Full English and Arabic support
- **🔒 Data Protection** - Password-protected data reset
- **📊 Reports & Analytics** - Sales reports with CSV export
- **🎨 Fully Customizable** - Colors, logos, names, categories all editable

## 🚀 Quick Start (Run from Source)

### Step 1: Install Python
1. Go to https://www.python.org/downloads/
2. Download Python 3.11 or newer
3. **IMPORTANT**: Check "Add Python to PATH" during installation
4. Click Install Now

### Step 2: Install Dependencies
Open Command Prompt (CMD) and run:
```cmd
cd path\to\FarroujPOS
pip install -r requirements.txt
```

### Step 3: Run the Application
```cmd
python main.py
```

## 📦 Creating a Windows Installer (.exe)

### Option A: Simple Executable
```cmd
pip install pyinstaller
python build.py
```
The .exe will be in the `dist` folder.

### Option B: Professional Installer
1. Download Inno Setup from https://jrsoftware.org/isinfo.php
2. Install Inno Setup
3. Build the executable first (Option A)
4. Open `installer/installer.iss` in Inno Setup
5. Click Build → Output is a professional setup wizard

## 🔧 First Time Setup

### Default Login
- **Username:** `admin`
- **Password:** `admin123`

### 1. Configure Your Business
1. Go to **Settings** → **Business Info**
2. Enter your restaurant name (English & Arabic)
3. Upload your logo (PNG, JPG, any format)
4. Add address and phone number

### 2. Set Up Currencies
1. Go to **Settings** → **Currency**
2. Enable LBP and/or USD
3. Set exchange rate (e.g., 90000 LBP = 1 USD)
4. Choose default currency

### 3. Customize Receipt
1. Go to **Settings** → **Receipt**
2. Add custom header/footer text
3. Enable/disable logo and QR code
4. Set paper width (58mm or 80mm)

### 4. Build Your Menu
1. Go to **Menu** → **Categories**
   - Edit existing categories (Farrouj, Arguileh, etc.)
   - Change colors, names, sort order
   - Add new categories
2. Go to **Menu** → **Menu Items**
   - Add food items with prices
   - Upload item images
   - Set availability and popularity

## 🖨️ Thermal Printer Setup

### USB Connection (Most Common)
1. Plug in your thermal printer via USB
2. Install printer drivers if needed
3. The app auto-detects these common models:
   - Epson (VID: 0x04b8)
   - Zjiang/OCPP (VID: 0x0416)
   - XPrinter (VID: 0x1fc9)

### If Auto-Detection Fails
1. Open Device Manager
2. Find your printer under "Ports (COM & LPT)" or "Universal Serial Bus devices"
3. Note the COM port (e.g., COM3)
4. The app will try COM3 automatically

### Paper Size
- **58mm**: Small portable printers
- **80mm**: Standard receipt printers (recommended)

## 📊 Using the System

### Taking Orders (Cashier Screen)
1. Click category buttons (Farrouj, Sandwiches, etc.)
2. Click food items to add to cart
3. Adjust quantities with +/- buttons
4. Choose order type: Dine In / Takeaway / Delivery
5. For Delivery: Enter customer name, phone, address
6. Select currency (LBP or USD)
7. Click **CHECKOUT** to complete
8. Click **Print Receipt** or **Export PDF**

### Managing Deliveries
1. Go to **Delivery** tab
2. View all delivery orders by date
3. Update status: Pending → Out for Delivery → Delivered
4. Track customer details and addresses

### Inventory Management
1. Go to **Inventory** tab
2. View stock levels for all items
3. Red = Out of Stock, Yellow = Low Stock
4. Click **Adjust** to update quantities
5. Set minimum stock alerts

### Reports & Analytics
1. Go to **Reports** tab
2. Select date range and report type:
   - Sales Summary
   - Daily Breakdown
   - Top Selling Items
   - Category Performance
3. Click **Export CSV** to save reports

## 🗂️ Default Categories

| English | Arabic | Color |
|---------|--------|-------|
| Farrouj | فروج | 🔴 Red |
| Arguileh | أرجيلة | 🟣 Purple |
| Sandwiches | ساندويش | 🟡 Orange |
| Daily Meals | وجبات يومية | 🟢 Green |
| Sweets | حلويات | 🔴 Pink |
| Drinks | مشروبات | 🔵 Blue |
| Plates | صحون | 🟠 Orange |
| Taouk | تاووق | 🟢 Teal |
| Mezza | مقبلات | 🟤 Brown |

## 🔒 Data Management

### Password-Protected Reset
1. Go to **Settings** → **Data Management**
2. Choose:
   - **Reset Sales Data Only**: Clears orders but keeps menu
   - **Factory Reset**: Clears everything, restores defaults
3. Enter admin password: `admin123`
4. Confirm the irreversible action

### Backup Database
1. Go to **Settings** → **Data Management**
2. Click **Export Database**
3. Save the .db file to USB or cloud storage

## 🛠️ Troubleshooting

### App Won't Start
- Make sure Python is added to PATH
- Run `pip install -r requirements.txt` again
- Check that all files are in the correct folders

### Printer Not Working
- Check USB connection
- Try different USB ports
- Install printer drivers from manufacturer
- Check if printer appears in Device Manager

### Arabic Text Not Displaying
- Install Arabic language pack in Windows
- The app uses system fonts that support Arabic

### Database Errors
- Delete folder: `%USERPROFILE%\FarroujPOS\data\`
- Restart the app (database will be recreated)

## 📁 File Locations

| Purpose | Location |
|---------|----------|
| Database | `%USERPROFILE%\FarroujPOS\data\farrouj_pos.db` |
| Settings | Stored in SQLite database |
| Receipts | Exported to location you choose |
| Backups | Manual export from Settings |

## 📝 License

Free for commercial use. Customize as needed for your restaurant.

## 📞 Support

For technical issues:
1. Check this README first
2. Verify all installation steps
3. Ensure Windows is updated
4. Try running as Administrator

---
**Made with ❤️ for Lebanese Restaurants**
