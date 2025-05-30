from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QLineEdit, QTabWidget, QWidget, QGridLayout,
                            QMessageBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import csv
from datetime import datetime
import os

class PaymentWindow(QDialog):
    def __init__(self, total_amount, parent=None):
        super().__init__(parent)
        self.total_amount = total_amount
        self.parent = parent  # Store parent reference to access order details
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Payment")
        self.setMinimumSize(600, 400)
        
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
            QLineEdit, QDoubleSpinBox {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 10px;
                color: #ffffff;
                font-size: 16px;
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
        
        # Total amount display
        total_label = QLabel(f"Total Amount: €{self.total_amount:.2f}")
        total_label.setFont(QFont("Arial", 20, QFont.Bold))
        total_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(total_label)
        
        # Payment methods tabs
        self.tabs = QTabWidget()
        self.setup_payment_tabs()
        layout.addWidget(self.tabs)
        
        # Tip section
        tip_layout = QHBoxLayout()
        tip_label = QLabel("Tip Amount:")
        self.tip_input = QDoubleSpinBox()
        self.tip_input.setRange(0, 1000)
        self.tip_input.setDecimals(2)
        self.tip_input.setSuffix(" €")
        self.tip_input.setValue(0)
        
        tip_layout.addWidget(tip_label)
        tip_layout.addWidget(self.tip_input)
        layout.addLayout(tip_layout)
        
        # Final amount display
        self.final_amount_label = QLabel(f"Final Amount (with tip): €{self.total_amount:.2f}")
        self.final_amount_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.final_amount_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.final_amount_label)
        
        # Connect tip input to update final amount
        self.tip_input.valueChanged.connect(self.update_final_amount)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        self.process_btn = QPushButton("Process Payment")
        self.cancel_btn = QPushButton("Cancel")
        
        self.process_btn.clicked.connect(self.process_payment)
        self.cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.process_btn)
        buttons_layout.addWidget(self.cancel_btn)
        layout.addLayout(buttons_layout)
        
    def setup_payment_tabs(self):
        # Cash payment tab
        cash_tab = QWidget()
        cash_layout = QVBoxLayout(cash_tab)
        
        # Amount received input
        received_layout = QHBoxLayout()
        received_label = QLabel("Amount Received:")
        self.cash_received = QDoubleSpinBox()
        self.cash_received.setRange(0, 10000)
        self.cash_received.setDecimals(2)
        self.cash_received.setSuffix(" €")
        self.cash_received.setValue(self.total_amount)
        self.cash_received.valueChanged.connect(self.update_change)
        
        received_layout.addWidget(received_label)
        received_layout.addWidget(self.cash_received)
        cash_layout.addLayout(received_layout)
        
        # Change display
        self.change_label = QLabel("Change: €0.00")
        self.change_label.setFont(QFont("Arial", 16))
        cash_layout.addWidget(self.change_label)
        
        self.tabs.addTab(cash_tab, "Cash")
        
        # PIN payment tab
        pin_tab = QWidget()
        pin_layout = QVBoxLayout(pin_tab)
        
        # Simple PIN payment info
        pin_info = QLabel("Payment will be processed via PIN terminal")
        pin_info.setFont(QFont("Arial", 16))
        pin_info.setAlignment(Qt.AlignCenter)
        pin_layout.addWidget(pin_info)
        
        self.tabs.addTab(pin_tab, "PIN")
        
        # Split payment tab
        split_tab = QWidget()
        split_layout = QVBoxLayout(split_tab)
        
        # Number of ways to split
        split_ways_layout = QHBoxLayout()
        split_ways_label = QLabel("Split into:")
        self.split_ways = QDoubleSpinBox()
        self.split_ways.setRange(2, 10)
        self.split_ways.setValue(2)
        self.split_ways.valueChanged.connect(self.update_split_amount)
        
        split_ways_layout.addWidget(split_ways_label)
        split_ways_layout.addWidget(self.split_ways)
        split_layout.addLayout(split_ways_layout)
        
        # Amount per person
        self.split_amount_label = QLabel(f"Amount per person: €{self.total_amount/2:.2f}")
        self.split_amount_label.setFont(QFont("Arial", 16))
        split_layout.addWidget(self.split_amount_label)
        
        self.tabs.addTab(split_tab, "Split")
        
    def update_change(self):
        received = self.cash_received.value()
        change = received - (self.total_amount + self.tip_input.value())
        self.change_label.setText(f"Change: €{change:.2f}")
        
    def update_final_amount(self):
        final_amount = self.total_amount + self.tip_input.value()
        self.final_amount_label.setText(f"Final Amount (with tip): €{final_amount:.2f}")
        self.update_change()
        
    def update_split_amount(self):
        ways = self.split_ways.value()
        amount_per_person = (self.total_amount + self.tip_input.value()) / ways
        self.split_amount_label.setText(f"Amount per person: €{amount_per_person:.2f}")
        
    def generate_bill_csv(self):
        """Generate a CSV bill/receipt for the payment"""
        try:
            # Get order details from parent (OrderMenu)
            order_id = self.parent.current_order_id
            table_number = self.parent.table_number
            user_name = self.parent.user_data[1]  # Name of user who took the order
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bill_table{table_number}_{timestamp}.csv"
            filepath = os.path.join("Bills", filename)
            
            # Get order items from parent's database
            items = self.parent.db.get_order_items(order_id)
            
            # Write to CSV
            with open(filepath, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                # Write header
                writer.writerow(['Restaurant Bill'])
                writer.writerow([''])
                writer.writerow([f'Table Number: {table_number}'])
                writer.writerow([f'Order Taken By: {user_name}'])
                writer.writerow([f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
                writer.writerow([''])
                
                # Write items
                writer.writerow(['Item', 'Quantity', 'Price', 'Total'])
                for item in items:
                    name, quantity, price = item
                    total = quantity * price
                    writer.writerow([name, quantity, f'€{price:.2f}', f'€{total:.2f}'])
                
                # Write totals
                writer.writerow([''])
                writer.writerow(['Subtotal', '', '', f'€{self.total_amount:.2f}'])
                writer.writerow(['Tip', '', '', f'€{self.tip_input.value():.2f}'])
                writer.writerow(['Total', '', '', f'€{(self.total_amount + self.tip_input.value()):.2f}'])
                
                # Write payment details
                writer.writerow([''])
                writer.writerow(['Payment Details'])
                writer.writerow([f'Payment Method: {self.payment_result["method"].upper()}'])
                if self.payment_result["method"] == "cash":
                    writer.writerow([f'Amount Received: €{self.cash_received.value():.2f}'])
                    writer.writerow([f'Change: €{(self.cash_received.value() - (self.total_amount + self.tip_input.value())):.2f}'])
                elif self.payment_result["method"] == "split":
                    writer.writerow([f'Split into: {self.split_ways.value()} ways'])
                    writer.writerow([f'Amount per person: €{((self.total_amount + self.tip_input.value()) / self.split_ways.value()):.2f}'])
                
                writer.writerow([''])
                writer.writerow(['Thank you for your business!'])
            
            return filepath
        except Exception as e:
            print(f"Error generating bill: {str(e)}")
            return None

    def process_payment(self):
        current_tab = self.tabs.currentWidget()
        payment_method = ""
        
        if current_tab == self.tabs.widget(0):  # Cash
            received = self.cash_received.value()
            if received < (self.total_amount + self.tip_input.value()):
                QMessageBox.warning(self, "Error", "Insufficient amount received!")
                return
            payment_method = "cash"
            QMessageBox.information(self, "Success", "Cash payment processed successfully!")
            
        elif current_tab == self.tabs.widget(1):  # PIN
            payment_method = "pin"
            QMessageBox.information(self, "Success", "PIN payment processed successfully!")
            
        elif current_tab == self.tabs.widget(2):  # Split
            payment_method = "split"
            QMessageBox.information(self, "Success", f"Split payment processed for {self.split_ways.value()} ways!")
        
        # Return payment details
        self.payment_result = {
            'method': payment_method,
            'amount': self.total_amount,
            'tip': self.tip_input.value()
        }
        
        # Generate bill
        bill_file = self.generate_bill_csv()
        if bill_file:
            QMessageBox.information(self, "Bill Generated", f"Bill has been saved to {bill_file}")
        
        self.accept() 