from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout,
    QMessageBox, QDateTimeEdit, QSpinBox, QLabel,QInputDialog,QDialog,QDialogButtonBox,QScrollArea,QFrame, QHBoxLayout, QPushButton, QGridLayout, QTableWidget, QHeaderView, QTableWidgetItem
)
from PyQt5.QtCore import QDateTime, Qt,QTime
from PyQt5.QtGui import QFont,QColor
from DatabaseManagement import DatabaseManager
from Custom_UI import *
import os
import shutil

class RentCustomerCardWidget(QFrame):
    def __init__(self, row_data, parent_screen, has_active_rents):
        super().__init__()
        self.row_data = row_data
        self.parent_screen = parent_screen
        self.has_active_rents = has_active_rents
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
        
        # Header (Name and ID)
        header_layout = QHBoxLayout()
        name_label = QLabel(f"👤 <b>{self.row_data[1]}</b>")
        name_label.setStyleSheet(f"font-size: {int(30*SCRN_RATIO)}px; color: #333333; border: none;")
        id_label = QLabel(f"🔢 ID: {self.row_data[0]}")
        id_label.setStyleSheet(f"font-size: {int(20*SCRN_RATIO)}px; color: #888888; border: none;")
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        header_layout.addWidget(id_label)
        main_layout.addLayout(header_layout)
        
        # Details
        contact_lbl = QLabel(f"📱 Contact: {self.row_data[2]}")
        contact_lbl.setStyleSheet(f"font-size: {int(22*SCRN_RATIO)}px; color: #555555; border: none;")
        id_card_lbl = QLabel(f"🪪 ID Card: {self.row_data[4]}")
        id_card_lbl.setStyleSheet(f"font-size: {int(22*SCRN_RATIO)}px; color: #555555; border: none;")
        main_layout.addWidget(contact_lbl)
        main_layout.addWidget(id_card_lbl)
        
        amount_due = float(self.row_data[6]) - float(self.row_data[7])
        amount_lbl = QLabel(f"💰 Amount Due: <b>Rs. {amount_due:.2f}</b>")
        color = "#D32F2F" if amount_due > 0 else "#388E3C"
        amount_lbl.setStyleSheet(f"font-size: {int(22*SCRN_RATIO)}px; color: {color}; border: none;")
        main_layout.addWidget(amount_lbl)
            
        main_layout.addSpacing(int(10*SCRN_RATIO))
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch() # Push buttons to the right
        
        rent_btn = QPushButton("➕ Rent Items")
        rent_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #388E3C; color: white; border-radius: {int(8*SCRN_RATIO)}px; padding: {int(12*SCRN_RATIO)}px; font-weight: bold; font-size: {int(22*SCRN_RATIO)}px;
            }}
            QPushButton:hover {{ background-color: #4CAF50; }}
        """)
        rent_btn.clicked.connect(self.on_rent)
        btn_layout.addWidget(rent_btn)
        
        if self.has_active_rents:
            return_btn = QPushButton("🔙 Return Items")
            return_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #1976D2; color: white; border-radius: {int(8*SCRN_RATIO)}px; padding: {int(12*SCRN_RATIO)}px; font-weight: bold; font-size: {int(22*SCRN_RATIO)}px;
                }}
                QPushButton:hover {{ background-color: #2196F3; }}
            """)
            return_btn.clicked.connect(self.on_return)
            btn_layout.addWidget(return_btn)

            edit_btn = QPushButton("✏️ Edit/Clear")
            edit_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #F57C00; color: white; border-radius: {int(8*SCRN_RATIO)}px; padding: {int(12*SCRN_RATIO)}px; font-weight: bold; font-size: {int(22*SCRN_RATIO)}px;
                }}
                QPushButton:hover {{ background-color: #FF9800; }}
            """)
            edit_btn.clicked.connect(self.on_edit)
            btn_layout.addWidget(edit_btn)
            
        main_layout.addLayout(btn_layout)

    def on_rent(self):
        self.parent_screen.calling_manager.show_stock_table_screen_for_rent_item(self.row_data[0])

    def on_return(self):
        self.parent_screen.calling_manager.show_rented_items_screen_for_customer(self.row_data[0], True)

    def on_edit(self):
        self.parent_screen.calling_manager.show_rented_item_for_edit_rent_screen(self.row_data[0], True)


class RentManagement(QWidget):
    def __init__(self, main_stacked_widget, main_menu_screen):
        super().__init__()
        self.main_stacked_widget = main_stacked_widget
        self.main_menu_screen = main_menu_screen
        self.db_manager = DatabaseManager()
        self.active_rents_search = False

    def setup_rent_management_screen(self):
        customers_data = self.db_manager.get_all_customers_based_on_constraints(active_rents_search=False)
        if len(customers_data) == 0:
            QMessageBox.warning(self, "No Customers", "There are no customers available so can't proceed")
            return

        active_customer_ids = {row[0] for row in self.db_manager.get_all_customers_based_on_constraints(active_rents_search=True)}
        
        self.card_screen = CardScreen(
            self.main_stacked_widget,
            title="🤝 Rent Management",
            card_generator_func=lambda row, parent: RentCustomerCardWidget(row, parent, row[0] in active_customer_ids),
            table_data=customers_data,
            search_columns={
                "Search by ID Card": 4,
                "Search by Name": 1
            },
            filter_options=[
                ("All Customers", lambda: self.filter_customers("all")),
                ("With Active Rents", lambda: self.filter_customers("active")),
                ("No Active Rents", lambda: self.filter_customers("inactive"))
            ],
            button_actions=[],
            back_action=self.return_to_main_menu,
            db_columns=['id_card_number', 'name'],
            search_function=self.get_customers_based_on_search
        )
        self.card_screen.calling_manager = self
        self.rent_management_screen = self.card_screen

    def filter_customers(self, filter_type):
        self.active_rents_search = (filter_type == "active")
        
        if filter_type == "active":
            customers_data = self.db_manager.get_all_customers_based_on_constraints(active_rents_search=True)
            active_customer_ids = {row[0] for row in customers_data}
        elif filter_type == "inactive":
            all_customers = self.db_manager.get_all_customers_based_on_constraints(active_rents_search=False)
            active_ids = {row[0] for row in self.db_manager.get_all_customers_based_on_constraints(active_rents_search=True)}
            customers_data = [c for c in all_customers if c[0] not in active_ids]
            active_customer_ids = set()
        else: # "all"
            customers_data = self.db_manager.get_all_customers_based_on_constraints(active_rents_search=False)
            active_customer_ids = {row[0] for row in self.db_manager.get_all_customers_based_on_constraints(active_rents_search=True)}
            
        self.card_screen.card_generator_func = lambda row, parent: RentCustomerCardWidget(row, parent, row[0] in active_customer_ids)
        self.card_screen.initial_data = customers_data
        
        # Trigger an update of the cards via search input if typed, otherwise just populate
        self.card_screen.perform_database_search(calling_from_outside=True)

    def get_customers_based_on_search(self, column_param_dict):
        results = self.db_manager.get_all_customers_based_on_constraints(self.active_rents_search, column_param_dict)
        return results

    def refresh_rent_management_screen(self):
        self.setup_rent_management_screen()
        self.return_to_rent_management()
    
    def show_stock_table_screen_for_rent_item(self, row):
       ### One Time Passing id as tuple to the function and one time the row number obtained from the table so have to extract id
        if not type(row)==tuple:
            if type(row) == int or type(row) == str:
                customer_id = row
            else:
                customer_id = self.customer_table.item(row, 0).text()
            customer_data = self.db_manager.get_single_item(customer_id,table_name=tables["customers"])
            customer_id = customer_data[0]
        else:
            customer_id=row[0]

        # Show Stock Table Screen
        stock_data = self.db_manager.get_stock_with_latest_price()
        if type(stock_data)==tuple:
            QMessageBox.warning(self, "Error", stock_data[0])
            return
        ## Assigning Quantity to Rent = 0 for every row
        stock_data = [stock + ('0',) for stock in stock_data]
        self.stock_selector=StockSelector(available_quantity_index=3)
        self.stock_table = TableScreen(
            self.main_stacked_widget,
            title="Select Items to Rent",
            headers=['Stock ID', 'Item Name','Total Quantity','Available Quantity', 'Price','Price Updated Date', 'Quantity to Rent'],
            table_data=stock_data,
            editable_columns=[6],
            button_actions=[('Rent Items', lambda: self.confirm_rent_items( customer_id)),("View Selected Items", self.stock_selector.show_selected_items)],
            back_action=self.return_to_rent_management,
            full_data_columns=[5],
            search_columns={"Search By Stock Name": 1},
            show_pagination=True,
            ending_zero=True,
            db_columns=['st_name'],
            search_function=self.db_manager.get_stock_with_latest_price,
            last_col_function={"Add":self.stock_selector.add_item},

        ).table_widget
        self.stock_selector.table_widget=self.stock_table

    def get_current_date_or_custom(self):
        # Handle Date-Time Selection
        current_date_time = QDateTime.currentDateTime()
        if QMessageBox.question(
            self, "Use Current Date-Time",
            f"Use the current date-time ({current_date_time.toString('MM/dd/yyyy hh:mm AP')}) for this rental?",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.No:
            # Create a QDateTimeEdit widget for date and time selection
            date_time_picker = QDateTimeEdit(self)
            date_time_picker.setDateTime(current_date_time)  # Set the current date-time as default
            date_time_picker.setDisplayFormat("MM/dd/yyyy hh:mm AP")  # Format as MM/DD/YYYY hh:mm AM/PM
            date_time_picker.setCalendarPopup(True)  # Enable calendar popup for date selection

            # Show the widget in a dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Select Date-Time")
            dialog_layout = QVBoxLayout(dialog)
            dialog_layout.addWidget(date_time_picker)

            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            dialog_layout.addWidget(button_box)

            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)

            if dialog.exec_() == QDialog.Accepted:
                current_date_time = date_time_picker.dateTime()
        return current_date_time.toString(DATABASE_DATETIME_FORMAT)

    def confirm_rent_items(self, customer_id):
        final_stock_data=self.stock_selector.get_selected_items()
        if len(final_stock_data)==0:
            QMessageBox.warning(self, "Validation Error", "No items selected for rent.")
            return
        current_date_time = self.get_current_date_or_custom()
        advance_amount=0.0
        if QMessageBox.question(
            self, "Advance Payment",
            f"Would you like to proceed with advance payment for this rental?",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            advance_amount, ok = QInputDialog.getDouble(self, "Advance Payment", "Enter the advance payment amount:", 0.0, 0.0, 100000.0, 2)
            if not ok:
                advance_amount=0.0

        if float(advance_amount)>0:
            response = self.db_manager.addition_subtraction_on_cells(tables["customers"], customer_id,advance_amount,"amount_paid")
            if check_warning(self,response):
                return
            response=self.db_manager.insert_data(tables["payments"],columns=PAYMENTS_DB_COLUMNS,values=[customer_id,advance_amount,"0",current_date_time])
            if check_warning(self,response):
                return
            
        for row in final_stock_data:
            response=self.db_manager.insert_data(tables["rent"],columns=RENT_DB_COLUMNS,values=[customer_id,row[0],row[6],current_date_time,'Rented',0])
            if check_warning(self,response):
                return
            rent_quantity=float(row[6])*-1
            response=self.db_manager.addition_subtraction_on_cells(tables["stock"], row[0], rent_quantity, "available_quantity")
            if check_warning(self,response):
                return
        QMessageBox.information(self, "Success", "Item rented successfully.")
        self.refresh_rent_management_screen()

    def confirm_deletion(self, title, message):
        reply = QMessageBox.question(
            self, title,
            message,
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        return reply == QMessageBox.Yes

    def return_to_rent_management(self):
        self.main_stacked_widget.setCurrentWidget(self.rent_management_screen)

    def show_rented_items_screen_for_customer(self, row, is_customer_id=False):
        if is_customer_id:
            customer_id=row
        else:
            customer_id = self.customer_table.item(row, 0).text()
        
        rented_items=self.db_manager.get_rent_data(customer_id=customer_id,status_list=["Rented","Stock Recieved"])
        if len(rented_items) == 0:
            return
        self.rented_items_table = TableScreen(
            self.main_stacked_widget,
            title="Rented Items",
            headers=['Rent ID', "Customer ID","Customer Name", "Stock ID","Stock Name","Quantity Rented","Quantity Returned",  'Rent Date-Time', "Return Date", 'Status', 'Amount Due'],
            
            table_data=rented_items,
            editable_columns=[6],
            button_actions=[
                ('Return Specified', lambda: self.return_all_items(customer_id,all_items=False)),
                ('Return All', lambda: self.return_all_items(customer_id,all_items=True)),
            ],
            back_action=self.return_to_rent_management,
            full_data_columns=[2,7,8],
            sortable_columns=[5,7,8,9],
            hidden_columns=[0,1,3],
            search_columns={"Search By Stock Name": 4,"Search By Status": 9},
            show_pagination=False,
        ).table_widget


    def calculate_days( self,rent_date, return_date):

        # Calculate base days
        days = rent_date.daysTo(return_date)
        
        # Get times for comparison
        rent_time = rent_date.time()
        return_time = return_date.time()
        
        # Set default thresholds
        evening_rent_time = QTime(18, 0)  # 6:00 PM
        morning_return_time = QTime(9, 0)  # 9:00 AM
        
        # Read custom thresholds if available
        if os.path.exists("Time_Thresholds.txt"):
            with open("Time_Thresholds.txt", "r") as file:
                lines = file.readlines()
                evening_rent_time = QTime(int(lines[0].split(":")[1]), 0)
                morning_return_time = QTime(int(lines[1].split(":")[1]), 0)
        else:
            # Create default threshold file
            with open("Time_Thresholds.txt", "w") as file:
                file.write("Evening Rent Time:18\nMorning Return Time:9")
        
        # Same day rentals always count as 1 day
        if days == 0:
            return 1
        
        # Add 1 to base days for partial days
        days += 1
        
        # Evening rental discount (6 PM - 11:59 PM)
        if rent_time >= evening_rent_time:  # Removed upper bound check as QTime handles wraparound
            days -= 1
            
        # Early return discount (12 AM - 9 AM)
        # Only apply if rental is more than 1 day and hasn't already been reduced to 1
        if days > 1 and return_time <= morning_return_time:
            days -= 1
            
        return max(1, days)  # Ensure we never return less than 1 day
                    

    def calculate_bill(self,table_data,calling_from_rent_management=False,user_return_date=None):
        rented_items=table_data
        
        progress=create_progress_dialog(self,title="Calculating Bill",data_length=len(rented_items))

        
        total_amount = 0
        grouped_items = {}
        rent_amount_due_dict = {}
        rented_items_total = 0

        for index, item in enumerate(rented_items):
            # Update progress
            progress.setValue(index)
            if progress.wasCanceled():
                return False
            
            if item[9].lower() == 'paid':
                continue
            
            item_total = 0.0
            rent_date = QDateTime.fromString(item[7], DATABASE_DATETIME_FORMAT)

            if item[9].strip() == 'Stock Recieved':
                return_date = QDateTime.fromString(item[8], DATABASE_DATETIME_FORMAT)
            else:
                if user_return_date:
                    return_date = QDateTime.fromString(user_return_date, DATABASE_DATETIME_FORMAT)
                else:
                    return_date = QDateTime.currentDateTime()
                    
            days_rented = self.calculate_days(rent_date, return_date)
            stock_price = self.db_manager.get_stock_price_on_rent_date(item[3], item[7])
            if stock_price[0] == '':
                progress.close()
                QMessageBox.warning(self, "Error", f"Stock Price not found for name {item[4]} For Date: " + rent_date.toString(DATE_TIME_FORMAT_QT))
                return False
            
            stock_price = float(stock_price[0])

            item_total = days_rented * float(stock_price) * int(item[5])
            item_total_fridays = self.count_fridays(rent_date, return_date)* float(stock_price) * int(item[5])
            if item[9].lower() == "rented":
                rented_items_total += item_total
            total_amount += item_total
            
            rent_date_without_time=rent_date.toString(DATE_TIME_FORMAT_QT.replace(" hh:mm AP",""))

            days_rented_modified=f'{days_rented} : {rent_date_without_time}'
            # Group items by days rented
            if days_rented_modified not in grouped_items:
                grouped_items[days_rented_modified] = {
                    "items": [],
                    "total_weeks": days_rented // 7,
                    "total_fridays": self.count_fridays(rent_date, return_date),
                    "total_amount": 0,
                    "rent_date": rent_date.toString(DATE_TIME_FORMAT_QT),
                    "return_date": return_date.toString(DATE_TIME_FORMAT_QT),
                    'days_rented':days_rented,
                    'total_fridays_amount':0,
                }

            grouped_items[days_rented_modified]["items"].append({
                "item_name": item[4],
                "quantity": item[5],
                "days_rented": days_rented,
                "item_total": item_total,
                "item_price": stock_price,
                "status": item[9],
                "item_total_fridays": item_total_fridays,
            })

            grouped_items[days_rented_modified]["total_amount"] += item_total
            grouped_items[days_rented_modified]["total_fridays_amount"] += item_total_fridays

            
            if isinstance(rented_items[index],list):
                rented_items[index][10] = item_total
            
            rent_amount_due_dict[item[0]] = item_total
                
        grouped_items['rented_items_total']=rented_items_total


        # Close progress dialog
        progress.setValue(len(rented_items))
        if not calling_from_rent_management:
            if check_warning(self, self.db_manager.update_all_specific_column(tables["rent"], updates=rent_amount_due_dict, column_name="amount_due")):
                    return False
        return (grouped_items,rented_items)
    



    def show_bill_summary(self, customer_id, grouped_items):
        total_rented_items_amount = grouped_items.pop('rented_items_total', 0)
        
        screen_width,screen_height=get_screen_size()

        # Calculate dialog dimensions (70% of screen width, 80% of screen height)
        dialog_width = int(screen_width * 0.7)
        dialog_height = int(screen_height * 0.8)

        # Create bill dialog with calculated dimensions
        bill_dialog = QDialog(self)
        bill_dialog.setWindowTitle("Bill Summary")
        bill_dialog.setFont(QFont("Arial", int(10*SCRN_RATIO)))
        bill_dialog.setMinimumWidth(int(900*SCRN_RATIO))
        bill_dialog.resize(dialog_width, dialog_height)
        # Position at 1/4 of screen width
        bill_dialog.move(int(30*SCRN_RATIO), (screen_height - bill_dialog.height()) // 2)

        # Main layout
        main_layout = QVBoxLayout(bill_dialog)
        main_layout.setContentsMargins(int(20*SCRN_RATIO), int(20*SCRN_RATIO), 
                                    int(20*SCRN_RATIO), int(20*SCRN_RATIO))
        
        # Create scroll area for entire content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
        
        # Main content widget
        content_widget = QWidget()
        scroll_layout = QVBoxLayout(content_widget)
        scroll_layout.setSpacing(int(20*SCRN_RATIO))
        
        # Add header label
        header_label = QLabel("Bill Summary")
        header_label.setFont(QFont("Arial", int(12*SCRN_RATIO), QFont.Bold))
        scroll_layout.addWidget(header_label)
        
        total_amount = 0
        total_fridays_amount = 0
        # Create table for each rental group
        for days_rented, data in grouped_items.items():
            # Group frame
            group_frame = QFrame()
            group_frame.setFrameStyle(QFrame.Box | QFrame.Raised)
            group_layout = QVBoxLayout(group_frame)
            group_layout.setSpacing(int(15*SCRN_RATIO))
            
            # Rental period info
            period_grid = QGridLayout()
            period_grid.setSpacing(int(10*SCRN_RATIO))
            period_grid.addWidget(create_bold_label("Days Rented:"), 0, 0)
            period_grid.addWidget(create_bold_label(str(data['days_rented'])), 0, 1)
            period_grid.addWidget(create_bold_label("Total Weeks:"), 0, 2)
            period_grid.addWidget(create_bold_label(str(data['total_weeks'])), 0, 3)
            period_grid.addWidget(create_bold_label("Total Fridays:"), 0, 4)
            period_grid.addWidget(create_bold_label(str(data['total_fridays'])), 0, 5)
            period_grid.addWidget(create_bold_label("Rent Date:"), 1, 0)
            period_grid.addWidget(create_bold_label(str(data['rent_date'])), 1, 1)
            period_grid.addWidget(create_bold_label("Return Date:"), 1, 2)
            period_grid.addWidget(create_bold_label(str(data['return_date'])), 1, 3)
            group_layout.addLayout(period_grid)
            

            # Items table
            table = QTableWidget()
            table.setColumnCount(5)
            table.setHorizontalHeaderLabels(["Item Name", "Price (Rs)", "Quantity", "Total (Rs)", "Status"])
            table.setRowCount(len(data['items']))
            
            # Configure table properties
            table.verticalHeader().hide()  # Hide row numbers
            table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable vertical scrollbar
            table.verticalHeader().setDefaultSectionSize(int(40*SCRN_RATIO))  # Set row height
            
            # Make all columns stretch
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
            # Style the header
            header = table.horizontalHeader()
            header.setFixedHeight(int(40*SCRN_RATIO))
            header.setStyleSheet("QHeaderView::section { background-color: #f0f0f0; padding: 5px; }")
            
            # Populate table
            for row, item in enumerate(data['items']):
                name_item = QTableWidgetItem(item['item_name'])
                name_item.setFont(QFont("Arial", int(12*SCRN_RATIO)))
                price_item = QTableWidgetItem(f"{item['item_price']:.2f}")
                price_item.setFont(QFont("Arial", int(12*SCRN_RATIO)))
                price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                qty_item = QTableWidgetItem(str(item['quantity']))
                qty_item.setFont(QFont("Arial", int(12*SCRN_RATIO)))
                qty_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                total_item = QTableWidgetItem(f"{item['item_total']:.2f}")
                total_item.setFont(QFont("Arial", int(12*SCRN_RATIO)))
                total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                status_item = QTableWidgetItem(item['status'])
                status_item.setFont(QFont("Arial", int(12*SCRN_RATIO)))
                status_item.setTextAlignment(Qt.AlignCenter)
                
                # Set background colors
                if item['status'].lower() == 'stock recieved':
                    status_item.setBackground(QColor(200, 255, 200))  # Light green
                else:
                    status_item.setBackground(QColor(200, 200, 255))  # Light blue
                
                table.setItem(row, 0, name_item)
                table.setItem(row, 1, price_item)
                table.setItem(row, 2, qty_item)
                table.setItem(row, 3, total_item)
                table.setItem(row, 4, status_item)

                table.setEditTriggers(QTableWidget.NoEditTriggers)

            # Set fixed table height based on content
            table_height = (table.horizontalHeader().height() + 
                        table.rowHeight(0) * table.rowCount())
            table.setFixedHeight(table_height)
            
            group_layout.addWidget(table)
            
            # Group total
            group_total = QLabel(f"Group Total: Rs {data['total_amount']:.2f}")
            group_total.setAlignment(Qt.AlignRight)
            group_total.setFont(QFont("Arial", int(18*SCRN_RATIO), QFont.Bold))
            group_layout.addWidget(group_total)
            

            group_firday_total = QLabel(f"Fridays Amount: Rs {data['total_fridays_amount']:.2f}")
            group_firday_total.setAlignment(Qt.AlignRight)
            group_firday_total.setFont(QFont("Arial", int(16*SCRN_RATIO), QFont.Bold))
            group_layout.addWidget(group_firday_total)
            
            scroll_layout.addWidget(group_frame)
            total_amount += data['total_amount']
            total_fridays_amount += data['total_fridays_amount']
        
        # Get already paid amount
        already_paid_amount = float(self.db_manager.get_single_item(customer_id, tables["customers"])[7])
        
        # Summary section
        summary_frame = QFrame()
        summary_frame.setFrameStyle(QFrame.Box | QFrame.Raised)
        summary_layout = QVBoxLayout(summary_frame)
        summary_layout.setSpacing(int(10*SCRN_RATIO))
        
        summary_layout.addWidget(create_bold_label(f"Grand Total Amount: Rs {total_amount:.2f}"))
        summary_layout.addWidget(create_bold_label(f'Grand Total Fridays Amount: Rs {total_fridays_amount:.2f}'))
        summary_layout.addWidget(create_bold_label(f"Amount Already Paid: Rs {already_paid_amount:.2f}"))
        amount_due = total_amount - already_paid_amount
        due_label = create_bold_label(f"Amount To Be Paid Now: Rs {amount_due:.2f}")
        due_label.setStyleSheet("color: red;")
        summary_layout.addWidget(due_label)
        
        if total_rented_items_amount > 0:
            stock_amount = amount_due - total_rented_items_amount
            if stock_amount <= 0:
                summary_layout.addWidget(create_bold_label("Remaining Amount for Received Stock: Rs 0"))
                if total_rented_items_amount + stock_amount < 0:
                    summary_layout.addWidget(create_bold_label("Remaining Amount for Rented Items: Rs 0"))
                else:
                    summary_layout.addWidget(create_bold_label(
                        f"Remaining Amount for Rented Items: Rs {total_rented_items_amount + stock_amount:.2f}"))
            else:
                summary_layout.addWidget(create_bold_label(
                    f"Remaining Amount for Received Stock: Rs {stock_amount:.2f}"))
                summary_layout.addWidget(create_bold_label(
                    f"Remaining Amount for Rented Items: Rs {total_rented_items_amount:.2f}"))
        
        scroll_layout.addWidget(summary_frame)
        
        # Update customer amount due
        response = self.db_manager.update_customer_amount_due(customer_id, total_amount)
        if check_warning(self, response):
            return False
        
        # Set the scroll content
        scroll_area.setWidget(content_widget)
        
        # Add OK button
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        main_layout.addWidget(button_box)
        button_box.accepted.connect(bill_dialog.accept)
        
        # Show dialog
        bill_dialog.show()
        
        return (True, total_amount, total_rented_items_amount, already_paid_amount, bill_dialog)

    def allocate_payments_to_items(self, items, total_paid_amount):
        """
        Allocates available payment amount to rented items, starting with highest amount items.
        Returns updated items list with payment statuses and remaining amount.
        """
        # Create a copy of the items list to avoid modifying the original directly
        sorted_items = sorted(items, key=lambda x: float(x[10]), reverse=True)
        remaining_amount = total_paid_amount
        
        for item in sorted_items:
            item_amount = float(item[10])
            if item[9].lower() != 'stock recieved':
                continue
                
            if remaining_amount >= item_amount:
                # Can pay for this item completely
                item[9] = 'Paid'
                item[10] = 0  # Set amount_due to 0
                remaining_amount -= item_amount
            
        return sorted_items, remaining_amount


    def show_payment_dialog(self, customer_id, total_amount, total_rented_items_amount, already_paid_amount,stock_data,final_rented_items, bill_dialog=None):
        # Create payment dialog



        payment_dialog = QDialog(self)
        payment_dialog.setWindowTitle("Return All Items")
        payment_dialog.resize(int(400*SCRN_RATIO), int(200*SCRN_RATIO))
        
   
        amount_to_be_paid_now = int(total_amount-already_paid_amount)
        screen_width,screen_height=get_screen_size()

        # Position payment dialog on right side
        payment_dialog.move(screen_width - payment_dialog.width(), 
                          (screen_height - payment_dialog.height()) // 2)
        
        payment_layout = QVBoxLayout(payment_dialog)

        paid_label = create_bold_label("Amount Paid:")
        paid_spin = QSpinBox()
        paid_spin.setRange(-100000, 100000)
        paid_spin.setValue(amount_to_be_paid_now)
        paid_spin.setFont(QFont("Arial", int(18*SCRN_RATIO)))
        payment_layout.addWidget(paid_label)
        payment_layout.addWidget(paid_spin)

        discount_label =create_bold_label("Discount:")
        discount_spin = QSpinBox()
        discount_spin.setRange(0, 100000)
        discount_spin.setFont(QFont("Arial", int(18*SCRN_RATIO)))
        payment_layout.addWidget(discount_label)
        payment_layout.addWidget(discount_spin)

        payment_button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        payment_layout.addWidget(payment_button_box)

        def handle_payment_finalization():
            paid_amount = paid_spin.value()
            discount_amount = discount_spin.value()
            total_paid_amount = already_paid_amount + paid_amount + discount_amount
            remaining_amount = total_amount - total_paid_amount
            
            if remaining_amount < 0:
                QMessageBox.warning(payment_dialog, "Payment Error", "Customer has some Pending Amount on you")
                return
            
            self.update_stock_quantities(stock_data)

            
            # Store the result in a new variable instead of trying to reassign to final_rented_items
            processed_items, remaining_payment = self.allocate_payments_to_items(final_rented_items, total_paid_amount)
            total_amount_due=total_amount-remaining_payment

            if remaining_amount > 0 or total_rented_items_amount > 0:
                if check_warning(self, self.db_manager.update_multiple_columns(
                    tables["customers"],
                    customer_id,
                    ["amount_paid", "total_amount_due"],
                    [remaining_payment, total_amount_due]
                )):
                    return
            # Now use processed_items in the loop
            for item in processed_items:
                if item[0] is None:
                    self.db_manager.insert_data(
                        table_name=tables["rent"],
                        columns=RENT_DB_COLUMNS,
                        values=[customer_id, item[3], item[5], item[7], 'Rented', item[10]]
                    )
                else:
                    self.db_manager.update_multiple_columns(
                        tables["rent"], 
                        item[0], 
                        ["payment_status", "return_date", "quantity", 'amount_due'], 
                        [item[9], item[8], item[5], item[10]]
                    )
            
            if remaining_amount == 0:
                if total_rented_items_amount <= 0:
                    if check_warning(self, self.db_manager.update_multiple_columns(
                        tables["customers"],
                        customer_id,
                        ["amount_paid", "total_amount_due"],
                        [0, 0]
                    )):
                        return
                    
                    rented_items = self.db_manager.get_all_with_payment_status_matching(
                        matching_column="customer_id",
                        item_id=customer_id,
                        to_match_id=True
                    )

                    if check_warning(self, self.db_manager.update_payement_to_paid_for_all(customer_id, rented_items)):
                        return

            if paid_amount > 0 or discount_amount > 0:
                self.db_manager.insert_data(
                    tables["payments"],
                    columns=PAYMENTS_DB_COLUMNS,
                    values=[
                        customer_id,
                        paid_amount,
                        discount_amount,
                        QDateTime.currentDateTime().toString(DATABASE_DATETIME_FORMAT)
                    ]
                )

            QMessageBox.information(payment_dialog, "Success", "Items returned successfully.")
            if bill_dialog:
                bill_dialog.accept()
            payment_dialog.accept()

        def handle_payment_cancellation():
            if bill_dialog:
                bill_dialog.accept()
            payment_dialog.reject()

        payment_button_box.accepted.connect(handle_payment_finalization)
        payment_button_box.rejected.connect(handle_payment_cancellation)
        
        payment_dialog.show()
        result = payment_dialog.exec_()
        return result == QDialog.Accepted

    def return_all_items(self, customer_id, all_items):
        return_date_time = self.get_current_date_or_custom()
        response_data = self.check_all_inputs_rented_table(return_all_items=all_items,return_date=return_date_time)
        if not response_data:
            return
        final_rented_items,stock_returned = response_data
        
        grouped_items,final_rented_items = self.calculate_bill(user_return_date=return_date_time,table_data=final_rented_items,calling_from_rent_management=True)
        if not grouped_items:
            return False
        
        response = self.show_bill_summary(customer_id, grouped_items=grouped_items)

        if not response or not isinstance(response, tuple):
            return
        
        _, total_amount, total_rented_items_amount, already_paid_amount, bill_dialog = response
        
        # Show payment dialog alongside bill
        if self.show_payment_dialog(customer_id, total_amount, total_rented_items_amount, already_paid_amount, bill_dialog=bill_dialog,stock_data=stock_returned,final_rented_items=final_rented_items):
            self.return_to_rent_management()

        
    def count_fridays(self, start_date, end_date):
        fridays = 0
        while start_date <= end_date:
            if start_date.date().dayOfWeek() == Qt.Friday:
                fridays += 1
            start_date = start_date.addDays(1)
        return fridays

    
    def check_all_inputs_rented_table(self,return_date,return_all_items=True):
        rented_items = get_table_data(self.rented_items_table)

        if isinstance(rented_items, tuple):
            QMessageBox.warning(self, "Error", rented_items[0])
            return False
    
        final_rented_items=[]
        stock_returned = {}
        
        for item in rented_items:
            ### Skips the items which are already paid
            ### Quantity Returned item[6]
            if (item[9].strip() == 'Stock Recieved') or (int(item[6]) == 0 and not return_all_items):
                final_rented_items.append(item)
                continue    
            
            rent_id, quantity_returned = int(item[0]),item[6]
            if has_alphabet_or_special_char(quantity_returned) or int(quantity_returned) < 0:
                QMessageBox.warning(self, "Validation Error", f"Enter a valid quantity to return for item ID {rent_id}\nName: {item[4]}")
                return False
            
            quantity_returned=int(quantity_returned)
            previous_quantity = int(item[5])
            stock_id=int(item[3])

            if quantity_returned > previous_quantity:
                QMessageBox.warning(self, "Validation Error", f"Quantity can't be increased for item ID {rent_id}. Go to Rent Items for this.\nName: {item[4]}")
                return False
            if quantity_returned == previous_quantity or return_all_items:
                item[9]="Stock Recieved"
                item[8]=return_date
                stock_returned[stock_id] = previous_quantity
                final_rented_items.append(item)
            else:
                stock_returned[stock_id] = quantity_returned
                ### Setting Up two Rented Items one will be pending and for other remaining quantity a new rent will be made
                remaining_quantity = previous_quantity - quantity_returned
                new_rent_item=item.copy()
                item[9]="Stock Recieved"
                item[5]=quantity_returned
                item[8]=return_date

                ## Setting Up Rent For Remaining Quantity
                new_rent_item[0]=None
                new_rent_item[9]='Rented'
                new_rent_item[7]=item[7]
                new_rent_item[8]=None
                new_rent_item[5]=remaining_quantity
                final_rented_items.append(item)
                final_rented_items.append(new_rent_item)

        return (final_rented_items, stock_returned)

    def _update_full_returned_items(self, full_returned_items, return_date_time):
        for item in full_returned_items:
            response = self.db_manager.update_multiple_columns(
                tables["rent"], item, ["payment_status", "return_date"], ["Stock Recieved", return_date_time]
            )
            if check_warning(self, response):
                return False
        return True


    def update_stock_quantities(self, stock_returned):
        for stock_id, quantity in stock_returned.items():
            response = self.db_manager.addition_subtraction_on_cells(
                tables["stock"], stock_id, quantity, "available_quantity"
            )
            if check_warning(self, response):
                return False
        return True

            

    def show_rented_item_for_edit_rent_screen(self, row, is_customer_id=False):
        if is_customer_id:
            self.customer_id = row
        else:
            self.customer_id = self.customer_table.item(row, 0).text()

        rented_items=self.db_manager.get_rent_data(customer_id=self.customer_id,status_list=["Rented",'Stock Recieved'])
        if len(rented_items) == 0:
            return
        self.rented_items_table = TableScreen(
            self.main_stacked_widget,
            title="Rented Items",
            headers=['Item ID', "Customer ID","Customer Name","Stock ID","Stock Name", "Quantity Rented", "Quantity Returned",'Rent Date-Time',"Return Date", 'Status','Amount Due'],
            table_data=rented_items,
            button_actions=[
                ('Update All', self.update_All_rented_items),
                ('Delete / Clear Rents', self.delete_rent_items),
            ],
            back_action=self.return_to_rent_management,
            editable_columns=[3,4,5,6,7,8,9],
            full_data_columns=[2,7,8],
            sortable_columns=[5,6,7,9],
            hidden_columns=[0,1,3],
            search_columns={"Search By Stock Name": 4},
            show_pagination=False,
            last_col_function={"Update": self.update_single_rent_item,'Clear':self.delete_single_rent_item}
        ).table_widget

    def is_valid_payment_status(self,payment_status):
        if payment_status in ["Paid","Stock Recieved","Rented"]:
            return True
        return False

    def is_valid_date(self,date_str):
        if date_str is None:
            return False
        return date_str.strip() != ''
    


    def update_single_rent_item(self,row):
        row_data=get_single_row_data(self.rented_items_table,row)
        self.update_All_rented_items(single_row_data=row_data)


    def delete_single_rent_item(self,row):
        row_data=get_single_row_data(self.rented_items_table,row)
        self.delete_rent_items(row=row_data)

    def delete_rent_items(self, row=None):

        if QMessageBox.question(
            self, "Confirmation", "This Action will Clear the Rent Record\nAre you sure you want to Clear this item?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        ) == QMessageBox.No:
            return False

        self.backup_database()
        rent_data=None
        if not row:
            rent_data = get_table_data(self.rented_items_table)
        else:
            rent_data = [row]

        for item in rent_data:
            if not item[9].strip() == 'Stock Recieved':
                stock_id = int(item[3])
                quantity_rented = int(item[5])
                response = self.db_manager.addition_subtraction_on_cells(
                    tables["stock"], stock_id, quantity_rented, "available_quantity"
                )
                if check_warning(self, response):
                    QMessageBox.warning(self, "Error", "Failed to delete item.")
                    return False
            self.db_manager.delete_single_item(table_name=tables["rent"], id=item[0])
            
        QMessageBox.information(self, "Success", "Item deleted successfully.")
        if not row:
            self.return_to_rent_management()
        else:
            table_data = get_table_data(self.rented_items_table)
            if len(table_data)<=1:
                self.return_to_rent_management()
            else:
                self.show_rented_item_for_edit_rent_screen(self.customer_id, True)
        
    
    def safe_adding_stock_returning_data(self,stock_returning_data, stock_id, quantity):
        if stock_id in stock_returning_data:
            stock_returning_data[stock_id] += quantity
        else:
            stock_returning_data[stock_id] = quantity


    def backup_database(self):
        backup_folder = "D:/Database_Backup"
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)
        
        database_path = 'stock_rental_system.db'
        current_date_time = QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")
        backup_file_name = f"stock_rental_system_backup_{current_date_time}.db"
        backup_file_path = os.path.join(backup_folder, backup_file_name)
        
        try:
            shutil.copy(database_path, backup_file_path)
            print(f'Database Backup Created Successfully: {backup_file_name}')
        except Exception as e:
            QMessageBox.warning(self, "Backup Failed", f"Failed to create database backup. Error: {str(e)}")

    def update_All_rented_items(self, single_row_data=None):

        self.backup_database()
        if not single_row_data:
            rented_items = get_table_data(self.rented_items_table)
        else:
            rented_items = [single_row_data]

        final_edited_items = []
        stock_returning_data = {}
        
        # rented_items_previous_data = self.db_manager.get_rent_data(customer_id=self.customer_id, status_list=["Rented", 'Stock Recieved'])
        
        if not rented_items:
            QMessageBox.warning(self, "Validation Error", "No items to update.")
            return False
        
        for index, row in enumerate(rented_items):
            previous_rent_data = self.db_manager.get_single_item(row[0], tables["rent"])

            previous_quantity_rented = int(previous_rent_data[3])
            quantity_rented = int(row[5])
            quantity_returned = int(row[6])

            previous_status = previous_rent_data[6]
            new_status = rented_items[index][9]

            if previous_rent_data[0] is None:
                QMessageBox.warning(self, "Validation Error", f"Item ID {row[0]} not found in database.")
                return False
            
            if not self.is_valid_payment_status(row[9]):
                QMessageBox.warning(self, "Validation Error", f"Enter a valid payment status for item ID {row[0]}\nName: {row[4]}")
                return False
            
            if not self.is_valid_date(row[7]) or ((new_status=='Paid' or new_status=='Stock Recieved') and not self.is_valid_date(row[8])):
                QMessageBox.warning(self, "Validation Error", f"Enter a valid date-time for item ID {row[0]}\nName: {row[4]}")
                return False

            if has_alphabet_or_special_char(row[6]) or int(row[6]) < 0:
                QMessageBox.warning(self, "Validation Error", f"Enter a valid quantity for item ID {row[0]}\nName: {row[4]}")
                return False


            if quantity_returned > quantity_rented:
                QMessageBox.warning(self, "Validation Error", f"Quantity Returned can't be greater than Quantity Rented for item ID {row[0]}\nName: {row[4]}")
                return False
            
            if quantity_rented>previous_quantity_rented:
                QMessageBox.warning(self, "Validation Error", f"If you want to increase the Rent Quantity go to Rent Section and create a new rent record {row[0]}\nName: {row[4]}")
                return False
            
            if quantity_rented ==0:
                QMessageBox.warning(self, "Validation Error", f"Setting Quantity Rented 0 for item ID {row[0]}\nName: {row[4]} will clear this Rent Record.\nIf you want to clear this Rent Record, please go to Clear Rent Button")
                return False

            stock_id=int(row[3])

            if new_status =='Paid':
                if previous_status == "Rented":
                    self.safe_adding_stock_returning_data(stock_returning_data, stock_id, quantity_rented)
                row[10] = 0
            
            elif new_status == 'Rented':

                
                if previous_status == 'Stock Recieved':
                    row[8] = None    
                    new_stock_quantity = ((-1*previous_quantity_rented)+(previous_quantity_rented-quantity_rented))

                else:
                    new_stock_quantity = previous_quantity_rented - quantity_rented

                self.safe_adding_stock_returning_data(stock_returning_data, stock_id, new_stock_quantity)
                
                
            

            elif new_status == 'Stock Recieved':
                if previous_status == 'Rented':
                    QMessageBox.information(self, "Validation Error", f"If you want to change the status from Rented to Stock Recieved, Please Return the Items First. Then you change the status to Rented.\nName: {row[4]}")
                    return False
            
                new_stock_quantity = 0
                if quantity_rented != quantity_returned:
                    new_rent_quantity = -1 * (quantity_rented - quantity_returned)           
                    self.safe_adding_stock_returning_data(stock_returning_data, stock_id, new_rent_quantity)
                    row[5] = quantity_returned
                    self.db_manager.insert_data(table_name=tables['rent'],columns=RENT_DB_COLUMNS,values=[row[1],stock_id,quantity_rented-quantity_returned,row[7],'Rented',0])
            


            # Remove Customer Name, Stock Name, Quantity Returned
            row = row[:11]

            row.pop(2)
            row.pop(3)
            row.pop(4)
            row = tuple(row)
            final_edited_items.append(row)

        for row in final_edited_items:
            response = self.db_manager.update_rent(*row)
            if check_warning(self, response):
                return
        
        self.update_stock_quantities(stock_returning_data)
        QMessageBox.information(self, "Success", "Items updated successfully.")
        self.return_to_rent_management()


    def return_to_main_menu(self):
        self.main_stacked_widget.setCurrentWidget(self.main_menu_screen)
