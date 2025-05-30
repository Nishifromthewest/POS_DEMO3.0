from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QTableWidget, QTableWidgetItem, QComboBox,
                            QSpinBox, QMessageBox, QTabWidget, QWidget, QGridLayout,
                            QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from database import Database
from paymentwindow import PaymentWindow
from logger import pos_logger

class MenuItemButton(QPushButton):
    def __init__(self, item_data, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        self.setup_ui()
        
    def setup_ui(self):
        name, price = self.item_data[1], self.item_data[3]
        self.setText(f"{name}\n€{price:.2f}")
        self.setMinimumHeight(80)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 10px;
                padding: 10px;
                color: #ffffff;
                font-size: 16px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
        """)

class DrinksTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create scroll area for drinks
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #1e1e1e;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #2d2d2d;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #3d3d3d;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Create widget to hold all drink categories
        drinks_widget = QWidget()
        drinks_layout = QVBoxLayout(drinks_widget)
        drinks_layout.setSpacing(20)
        
        # Add drink categories
        self.add_drink_category(drinks_layout, "Warme Dranken", [
            ("Koffie", 2.50),
            ("Cappuccino", 3.50),
            ("Latte Macchiato", 3.75),
            ("Espresso", 2.00),
            ("Thee", 2.50),
            ("Chocolademelk", 3.00)
        ])
        
        self.add_drink_category(drinks_layout, "Koude Dranken", [
            ("Cola", 2.50),
            ("Fanta", 2.50),
            ("Sprite", 2.50),
            ("Ice Tea", 2.75),
            ("Mineraalwater", 2.00),
            ("Sinaasappelsap", 3.00)
        ])
        
        self.add_drink_category(drinks_layout, "Bieren", [
            ("Pils", 3.00),
            ("Speciaal Bier", 3.50),
            ("Witbier", 3.75),
            ("Radler", 3.25)
        ])
        
        self.add_drink_category(drinks_layout, "Wijnen", [
            ("Rode Wijn (glas)", 4.00),
            ("Witte Wijn (glas)", 4.00),
            ("Rosé (glas)", 4.00),
            ("Prosecco (glas)", 4.50)
        ])
        
        self.add_drink_category(drinks_layout, "Cocktails", [
            ("Mojito", 8.50),
            ("Caipirinha", 8.50),
            ("Margarita", 8.50),
            ("Pina Colada", 8.50)
        ])
        
        scroll.setWidget(drinks_widget)
        layout.addWidget(scroll)
    
    def add_drink_category(self, parent_layout, category_name, drinks):
        # Create category frame
        category_frame = QWidget()
        category_frame.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        category_layout = QVBoxLayout(category_frame)
        
        # Add category title
        title = QLabel(category_name)
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #ffffff;")
        category_layout.addWidget(title)
        
        # Add drinks grid
        drinks_grid = QGridLayout()
        drinks_grid.setSpacing(10)
        
        for i, (name, price) in enumerate(drinks):
            btn = QPushButton(f"{name}\n€{price:.2f}")
            btn.setMinimumHeight(80)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3d3d3d;
                    border: 1px solid #4d4d4d;
                    border-radius: 10px;
                    padding: 10px;
                    color: #ffffff;
                    font-size: 16px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #4d4d4d;
                }
            """)
            btn.clicked.connect(lambda checked, n=name, p=price: self.add_drink(n, p))
            drinks_grid.addWidget(btn, i // 3, i % 3)
        
        category_layout.addLayout(drinks_grid)
        parent_layout.addWidget(category_frame)
    
    def add_drink(self, name, price):
        # Add drink to parent's order
        if self.parent:
            self.parent.add_drink_to_order(name, price)

class OrderMenu(QDialog):
    def __init__(self, table_number, user_data, parent=None):
        super().__init__(parent)
        self.table_number = table_number
        self.user_data = user_data  # (id, name, role)
        self.db = Database()
        self.current_order_id = None
        self.setup_ui()
        self.showMaximized()  # Show maximized by default
        self.load_existing_order()  # Load existing order if any
        
    def setup_ui(self):
        self.setWindowTitle(f"Table {self.table_number} - Order Menu")
        self.setMinimumSize(1200, 900)  # Increased minimum size
        
        # Set dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 10px;
                padding: 15px;
                color: #ffffff;
                font-size: 16px;
                min-width: 120px;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            QPushButton#exitButton {
                background-color: #d32f2f;
                border: 1px solid #b71c1c;
            }
            QPushButton#exitButton:hover {
                background-color: #b71c1c;
            }
            QLabel {
                color: #ffffff;
                font-size: 16px;
            }
            QTableWidget {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                color: #ffffff;
                gridline-color: #3d3d3d;
                font-size: 16px;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTableWidget::item:selected {
                background-color: #3d3d3d;
            }
            QTabWidget::pane {
                border: 1px solid #3d3d3d;
                background-color: #2d2d2d;
                border-radius: 10px;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 15px 30px;
                margin: 2px;
                border: 1px solid #3d3d3d;
                border-radius: 10px;
                font-size: 16px;
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background-color: #3d3d3d;
                border: 1px solid #4d4d4d;
            }
            QTabBar::tab:hover {
                background-color: #3d3d3d;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # User info
        user_info = QLabel(f"Order taken by: {self.user_data[1]}")
        user_info.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(user_info)
        
        # Menu tabs
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.setup_menu_tabs()
        layout.addWidget(self.tabs)
        
        # Current order table
        self.order_table = QTableWidget()
        self.order_table.setColumnCount(4)
        self.order_table.setHorizontalHeaderLabels(["Item", "Quantity", "Price", "Total"])
        self.order_table.horizontalHeader().setStretchLastSection(True)
        self.order_table.verticalHeader().setDefaultSectionSize(50)
        layout.addWidget(self.order_table)
        
        # Total amount
        self.total_label = QLabel("Total: €0.00")
        self.total_label.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(self.total_label)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        
        self.confirm_btn = QPushButton("Bestelling Bevestigen")
        self.pay_btn = QPushButton("Afrekenen")
        self.delete_btn = QPushButton("Delete Order")
        self.exit_btn = QPushButton("Exit")
        self.exit_btn.setObjectName("exitButton")
        
        self.confirm_btn.clicked.connect(self.confirm_order)
        self.pay_btn.clicked.connect(self.pay_order)
        self.delete_btn.clicked.connect(self.delete_order)
        self.exit_btn.clicked.connect(self.exit_menu)
        
        buttons_layout.addWidget(self.confirm_btn)
        buttons_layout.addWidget(self.pay_btn)
        buttons_layout.addWidget(self.delete_btn)
        buttons_layout.addWidget(self.exit_btn)
        
        layout.addLayout(buttons_layout)
        
    def setup_menu_tabs(self):
        # Add food menu tabs
        menu_items = self.db.get_menu_items()
        categories = {}
        
        # Group items by category
        for item in menu_items:
            category = item[2]
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        # Create tabs for each category
        for category, items in categories.items():
            tab = QWidget()
            layout = QGridLayout(tab)
            layout.setSpacing(15)
            
            # Create a grid of menu item buttons
            for i, item in enumerate(items):
                btn = MenuItemButton(item)
                btn.clicked.connect(lambda checked, i=item: self.add_to_order(i, 1))
                layout.addWidget(btn, i // 3, i % 3)  # 3 items per row
            
            self.tabs.addTab(tab, category)
        
        # Add drinks tab
        drinks_tab = DrinksTab(self)
        self.tabs.addTab(drinks_tab, "Dranken")
    
    def add_to_order(self, item, quantity):
        if quantity <= 0:
            return
            
        if not self.current_order_id:
            self.current_order_id = self.db.create_order(self.table_number, self.user_data[0])
            
        if self.db.add_item_to_order(self.current_order_id, item[0], quantity):
            self.update_order_table()
        else:
            QMessageBox.warning(self, "Error", "Failed to add item to order!")
    
    def update_order_table(self):
        if not self.current_order_id:
            return
            
        items = self.db.get_order_items(self.current_order_id)
        self.order_table.setRowCount(len(items))
        
        total = 0
        for row, item in enumerate(items):
            name, quantity, price = item
            
            name_item = QTableWidgetItem(name)
            quantity_item = QTableWidgetItem(str(quantity))
            price_item = QTableWidgetItem(f"€{price:.2f}")
            total_item = QTableWidgetItem(f"€{quantity * price:.2f}")
            
            # Make items non-editable
            for table_item in [name_item, quantity_item, price_item, total_item]:
                table_item.setFlags(table_item.flags() & ~Qt.ItemIsEditable)
            
            self.order_table.setItem(row, 0, name_item)
            self.order_table.setItem(row, 1, quantity_item)
            self.order_table.setItem(row, 2, price_item)
            self.order_table.setItem(row, 3, total_item)
            
            total += quantity * price
        
        self.total_label.setText(f"Total: €{total:.2f}")
    
    def confirm_order(self):
        if not self.current_order_id:
            QMessageBox.warning(self, "Error", "No active order!")
            return
            
        if self.db.update_order_status(self.current_order_id, "confirmed"):
            # Generate kitchen order CSV
            csv_file = self.db.generate_kitchen_order_csv(self.current_order_id)
            if csv_file:
                QMessageBox.information(self, "Success", f"Order confirmed! Kitchen order saved to {csv_file}")
                # Close the dialog after successful confirmation
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to generate kitchen order!")
        else:
            QMessageBox.warning(self, "Error", "Failed to confirm order!")
    
    def pay_order(self):
        if not self.current_order_id:
            QMessageBox.warning(self, "Error", "No active order!")
            return
            
        # Get total amount from the label
        total_text = self.total_label.text()
        total_amount = float(total_text.replace("Total: €", ""))
        
        # Show payment window
        payment_window = PaymentWindow(total_amount, self)
        if payment_window.exec_() == QDialog.Accepted:
            # Save transaction details
            payment_result = payment_window.payment_result
            if self.db.add_transaction(
                self.current_order_id,
                payment_result['method'],
                payment_result['amount'],
                payment_result['tip'],
                self.user_data[0]  # Pass the user_id who processed the payment
            ):
                if self.db.update_order_status(self.current_order_id, "paid"):
                    QMessageBox.information(self, "Success", "Order paid successfully!")
                    # Only clear the order after payment
                    self.current_order_id = None
                    self.order_table.setRowCount(0)
                    self.total_label.setText("Total: €0.00")
                else:
                    QMessageBox.warning(self, "Error", "Failed to update order status!")
            else:
                QMessageBox.warning(self, "Error", "Failed to save transaction!")
    
    def delete_order(self):
        if not self.current_order_id:
            QMessageBox.warning(self, "Error", "No active order!")
            return
            
        reply = QMessageBox.question(self, "Confirm Delete", 
                                   "Are you sure you want to delete this order?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if self.db.update_order_status(self.current_order_id, "deleted"):
                QMessageBox.information(self, "Success", "Order deleted successfully!")
                self.current_order_id = None
                self.order_table.setRowCount(0)
                self.total_label.setText("Total: €0.00")
            else:
                QMessageBox.warning(self, "Error", "Failed to delete order!")
    
    def load_existing_order(self):
        """Load existing order for the table if any"""
        existing_order_id = self.db.get_active_order_for_table(self.table_number)
        if existing_order_id:
            self.current_order_id = existing_order_id
            self.update_order_table()
            # Disable confirm button if order is already confirmed
            order_details = self.db.get_order_details(existing_order_id)
            if order_details and order_details[2] == "confirmed":
                self.confirm_btn.setEnabled(False)
                self.confirm_btn.setText("Order Confirmed")
    
    def exit_menu(self):
        """Handle exit button click"""
        if self.current_order_id:
            reply = QMessageBox.question(
                self, 
                "Confirm Exit",
                "There is an active order. Are you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        pos_logger.log_audit(
            user=f"{self.user_data[1]} (ID: {self.user_data[0]})",
            action="Exit Order Menu",
            details=f"Table: {self.table_number}"
        )
        self.accept()

    def add_drink_to_order(self, name, price):
        """Add a drink to the current order"""
        if not self.current_order_id:
            self.current_order_id = self.db.create_order(self.table_number, self.user_data[0])
        
        # Create a temporary menu item for the drink
        drink_item = (0, name, "Dranken", price, "")  # (id, name, category, price, description)
        if self.db.add_item_to_order(self.current_order_id, 0, 1):  # Using 0 as temporary ID
            self.update_order_table()
            pos_logger.log_audit(
                user=f"{self.user_data[1]} (ID: {self.user_data[0]})",
                action="Add Drink to Order",
                details=f"Drink: {name}, Price: €{price:.2f}"
            )
        else:
            QMessageBox.warning(self, "Error", "Failed to add drink to order!") 