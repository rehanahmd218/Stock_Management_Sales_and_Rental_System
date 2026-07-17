from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout,
    QMessageBox, QSpinBox, QLabel,QDialog,QDialogButtonBox,QScrollArea
)
from PyQt5.QtCore import QDateTime,QEvent
from PyQt5.QtGui import QFont
from DatabaseManagement import DatabaseManager
from Custom_UI import *

class SaleManagement(QWidget):
    def __init__(self, main_stacked_widget, main_menu_screen):
        super().__init__()
        self.main_stacked_widget = main_stacked_widget
        self.main_menu_screen = main_menu_screen
        self.db_manager = DatabaseManager()
        self.reamining_amount_for_customer=0.0

    def setup_sale_management_screen(self):
        selling_buttons = [
            ("Add Stock", self.show_add_stock_screen),
            ("Manage Stock", self.show_manage_stock_screen),
            ("Sell Items", self.show_stock_item_screen_for_sell_items),
            ("Unpaid Customers", self.show_unpaid_customers),
            ("Back to Main Menu", self.return_to_main_menu)
        ]
        self.sale_management_screen = setup_options_management_screen(
            self.main_stacked_widget, "Sales Management", selling_buttons
        )[1]

    def show_unpaid_customers(self):
        unpaid_customers=self.db_manager.get_unpaid_customers()
        if len(unpaid_customers)==0:
            QMessageBox.warning(self, "Error", "No Unpaid Customers")
            self.return_to_sale_management()
            return
        unpaid_customers=get_all_items_with_adding_leading_zero(unpaid_customers)
        self.unpaid_customers_table=TableScreen(
            self.main_stacked_widget,
            title="Unpaid Customers",
            headers=['Customer ID', 'Name', "Mobile No","ID Card",'Amount Remaining', 'Loan Date', 'Amount Paid'],
            table_data=unpaid_customers,
            search_columns={"Search by Name": 1,"Search by Mobile No": 2,"Search by ID Card": 3},
            back_action=self.return_to_sale_management,
            sortable_columns=[1,4,5],
            editable_columns=[1,2,3,4,6],
            full_data_columns=[5],
            last_col_function={"Update":self.update_customer,"Clear Amount":self.clear_amount},
            show_pagination=True,
            db_columns=['customer_name','customer_mobile','id_card'],
            table_name=tables["unpaid_customers"],
            ending_zero=True,
        ).table_widget
    
    def update_customer(self,row):
        self.update_unpaid_customer(row,full_paid=False)

    def clear_amount(self,row):
        self.update_unpaid_customer(row,full_paid=True)

    def update_unpaid_customer(self,row,full_paid):
        single_customer_data=get_single_row_data(self.unpaid_customers_table,row)
        amount_remaining=float(single_customer_data[4])-float(single_customer_data[6])
        if amount_remaining<0:
            QMessageBox.warning(self, "Error", "Amount Paid is more than Amount Remaining")
            return
        
        if full_paid or amount_remaining==0:
            if not check_warning(self,self.db_manager.update_multiple_columns(tables['unpaid_customers'],item_id=single_customer_data[0],columns=['amount_due','loan_date'],values=[0,None],matching_column='id')):
                QMessageBox.information(self, "Success", "Amount Cleared Successfully")
                self.show_unpaid_customers()
                return
        else:
            if not check_warning(self,self.db_manager.update_multiple_columns(tables['unpaid_customers'],item_id=single_customer_data[0],columns=['amount_due'],values=[amount_remaining],matching_column='id')):
                QMessageBox.information(self, "Success", "Amount Updated Successfully")
                self.show_unpaid_customers()
                return
            return
    

    def show_stock_item_screen_for_sell_items(self):
        stock_data = self.db_manager.get_all_items(table_name=tables['selling_stock'])
        if len(stock_data) == 0:
            QMessageBox.warning(self, "Error", "No Stock Available to Sell")
            return
        stock_data=[stock+('0',) for stock in stock_data]
      
        
        self.stock_selector = StockSelector(available_quantity_index=2)
        # Create table screen with additional button
        self.selling_stock_table = TableScreen(
            self.main_stacked_widget,
            title="Select Stock Items to Sell",
            headers=['Stock ID', 'Name', 'Available Quantity', 'Cost Price', 'Sale Price', "Price Date", "Quantity Sold"],
            table_data=stock_data,
            search_columns={"Search by Name": 1},
            button_actions=[
                ("View Selected Items", self.stock_selector.show_selected_items),
                ("Sell Items", self.confirm_sell_item)
            ],
            back_action=self.return_to_sale_management,
            # hidden_columns=[0,3],
            sortable_columns=[1,2,4,5],
            editable_columns=[6],
            full_data_columns=[5],
            show_pagination=True,
            db_columns=['item_name'],
            table_name=tables["selling_stock"],
            ending_zero=True,
            last_col_function={"Add":self.stock_selector.add_item},
            
        ).table_widget
        self.stock_selector.table_widget=self.selling_stock_table
    



    def confirm_sell_item(self):
        final_stock_data=self.stock_selector.get_selected_items()
        if len(final_stock_data)==0:
            QMessageBox.warning(self, "Validation Error", "No items selected to Sell")
            return
        selling_date = QDateTime.currentDateTime().toString(DATABASE_DATETIME_FORMAT)
        all_items_data={}
        all_items_data["items"] = []
        total_amount=0

        for row in final_stock_data:
            single_row_data={
                "id":row[0],
                "quantity":row[6],
                "selling_date":selling_date,
                "total_cost_amount":int(row[3])*int(row[6]),
                "total_sale_amount":int(row[4])*int(row[6]),
                "item_name":row[1],
                "single_item_price":row[4]
            }
            all_items_data["items"].append(single_row_data)
            total_amount+=single_row_data["total_sale_amount"]
        all_items_data["total_amount"]=total_amount
        bill_dialog=self.show_bill_summary(all_items_data)
        if self.show_payment_dialog(all_items_data,bill_dialog):
            self.show_stock_item_screen_for_sell_items()
      



            
    def show_bill_summary(self, all_items_data):
        screen_width, screen_height = get_screen_size()

        # Calculate dialog dimensions (70% of screen width, 80% of screen height)
        dialog_width = int(screen_width * 0.7)
        dialog_height = int(screen_height * 0.5)

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
        header_label.setFont(QFont("Arial", int(15*SCRN_RATIO), QFont.Bold))
        scroll_layout.addWidget(header_label)

        # Create table for items
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Item Name", "Price (Rs)", "Quantity", "Total (Rs)"])
        table.setRowCount(len(all_items_data["items"]))
        
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
        for row, item in enumerate(all_items_data["items"]):
            name_item = QTableWidgetItem(item['item_name'])
            name_item.setFont(QFont("Arial", int(18 * SCRN_RATIO)))
            price_item = QTableWidgetItem(f"{float(item['single_item_price']):.2f}")
            price_item.setFont(QFont("Arial", int(18 * SCRN_RATIO)))
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            qty_item = QTableWidgetItem(str(item['quantity']))
            qty_item.setFont(QFont("Arial", int(18 * SCRN_RATIO)))
            qty_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            total_item = QTableWidgetItem(f"{item['total_sale_amount']:.2f}")
            total_item.setFont(QFont("Arial", int(18 * SCRN_RATIO)))
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            table.setItem(row, 0, name_item)
            table.setItem(row, 1, price_item)
            table.setItem(row, 2, qty_item)
            table.setItem(row, 3, total_item)
            table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Set fixed table height based on content
        table_height = (table.horizontalHeader().height() + 
                    table.rowHeight(0) * table.rowCount())
        table.setFixedHeight(table_height)
        
        scroll_layout.addWidget(table)
        
        # Add grand total
        grand_total = create_bold_label(f"Grand Total: Rs {all_items_data['total_amount']:.2f}")
        grand_total.setAlignment(Qt.AlignRight)
        scroll_layout.addWidget(grand_total)
        
        # Set the scroll content
        scroll_area.setWidget(content_widget)
        
        # Add OK button
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        main_layout.addWidget(button_box)
        button_box.accepted.connect(bill_dialog.accept)
        
        # Show dialog
        bill_dialog.show()
        return bill_dialog


    def show_payment_dialog(self, all_items_data, bill_dialog):
        payment_dialog = QDialog(self)
        payment_dialog.setWindowTitle("Pay Amount")
        payment_dialog.setFont(QFont("Arial", int(10*SCRN_RATIO)))
        payment_dialog.resize(int(400*SCRN_RATIO), int(200*SCRN_RATIO))
        
        # Position on right if showing alongside bill
        screen_width, screen_height = get_screen_size()
        payment_dialog.move(screen_width - payment_dialog.width(), 
                        (screen_height - payment_dialog.height()) // 2)
        
        payment_layout = QVBoxLayout(payment_dialog)
        
        # Setup paid amount input
        paid_label = create_bold_label("Amount Paid:")
        paid_spin = QSpinBox()
        paid_spin.setRange(-100000, 100000)
        total_amount = all_items_data["total_amount"]
        paid_spin.setValue(int(total_amount))
        paid_spin.setFont(QFont("Arial", int(18*SCRN_RATIO)))
        payment_layout.addWidget(paid_label)
        payment_layout.addWidget(paid_spin)
        
        # Setup discount input
        discount_label = create_bold_label("Discount:")
        discount_spin = QSpinBox()
        discount_spin.setRange(0, 100000)
        discount_spin.setFont(QFont("Arial", int(18*SCRN_RATIO)))
        payment_layout.addWidget(discount_label)
        payment_layout.addWidget(discount_spin)
        
        payment_button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        payment_layout.addWidget(payment_button_box)
        
        def distribute_discount(items, total_discount):
            if not items or total_discount == 0:
                return [{**item, 'discount': 0, 'final_sale_amount': float(item['total_sale_amount'])} 
                    for item in items]
            
            total_value = sum(float(item['total_sale_amount']) for item in items)
            distributed_items = []
            remaining_discount = total_discount
            
            for item in items:
                item_value = float(item['total_sale_amount'])
                item_discount = round((item_value / total_value) * total_discount, 2)
                remaining_discount -= item_discount
                
                distributed_items.append({
                    **item,
                    'discount': item_discount,
                    'final_sale_amount': item_value - item_discount
                })
            
            # Handle remaining discount due to rounding
            if remaining_discount != 0:
                max_value_item = max(distributed_items, key=lambda x: float(x['total_sale_amount']))
                max_value_item['discount'] += remaining_discount
                max_value_item['final_sale_amount'] -= remaining_discount
            
            return distributed_items
        
        def show_profit_summary(items_with_discount):
            profit_dialog = QDialog(payment_dialog)
            profit_dialog.setWindowTitle("Profit Summary")
            profit_dialog.setFont(QFont("Arial", int(18*SCRN_RATIO)))
            profit_dialog.resize(int(400*SCRN_RATIO), int(300*SCRN_RATIO))
            
            profit_layout = QVBoxLayout(profit_dialog)
            total_profit = 0
            
            for item in items_with_discount:
                profit = item['final_sale_amount'] - float(item['total_cost_amount'])
                profit_label = QLabel(f"{item['item_name']}: Rs {profit:.2f}")
                profit_label = create_bold_label(text=f"{item['item_name']}: Rs {profit:.2f}",font_size=15)
                profit_layout.addWidget(profit_label)
                total_profit += profit
            
            total_profit_label = create_bold_label(f"Total Profit: Rs {total_profit:.2f}",font_size=15)
            total_profit_label.setFont(QFont("Arial", int(15*SCRN_RATIO), QFont.Bold))
            profit_layout.addWidget(total_profit_label)
            
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            profit_layout.addWidget(button_box)
            
            button_box.accepted.connect(profit_dialog.accept)
            button_box.rejected.connect(profit_dialog.reject)
            
            return profit_dialog.exec_() == QDialog.Accepted
        
        def process_sale(items_with_discount):
            for item in items_with_discount:
                # Update stock quantity
                if check_warning(self, self.db_manager.addition_subtraction_on_cells(
                    table_name=tables['selling_stock'],
                    column_name='available_quantity',
                    item_id=item['id'],
                    value=-int(item['quantity'])
                )):
                    return False
                
                # Calculate final values
                final_sale_amount = item['final_sale_amount']
                profit = final_sale_amount - float(item['total_cost_amount'])
                
                # Record sale
                if check_warning(self, self.db_manager.insert_data(
                    table_name=tables['sold_items'],
                    columns=SOLD_ITEMS_DB_COLUMNS,
                    values=[
                        item["item_name"],
                        item['quantity'],
                        item['total_cost_amount'],
                        final_sale_amount,
                        item['discount'],
                        profit,
                        item['selling_date']
                    ]
                )):
                    return False
            
            return True
        
        def handle_payment_finalization():
            paid_amount = paid_spin.value()
            discount_amount = discount_spin.value()
            remaining_amount = total_amount - paid_amount - discount_amount
            
            if remaining_amount < 0:
                QMessageBox.warning(payment_dialog, "Payment Error", "Paid amount exceeds total amount.")
                return
            
            # Calculate discounts and show profit summary
            items_with_discount = distribute_discount(all_items_data["items"], discount_amount)
            if not show_profit_summary(items_with_discount):
                return
            
            # Process the sale
            if not process_sale(items_with_discount):
                return
            
            # Handle remaining amount if any
            if remaining_amount > 0:
                self.reamining_amount_for_customer = remaining_amount
                self.show_customers_screen_for_loan_selection()
                handle_payment_cancellation()
                return
            
            QMessageBox.information(payment_dialog, "Success", "Items Sold successfully.")
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
        return payment_dialog.exec_() == QDialog.Accepted
    
    def show_customers_screen_for_loan_selection(self):
        customers_data=self.db_manager.get_all_items(table_name=tables['unpaid_customers'])
        if len(customers_data)==0:
            self.show_new_unpaid_customer_input()
            return
        self.customers_table = TableScreen(
            self.main_stacked_widget,
            title="Select Customers for Loan",
            headers=['Customer ID', 'Name', "Mobile No","ID Card",'Amount Remaining', 'Loan Date'],
            table_data=customers_data,
            search_columns={"Search by Name": 1,"Search by Mobile No": 2,"Search by ID Card": 3},
            button_actions=[("Add a New Person",self.show_new_unpaid_customer_input)],
            hidden_columns=[0],
            sortable_columns=[4,5],
            full_data_columns=[5],
            last_col_function={"Confirm":self.confirm_loan},
            show_pagination=True,
            db_columns=['customer_name','customer_mobile','id_card'],
            table_name=tables["unpaid_customers"],
        ).table_widget
    
    def show_new_unpaid_customer_input(self):
        setup_input_screen(
            self.main_stacked_widget,
            title="Add New Customer",
            form_fields=[
                ("Name:", "name_input"),
                ("Mobile No:", "mobile_no_input"),
                ("ID Card:", "id_card_input"),
                ("Amount Due:", "amount_due_input")
            ],
            save_stock_method=self.add_new_unpaid_customer,
            back_action=self.return_to_sale_management,
            calling_object=self
        )
        self.amount_due_input.setText(str(self.reamining_amount_for_customer))
    
    def add_new_unpaid_customer(self):
        name = self.name_input.text()
        mobile_no = self.mobile_no_input.text()
        id_card = self.id_card_input.text()
        amount_due = self.amount_due_input.text()
        current_date_time=QDateTime.currentDateTime().toString(DATABASE_DATETIME_FORMAT)
        if not check_warning(self,self.db_manager.insert_data(table_name=tables['unpaid_customers'],columns=UNPAID_CUSTOMERS_DB_COLUMNS,values=[name,mobile_no,id_card,amount_due,current_date_time])):
            QMessageBox.information(self, "Success", "Customer Added Successfully and Loaned Amount Updated")
            self.name_input.clear()
            self.mobile_no_input.clear()
            self.id_card_input.clear()
            self.amount_due_input.clear()

        self.return_to_sale_management()
        return
    
    def confirm_loan(self,row):
        single_customer_data=get_single_row_data(self.customers_table,row)
        current_datetime=QDateTime.currentDateTime().toString(DATABASE_DATETIME_FORMAT)
        if float(single_customer_data[4])==0 or single_customer_data[5]=="None" or single_customer_data[5].strip()=="":
            self.db_manager.update_multiple_columns(tables['unpaid_customers'],item_id=single_customer_data[0],columns=['amount_due',"loan_date"],values=[float(self.reamining_amount_for_customer),current_datetime],matching_column='id')
        else:
            check_warning(self,self.db_manager.update_multiple_columns(tables['unpaid_customers'],item_id=single_customer_data[0],columns=['amount_due'],values=[float(single_customer_data[4])+self.reamining_amount_for_customer],matching_column='id'))

        QMessageBox.information(self, "Success", "Loan Amount Updated Successfully")
        self.return_to_sale_management()
        return


    def show_add_stock_screen(self):
        # Add Stock Screen
        # Input Fields
        form_fields = [
            ("Item Name:", "name_input"),
            ("Available Quantity:", "avail_quantity_input"),
            ("Buying Price:", "cost_price_input"),
            ("Selling Price:", "sale_price_input")
        ]
        self.add_stock_screen,self.save_stock_button = setup_input_screen(
            self.main_stacked_widget, title="Add Stock", form_fields=form_fields,
             save_stock_method=self.add_stock,
             back_action=self.return_to_sale_management,
             calling_object=self,
        )


    def eventFilter(self, obj, event):
        if not hasattr(self, 'add_stock_screen'):
            return super().eventFilter(obj, event)  # Return without handling if not initialized
        if obj == self.add_stock_screen and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Backspace:
                self.return_to_sale_management()
            elif event.key() in [Qt.Key_Enter, Qt.Key_Return]:
                focus_widget = self.add_stock_screen.focusWidget()
                if focus_widget == self.save_stock_button:
                    self.add_stock()
                return True
        return super().eventFilter(obj, event)
    
    def add_stock(self):
        name = self.name_input.text()
        avail_quantity = self.avail_quantity_input.text()
        cost_price=self.cost_price_input.text()
        sale_price = self.sale_price_input.text()
        current_date_time=QDateTime.currentDateTime().toString(DATABASE_DATETIME_FORMAT)
        if not self.check_stock_inputs(name, avail_quantity, cost_price,sale_price):
            return
        if not check_warning(self,self.db_manager.insert_data(table_name=tables['selling_stock'],columns=SELLING_STOCK_DB_COLUMNS,values=[name,avail_quantity,cost_price,sale_price,current_date_time])):
            QMessageBox.information(self, "Success", "Stock Added Successfully")
        
        self.name_input.clear()
        self.avail_quantity_input.clear()
        self.cost_price_input.clear()
        self.sale_price_input.clear()

        
    def check_stock_inputs(self, name, avail_quantity, cost_price,sale_price):
        if not all([name, avail_quantity, cost_price, sale_price]):
            QMessageBox.warning(self, "Validation Error", "Please fill in all fields")
            return False
        if has_alphabet_or_special_char(avail_quantity) or has_alphabet_or_special_char(cost_price) or has_alphabet_or_special_char(sale_price):
            QMessageBox.warning(self, "Validation Error", "Please enter valid numbers")
            return False
        return True
    
    def show_manage_stock_screen(self):
        all_data=self.db_manager.get_all_items(table_name=tables['selling_stock'])
        if len(all_data)==0:
            QMessageBox.warning(self, "Error", "No Selling Stock Available")
            self.return_to_sale_management()
            return
      
        self.selling_stock_table=TableScreen(
            self.main_stacked_widget,
            title="Manage Stock",
            headers=['Stock ID', 'Name', 'Available Quantity',"Cost Price", 'Sale Price','Price Updated Date'],
            table_data=all_data,
            search_columns={
                "Search by Name": 1
            },
            button_actions=[("Update All Stock", self.update_all_stock), ("Delete All Stock", self.delete_all_stock)],
            back_action=self.return_to_sale_management,
            editable_columns=[1,2,3,4],
            sortable_columns=[1,2,3,4,5],
            full_data_columns=[5],
            last_col_function={"Update": self.update_singe_stock, "Delete": self.delete_single_stock},
            hidden_columns=[0],
            show_pagination=True,
            db_columns=['item_name'],
            table_name=tables["selling_stock"],
        ).table_widget

    def check_stock_price_updation(self,row):
        previous_price = float(self.db_manager.get_single_item(table_name=tables['selling_stock'], matching_column='id', item_id=row[0])[4])
        new_price = float(row[4])
        row=tuple(row)
        if previous_price != new_price:
            current_date_time = QDateTime.currentDateTime().toString(DATABASE_DATETIME_FORMAT)
            return row[:5] + (current_date_time,)
        else:
            return row

    def update_all_stock(self):
        table_data = get_table_data(self.selling_stock_table)
        if type(table_data) == tuple:
            QMessageBox.warning(self, "Error", "No Data to Update")
            return
        
        for i, row in enumerate(table_data):
            if not self.check_stock_inputs(row[1], row[2], row[3], row[4]):
                return
            
            table_data[i] = self.check_stock_price_updation(row)
        
        if not check_warning(self, self.db_manager.update_multiple_columns_from_list( tables['selling_stock'], ['item_name', 'available_quantity', 'buying_price', 'selling_price', 'price_updated_date'],table_data, 'id')):
            QMessageBox.information(self, "Success", "Stock Updated Successfully")
            self.show_manage_stock_screen()
        
        
            
        
        
    def delete_all_stock(self):
        if not self.deletion_confirmation("Are you sure you want to delete all stock?"):
            return
        if not check_warning(self,self.db_manager.delete_all_items(tables['selling_stock'])):
            QMessageBox.information(self, "Success", "All Stock Deleted Successfully")
            self.return_to_sale_management()


    def update_singe_stock(self,row):
        single_stock_data=get_single_row_data(self.selling_stock_table,row)
        if not self.check_stock_inputs(*single_stock_data[1:5]):
            return
        single_stock_data=self.check_stock_price_updation(single_stock_data)
        ## Removing Last two action column none values
        single_stock_data=single_stock_data[0:6]
        if not check_warning(self,self.db_manager.update_multiple_columns(tables['selling_stock'],item_id=single_stock_data[0],columns=['item_name', 'available_quantity', 'buying_price', 'selling_price', 'price_updated_date'],values=single_stock_data[1:],matching_column='id')):
            QMessageBox.information(self, "Success", "Stock Updated Successfully")
            self.show_manage_stock_screen()

    def deletion_confirmation(self,warning_message):
        reply = QMessageBox.question(self, "Deletion Warning", warning_message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        return reply == QMessageBox.Yes
        

    def delete_single_stock(self,row):
        single_stock_data=get_single_row_data(self.selling_stock_table,row)
        if not self.deletion_confirmation("Are you sure you want to delete this stock?"):
            return
        

        if not check_warning(self,self.db_manager.delete_single_item(table_name=tables['selling_stock'],id=single_stock_data[0])):
            QMessageBox.information(self, "Success", "Stock Deleted Successfully")
            self.show_manage_stock_screen()
        
    def return_to_sale_management(self):
        self.main_stacked_widget.setCurrentWidget(self.sale_management_screen)


    def return_to_main_menu(self):
        self.main_stacked_widget.setCurrentWidget(self.main_menu_screen)
        