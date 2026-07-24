# 📦 Stock Management & Rental System

> A full-featured desktop business management application built with Python and PyQt5 — designed to handle stock inventory, customer profiles, rental operations, direct sales, payment tracking, and automated reporting — all in one place.

---

## 🎬 Video Demo

*(Upload your video demo here)*

---

## 📋 Table of Contents

- [About the Project](#-about-the-project)
- [Key Features](#-key-features)
- [Technologies & Architecture](#-technologies--architecture)
- [Project Structure](#-project-structure)
- [Database Schema](#-database-schema)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [How to Use](#-how-to-use)
- [Building an Executable](#-building-an-executable)
- [Configuration](#-configuration)
- [Privacy & Security](#-privacy--security)
- [Development Tools](#-development-tools)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🧾 About the Project

The **Stock Management & Rental System** is a professional-grade, offline-first desktop application tailored for businesses that both **rent out** and **sell** inventory items. It provides a unified dashboard for managing the full lifecycle of your business operations — from registering customers and issuing rental items, to tracking returns, calculating bills with smart day-counting logic, processing payments, and generating detailed financial reports.

The application is built on **PyQt5** with a **SQLite3** backend, making it lightweight, portable, and entirely self-contained — no internet connection is required for core operations. Optional **Google Drive** backup integration is available for database cloud sync.

---

## ✨ Key Features

### 📦 Stock Management (Rental Inventory)
- ➕ **Add, edit, and delete** rental stock items with name, total quantity, and available quantity
- 💰 **Dynamic price history** — each stock item maintains a full price change log with timestamps
- 🔍 **Search by name** using live database queries
- 📊 **View full price history** in a sortable, paginated table
- 🛡️ **Smart deletion protection** — warns before deleting stock items that are currently rented out
- ♻️ **Batch delete** with a progress dialog for large datasets

### 👥 Customer Management
- 🆕 **Register customers** with name, contact number, address, CNIC (13-digit ID card), and optional referrer name
- 🔍 **Search by name or CNIC** for quick lookups
- ✏️ **Edit customer records** including all personal details
- 🗑️ **Delete customers** with automatic stock quantity restoration if items are still rented
- 💳 **Financial tracking** — each customer card displays real-time total amount due vs. amount paid
- 🤝 **Seamless flow** — optionally rent items to a customer immediately after adding them

### 🤝 Rent Management
- 📋 **Customer card view** with color-coded indicators for active vs. cleared dues
- 🔎 **Filter customers** by: All, With Active Rents, No Active Rents
- 🛒 **Multi-item renting** — select multiple stock items and quantities in one session using an interactive selector
- 💵 **Advance payment capture** at the time of renting
- 📅 **Custom rent date** — use the current date-time or pick a custom one via calendar popup
- 🔙 **Return processing** with smart bill calculation:
  - Calculates days rented using configurable **evening rent** and **morning return** time thresholds
  - Same-day rentals always count as 1 day
  - **Friday counting** for special billing rules
  - Prices fetched based on the rate **at the time of rent** (historical price lookup)
- 💸 **Bill summary dialog** — grouped by rental period with itemized breakdown, group totals, and Friday amounts
- 💳 **Payment dialog** — supports partial payments, discounts, and automatic allocation to highest-amount items
- ✅ **Bulk return** or **selective item return** with individual quantity editing

### 💼 Sales Management
- 🏪 **Separate selling inventory** — maintains a distinct stock pool for sale items (item name, available quantity, cost price, selling price)
- 🛍️ **Sell multiple items** in one transaction using the same multi-item selector
- 📉 **Proportional discount distribution** — discounts are split across all sold items by value weight
- 📈 **Per-item profit calculation** shown in a dedicated profit summary dialog before confirming
- 👤 **Unpaid customer / loan tracking** — if a customer does not pay the full amount, the balance is assigned to a tracked unpaid customer record
- 🔄 **Update or clear loan amounts** for individual unpaid customers
- 📦 **Manage selling stock** with inline editing, bulk update, and individual/all delete options

### 📊 Reports & Analytics
- 📋 **Active Rents Report** — view all currently rented and stock-received items across all customers
- ✅ **Paid Rents Report** — full history of completed rental transactions
- 💰 **Payment Details** — all payment records with customer names, amounts, discounts, and timestamps
- 📈 **Sales History** — complete sales log with quantity, cost, sale amount, discount, profit, and date
- 🔢 **Sales Summary** — calculates total cost, total sales, total profit, total discount, total quantity sold, and exclusive totals excluding loan amounts
- 📆 **Flexible date filtering** on all report screens:
  - Filter by a **specific date**
  - Filter by a **date range**
  - Filter by **multiple hand-picked dates**
- 💡 **Upcoming payments calculator** — sums all outstanding dues minus already-paid amounts across active renters
- 🔄 **Recalculate all active rents** and push updated `amount_due` values back to the database

### ☁️ Google Drive Backup
- 🔐 **OAuth2 authentication** using `pydrive` — first-run browser-based login, credentials cached for future use
- 📤 **Upload the SQLite database** to Google Drive with one click
- 🔄 **Automatic versioning** — renames the existing cloud file with a timestamp before uploading the fresh copy, then deletes the old version
- 📊 **Real-time progress feedback** shown in the status label on the main menu

### 🎨 Theming System
- 🎨 **3 built-in themes**: Blue (default), Orange, and Black
- 🔄 **Live theme switching** from the main menu — the app restarts with the new theme applied globally
- 🖼️ **Theme-aware backgrounds** — each theme has its own matching background image
- 🧩 **Singleton ThemeManager** — all UI components share the same theme instance automatically

### 🖥️ UI & UX
- 📱 **Responsive layout** — automatically scales to 80% of the primary screen size
- 🃏 **Card-based views** for stock, customers, and rent — with hover effects and inline action buttons
- 📄 **Paginated tables** — supports 100+ records per page with pagination controls
- 🔎 **Live database search** on all major screens (by name, ID card, stock name, etc.)
- 🧭 **Navigation ribbon** at the top for quick module switching
- ⌨️ **Keyboard shortcuts** — Backspace to go back, Enter to submit on focused save buttons
- 📊 **Sortable table columns** on all table screens
- ⏳ **Progress dialogs** for long-running operations (batch delete, bill calculation, etc.)

---

## 🏗️ Technologies & Architecture

| Layer | Technology |
|---|---|
| **Language** | Python 3.x |
| **GUI Framework** | PyQt5 |
| **Database** | SQLite3 (via Python `sqlite3` module) |
| **Cloud Backup** | PyDrive (Google Drive API v2) |
| **Data Generation** | Faker (for test data seeding) |
| **Packaging** | PyInstaller |
| **Version Control** | Git |

### Architecture Overview

The application follows a **modular MVC-adjacent architecture**:

- **`MainManagement.py`** — Application entry point; creates the `QMainWindow`, instantiates all module managers, and wires up the main menu and navigation ribbon.
- **`DatabaseManagement.py`** — Centralized data access layer using a `@connection_required` decorator pattern to automatically open/commit/rollback/close connections around every query method.
- **`Custom_UI.py`** — Shared UI component library containing `TableScreen`, `CardScreen`, `StockSelector`, reusable styled buttons, labels, and all global constants (column names, table names, date formats, screen ratio).
- **`themes.py`** — Singleton `ThemeManager` class that holds and applies color themes across the whole application.
- **Module UI files** (`Stock_Management_ui.py`, `CustomerManagement_ui.py`, `RentManagement_ui.py`, `Sale_Management_ui.py`, `Reports_ui.py`) — Each encapsulates the UI logic, validation, and business rules for its domain.

---

## 📁 Project Structure

```
Management System Source Code_Clear_Pending/
│
├── 📄 MainManagement.py          # Entry point — main window, module wiring, Google Drive upload
├── 📄 DatabaseManagement.py      # All database CRUD and query operations (SQLite3)
├── 📄 Custom_UI.py               # Shared UI components: TableScreen, CardScreen, styled widgets
├── 📄 themes.py                  # Singleton ThemeManager with Blue/Orange/Black themes
│
├── 📄 Stock_Management_ui.py     # Rental stock: add, edit, delete, price history
├── 📄 CustomerManagement_ui.py   # Customer: register, edit, delete, financial summary
├── 📄 RentManagement_ui.py       # Renting, returning, bill calculation, payments
├── 📄 Sale_Management_ui.py      # Selling stock: add, sell, manage, loan tracking
├── 📄 Reports_ui.py              # Reports: active/paid rents, payments, sales history, analytics
│
├── 📄 DataGenerator.py           # Faker-based test data seeder (dev tool only)
│
├── 📄 MainManagement.spec        # PyInstaller build specification
├── 📄 Compile.bat                # Windows batch script for building the EXE
├── 📄 Command_to_create_exe.txt  # PyInstaller CLI command reference
├── 📄 copy_database.bat          # Utility script to copy/backup the database file
│
├── 📄 Time_Thresholds.txt        # Configurable rent billing thresholds (evening/morning times)
├── 📄 client_secrets.json        # Google Drive OAuth2 client config (excluded from git)
├── 📄 credentials.json           # Cached Google Drive credentials (excluded from git)
├── 📄 stock_rental_system.db     # SQLite3 database file (excluded from git)
│
├── 📄 .gitignore                 # Ignores .db, credentials, build artifacts, __pycache__
│
└── 📂 Assets/
    ├── 🖼️ rental icon-01.png     # Window title bar icon
    ├── 🖼️ app_icon.ico           # Application icon (used for EXE)
    ├── 🖼️ blue_background.png    # Blue theme background
    ├── 🖼️ orange_background.png  # Orange theme background
    ├── 🖼️ black_background.png   # Black theme background
    ├── 🖼️ blue_theme.png         # Blue theme button selector image
    ├── 🖼️ orange_theme.png       # Orange theme button selector image
    └── 🖼️ black_theme.png        # Black theme button selector image
```

---

## 🗄️ Database Schema

The system uses a single **SQLite3** database file (`stock_rental_system.db`) with the following tables:

| Table | Purpose |
|---|---|
| `Stock` | Rental inventory — name, total qty, available qty |
| `Stock_Price` | Price history per stock item with timestamps |
| `Customer` | Customer registry with contact, CNIC, financials |
| `Rent` | Rental transactions — links customer + stock, tracks status |
| `Payments` | Payment records with amount and discount per customer |
| `Selling_Stock` | Separate inventory for items available for sale |
| `Sold_Items` | Sales transaction log with cost, revenue, discount, profit |
| `Unpaid_Customers` | Standalone loan/credit tracker for sale customers |

> Foreign keys are enforced with `PRAGMA foreign_keys = ON`. Cascade delete is enabled on child tables.

---

## ✅ Prerequisites

Before running or developing this project, ensure you have the following installed:

- 🐍 **Python 3.8+** — [python.org](https://www.python.org/downloads/)
- 📦 **pip** (comes bundled with Python)
- The following Python packages:

```bash
pip install PyQt5 pydrive faker pyinstaller
```

> **Note:** `pydrive` requires a `client_secrets.json` file from Google Cloud Console to enable Drive backup. See [Configuration](#-configuration) for details. The app runs fully without it if you do not need the Upload feature.

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/stock-rental-system.git
cd stock-rental-system
```

### 2. Install Dependencies

```bash
pip install PyQt5 pydrive faker pyinstaller
```

### 3. Run the Application

```bash
python MainManagement.py
```

The application will automatically create the SQLite database (`stock_rental_system.db`) and all required tables on the first launch.

---

## 📖 How to Use

### 🏠 Main Menu
When you launch the app, you land on the **Main Menu** with buttons for each module:
- **Stock Management** — manage your rental inventory
- **Customer Management** — register and manage customers
- **Rent Management** — issue and return rental items
- **Sales Management** — sell items from a separate inventory
- **Reports** — view analytics and financial summaries
- **Upload Database** — sync your database to Google Drive

A **navigation ribbon** at the top provides quick switching between the most-used modules.

---

### 📦 Adding Rental Stock
1. Go to **Stock Management**
2. Click **➕ Add New Stock**
3. Fill in: Item Name, Total Quantity, Available Quantity, Rental Price (per day)
4. Click **Save** — the stock appears as a card with the price and last update date

---

### 👥 Adding a Customer
1. Go to **Customer Management**
2. Click **➕ Add New Customer**
3. Fill in: Name, Contact Number (11 digits), Address, CNIC (13 digits), Referrer (optional)
4. Click **Save** — you will be asked if you want to immediately rent items to this customer

---

### 🤝 Renting Items
1. Go to **Rent Management**
2. Find the customer by searching by name or CNIC, or use the **With Active Rents** filter
3. Click **➕ Rent Items** on the customer card
4. On the stock table, enter the **Quantity to Rent** for each item, or click **Add** to add to your selection basket
5. Click **View Selected Items** to review your selection
6. Click **Rent Items** — confirm the date/time and optionally capture an advance payment
7. Stock quantities are automatically decremented

---

### 🔙 Returning Items & Billing
1. In **Rent Management**, click **🔙 Return Items** on a customer with active rents
2. The rented items table appears — adjust return quantities per item if needed
3. Click **Return All** or **Return Specified**
4. The **Bill Summary dialog** appears showing:
   - Items grouped by rental period
   - Days rented, total weeks, total Fridays
   - Per-item cost breakdown
   - Grand total, amount already paid, and amount due now
5. A **Payment dialog** appears — enter amount paid and any discount
6. On confirmation, stock quantities are restored and the customer's financial record is updated

---

### 💼 Selling Items
1. Go to **Sales Management → Sell Items**
2. Select items and enter quantities to sell
3. Review the **Bill Summary** and confirm
4. Enter the **amount paid** and **discount** — a Profit Summary per item is shown before finalizing
5. If a remaining amount exists (partial payment), you can assign it to an existing or new **Unpaid Customer**

---

### 📊 Viewing Reports
1. Go to **Reports**
2. Choose from:
   - **Show Active Rents** — see all outstanding rentals; use **Refresh Rents** to recalculate all dues
   - **Show Paid Rents** — history of fully settled rentals
   - **Show Payment Details** — payment ledger with customer names
   - **Sales History** — complete sales log with profit data
3. Use the **Filter** dropdown on any report to filter by specific date, date range, or multiple dates
4. Use **Show Sales Summary** or **Calculate All Payments** for aggregated financial totals

---

### ☁️ Uploading to Google Drive
1. Set up `client_secrets.json` (see [Configuration](#-configuration))
2. From the Main Menu, click **Upload Database**
3. A browser window opens for Google OAuth2 login (first time only)
4. Credentials are saved to `credentials.json` for future logins
5. The database is uploaded; any existing file on Drive is renamed with a timestamp before replacement

---

## 🔨 Building an Executable

To build a standalone Windows `.exe`:

```bash
pyinstaller --add-data "Assets:Assets" --onedir --windowed --icon=Assets/app_icon.ico MainManagement.py
```

Or run the provided batch file:

```bash
Compile.bat
```

The output will be in the `dist/MainManagement/` folder. Distribute the entire `dist/MainManagement/` directory — the `.exe` requires the `Assets/` folder alongside it.

> **Note:** The `stock_rental_system.db` file is created in the **working directory** when the app first runs. Place the `dist/MainManagement/` folder wherever you want the data to live.

---

## ⚙️ Configuration

### Time Thresholds (`Time_Thresholds.txt`)
This file controls the billing day-count logic for rentals:

```
Evening Rent Time:18
Morning Return Time:9
```

- **Evening Rent Time**: If a customer rents after this hour (24h format), one day is deducted from the bill (late-evening discount)
- **Morning Return Time**: If a customer returns before this hour, one day is deducted (early-morning return discount)
- The file is auto-created with defaults (`18` and `9`) on first run if it does not exist

### Google Drive (`client_secrets.json`)
To enable Google Drive backup:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable the **Google Drive API**
3. Create **OAuth 2.0 credentials** (Desktop app type)
4. Download the JSON and save it as `client_secrets.json` in the project root
5. On first use, a browser window opens for authentication; credentials are saved to `credentials.json`

> ⚠️ **Both `client_secrets.json` and `credentials.json` are in `.gitignore` and must NEVER be committed to version control.**

---

## 🔒 Privacy & Security

- 🗄️ **All data is stored locally** in a single SQLite3 file — no data leaves your machine without your explicit action
- 🔐 **Google Drive integration** uses OAuth2 — your Google password is never stored; only an access/refresh token is cached in `credentials.json`
- 🚫 **Credentials excluded from Git** — `.gitignore` ensures `client_secrets.json`, `credentials.json`, and `*.db` files are never tracked
- 🔑 **CNIC validation** — the system enforces a 13-digit numeric format for national ID cards
- 📞 **Contact number validation** — enforces an 11-digit numeric format for Pakistani mobile numbers
- 🛡️ **Foreign key constraints** with `ON DELETE CASCADE` prevent orphaned records
- ↩️ **Transaction rollback** — the `@connection_required` decorator automatically rolls back any failed database operation to maintain data integrity

---

## 🧰 Development Tools

- **`DataGenerator.py`** — A development utility using the `Faker` library to seed the database with realistic test data:
  - Customers with realistic names, phone numbers, CNICs, and addresses
  - Stock items with randomized price histories
  - Rental records (paid and active)
  - Sales transactions with full profit data
  - Unpaid customer records and payment histories

  > ⚠️ This is a **dev-only tool**. Do not run it on a production database.

- **`copy_database.bat`** — A Windows batch script to quickly back up the database file locally.

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes and commit: `git commit -m "Add: your feature description"`
4. Push to your fork: `git push origin feature/your-feature-name`
5. Open a Pull Request with a clear description of your changes

Please ensure:
- No credentials or `.db` files are committed
- Code follows the existing module structure
- New UI screens are added to the appropriate module file

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

<div align="center">

Built with ❤️ using **Python** & **PyQt5**

⭐ Star this repo if you found it useful!

</div>
