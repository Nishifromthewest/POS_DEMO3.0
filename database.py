import sqlite3
from typing import List, Tuple, Optional
import csv
from datetime import datetime
import os
import pandas as pd
import numpy as np

class Database:
    def __init__(self, db_name: str = "pos_system.db"):
        self.db_name = db_name
        # Create necessary directories
        os.makedirs("Bills", exist_ok=True)
        os.makedirs("Kitchen_tickets", exist_ok=True)
        self.init_db()

    def init_db(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'staff')),
                pin TEXT NOT NULL
            )
        ''')
        
        # Create menu items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT
            )
        ''')
        
        # Create orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_number INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create order items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                menu_item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders (id),
                FOREIGN KEY (menu_item_id) REFERENCES menu_items (id)
            )
        ''')
        
        # Create transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                payment_method TEXT NOT NULL,
                amount REAL NOT NULL,
                tip_amount REAL NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create default admin user if not exists
        cursor.execute("SELECT * FROM users WHERE role = 'admin'")
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (name, role, pin) VALUES (?, ?, ?)",
                ("Admin", "admin", "1234")
            )
            
        # Insert default Japanese menu items if not exists
        cursor.execute("SELECT COUNT(*) FROM menu_items")
        if cursor.fetchone()[0] == 0:
            menu_items = [
                ("Miso Soup", "Starters", 4.50, "Traditional Japanese soup with tofu and seaweed"),
                ("Edamame", "Starters", 5.50, "Steamed soybeans with sea salt"),
                ("Gyoza", "Starters", 7.50, "Pan-fried dumplings with pork and vegetables"),
                ("California Roll", "Sushi", 8.50, "Crab, avocado, and cucumber roll"),
                ("Salmon Nigiri", "Sushi", 9.50, "Fresh salmon over pressed sushi rice"),
                ("Tuna Roll", "Sushi", 8.50, "Fresh tuna roll with cucumber"),
                ("Chicken Teriyaki", "Main Dishes", 15.50, "Grilled chicken with teriyaki sauce"),
                ("Beef Ramen", "Main Dishes", 14.50, "Noodles in beef broth with vegetables"),
                ("Vegetable Tempura", "Side Dishes", 7.50, "Assorted vegetables in crispy batter"),
                ("Green Tea Ice Cream", "Desserts", 5.50, "Traditional Japanese dessert")
            ]
            cursor.executemany(
                "INSERT INTO menu_items (name, category, price, description) VALUES (?, ?, ?, ?)",
                menu_items
            )
        
        conn.commit()
        conn.close()

    def add_user(self, name: str, role: str, pin: str) -> bool:
        """Add a new user to the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, role, pin) VALUES (?, ?, ?)",
                (name, role, pin)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error:
            return False

    def remove_user(self, user_id: int) -> bool:
        """Remove a user from the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error:
            return False

    def get_all_users(self) -> List[Tuple]:
        """Get all users from the database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, role, pin FROM users")
        users = cursor.fetchall()
        conn.close()
        return users

    def verify_user(self, name: str, pin: str) -> Optional[Tuple]:
        """Verify user credentials and return user data if valid"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, role FROM users WHERE name = ? AND pin = ?",
            (name, pin)
        )
        user = cursor.fetchone()
        conn.close()
        return user

    def get_menu_items(self) -> List[Tuple]:
        """Get all menu items"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, category, price, description FROM menu_items")
        items = cursor.fetchall()
        conn.close()
        return items

    def create_order(self, table_number: int, user_id: int) -> int:
        """Create a new order and return its ID"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO orders (table_number, user_id, status) VALUES (?, ?, ?)",
            (table_number, user_id, "pending")
        )
        order_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return order_id

    def add_item_to_order(self, order_id: int, menu_item_id: int, quantity: int) -> bool:
        """Add an item to an existing order"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO order_items (order_id, menu_item_id, quantity) VALUES (?, ?, ?)",
                (order_id, menu_item_id, quantity)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error:
            return False

    def get_order_items(self, order_id: int) -> List[Tuple]:
        """Get all items in an order"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT mi.name, oi.quantity, mi.price
            FROM order_items oi
            JOIN menu_items mi ON oi.menu_item_id = mi.id
            WHERE oi.order_id = ?
        """, (order_id,))
        items = cursor.fetchall()
        conn.close()
        return items

    def delete_order_items(self, order_id: int) -> bool:
        """Delete all items associated with an order"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error:
            return False

    def update_order_status(self, order_id: int, status: str) -> bool:
        """Update the status of an order"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            if status == "deleted":
                # First delete all order items
                if not self.delete_order_items(order_id):
                    return False
                    
            cursor.execute(
                "UPDATE orders SET status = ? WHERE id = ?",
                (status, order_id)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error:
            return False

    def get_order_details(self, order_id: int) -> Tuple:
        """Get order details including user information"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.id, o.table_number, o.status, o.created_at, u.name as user_name
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE o.id = ?
        """, (order_id,))
        order = cursor.fetchone()
        conn.close()
        return order

    def clear_all_orders(self) -> bool:
        """Clear all orders and their items from the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # First delete all order items
            cursor.execute("DELETE FROM order_items")
            
            # Then delete all orders
            cursor.execute("DELETE FROM orders")
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error:
            return False

    def get_active_order_for_table(self, table_number: int) -> Optional[int]:
        """Get the active (pending or confirmed) order ID for a table"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM orders 
            WHERE table_number = ? AND status IN ('pending', 'confirmed')
            ORDER BY created_at DESC LIMIT 1
        """, (table_number,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def generate_kitchen_order_csv(self, order_id: int) -> str:
        """Generate a CSV file for kitchen orders"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Get order details including user
        cursor.execute("""
            SELECT o.table_number, o.created_at, mi.name, oi.quantity, u.name as user_name
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            JOIN menu_items mi ON oi.menu_item_id = mi.id
            JOIN users u ON o.user_id = u.id
            WHERE o.id = ?
        """, (order_id,))
        items = cursor.fetchall()
        
        if not items:
            return None
            
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"kitchen_order_{order_id}_{timestamp}.csv"
        filepath = os.path.join("Kitchen_tickets", filename)
        
        # Write to CSV
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Table Number', 'Order Time', 'Item', 'Quantity', 'Ordered By'])
            for item in items:
                writer.writerow(item)
        
        conn.close()
        return filepath

    def add_transaction(self, order_id: int, payment_method: str, amount: float, tip_amount: float, user_id: int) -> bool:
        """Add a new transaction record"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO transactions (order_id, payment_method, amount, tip_amount, user_id) VALUES (?, ?, ?, ?, ?)",
                (order_id, payment_method, amount, tip_amount, user_id)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error:
            return False

    def get_daily_revenue(self, date):
        """Get total revenue for a specific date"""
        conn = sqlite3.connect(self.db_name)
        query = """
            SELECT created_at, amount, payment_method, tip_amount
            FROM transactions
            WHERE DATE(created_at) = ?
        """
        df = pd.read_sql_query(query, conn, params=(date,))
        conn.close()
        
        if df.empty:
            return {
                'total_revenue': 0.0,
                'hourly_revenue': pd.Series(),
                'revenue_by_payment': pd.Series()
            }
            
        return {
            'total_revenue': df['amount'].sum(),
            'hourly_revenue': df.groupby(df['created_at'].dt.hour)['amount'].sum(),
            'revenue_by_payment': df.groupby('payment_method')['amount'].sum()
        }

    def get_daily_tips(self, date):
        """Get total tips for a specific date"""
        conn = sqlite3.connect(self.db_name)
        query = """
            SELECT created_at, tip_amount, payment_method
            FROM transactions
            WHERE DATE(created_at) = ?
        """
        df = pd.read_sql_query(query, conn, params=(date,))
        conn.close()
        
        if df.empty:
            return {
                'total_tips': 0.0,
                'tips_by_payment': pd.Series(),
                'tips_by_hour': pd.Series()
            }
            
        return {
            'total_tips': df['tip_amount'].sum(),
            'tips_by_payment': df.groupby('payment_method')['tip_amount'].sum(),
            'tips_by_hour': df.groupby(df['created_at'].dt.hour)['tip_amount'].sum()
        }

    def get_daily_transaction_analysis(self, date):
        """Get comprehensive transaction analysis for a specific date"""
        conn = sqlite3.connect(self.db_name)
        query = """
            SELECT t.created_at, t.amount, t.payment_method, t.tip_amount,
                   o.table_number, u.name as server_name
            FROM transactions t
            JOIN orders o ON t.order_id = o.id
            JOIN users u ON t.user_id = u.id
            WHERE DATE(t.created_at) = ?
        """
        df = pd.read_sql_query(query, conn, params=(date,))
        conn.close()
        
        if df.empty:
            return {
                'transaction_count': 0,
                'average_order': 0.0,
                'hourly_transactions': pd.Series(),
                'table_analysis': pd.DataFrame(),
                'server_analysis': pd.DataFrame()
            }
            
        df['created_at'] = pd.to_datetime(df['created_at'])
        
        return {
            'transaction_count': len(df),
            'average_order': df['amount'].mean(),
            'hourly_transactions': df.groupby(df['created_at'].dt.hour).size(),
            'table_analysis': df.groupby('table_number').agg({
                'amount': ['count', 'sum', 'mean'],
                'tip_amount': 'sum'
            }).round(2),
            'server_analysis': df.groupby('server_name').agg({
                'amount': ['count', 'sum', 'mean'],
                'tip_amount': 'sum'
            }).round(2)
        }

    def get_daily_menu_analysis(self, date):
        """Get detailed menu item analysis for a specific date"""
        conn = sqlite3.connect(self.db_name)
        query = """
            SELECT o.created_at, mi.name, mi.category, mi.price,
                   oi.quantity, o.table_number
            FROM order_items oi
            JOIN menu_items mi ON oi.menu_item_id = mi.id
            JOIN orders o ON oi.order_id = o.id
            WHERE DATE(o.created_at) = ?
        """
        df = pd.read_sql_query(query, conn, params=(date,))
        conn.close()
        
        if df.empty:
            return {
                'top_items': pd.DataFrame(),
                'category_analysis': pd.DataFrame(),
                'hourly_sales': pd.DataFrame()
            }
            
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['revenue'] = df['price'] * df['quantity']
        
        return {
            'top_items': df.groupby('name').agg({
                'quantity': 'sum',
                'revenue': 'sum'
            }).sort_values('quantity', ascending=False).head(10),
            
            'category_analysis': df.groupby('category').agg({
                'quantity': 'sum',
                'revenue': 'sum'
            }).sort_values('revenue', ascending=False),
            
            'hourly_sales': df.groupby(df['created_at'].dt.hour).agg({
                'quantity': 'sum',
                'revenue': 'sum'
            })
        }

    def get_daily_tax_analysis(self, date):
        """Get detailed tax analysis for a specific date"""
        conn = sqlite3.connect(self.db_name)
        query = """
            SELECT t.created_at, t.amount, t.payment_method,
                   mi.category, mi.price, oi.quantity
            FROM transactions t
            JOIN orders o ON t.order_id = o.id
            JOIN order_items oi ON o.id = oi.order_id
            JOIN menu_items mi ON oi.menu_item_id = mi.id
            WHERE DATE(t.created_at) = ?
        """
        df = pd.read_sql_query(query, conn, params=(date,))
        conn.close()
        
        if df.empty:
            return {
                'total_tax': 0.0,
                'tax_by_category': pd.Series(),
                'tax_by_hour': pd.Series()
            }
            
        # Apply different tax rates based on category
        df['tax_rate'] = np.where(df['category'].isin(['Drinks', 'Food']), 0.09, 0.21)
        df['tax_amount'] = df['amount'] * df['tax_rate']
        
        return {
            'total_tax': df['tax_amount'].sum(),
            'tax_by_category': df.groupby('category')['tax_amount'].sum(),
            'tax_by_hour': df.groupby(df['created_at'].dt.hour)['tax_amount'].sum()
        }

    def get_daily_summary(self, date):
        """Get a comprehensive daily summary"""
        revenue_data = self.get_daily_revenue(date)
        tips_data = self.get_daily_tips(date)
        transaction_data = self.get_daily_transaction_analysis(date)
        menu_data = self.get_daily_menu_analysis(date)
        tax_data = self.get_daily_tax_analysis(date)
        
        summary = {
            'date': date,
            'revenue': {
                'total': revenue_data['total_revenue'],
                'by_hour': revenue_data['hourly_revenue'],
                'by_payment': revenue_data['revenue_by_payment']
            },
            'tips': {
                'total': tips_data['total_tips'],
                'by_payment': tips_data['tips_by_payment'],
                'by_hour': tips_data['tips_by_hour']
            },
            'transactions': {
                'count': transaction_data['transaction_count'],
                'average_order': transaction_data['average_order'],
                'hourly_distribution': transaction_data['hourly_transactions'],
                'table_analysis': transaction_data['table_analysis'],
                'server_analysis': transaction_data['server_analysis']
            },
            'menu': {
                'top_items': menu_data['top_items'],
                'category_analysis': menu_data['category_analysis'],
                'hourly_sales': menu_data['hourly_sales']
            },
            'tax': {
                'total': tax_data['total_tax'],
                'by_category': tax_data['tax_by_category'],
                'by_hour': tax_data['tax_by_hour']
            }
        }
        
        return summary

    def get_daily_average_order(self, date):
        """Get average order value for a specific date"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COALESCE(AVG(amount), 0)
            FROM transactions
            WHERE DATE(created_at) = ?
        """, (date,))
        result = cursor.fetchone()[0] or 0.0
        conn.close()
        return result

    def get_daily_transaction_count(self, date):
        """Get number of transactions for a specific date"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*)
            FROM transactions
            WHERE DATE(created_at) = ?
        """, (date,))
        result = cursor.fetchone()[0] or 0
        conn.close()
        return result

    def get_daily_guest_count(self, date):
        """Get total number of guests for a specific date"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(DISTINCT table_number)
            FROM orders
            WHERE DATE(created_at) = ?
        """, (date,))
        result = cursor.fetchone()[0] or 0
        conn.close()
        return result

    def get_daily_average_guests(self, date):
        """Get average number of guests per table for a specific date"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COALESCE(AVG(table_count), 0)
            FROM (
                SELECT table_number, COUNT(*) as table_count
                FROM orders
                WHERE DATE(created_at) = ?
                GROUP BY table_number
            )
        """, (date,))
        result = cursor.fetchone()[0] or 0.0
        conn.close()
        return result

    def get_daily_payment_method_total(self, date, method):
        """Get total amount for a specific payment method on a date"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0)
            FROM transactions
            WHERE DATE(created_at) = ? AND payment_method = ?
        """, (date, method))
        result = cursor.fetchone()[0] or 0.0
        conn.close()
        return result

    def get_daily_tax_total(self, date):
        """Get total tax collected for a specific date"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COALESCE(SUM(amount * 0.21), 0)
            FROM transactions
            WHERE DATE(created_at) = ?
        """, (date,))
        result = cursor.fetchone()[0] or 0.0
        conn.close()
        return result

    def get_daily_tax_by_rate(self, date, rate):
        """Get tax collected for a specific rate on a date"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COALESCE(SUM(amount * ?), 0)
            FROM transactions
            WHERE DATE(created_at) = ?
        """, (rate/100, date))
        result = cursor.fetchone()[0] or 0.0
        conn.close()
        return result

    def get_daily_top_items(self, date, limit=5):
        """Get top selling items for a specific date"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.name, SUM(oi.quantity) as total_quantity, 
                   SUM(oi.quantity * m.price) as total_revenue
            FROM order_items oi
            JOIN menu_items m ON oi.menu_item_id = m.id
            JOIN orders o ON oi.order_id = o.id
            WHERE DATE(o.created_at) = ?
            GROUP BY m.id
            ORDER BY total_quantity DESC
            LIMIT ?
        """, (date, limit))
        result = cursor.fetchall()
        conn.close()
        return result

    def get_daily_employee_sales(self, date):
        """Get sales statistics per employee for a specific date"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.name, COUNT(DISTINCT o.id) as order_count,
                   COALESCE(SUM(t.amount), 0) as total_revenue
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id
            LEFT JOIN transactions t ON o.id = t.order_id
            WHERE DATE(o.created_at) = ?
            GROUP BY u.id
            ORDER BY total_revenue DESC
        """, (date,))
        result = cursor.fetchall()
        conn.close()
        return result 