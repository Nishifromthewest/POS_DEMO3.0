from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QTableWidget, QTableWidgetItem, QComboBox,
                            QSpinBox, QMessageBox, QTabWidget, QWidget, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from database import Database
from paymentwindow import PaymentWindow

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
        
        self.confirm_btn.clicked.connect(self.confirm_order)
        self.pay_btn.clicked.connect(self.pay_order)
        self.delete_btn.clicked.connect(self.delete_order)
        
        buttons_layout.addWidget(self.confirm_btn)
        buttons_layout.addWidget(self.pay_btn)
        buttons_layout.addWidget(self.delete_btn)
        
        layout.addLayout(buttons_layout)
        
    def setup_menu_tabs(self):
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