from PyQt5.QtWidgets import (
     QMainWindow,
      QMessageBox, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PyQt5.QtCore import QEvent, Qt
from Custom_UI import *
from DatabaseManagement import DatabaseManager


class CustomerCardWidget(QFrame):
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
        name_label = QLabel(f"👤 <b>{self.row_data[1]}</b>")
        name_label.setStyleSheet(f"font-size: {int(30*SCRN_RATIO)}px; color: #333333; border: none;")
        id_label = QLabel(f"🪪 {self.row_data[0]}")
        id_label.setStyleSheet(f"font-size: {int(20*SCRN_RATIO)}px; color: #888888; border: none;")
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        header_layout.addWidget(id_label)
        main_layout.addLayout(header_layout)
        
        # Details
        details = [
            (f"📱 Contact: {self.row_data[2]}"),
            (f"📍 Address: {self.row_data[3]}"),
            (f"🪪 ID Card: {self.row_data[4]}"),
            (f"👥 Referrer: {self.row_data[5]}")
        ]
        
        for detail in details:
            lbl = QLabel(detail)
            lbl.setStyleSheet(f"font-size: {int(22*SCRN_RATIO)}px; color: #555555; border: none;")
            main_layout.addWidget(lbl)
            
        main_layout.addSpacing(int(10*SCRN_RATIO))
        
        # Financials
        fin_layout = QHBoxLayout()
        total_due_lbl = QLabel(f"💰 Total Due: <b>{self.row_data[6]}</b>")
        total_due_lbl.setStyleSheet(f"font-size: {int(22*SCRN_RATIO)}px; color: #D32F2F; border: none;")
        paid_lbl = QLabel(f"💵 Paid: <b>{self.row_data[7]}</b>")
        paid_lbl.setStyleSheet(f"font-size: {int(22*SCRN_RATIO)}px; color: #388E3C; border: none;")
        fin_layout.addWidget(total_due_lbl)
        fin_layout.addStretch()
        fin_layout.addWidget(paid_lbl)
        main_layout.addLayout(fin_layout)
        
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
        self.parent_screen.calling_manager.show_edit_customer_screen(self.row_data)

    def on_delete(self):
        self.parent_screen.calling_manager.delete_single_customer(self.row_data)


class CustomerManagement(QMainWindow):
    def __init__(self, main_stacked_widget, main_menu_screen):
        super().__init__()
        self.initUI()
        self.main_stacked_widget = main_stacked_widget
        self.main_menu_screen = main_menu_screen
        self.db_manager = DatabaseManager()
        self.editing_customer_id = None

    def initUI(self):
        pass

    def setup_customer_management_screen(self):
        data = self.db_manager.get_all_items(table_name=tables["customers"])
        if len(data) == 0:
            QMessageBox.information(self, "No Data", "No Customers Found. You can add one.")
            data = []

        self.card_screen = CardScreen(
            self.main_stacked_widget,
            title="👥 Customer Management",
            card_generator_func=self.generate_customer_card,
            table_data=data,
            search_columns={
                "Search by ID Card": 4,
                "Search by Name": 1
            },
            button_actions=[
                ("➕ Add New Customer", self.show_add_customer_screen),
                ("🗑️ Delete All", self.delete_all_customers)
            ],
            back_action=self.return_to_main_menu,
            db_columns=['id_card_number', 'name'],
            table_name=tables["customers"]
        )
        self.card_screen.calling_manager = self
        self.customer_management_screen = self.card_screen

    def generate_customer_card(self, row_data, parent_screen):
        return CustomerCardWidget(row_data, parent_screen)

    def refresh_customer_management_screen(self):
        data = self.db_manager.get_all_items(table_name=tables["customers"])
        self.card_screen.populate_cards(data)
        self.return_to_customer_management()

    def show_add_customer_screen(self):
        self.editing_customer_id = None
        form_fields = [
            ("Name of Customer:", "name_input"),
            ("Contact Number:", "contact_input"),
            ("Address:", "address_input"),
            ("ID Card Number:", "id_card_input"),
            ("Referrer Name:", "referrer_input")
        ]

        self.add_customer_screen, self.save_button = setup_input_screen(
            self.main_stacked_widget,
            title="➕ Add New Customer",
            form_fields=form_fields,
            save_stock_method=self.save_customer,
            back_action=self.return_to_customer_management,
            calling_object=self
        )

    def show_edit_customer_screen(self, customer_data):
        self.editing_customer_id = customer_data[0]
        self.current_editing_data = customer_data
        form_fields = [
            ("Name of Customer:", "name_input"),
            ("Contact Number:", "contact_input"),
            ("Address:", "address_input"),
            ("ID Card Number:", "id_card_input"),
            ("Referrer Name:", "referrer_input")
        ]

        self.add_customer_screen, self.save_button = setup_input_screen(
            self.main_stacked_widget,
            title="✏️ Edit Customer",
            form_fields=form_fields,
            save_stock_method=self.update_existing_customer,
            back_action=self.return_to_customer_management,
            calling_object=self
        )
        
        # Pre-fill data
        self.name_input.setText(str(customer_data[1]))
        self.contact_input.setText(str(customer_data[2]))
        self.address_input.setText(str(customer_data[3]))
        self.id_card_input.setText(str(customer_data[4]))
        self.referrer_input.setText(str(customer_data[5]))

    def eventFilter(self, obj, event):
        if not hasattr(self, 'add_customer_screen'):
            return super().eventFilter(obj, event)
        if obj == self.add_customer_screen and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Backspace:
                self.return_to_customer_management()
            elif event.key() in [Qt.Key_Enter, Qt.Key_Return]:
                focus_widget = self.add_customer_screen.focusWidget()
                if focus_widget == self.save_button:
                    if self.editing_customer_id is None:
                        self.save_customer()
                    else:
                        self.update_existing_customer()
                return True
        return super().eventFilter(obj, event)

    def check_customer_inputs(self, name, contact, address, id_card):
        if not all([name, contact, address, id_card]):
            QMessageBox.warning(self, "Validation Error", "Please fill in all fields")
            return False
            
        if has_alphabet_or_special_char(id_card) or len(id_card) != 13:
            QMessageBox.warning(self, "Validation Error", "Problem in ID Card , Either less than 13 digits or has alphabet or special character")
            return False
            
        if has_alphabet_or_special_char(contact) or len(contact) != 11:
            QMessageBox.warning(self, "Validation Error", "Problem in Contact , Either less than 11 digits or has alphabet or special character")
            return False
        return True

    def save_customer(self):
        name = self.name_input.text()
        contact = self.contact_input.text()
        address = self.address_input.text()
        id_card = self.id_card_input.text()
        referrer = self.referrer_input.text()
        total_amount_due = 0
        amount_paid = 0
        
        if not self.check_customer_inputs(name, contact, address, id_card):
            return
            
        response = self.db_manager.insert_data(table_name=tables['customers'], columns=CUSTOMER_DB_COLUMNS, values=[name, contact, address, id_card, referrer, total_amount_due, amount_paid])
        if check_warning(self, response):
            return
            
        QMessageBox.information(self, "Customer Saved", f"Customer '{name}' has been saved successfully!")
        self.clear_customer_inputs()
        
        if QMessageBox.question(self, "Rent Items", "Do you want rent items against this customer?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
            self.refresh_customer_management_screen()
        else:
            from RentManagement_ui import RentManagement
            rent_management = RentManagement(self.main_stacked_widget, self.main_menu_screen)
            customer_data = self.db_manager.get_single_item(table_name=tables["customers"], matching_column="id_card_number", item_id=id_card)
            rent_management.setup_rent_management_screen()
            rent_management.show_stock_table_screen_for_rent_item(customer_data)

    def update_existing_customer(self):
        name = self.name_input.text()
        contact = self.contact_input.text()
        address = self.address_input.text()
        id_card = self.id_card_input.text()
        referrer = self.referrer_input.text()
        
        if not self.check_customer_inputs(name, contact, address, id_card):
            return
            
        # The data format for update_customer is the full row: [id, name, contact, address, id_card, referrer, total_due, amount_paid]
        updated_data = [self.editing_customer_id, name, contact, address, id_card, referrer, self.current_editing_data[6], self.current_editing_data[7]]
        response = self.db_manager.update_customer(*updated_data)
        if check_warning(self, response):
            return
            
        QMessageBox.information(self, "Update Successful", "Customer details updated successfully.")
        self.refresh_customer_management_screen()

    def clear_customer_inputs(self):
        self.name_input.clear()
        self.contact_input.clear()
        self.address_input.clear()
        self.id_card_input.clear()
        self.referrer_input.clear()

    def delete_single_customer(self, row_data):
        if not self.confirm_deletion("Delete Customer", f"Are you sure you want to delete {row_data[1]}?"):
            return
            
        customer_id = row_data[0]
        data = self.db_manager.get_all_with_payment_status_matching(to_match_id=True, matching_column='customer_id', item_id=customer_id)
        if data and len(data) > 0:
            QMessageBox.warning(self, "Error", "Customer has pending payments, Please clear them first")
            if not self.confirm_deletion("Again Confirmation", "You still want to delete this customer data it will delete all their records?"):
                return
                
        self.update_stock_quantity_for_deleted_customer(data)
        response = self.db_manager.delete_single_item(customer_id, table_name=tables["customers"])
        if check_warning(self, response):
            return
            
        QMessageBox.information(self, "Delete Successful", "Customer has been deleted successfully.")
        self.refresh_customer_management_screen()

    def delete_all_customers(self):
        if not self.confirm_deletion("Delete All Customers", "Are you sure you want to delete all customers?"):
            return
            
        data = self.db_manager.get_all_with_payment_status_matching()
        if data and len(data) > 0:
            QMessageBox.warning(self, "Error", "Some customers have pending payments, Please clear them first")
            if not self.confirm_deletion("Again Confirmation", "You still want to delete all customers data it will all their information"):
                return
                
        if len(data) > 0:
            self.update_stock_quantity_for_deleted_customer(data)
            
        response = self.db_manager.delete_all_items(tables["customers"])
        if check_warning(self, response):
            return
            
        QMessageBox.information(self, "Delete All Successful", "All customers have been deleted successfully.")
        self.refresh_customer_management_screen()

    def update_stock_quantity_for_deleted_customer(self, data):
        for item in data:
            if item[6].lower() == 'rented':
                check_warning(self, self.db_manager.addition_subtraction_on_cells(table_name=tables['stock'], item_id=item[2], column_name='available_quantity', value=item[3]))
                
    def confirm_deletion(self, title, message):
        reply = QMessageBox.question(
            self, title,
            message,
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        return reply == QMessageBox.Yes

    def return_to_main_menu(self):
        self.main_stacked_widget.setCurrentWidget(self.main_menu_screen)

    def return_to_customer_management(self):
        self.main_stacked_widget.setCurrentWidget(self.customer_management_screen)
