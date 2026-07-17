from PyQt5.QtWidgets import (
    QWidget,
    QMessageBox,QDialog,QVBoxLayout,QCalendarWidget,QLabel,QPushButton
)
from DatabaseManagement import DatabaseManager
from RentManagement_ui import RentManagement
from Custom_UI import *

class CalendarDialog(QDialog):
    def __init__(self, parent=None, title="Select Date"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        if title:
            label = QLabel(title)
            layout.addWidget(label)
        
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        layout.addWidget(self.calendar)
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)
        
        self.setLayout(layout)
    
    def get_selected_date(self):
        return self.calendar.selectedDate().toString("yyyy-MM-dd")

class ReportManagement(QWidget):
    def __init__(self, main_stacked_widget, main_menu_screen):
        super().__init__()
        self.main_stacked_widget = main_stacked_widget
        self.main_menu_screen = main_menu_screen
        self.db_manager = DatabaseManager()
        self.setup_report_management_screen()
        self.rent_management=RentManagement(self.main_stacked_widget,self.main_menu_screen)
        # self.is_table_data_of_payments=False
        self.table_for_which_screen="Active Rents"
        self.filter_dates={
            "specific_date":None,
            "date_range":[],
            "multiple_dates":[]
        }
    
    
    def setup_report_management_screen(self):
        rent_buttons = [
            ("Show Active Rents", self.show_active_rents_screen),
            ("Show Paid Rents", self.show_paid_rent_screen),
            ("Show Payment Details", self.show_payment_details),
            ("Sales History", self.show_selling_history_screen),
                    ("Back to Main Menu", self.return_to_main_menu)
        ]

        self.report_management_screen = setup_options_management_screen(
            self.main_stacked_widget, "Reports Management", rent_buttons
        )[1]


    def show_selling_history_screen(self):
        self.make_filter_dates_none()
        self.table_for_which_screen="Sales History"
        selling_history_data = self.db_manager.get_all_items(table_name=tables['sold_items'])
        if len(selling_history_data)==0:
            QMessageBox.warning(self, "Error", "No Selling History Available")
            return
        
        self.table_object= TableScreen(
            self.main_stacked_widget,
            title="Selling History",
            headers=['ID', 'Item Name', 'Quantity Sold', 'Total Cost Amount', 'Total Sale Amount','Discount Amount', 'Profit', 'Selling Date'],
            table_data=selling_history_data,
            search_columns={"Search by Name": 1},
            back_action=self.return_to_report_management,
            sortable_columns=[1,2,3,4,5,6],
            hidden_columns=[0],
            full_data_columns=[6],
            filter_options=[
                ("Filter by Specific Date", self.filter_by_specific_date),
                ("Filter by Date Range", self.filter_by_date_range),
                ("Filter by Multiple Dates", self.filter_by_multiple_dates)
            ],
            button_actions=[('Show Sales Summary',self.calculate_sold_items_sales_and_profit),('Reload Table',self.show_selling_history_screen)],
            search_function=self.filter_table_data,
            db_columns=['stock_name']
        )
        self.reports_table_data=self.table_object.table_widget



    def calculate_all_payments_from_payments_table(self):
        self.calculate_all_payments(3,show_bill=True)
    def calculate_all_discounts_from_discount_table(self):
        self.calculate_all_payments(4,show_bill=True)

    def calculate_all_payments(self,index_number,show_bill=False):
        payment_data=self.get_data_for_calculation()
        if not payment_data:
            return
        total_payment = sum([float(row[index_number]) for row in payment_data])
        if show_bill:
            QMessageBox.information(self, "Total Payments", f"Total Payments: Rs: {total_payment:.2f}")
        return total_payment
    

    def get_data_for_calculation(self):
        results_data=self.table_object.table_data
        # if len(results_data)<=PAGINATION_THRESHOLD:
        #     results_data= get_table_data(self.reports_table_data)
        if not results_data or len(results_data)==0 or isinstance(results_data,tuple):
            QMessageBox.warning(self, "Error", "No data found.")
            return None
        return results_data
    
    def calculate_sold_items_sales_and_profit(self):
        sold_items_data=self.get_data_for_calculation()
        if not sold_items_data:
            return
        date_based_payments=self.calculate_date_based_payments(sold_items_data=sold_items_data)
        if not date_based_payments:
            return
        profit_with_loan_amount=date_based_payments['total_profit']
        sales_with_loan_amount=date_based_payments['total_sales']
        total_cost_amount=date_based_payments['total_cost']
        total_discount_amount=date_based_payments['total_discount']
        total_quantity_sold=date_based_payments['total_quantity']
        unpaid_customers=self.db_manager.get_unpaid_customers()
        if unpaid_customers:
            for customer in unpaid_customers:
                formatted_date=customer[5].split(' ')[0]
                if formatted_date in date_based_payments['dates']:
                    date_based_payments['total_sales']-=float(customer[4])
        profit_without_loan_amount=date_based_payments['total_sales']-date_based_payments['total_cost']
        sales_without_loan_amount=date_based_payments['total_sales']
        QMessageBox.information(self, "Sales and Profits", f"Total Cost: Rs: {total_cost_amount:.2f}\nTotal Sales: Rs: {sales_with_loan_amount:.2f}\nTotal Profit: Rs: {profit_with_loan_amount:.2f}\nTotal Discount: Rs: {total_discount_amount:.2f}\nTotal Quantity Sold: {total_quantity_sold}\nTotal Sales (Excluding Loan Amount): Rs: {sales_without_loan_amount:.2f}\nTotal Profit (Excluding Loan Amount): Rs: {profit_without_loan_amount:.2f}")


    def calculate_date_based_payments(self,sold_items_data):
        progress=create_progress_dialog(self,title='Calculating Profits',data_length=len(sold_items_data))
        date_based_payments={
            'dates':[],
            'total_sales':0,
            'total_cost':0,
            'total_profit':0,
            'total_discount':0,
            'total_quantity':0
        }
        for index,row in enumerate(sold_items_data):
            progress.setValue(index)
            if progress.wasCanceled():
                return False
            formatted_date=row[7].split(' ')[0]
            if formatted_date not in date_based_payments:
                date_based_payments['dates'].append(formatted_date)
            date_based_payments['total_quantity']+=float(row[2])
            date_based_payments['total_cost']+=float(row[3])
            date_based_payments['total_sales']+=float(row[4])
            date_based_payments['total_discount']+=float(row[5])
            date_based_payments['total_profit']+=float(row[6])
        progress.setValue(len(sold_items_data))
        return date_based_payments
    
    
    
    def return_to_main_menu(self):
        self.main_stacked_widget.setCurrentWidget(self.main_menu_screen)

    def show_payment_details(self):
        self.make_filter_dates_none()
        self.table_for_which_screen="Payment Details"
        # Fetch data using a JOIN query
        payment_data = self.db_manager.get_all_payments()
        
        if len(payment_data)==0:
            QMessageBox.warning(self, "Error", "No payments data found.")
            return
        
        # Display the data in the table
        self.table_object= TableScreen(
            self.main_stacked_widget,
            title="Payment Details",
            headers=['Payment ID', "Customer ID", "Customer Name", "Amount Paid","Discount", 'Payment Date-Time'],
            table_data=payment_data,
            button_actions=[("Calculate All Payments", self.calculate_all_payments_from_payments_table),("Calculate Discounts",self.calculate_all_discounts_from_discount_table),('Reload Table',self.show_payment_details)],
            back_action=self.return_to_report_management,
            search_columns={
                "Search by Customer Name": 2
            },
            filter_options=[
                ("Filter by Specific Date", self.filter_by_specific_date),
                ("Filter by Date Range", self.filter_by_date_range),
                ("Filter by Multiple Dates", self.filter_by_multiple_dates)
            ],
            full_data_columns=[2,4],
            sortable_columns=[0,1,2,3,4],
            hidden_columns=[0,1],
            search_function=self.filter_table_data,
            db_columns=['name']
        )
        self.reports_table_data=self.table_object.table_widget


    def show_active_rents_screen(self):
        self.table_for_which_screen="Active Rents"
        rent_data=self.db_manager.get_rent_data(status_list=['Stock Recieved','Rented'])
        if not rent_data or len(rent_data)==0:
            QMessageBox.warning(self, "Error", "No active rents data found.")
            return
        
        button_actions=[
                ('Show Upcoming Payments', self.show_upcoming_payments),
                ('Refresh Rents', self.calculate_rents),
                ('Reload Table', self.show_active_rents_screen)
            ]
        self.show_rent_items_screen(rent_data=rent_data,button_actions=button_actions)


    def make_filter_dates_none(self):
        self.filter_dates["specific_date"]=None
        self.filter_dates["date_range"]=[]
        self.filter_dates["multiple_dates"]=[]

    def show_paid_rent_screen(self):
        self.table_for_which_screen="Paid Rents"
        rent_data=self.db_manager.get_rent_data(status_list=['Paid'])
        if not rent_data or len(rent_data)==0:
            QMessageBox.warning(self, "Error", "No paid rents data found.")
            return
        button_actions=[
                ('Reload Table', self.show_paid_rent_screen)
            ]
        self.show_rent_items_screen(rent_data=rent_data,button_actions=button_actions)

    def show_rent_items_screen(self,rent_data,button_actions=None):
        self.make_filter_dates_none()

        self.table_object = TableScreen(
            self.main_stacked_widget,
            title="Rented Items",
            headers=['Rent ID', "Customer ID", "Customer Name", "Stock ID", "Stock Name", "Quantity Rented","Quantity Returned", 'Rent Date-Time', "Return Date", 'Status', 'Amount Due'],
            table_data=rent_data,
            editable_columns=[],
            button_actions=button_actions,
            back_action=self.return_to_report_management,

            search_columns={
                "Search by Customer Name": 2,
                "Search by Stock Name": 4
            },

            filter_options=[
                ("Filter by Specific Date", self.filter_by_specific_date),
                ("Filter by Date Range", self.filter_by_date_range),
                ("Filter by Multiple Dates", self.filter_by_multiple_dates)
            ],
            full_data_columns=[2,4,6,7,8],
            sortable_columns=[0,1,2,3,4,5,6,7,8,9],
            hidden_columns=[0,1,3],
            search_function=self.filter_table_data,
            db_columns=['name','st_name']
        )
        self.reports_table_data=self.table_object.table_widget

    def show_upcoming_payments(self):
        """
        Show upcoming payments for customers. The upcoming payments are calculated by subtracting the amount paid by the customer from the total amount due.
        """
        rent_data=self.get_data_for_calculation()
        if not rent_data:
            return
        progress=create_progress_dialog(self,title='Calculating Upcoming Payments',data_length=len(rent_data))
        customers_upcoming_payments = {}
        customer_id=0
        for index,row in enumerate(rent_data):
            progress.setValue(index)
            if progress.wasCanceled():
                return False
            customer_id=int(row[1])
            if customer_id not in customers_upcoming_payments:
                customers_upcoming_payments[customer_id] = float(row[10])
            else:
                customers_upcoming_payments[customer_id] += float(row[10])
        all_customers = self.db_manager.get_all_items(tables["customers"])

        total_upcoming_payments = 0
        for customer in all_customers:
            if customer[0] in customers_upcoming_payments:
                customers_upcoming_payments[customer[0]]-=float(customer[7])
                total_upcoming_payments+=customers_upcoming_payments[customer[0]]
        progress.setValue(len(rent_data))
        QMessageBox.information(
            self, "Upcoming Payments",
            f"Total Upcoming Payments: Rs: {total_upcoming_payments:.2f}"
        )

    def calculate_rents(self):
        rent_data=self.db_manager.get_rent_data(status_list=['Stock Recieved','Rented'])
        if isinstance(rent_data, tuple):
            QMessageBox.warning(self, "Error", rent_data[0])
            return

        grouped_items = self.rent_management.calculate_bill(rent_data,calling_from_rent_management=False)
        if not grouped_items:
            return

        QMessageBox.information(self, "Success", "Rents calculated and updated successfully.")
        self.show_active_rents_screen()


    def filter_by_specific_date(self):
        self.make_filter_dates_none()
        calendar_dialog = CalendarDialog(self, "Select Specific Date")
        if calendar_dialog.exec_() == QDialog.Accepted:
            date = calendar_dialog.get_selected_date()
            self.filter_dates["specific_date"]=date
        self.table_object.perform_database_search(calling_from_outside=True)
        

    def filter_by_date_range(self):
        self.make_filter_dates_none()
        start_calendar = CalendarDialog(self, "Select Start Date")
        if start_calendar.exec_() == QDialog.Accepted:
            start_date = start_calendar.get_selected_date()
            
            
            end_calendar = CalendarDialog(self, "Select End Date")
            if end_calendar.exec_() == QDialog.Accepted:
                end_date = end_calendar.get_selected_date()
                self.filter_dates["date_range"]=[start_date,end_date]
        self.table_object.perform_database_search(calling_from_outside=True)

    def filter_by_multiple_dates(self):
        dates = []
        self.make_filter_dates_none()
        while True:
            calendar_dialog = CalendarDialog(self, f"Select Date {len(dates) + 1}")
            if calendar_dialog.exec_() == QDialog.Accepted:
                self.filter_dates['multiple_dates'].append(calendar_dialog.get_selected_date())

                # Ask if user wants to add another date
                reply = QMessageBox.question(
                    self, 
                    'Add More Dates',
                    'Do you want to select another date?',
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                if reply == QMessageBox.No:
                    break
            else:
                break
        self.table_object.perform_database_search(calling_from_outside=True)
    

    def filter_table_data(self,search_criteria):
        new_search_criteria={}
        for key,value in search_criteria.items():
            if key=="name":
                new_search_criteria["Customer"]={key:value}
            elif key=="st_name":
                new_search_criteria["Stock"]={key:value}
            elif key=='stock_name':
                new_search_criteria["Sold_Items"]={key:value}
    
        if self.table_for_which_screen=="Active Rents":
            results_data=self.db_manager.get_rent_data(status_list=['Stock Recieved','Rented'],table_filters=new_search_criteria,filter_dates=self.filter_dates)
        elif self.table_for_which_screen=="Paid Rents":
            results_data=self.db_manager.get_rent_data(status_list=['Paid'],table_filters=new_search_criteria,filter_dates=self.filter_dates)

        elif self.table_for_which_screen=="Payment Details":
            results_data=self.db_manager.get_all_payments(table_filters=new_search_criteria,filter_dates=self.filter_dates)
            

        elif self.table_for_which_screen=="Sales History":
            results_data=self.db_manager.get_all_sales(filter_dates=self.filter_dates,table_filters=new_search_criteria)
        return results_data

                    

    def return_to_report_management(self):
        self.main_stacked_widget.setCurrentWidget(self.report_management_screen)
