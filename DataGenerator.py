from faker import Faker
import random
from datetime import datetime, timedelta
import sqlite3
import string
import math

class DataGenerator:
    def __init__(self, db_path: str = "stock_rental_system.db"):
        self.fake = Faker()
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.stock_names = set()
        
    def generate_unique_id_card(self) -> str:
        """Generate a unique 13-digit ID card number."""
        while True:
            id_card = ''.join(random.choices(string.digits, k=13))
            self.cursor.execute("SELECT COUNT(*) FROM Customer WHERE id_card_number = ?", (id_card,))
            if self.cursor.fetchone()[0] == 0:
                return id_card

    def generate_phone_number(self) -> str:
        """Generate an 11-digit phone number starting with '03'."""
        return '03' + ''.join(random.choices(string.digits, k=9))

    def generate_unique_stock_name(self) -> str:
        """Generate a unique stock name."""
        while True:
            name = f"{self.fake.word()}"
            if name not in self.stock_names:
                self.stock_names.add(name)
                print('Stock Name: '+name)
                return name
            print('stuck in loop')

    def generate_price_history(self, stock_id: int, base_price: int):
        """Generate price history for a stock item between 2021-2024."""
        start_date = datetime(2021, 1, 1)
        end_date = datetime(2024, 12, 31)
        current_date = start_date
        current_price = base_price

        while current_date <= end_date:
            # 30% chance of price change each month
            if random.random() < 0.3:
                # Price can change by -20% to +20%
                change_percentage = random.uniform(-0.20, 0.20)
                new_price = max(30, min(500, round(current_price * (1 + change_percentage), -1)))  # Round to nearest 10
                
                if new_price != current_price:
                    current_price = new_price
                    self.cursor.execute("""
                        INSERT INTO Stock_Price (stock_id, price, price_date)
                        VALUES (?, ?, ?)
                    """, (stock_id, current_price, current_date.strftime('%Y-%m-%d %H:%M')))

            current_date += timedelta(days=random.randint(20, 40))  # Random interval between price changes

    def insert_customers(self, count: int = 20000):
        """Insert the specified number of customers."""
        print("Inserting customers...")
        for i in range(count):
            if i % 1000 == 0:
                print(f"Inserted {i} customers")
            
            customer_data = (
                self.fake.name(),
                self.generate_phone_number(),
                self.fake.address().replace('\n', ', '),
                self.generate_unique_id_card(),
                self.fake.name() if random.random() < 0.3 else None,
                0.0,  # total_amount_due
                0.0   # amount_paid
            )
            
            self.cursor.execute("""
                INSERT INTO Customer (name, contact_number, address, id_card_number, 
                referrer_name, total_amount_due, amount_paid)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, customer_data)
            
            if i % 5000 == 0:
                self.conn.commit()
        
        self.conn.commit()

    def insert_stock_items(self, count: int = 500):
        """Insert stock items and their prices."""
        print("Inserting stock items...")
        for i in range(count):
            if i % 1000 == 0:
                print(f"Inserted {i} stock items")
                
            quantity = random.randint(5, 50) * 10
            stock_data = (
                self.generate_unique_stock_name(),
                quantity,
                quantity
            )
            
            self.cursor.execute("""
                INSERT INTO Stock (st_name, total_quantity, available_quantity)
                VALUES (?, ?, ?)
            """, stock_data)
            
            stock_id = self.cursor.lastrowid
            print(stock_id)
            # Generate price history
            initial_price = random.randint(3, 50) * 10
            # self.generate_price_history(stock_id, initial_price)
            start_date= datetime.strptime('2021-01-01 00:00','%Y-%m-%d %H:%M')
            end_date= datetime.strptime('2023-12-30 00:00','%Y-%m-%d %H:%M')
            random_date=self.fake.date_time_between(start_date=start_date,end_date=end_date)
            self.cursor.execute(
                """
                INSERT INTO Stock_Price (stock_id, price, price_date)
                VALUES (?, ?, ?)
                """, (stock_id, initial_price, random_date.strftime('%Y-%m-%d %H:%M'))
            )
            if i % 1000 == 0:  # Commit more frequently due to multiple price insertions
                self.conn.commit()
        
        self.conn.commit()

    def insert_selling_stock(self, count: int = 500):
        """Insert selling stock items."""
        print("Inserting selling stock...")
        for i in range(count):
            if i % 1000 == 0:
                print(f"Inserted {i} selling stock items")
                
            buying_price = random.randint(3, 50) * 10
            margin = random.uniform(0.21, 0.30)
            selling_price = math.ceil(buying_price * (1 + margin))
            
            stock_data = (
                self.generate_unique_stock_name(),
                random.randint(1, 50) * 10,
                buying_price,
                selling_price,
                self.fake.date_time_between(
                    start_date=datetime(2021, 1, 1),
                    end_date=datetime(2024, 12, 31)
                ).strftime('%Y-%m-%d %H:%M')
            )
            
            self.cursor.execute("""
                INSERT INTO Selling_Stock (item_name, available_quantity, 
                buying_price, selling_price, price_updated_date)
                VALUES (?, ?, ?, ?, ?)
            """, stock_data)
            
            if i % 5000 == 0:
                self.conn.commit()
        
        self.conn.commit()

    def insert_rent_records(self, paid_count: int = 5000, rented_count: int = 15000):
        """Insert rent records."""
        print("Inserting rent records...")
        
        # Get all customer IDs
        self.cursor.execute("SELECT id FROM Customer")
        customer_ids = [row[0] for row in self.cursor.fetchall()]
        
        # Get all stock IDs and their available quantities
        self.cursor.execute("SELECT id, available_quantity FROM Stock")
        stock_data = self.cursor.fetchall()
        stock_quantities = {row[0]: row[1] for row in stock_data}
        
        rent_date_start = datetime(2025, 1, 1)
        rent_date_end = datetime(2025, 1, 14)
        
        # Insert paid rentals
        for i in range(paid_count):
            if i % 1000 == 0:
                print(f"Inserted {i} paid rentals")
                
            customer_id = random.choice(customer_ids)
            stock_id = random.choice(list(stock_quantities.keys()))
            available_qty = stock_quantities[stock_id]
            rent_qty = min(random.randint(1, 5), available_qty)
            rent_date = self.fake.date_time_between(
                start_date=rent_date_start,
                end_date=rent_date_end
            )
            
            self.cursor.execute("""
                INSERT INTO Rent (customer_id, stock_id, quantity, rent_date,
                return_date, payment_status, amount_due)
                VALUES (?, ?, ?, ?, ?, 'Paid', ?)
            """, (
                customer_id, stock_id, rent_qty,
                rent_date.strftime('%Y-%m-%d %H:%M'),
                (rent_date + timedelta(days=random.randint(1, 7))).strftime('%Y-%m-%d %H:%M'),
                0.0
            ))
            
            
            if i % 1000 == 0:
                self.conn.commit()
        
        # Insert rented (unpaid) rentals
        for i in range(rented_count):
            if i % 1000 == 0:
                print(f"Inserted {i} rented (unpaid) rentals")
                
            customer_id = random.choice(customer_ids)
            stock_id = random.choice(list(stock_quantities.keys()))
            available_qty = stock_quantities[stock_id]
            
            if available_qty < 1:
                continue
                
            rent_qty = min(random.randint(1, 3), available_qty)

            amount_due = random.randint(100, 1000)
            
            self.cursor.execute("""
                INSERT INTO Rent (customer_id, stock_id, quantity, rent_date,
                payment_status, amount_due)
                VALUES (?, ?, ?, ?, 'Rented', ?)
            """, (
                customer_id, stock_id, rent_qty,
                self.fake.date_time_between(
                    start_date=rent_date_start,
                    end_date=rent_date_end
                ).strftime('%Y-%m-%d %H:%M'),
                amount_due
            ))
            
            # Update available quantity and customer's total amount due
            stock_quantities[stock_id] -= rent_qty
            self.cursor.execute("""
                UPDATE Stock 
                SET available_quantity = available_quantity - ?
                WHERE id = ?
            """, (rent_qty, stock_id))
            
            
            if i % 1000 == 0:
                self.conn.commit()
        
        self.conn.commit()

    def insert_sold_items(self, count: int = 8000):
        """Insert sold items records."""
        print("Inserting sold items...")
        
        self.cursor.execute("SELECT item_name, available_quantity, buying_price, selling_price FROM Selling_Stock")
        selling_stock = self.cursor.fetchall()
        
        for i in range(count):
            if i % 1000 == 0:
                print(f"Inserted {i} sold items")
                
            stock = random.choice(selling_stock)
            quantity = random.randint(1, min(5, stock[1]))  # Don't exceed available quantity
            
            # Apply discount to some items (20% chance)
            discount = random.randint(5, 15) if random.random() < 0.2 else 0
            
            total_cost = quantity * stock[2]
            total_sale = quantity * stock[3]
            discount_amount = (total_sale * discount) / 100
            profit = total_sale - total_cost - discount_amount
            
            self.cursor.execute("""
                INSERT INTO Sold_Items (stock_name, quantity, total_cost_amount,
                total_sale_amount, discount_amount, profit_amount, payment_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                stock[0], quantity, total_cost, total_sale,
                discount_amount, profit,
                self.fake.date_time_between(
                    start_date=datetime(2021, 1, 1),
                    end_date=datetime(2024, 12, 31)
                ).strftime('%Y-%m-%d %H:%M')
            ))
            
            # Update available quantity
            self.cursor.execute("""
                UPDATE Selling_Stock
                SET available_quantity = available_quantity - ?
                WHERE item_name = ?
            """, (quantity, stock[0]))
            
            if i % 1000 == 0:
                self.conn.commit()
        
        self.conn.commit()

    def insert_unpaid_customers(self, count: int = 3000):
        """Insert independent unpaid customer records."""
        print("Inserting unpaid customers...")
        
        for i in range(count):
            if i % 100 == 0:
                print(f"Inserted {i} unpaid customers")
            
            # Generate unique customer details
            customer_data = (
                self.fake.name(),
                self.generate_phone_number(),
                self.generate_unique_id_card(),
                random.randint(500, 5000),  # amount_due between 500 and 5000
                self.fake.date_time_between(
                    start_date=datetime(2024, 1, 1),
                    end_date=datetime(2025, 1, 14)
                ).strftime('%Y-%m-%d %H:%M')
            )
            
            self.cursor.execute("""
                INSERT INTO Unpaid_Customers 
                (customer_name, customer_mobile, id_card, amount_due, loan_date)
                VALUES (?, ?, ?, ?, ?)
            """, customer_data)
            
            if i % 100 == 0:
                self.conn.commit()
        
        self.conn.commit()

    def insert_payments(self, count: int = 15000):
        """Insert payment records."""
        print("Inserting payments...")
        
        self.cursor.execute("SELECT id FROM Customer")
        customer_ids = [row[0] for row in self.cursor.fetchall()]
        
        for i in range(count):
            if i % 1000 == 0:
                print(f"Inserted {i} payments")
                
            customer_id = random.choice(customer_ids)
            payment_amount = random.randint(100, 2000)
            discount = random.randint(0, 10) if random.random() < 0.1 else 0
            
            self.cursor.execute("""
                INSERT INTO Payments (customer_id, payment_amount, discount, payment_date)
                VALUES (?, ?, ?, ?)
            """, (
                customer_id,
                payment_amount,
                discount,
                self.fake.date_time_between(
                    start_date=datetime(2021, 1, 1),
                    end_date=datetime(2024, 12, 31)
                ).strftime('%Y-%m-%d %H:%M')
            ))
            
            
            if i % 1000 == 0:
                self.conn.commit()
        
        self.conn.commit()

    def generate_all_data(self):
        """Generate all required data in the correct order."""
        # self.insert_customers()
        # self.insert_stock_items()
        self.insert_selling_stock()
        # self.insert_rent_records()
        # self.insert_sold_items()
        # self.insert_payments()
        # self.insert_unpaid_customers()
        print("Data generation completed!")

    def __del__(self):
        """Cleanup database connection."""
        self.conn.close()


generator=DataGenerator()
generator.generate_all_data()