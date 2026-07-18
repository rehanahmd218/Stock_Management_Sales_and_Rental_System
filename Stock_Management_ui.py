from PyQt5.QtWidgets import (
    QMainWindow, QMessageBox, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PyQt5.QtCore import QDateTime, QEvent, Qt
from Custom_UI import *
from DatabaseManagement import DatabaseManager


class StockCardWidget(QFrame):
    def __init__(self, row_data, parent_screen):
        super().__init__()
        self.row_data = row_data
        self.parent_screen = parent_screen
        self.theme_manager = ThemeManager()
        self.initUI()
        
    def initUI(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: {int(15*SCRN_RATIO)}px;
                border: 1px solid #E0E0E0;
            }}
            QFrame:hover {{
                border: 2px solid {self.theme_manager.BUTTONS_BG_COLOR};
            }}
        """)
        self.setMinimumWidth(int(400*SCRN_RATIO))
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Name and ID
        header_layout = QHBoxLayout()
        name_label = QLabel(f"📦 <b>{self.row_data[1]}</b>")
        name_label.setStyleSheet(f"font-size: {int(30*SCRN_RATIO)}px; color: #333333; border: none;")
        id_label = QLabel(f"🪪 ID: {self.row_data[0]}")
        id_label.setStyleSheet(f"font-size: {int(20*SCRN_RATIO)}px; color: #888888; border: none;")
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        header_layout.addWidget(id_label)
        main_layout.addLayout(header_layout)
        
        # Details
        qty_lbl = QLabel(f"🔢 Quantity: <b>{self.row_data[3]}</b> available / {self.row_data[2]} total")
        qty_lbl.setStyleSheet(f"font-size: {int(22*SCRN_RATIO)}px; color: #555555; border: none;")
        main_layout.addWidget(qty_lbl)
        
        price_lbl = QLabel(f"💰 Rental Price: <b>Rs. {self.row_data[4]}</b>")
        price_lbl.setStyleSheet(f"font-size: {int(22*SCRN_RATIO)}px; color: #388E3C; border: none;")
        main_layout.addWidget(price_lbl)
        
        date_lbl = QLabel(f"📅 Price Updated: {QDateTime.fromString(str(self.row_data[5]), DATABASE_DATETIME_FORMAT).toString(DISPLAY_DATE_TIME_FORMAT)}")
        date_lbl.setStyleSheet(f"font-size: {int(20*SCRN_RATIO)}px; color: #888888; border: none;")
        main_layout.addWidget(date_lbl)
            
        main_layout.addSpacing(int(10*SCRN_RATIO))
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch() # Push buttons to the right
        
        edit_btn = QPushButton("✏️ Edit")
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFA000; color: white; border-radius: {int(8*SCRN_RATIO)}px; padding: {int(12*SCRN_RATIO)}px; font-weight: bold; font-size: {int(22*SCRN_RATIO)}px;
            }}
            QPushButton:hover {{ background-color: #FFB300; }}
        """)
        edit_btn.clicked.connect(self.on_edit)
        
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #D32F2F; color: white; border-radius: {int(8*SCRN_RATIO)}px; padding: {int(12*SCRN_RATIO)}px; font-weight: bold; font-size: {int(22*SCRN_RATIO)}px;
            }}
            QPushButton:hover {{ background-color: #E53935; }}
        """)
        delete_btn.clicked.connect(self.on_delete)
        
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        main_layout.addLayout(btn_layout)

    def on_edit(self):
        self.parent_screen.calling_manager.show_edit_stock_screen(self.row_data)

    def on_delete(self):
        self.parent_screen.calling_manager.delete_single_stock(self.row_data)


class StockManagement(QMainWindow):
    def __init__(self, main_stacked_widget, main_menu_screen):
        super().__init__()
        self.initUI()
        self.main_stacked_widget = main_stacked_widget
        self.main_menu_screen = main_menu_screen
        self.db_manager = DatabaseManager()
        self.editing_stock_id = None

    def initUI(self):
        pass

    def setup_stock_management_Screen(self):
        data = self.db_manager.get_stock_with_latest_price()
        if len(data) == 0 or isinstance(data, tuple):
            QMessageBox.information(self, "No Data", "No stock items available. You can add one.")
            data = []

        self.card_screen = CardScreen(
            self.main_stacked_widget,
            title="📦 Stock Management",
            card_generator_func=self.generate_stock_card,
            table_data=data,
            search_columns={
                "Search by Name": 1
            },
            button_actions=[
                ("➕ Add New Stock", self.show_add_stock_screen),
                ("📊 View Price History", self.show_stock_prices),
                ("🗑️ Delete All", self.delete_all_stock)
            ],
            back_action=self.return_to_main_menu,
            db_columns=['st_name'],
            table_name=tables["stock"]
        )
        self.card_screen.calling_manager = self
        self.stock_management_screen = self.card_screen

    def generate_stock_card(self, row_data, parent_screen):
        # Prevent UI breakage if there are unexpected tuple forms
        if isinstance(row_data, str) or (isinstance(row_data, tuple) and len(row_data) < 6):
             return QFrame()
        return StockCardWidget(row_data, parent_screen)

    def refresh_stock_management_screen(self):
        data = self.db_manager.get_stock_with_latest_price()
        if isinstance(data, tuple):
            data = []
        self.card_screen.populate_cards(data)
        self.return_to_stock_management()

    def show_add_stock_screen(self):
        self.editing_stock_id = None
        form_fields = [
            ("Item Name:", "name_input"),
            ("Total Quantity:", "total_quantity_input"),
            ("Available Quantity:", "avail_quantity_input"),
            ("Rental Price:", "price_input")
        ]
        
        self.add_stock_screen, self.save_stock_button = setup_input_screen(
            self.main_stacked_widget,
            title="➕ Add New Stock",
            form_fields=form_fields,
            save_stock_method=self.save_stock,
            back_action=self.return_to_stock_management,
            calling_object=self
        )

    def show_edit_stock_screen(self, stock_data):
        self.editing_stock_id = stock_data[0]
        self.current_editing_stock_price = stock_data[4]
        
        form_fields = [
            ("Item Name:", "name_input"),
            ("Total Quantity:", "total_quantity_input"),
            ("Available Quantity:", "avail_quantity_input"),
            ("Rental Price:", "price_input")
        ]
        
        self.add_stock_screen, self.save_stock_button = setup_input_screen(
            self.main_stacked_widget,
            title="✏️ Edit Stock",
            form_fields=form_fields,
            save_stock_method=self.update_existing_stock,
            back_action=self.return_to_stock_management,
            calling_object=self
        )
        
        # Pre-fill data
        self.name_input.setText(str(stock_data[1]))
        self.total_quantity_input.setText(str(stock_data[2]))
        self.avail_quantity_input.setText(str(stock_data[3]))
        self.price_input.setText(str(stock_data[4]))

    def show_stock_prices(self):
        stock_prices = self.db_manager.get_all_stock_prices()
        if len(stock_prices) == 0:
            QMessageBox.warning(self, "Error", "No stock items available to show prices.")
            return
            
        TableScreen(
            stacked_widget=self.main_stacked_widget,
            title="Stock Prices History",
            headers=['Stock Name', 'Price', 'Price Updated Date'],
            table_data=stock_prices,
            search_columns={"Search by Name": 0},
            button_actions=None,
            back_action=self.return_to_stock_management,
            full_data_columns=[3],
            sortable_columns=[1,2,3],
            show_pagination=True,
            db_columns=['st_name'],
            search_function=self.db_manager.get_all_stock_prices
        ).table_widget.sortByColumn(3, Qt.DescendingOrder)

    def eventFilter(self, obj, event):
        if not hasattr(self, 'add_stock_screen'):
            return super().eventFilter(obj, event)
        if obj == self.add_stock_screen and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Backspace:
                self.return_to_stock_management()
            elif event.key() in [Qt.Key_Enter, Qt.Key_Return]:
                focus_widget = self.add_stock_screen.focusWidget()
                if focus_widget == self.save_stock_button:
                    if self.editing_stock_id is None:
                        self.save_stock()
                    else:
                        self.update_existing_stock()
                return True
        return super().eventFilter(obj, event)

    def check_stock_inputs(self, name, total_quantity, avail_quantity, price):
        if not all([name, total_quantity, avail_quantity, price]):
            QMessageBox.warning(self, "Validation Error", "Please fill in all fields")
            return False
        if has_alphabet_or_special_char(total_quantity) or has_alphabet_or_special_char(avail_quantity) or has_alphabet_or_special_char(price):
            QMessageBox.warning(self, "Validation Error", "Quantity or Price must be a number")
            return False
        if float(avail_quantity) > float(total_quantity):
            QMessageBox.warning(self, "Validation Error", "Available quantity cannot be greater than total quantity")
            return False
        return True

    def save_stock(self):
        name = self.name_input.text()
        avail_quantity = self.avail_quantity_input.text()
        total_quantity = self.total_quantity_input.text()
        price = self.price_input.text()
        
        if not self.check_stock_inputs(name, total_quantity, avail_quantity, price):
            return
            
        current_date_time = QDateTime.currentDateTime().toString(DATABASE_DATETIME_FORMAT)
        response = self.db_manager.insert_data(tables['stock'], columns=STOCK_DB_COLUMNS, values=[name, total_quantity, avail_quantity])
        
        if response[1] == False:
            QMessageBox.warning(self, "Error", response[0])
            return
            
        stock_id = self.db_manager.get_last_item(tables["stock"])[0]
        response = self.db_manager.insert_data(tables['stock_price'], columns=STOCK_PRICE_DB_COLUMNS, values=[stock_id, price, current_date_time])

        if response[1] == False:
            QMessageBox.warning(self, "Error", response[0])
            return
            
        QMessageBox.information(self, "Stock Saved", f"Stock '{name}' has been saved successfully!")        
        self.refresh_stock_management_screen()

    def update_existing_stock(self):
        name = self.name_input.text()
        avail_quantity = self.avail_quantity_input.text()
        total_quantity = self.total_quantity_input.text()
        price = self.price_input.text()
        
        if not self.check_stock_inputs(name, total_quantity, avail_quantity, price):
            return
            
        stock_db_old_price = float(self.current_editing_stock_price)
        stock_table_new_price = float(price)
        
        if stock_db_old_price != stock_table_new_price:
            self.db_manager.insert_data(tables['stock_price'], columns=STOCK_PRICE_DB_COLUMNS, values=[self.editing_stock_id, price, QDateTime.currentDateTime().toString(DATABASE_DATETIME_FORMAT)])
            
        response = self.db_manager.update_multiple_columns(tables["stock"], columns=STOCK_DB_COLUMNS, values=[name, total_quantity, avail_quantity], item_id=self.editing_stock_id)
        
        if response[1] == False:
            QMessageBox.warning(self, "Error", response[0])
            return
            
        QMessageBox.information(self, "Update Successful", "Stock details updated successfully.")
        self.refresh_stock_management_screen()

    def delete_single_stock(self, row_data):
        if not confirm_deletion(self, "Delete Stock", f"Are you sure you want to delete {row_data[1]}?"):
            return

        stock_id = str(row_data[0])
        data = self.db_manager.get_all_with_payment_status_matching(to_match_id=True, item_id=stock_id, matching_column="stock_id")
        
        if data and len(data) > 0:
            QMessageBox.warning(self, 'Deletion Error', "This Stock Item is rented by someone. Don't delete it now.")
            if not confirm_deletion(self, "Confirmation", 'You still want to delete it?\nIt will delete all the values where this stock is used'):
                return
                
        response = self.db_manager.delete_single_item(stock_id, table_name=tables["stock"])
        if not response[1]:
            QMessageBox.warning(self, "Error", response[0])
            return
            
        QMessageBox.information(self, "Delete Successful", "Stock item has been deleted successfully.")
        self.refresh_stock_management_screen()

    def delete_all_stock(self):
        if not confirm_deletion(self, "Delete All Stock", "Are you sure you want to delete all stock items?"):
            return
            
        data = self.db_manager.get_all_with_payment_status_matching()
        if data and len(data) > 0:
            QMessageBox.warning(self, "Error", "Some stock items have been rented out. Please return them before deleting all stock items.")
            if not confirm_deletion(self, "Confirmation", 'You still want to delete it?\nIt will delete all the values where this stock is used'):
                return
                
        response = self.db_manager.delete_all_items(tables["stock"])
        if response[1] == False:
            QMessageBox.warning(self, "Error", response[0])
            return
            
        QMessageBox.information(self, "Delete All Successful", "All stock items have been deleted successfully.")
        self.refresh_stock_management_screen()

    def return_to_main_menu(self):
        self.main_stacked_widget.setCurrentWidget(self.main_menu_screen)
    
    def return_to_stock_management(self):
        self.main_stacked_widget.setCurrentWidget(self.stock_management_screen)

