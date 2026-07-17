import functools
import sqlite3
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtCore import Qt

class DatabaseManager:
    def __init__(self):
        pass

    def open_connection(self):
        self.connection = sqlite3.connect("stock_rental_system.db")
        self.connection.execute('PRAGMA foreign_keys = ON')
        self.cursor = self.connection.cursor()


    def connection_required(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            self.open_connection()
            try:
                result = func(self, *args, **kwargs)
                # Commit changes if function is successful
                self.connection.commit()
                if type(result) == list or type(result) == tuple:
                    return result

                return ("", True)
            except Exception as e:
                # Rollback changes if an exception occurs
                self.connection.rollback()
                return (str(e), False)
            finally:
                self.close_connection()
        return wrapper

    @connection_required
    def create_tables(self):
        queries = [
            """
            CREATE TABLE IF NOT EXISTS Stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            st_name TEXT UNIQUE NOT NULL COLLATE NOCASE,
            total_quantity INTEGER NOT NULL,
            available_quantity INTEGER NOT NULL
        );""",
        """
        CREATE TABLE IF NOT EXISTS Stock_Price(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_id INTEGER NOT NULL,
            price REAL NOT NULL,
            price_date DATETIME NOT NULL,
            FOREIGN KEY (stock_id) REFERENCES Stock (id) ON DELETE CASCADE
        )
""",

        """CREATE TABLE IF NOT EXISTS Customer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact_number TEXT NOT NULL,
            address TEXT NOT NULL,
            id_card_number TEXT UNIQUE NOT NULL,
            referrer_name TEXT,
            total_amount_due REAL DEFAULT 0.0, -- Tracks total amount due
            amount_paid REAL DEFAULT 0.0 -- Tracks total amount paid
        );""",

        """CREATE TABLE IF NOT EXISTS Rent (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            stock_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            rent_date DATETIME NOT NULL,
            return_date DATETIME,
            payment_status TEXT NOT NULL CHECK (payment_status IN ('Paid', 'Stock Recieved', 'Rented')),
            amount_due REAL DEFAULT 0.0 NOT NULL, -- Tracks amount due for the rent
            FOREIGN KEY (customer_id) REFERENCES Customer (id) ON DELETE CASCADE,
            FOREIGN KEY (stock_id) REFERENCES Stock (id) ON DELETE CASCADE
        );""","""
        
        CREATE TABLE IF NOT EXISTS Payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    payment_amount REAL NOT NULL,
    discount REAL NOT NULL,
    payment_date DATETIME NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customer (id) ON DELETE SET NULL
)""",
    """CREATE TABLE IF NOT EXISTS Selling_Stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT UNIQUE NOT NULL COLLATE NOCASE,
        available_quantity INTEGER NOT NULL,
        buying_price REAL NOT NULL,
        selling_price REAL NOT NULL,
        price_updated_date DATETIME NOT NULL
    )""",
        
    """
        CREATE TABLE IF NOT EXISTS Sold_Items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        total_cost_amount REAL NOT NULL,
        total_sale_amount REAL NOT NULL,
        discount_amount REAL NOT NULL,
        profit_amount REAL NOT NULL,
        payment_date DATETIME NOT NULL
    );""",

    """
    CREATE TABLE IF NOT EXISTS Unpaid_Customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        customer_mobile TEXT,
        id_card TEXT,
        amount_due REAL NOT NULL,
        loan_date DATETIME
    );""",
        ]

    
        for query in queries:
            self.cursor.execute(query)
        self.connection.commit()




    @connection_required
    def get_stock_with_latest_price(self, stock_name=None):
        """Get all stock items with their latest price. If stock_name is provided, filter by stock name."""
        conditions = ""
        parameters = []
        if stock_name:
            conditions = " AND " + " AND ".join([f"s.{column} LIKE ?" for column in stock_name.keys()])
            parameters = [value + '%' for value in stock_name.values()]
        query = f"""
        SELECT 
        s.id, 
        s.st_name, 
        s.total_quantity, 
        s.available_quantity, 
        sp.price, 
        sp.price_date
        FROM 
        Stock s
        LEFT JOIN 
        Stock_Price sp ON s.id = sp.stock_id
        WHERE 
        (sp.price_date, sp.price) = (
            SELECT price_date, MAX(price)
            FROM Stock_Price 
            WHERE stock_id = s.id
            GROUP BY price_date
            ORDER BY price_date DESC
            LIMIT 1
        )
        {conditions}
        GROUP BY 
        s.id, s.st_name, s.total_quantity, s.available_quantity, sp.price, sp.price_date
        """
        self.cursor.execute(query, parameters)
        return self.cursor.fetchall()

    @connection_required
    def get_all_stock_prices(self, stock_name=None):
        """Get all stock prices. If stock_name is provided, filter by stock name."""
        conditions = ""
        parameters = []
        if stock_name:
            conditions = " AND " + " AND ".join([f"s.{column} LIKE ?" for column in stock_name.keys()])
            parameters = [value + '%' for value in stock_name.values()]
        query = f"""
        SELECT 
            s.st_name, 
            sp.price, 
            sp.price_date
        FROM 
            Stock s
        JOIN 
            Stock_Price sp ON s.id = sp.stock_id
        {conditions}
        ORDER BY 
            s.st_name, sp.price_date DESC
        """
        self.cursor.execute(query, parameters)
        return self.cursor.fetchall()

    @connection_required
    def get_latest_stock_price(self,stock_id):
        """Get the latest price for a stock item."""
        self.cursor.execute(
            """
            SELECT price
            FROM Stock_Price
            WHERE stock_id = ?
            ORDER BY price_date DESC
            LIMIT 1
            """,
            (stock_id,)
        )
        return self.cursor.fetchone()
    
    @connection_required
    def get_stock_price_on_rent_date(self,stock_id,rent_date):
        """Get the price for a stock item based on the rent date."""
        self.cursor.execute(
            """
            SELECT price
            FROM Stock_Price
            WHERE stock_id = ? AND price_date <= ?
            ORDER BY price_date DESC
            LIMIT 1
            """,
            (stock_id,rent_date)
        )
        return self.cursor.fetchone()


    @connection_required
    def update_all_stock_items(self, updates):
        """Update all stock items with a list of updates. Updates should be a list of tuples."""
        for update in updates:
            stock_id = update[0]
            stock_name = update[1]
            total_quantity = update[2]
            available_quantity = update[3]
            self.cursor.execute(
                """
                UPDATE Stock
                SET total_quantity = ?, available_quantity = ?,st_name=?
                WHERE id = ?
                """,
                (total_quantity, available_quantity,
                  stock_name, stock_id)
            )
        self.connection.commit()




    ###! Some General Methods@connection_required
    @connection_required
    def search_items(self, table, column_param_dict):
        # Create placeholders for each column's condition
        conditions = " AND ".join([f"{column} LIKE ?" for column in column_param_dict.keys()])

        # Generate the SQL query
        query = f"SELECT * FROM {table} WHERE {conditions}"
        
        # Add wildcards to each parameter value
        parameters = [value + '%' for value in column_param_dict.values()]

        # Execute the query
        self.cursor.execute(query, parameters)
        return self.cursor.fetchall()



    @connection_required
    def addition_subtraction_on_cells(self,table_name,item_id,value,column_name):
        """Addition or subtraction on a cell in a table"""
        self.cursor.execute(f"UPDATE {table_name} SET {column_name}={column_name}+? WHERE id=?",(value,item_id))
        self.connection.commit()

    @connection_required
    def get_last_item(self,table_name):
        """Return the last stock item from the database."""
        self.cursor.execute(f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT 1")
        return self.cursor.fetchone()
    
    
    @connection_required
    def delete_single_item(self, id,table_name):
        """Delete a single stock item by its ID."""
        self.cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (id,))
        self.connection.commit()

    @connection_required
    def get_single_item(self, item_id,table_name,matching_column="id"):
        """Return a single stock item by its ID."""
        self.cursor.execute(f"SELECT * FROM {table_name} WHERE {matching_column} = ?", (item_id,))
        return self.cursor.fetchone()


    @connection_required
    def delete_all_items(self, table_name, batch_size=1000):
        # Get total count first
        self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_records = self.cursor.fetchone()[0]
        
        if total_records == 0:
            return
            
        # Create progress dialog
        progress = QProgressDialog("Deleting records...", "Cancel", 0, total_records)
        progress.setWindowTitle("Delete Progress")
        progress.setWindowModality(Qt.ApplicationModal)  # Make it modal for entire application
        progress.setWindowFlags(
            progress.windowFlags() | 
            Qt.WindowStaysOnTopHint |  # Keep window on top
            Qt.CustomizeWindowHint |    # Required for custom window behavior
            Qt.WindowTitleHint         # Show only the title bar
        )
        progress.setMinimumDuration(0)  # Show immediately
        progress.setMinimumWidth(300)
        
        records_deleted = 0
        
        try:
            while records_deleted < total_records and not progress.wasCanceled():
                # Delete next batch
                self.cursor.execute(
                    f"DELETE FROM {table_name} WHERE rowid IN "
                    f"(SELECT rowid FROM {table_name} LIMIT {batch_size})"
                )
                
                # Update counts and commit
                batch_count = self.cursor.rowcount
                records_deleted += batch_count
                self.connection.commit()
                
                # Update progress
                progress.setLabelText(f"Deleted {records_deleted:,} of {total_records:,} records")
                progress.setValue(records_deleted)
                
        except Exception as e:
            progress.close()
            raise e
        
        # Clean up
        progress.close()
        
        # If operation was canceled, rollback any uncommitted changes
        if progress.wasCanceled():
            self.connection.rollback()

    
    @connection_required
    def get_all_items(self,table_name):
        """Return all items from the database for the table_name"""
        # self.cursor.execute("SELECT * FROM Stock")
        self.cursor.execute(f'Select * from {table_name}')
        data = self.cursor.fetchall()
        return data

    @connection_required
    def get_all_with_payment_status_matching(self,to_match_id=False,item_id=None,matching_column=None):
        """Return all items from the database for the table_name"""
        if to_match_id:
            self.cursor.execute(f'Select * from Rent WHERE {matching_column}={item_id} AND payment_status IN ("Stock Recieved", "Rented");')
        else:
            self.cursor.execute('Select * from Rent WHERE payment_status IN ("Stock Recieved", "Rented");')
        data = self.cursor.fetchall()
        return data
    


    @connection_required
    def update_multiple_columns(self, table_name, item_id, columns, values,matching_column="id"):
    
        if len(columns) != len(values):
            raise ValueError("The number of columns must match the number of values.")
        
        # Construct the SET clause dynamically
        set_clause = ", ".join([f"{col}=?" for col in columns])
        
        # Prepare the SQL query
        sql_query = f"UPDATE {table_name} SET {set_clause} WHERE {matching_column} = ?"
        
        # Execute the query
        self.cursor.execute(sql_query, (*values, item_id))
        self.connection.commit()
    


    @connection_required
    def update_multiple_columns_from_list(self, table_name, columns, values,matching_column="id"):
        # Construct the SET clause dynamically
        set_clause = ", ".join([f"{col}=?" for col in columns])
        # Prepare the SQL query
        sql_query = f"UPDATE {table_name} SET {set_clause} WHERE {matching_column} = ?"
        for value in values:
            # Execute the query
            self.cursor.execute(sql_query, (*value[1:], value[0]))
        self.connection.commit()


    @connection_required
    def update_all_specific_column(self,table_name,updates,column_name):
        """Update a single stock item by its ID."""
        for item_id,value in updates.items():
            self.cursor.execute(f"UPDATE {table_name} SET {column_name}=? WHERE id = ?", (value,item_id))
        self.connection.commit()


    @connection_required
    def update_rent(self, rent_id, customer_id, stock_id, quantity, rent_date, return_date, payment_status,amount_due):
        """Update a single rent by its ID."""
        self.cursor.execute(
            """
            UPDATE Rent
            SET customer_id = ?, stock_id = ?, quantity = ?, rent_date = ?, return_date = ?, payment_status = ?, amount_due = ?
            WHERE id = ?
            """,
            (customer_id, stock_id, quantity, rent_date, return_date, payment_status,amount_due, rent_id)
        )


    @connection_required
    def update_payement_to_paid_for_all(self, customer_id,rented_items):
        """Get the details of rented items for a customer, update stock quantities, and set rent status to 'Paid'."""
        # Update stock quantities and rent status
        for item in rented_items:
            # Update stock quantity
            self.cursor.execute(
                    """
                    UPDATE Rent
                    SET payment_status = 'Paid', amount_due = 0
                    WHERE id = ?
                    """,
                    (item[0],)
                )

        self.connection.commit()
    

    # ##! Customer Management

    @connection_required
    def update_customer(self, customer_id, name, contact_number, address, id_card_number, referrer_name,total_amount_due,amount_paid):
        
        """Update a single customer by their ID."""
        self.cursor.execute(
            """
            UPDATE Customer
            SET name = ?, contact_number = ?, address = ?, id_card_number = ?, referrer_name = ?,total_amount_due=?,amount_paid=?
            WHERE id = ?
            """,
            (name, contact_number, address,
             id_card_number, referrer_name,total_amount_due,amount_paid, customer_id)
        )

    

    @connection_required
    def update_all_customers(self, updates):
        """Update all customers with a list of updates. Updates should be a list of tuples."""
        updates = [tuple(update[0]) if isinstance(update, list) and len(
            update) == 1 else tuple(update) for update in updates]
        for update in updates:
            # Flatten nested lists into tuples
            self.cursor.execute(
                """
                UPDATE Customer
                SET name = ?, contact_number = ?, address = ?, id_card_number = ?, referrer_name = ?,total_amount_due = ?,amount_paid = ?
                WHERE id = ?
                """,
                (update[1], update[2], update[3],update[4], update[5],update[6],update[7], update[0])
            )




    ### ! Payments Management

    @connection_required
    def update_customer_amount_due(self, customer_id, amount_due):
        """Update the total amount due for a customer."""
        self.cursor.execute(
            "UPDATE Customer SET total_amount_due = ? WHERE id = ?",
            (amount_due, customer_id)
        )



    

    ### ! Sale Management


    @connection_required
    def get_unpaid_customers(self):
        """Return all unpaid customers from the database."""
        self.cursor.execute("SELECT * FROM Unpaid_Customers where amount_due>0")
        return self.cursor.fetchall()
    

    @connection_required
    def insert_data(self, table_name, columns, values):
        """Insert data into a specified table."""
        # Construct the column names and placeholders for the SQL query
        columns_str = ", ".join(columns)
        placeholders = ", ".join(["?" for _ in columns])
        
        # Prepare the SQL query
        sql_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        
        # Execute the query
        self.cursor.execute(sql_query, values)
        self.connection.commit()


    def close_connection(self):
        self.connection.close()

    @connection_required
    def get_all_payments(self, filter_dates=None, table_filters=None):
        """Return all payments from the database."""
        query="""
            SELECT 
                p.id AS payment_id,
                p.customer_id,
                c.name AS customer_name,
                p.payment_amount AS amount_paid,
                p.discount,
                p.payment_date
            FROM Payments p
            JOIN Customer c ON p.customer_id = c.id
        """
        params = []
        return self.construct_query_and_params_on_conditons(query,params,filter_dates,table_filters,date_attribute_different_tables='p.payment_date')
    
    @connection_required
    def get_all_sales(self, filter_dates=None, table_filters=None):
        """Return all sales from the database."""
        query="""
            SELECT 
                u.id AS sale_id,
                u.stock_name,
                u.quantity,
                u.total_cost_amount,
                u.total_sale_amount,
                u.discount_amount,
                u.profit_amount,
                u.payment_date
            FROM Sold_Items u
            where 1=1
        """
        params = []
        return self.construct_query_and_params_on_conditons(query,params,filter_dates,table_filters,date_attribute_different_tables='u.payment_date')



    @connection_required
    def get_rent_data(self, customer_id=None, status_list=None, filter_dates=None, table_filters=None):
        # Base query with joins
        query = """
            SELECT 
                r.id as 'Rent ID',
                r.customer_id as 'Customer ID',
                c.name as 'Customer Name',
                r.stock_id as 'Stock ID',
                s.st_name as 'Stock Name',
                r.quantity as 'Quantity Rented',
                CASE 
                    WHEN r.payment_status IN ('Paid', 'Stock Recieved') THEN r.quantity
                    ELSE 0 
                END as 'Quantity Returned',
                r.rent_date as 'Rent Date-Time',
                r.return_date as 'Return Date',
                r.payment_status as 'Status',
                r.amount_due as 'Amount Due'
            FROM Rent r
            LEFT JOIN Customer c ON r.customer_id = c.id
            LEFT JOIN Stock s ON r.stock_id = s.id
            WHERE 1=1
        """
   
        params = []
        
        # Add customer ID filter if provided
        if customer_id:
            query += " AND r.customer_id = ?"  # Using ? for SQLite placeholder
            params.append(customer_id)
        
        # Add status filter if provided
        if status_list and len(status_list) > 0:
            placeholders = ', '.join(['?' for _ in range(0,len(status_list))])
            query += f" AND r.payment_status IN ({placeholders})"
            params.extend(status_list)

        return self.construct_query_and_params_on_conditons(query,params,filter_dates,table_filters,date_attribute_different_tables='r.rent_date')
    

    @connection_required
    def get_all_customers_based_on_constraints(self, active_rents_search=False, column_param_dict=None):
        """Get customers with optional status search and column filtering."""
        base_query = "SELECT DISTINCT c.* FROM Customer c"
        params = []

        if active_rents_search:
            base_query += """
                JOIN Rent r ON c.id = r.customer_id
                WHERE r.payment_status IN ('Stock Recieved', 'Rented')
            """
        else:
            base_query += " WHERE 1=1"

        if column_param_dict:
            conditions = " AND ".join([f"c.{column} LIKE ?" for column in column_param_dict.keys()])
            base_query += f" AND {conditions}"
            params.extend([value + '%' for value in column_param_dict.values()])

        self.cursor.execute(base_query, params)
        return self.cursor.fetchall()

    def construct_query_and_params_on_conditons(self,query,params,filter_dates,table_filters,date_attribute_different_tables):
        # Handle date filters
        if filter_dates:
            if filter_dates["specific_date"]:
                query += f" AND DATE({date_attribute_different_tables}) = ?"
                params.append(filter_dates["specific_date"])
            
            elif filter_dates["date_range"] and len(filter_dates["date_range"]) == 2:
                query += f" AND DATE({date_attribute_different_tables}) BETWEEN ? AND ?"
                params.extend([
                    filter_dates["date_range"][0],
                    filter_dates["date_range"][1]
                ])
            
            elif filter_dates["multiple_dates"] and len(filter_dates["multiple_dates"]) > 0:
                placeholders = ', '.join(['?' for _ in range(0,len(filter_dates["multiple_dates"]))])
                query += f" AND DATE({date_attribute_different_tables}) IN ({placeholders})"
                params.extend([date for date in filter_dates["multiple_dates"]])
        
        # Handle table-specific filters
        if table_filters:
            for table_name, columns in table_filters.items():
                table_alias = {
                    'Rent': 'r',
                    'Payments':'p',
                    'Customer': 'c',
                    'Stock': 's',
                    'Sold_Items':'u'
                }.get(table_name)

                if table_alias and columns:
                    for column, value in columns.items():
                        query += f" AND {table_alias}.{column} LIKE ?"
                        params.append(f"{value}%")
        self.cursor.execute(query, params)
        
        return self.cursor.fetchall()