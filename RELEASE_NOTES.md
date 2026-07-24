# 📋 Release Notes — Stock Management & Rental System

All notable changes to this project are documented in this file.

---

## [v1.0.0] — Initial Release 🎉

**Release Date:** July 2026

This is the first stable release of the **Stock Management & Rental System**. It includes the complete core feature set covering rental inventory, customer management, sales, reporting, and Google Drive cloud backup.

---

### 🆕 New Features

#### 📦 Stock Management
- Add, edit, and delete rental stock items (name, total quantity, available quantity, rental price)
- Full price history per stock item — prices are timestamped and stored separately to allow historical billing accuracy
- View complete price history in a sortable, paginated table
- Live search by item name with instant database queries
- Smart deletion guard: warns if a stock item has active rentals before deletion
- Batch delete with a modal progress dialog

#### 👥 Customer Management
- Full customer registry with name, contact number, address, CNIC (National ID card), and optional referrer name
- Input validation: 13-digit CNIC and 11-digit Pakistani mobile number enforced
- Search customers by name or CNIC
- Each customer card shows real-time financial summary (total amount due vs. total paid)
- Post-add shortcut: immediately navigate to rent items to a newly created customer
- Safe delete with automatic stock quantity restoration for unreturned items

#### 🤝 Rent Management
- Multi-item rental selection in a single session using an interactive stock basket
- Optional advance payment at the time of renting
- Custom rent date/time picker (calendar popup) or use current date/time
- Smart billing engine:
  - Day calculation respects configurable evening-rent and morning-return time thresholds
  - Same-day rentals count as 1 day minimum
  - Historical price lookup: bills use the price that was active on the rent date
  - Friday counter for businesses with Friday-based pricing rules
- Bill Summary dialog: groups items by rental period, shows days rented, weeks, Fridays, and per-group totals
- Payment dialog: supports partial payments, discounts, and smart allocation to highest-due items
- Bulk return or selective return with per-item quantity adjustment
- Filter customers by: All / With Active Rents / No Active Rents
- Edit/Clear functionality to correct active rent records

#### 💼 Sales Management
- Separate selling inventory (Selling_Stock) distinct from rental inventory
- Multi-item sell session with the same basket-style selector
- Proportional discount distribution across all sold items by value weight
- Per-item profit summary shown before sale confirmation
- Loan/unpaid tracking: remaining amount after partial payment is assigned to an Unpaid Customer record
- Manage selling stock with inline editing, single-row update, bulk update, and delete options
- Unpaid customer table with update and clear-amount actions

#### 📊 Reports & Analytics
- Active Rents report with live rent data across all customers
- Paid Rents report for historical completed transactions
- Payment Details ledger with customer names, amounts, discounts, and timestamps
- Sales History table with cost, sale amount, discount, profit, and date
- Sales Summary: total cost, total sales, total profit, total discount, total quantity sold, and exclusive totals excluding loan/unpaid amounts
- Flexible date filtering on all report screens:
  - By a specific date
  - By a date range
  - By multiple hand-picked dates
- Upcoming Payments calculator: aggregated outstanding dues minus already-paid amounts
- Recalculate all active rents button to push fresh `amount_due` values to the database

#### ☁️ Google Drive Backup
- OAuth2-based Google Drive authentication via `pydrive`
- First-time browser login; credentials cached locally for subsequent uploads
- Automatic file versioning: renames existing Drive file with timestamp before uploading the new version, then deletes the old one
- Real-time progress feedback on the main menu label

#### 🎨 Theming System
- Three built-in themes: **Blue** (default), **Orange**, and **Black**
- Live theme switching from the main menu — entire app relaunches with the new theme
- Theme-specific background images and color palettes
- Singleton `ThemeManager` ensures all UI components share the same active theme

#### 🖥️ UI & UX
- Responsive window sizing: auto-scales to 80% of the screen dimensions
- Card-based views for stock, customers, and rent management
- Paginated tables supporting 100+ records per page
- Sortable table columns across all table screens
- Live database-backed search on all major screens
- Navigation ribbon on the main menu for quick module access
- Keyboard shortcuts: Backspace (go back), Enter (submit on focused button)
- Progress dialogs for all long-running operations (batch delete, billing recalculation)

---

### 🏗️ Technical Highlights

- **SQLite3 database** with `PRAGMA foreign_keys = ON` and `ON DELETE CASCADE` for referential integrity
- **`@connection_required` decorator** pattern for automatic connection lifecycle management with commit/rollback
- **Modular architecture**: each business domain (stock, customer, rent, sales, reports) is a self-contained Python module
- **PyInstaller packaging**: builds a standalone Windows executable with all assets bundled
- **DataGenerator utility**: Faker-based test data seeder for development and load testing
- Configurable `Time_Thresholds.txt` for billing thresholds (no code change required)

---

### 🔒 Security & Privacy
- All data stored locally — no external transmission without explicit user action
- Google OAuth2 tokens stored locally only; excluded from version control via `.gitignore`
- Database file excluded from git tracking

---

### ⚠️ Known Limitations (v1.0.0)

- The application is **Windows-only** in its current build configuration (PyInstaller `.bat` script targets Windows paths)
- No multi-user or network database support — single-user, single-machine operation only
- Google Drive backup uploads the entire database; no incremental or differential backup
- `DataGenerator.py` must not be run on production data — it inserts thousands of test records

---

## 🗺️ Roadmap

The following features are planned for future releases:

- [ ] 🖨️ **Print / Export to PDF** — printable bill receipts and reports
- [ ] 📧 **Email notifications** — send billing summaries to customers via email
- [ ] 🔐 **Login / password protection** — restrict access to authorized users
- [ ] 🌐 **Multi-language support** — Urdu / regional language interface
- [ ] 📱 **Mobile-friendly companion app** — view reports and customer dues on mobile
- [ ] 🔄 **Automatic daily backup** — scheduled database backup to local folder or Google Drive
- [ ] 📊 **Dashboard charts** — visual graphs for revenue trends, rental activity, and profit margins

---

*For questions, issues, or feature requests, please open a GitHub Issue or submit a Pull Request.*
