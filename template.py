import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QGridLayout, 
                            QFrame, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor

class POSSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("POS System")
        self.setMinimumSize(1200, 800)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 10px;
                color: #ffffff;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            QPushButton:pressed {
                background-color: #4d4d4d;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QFrame {
                border: 1px solid #3d3d3d;
                border-radius: 5px;
            }
        """)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left panel for categories and products
        left_panel = QFrame()
        left_layout = QVBoxLayout(left_panel)
        
        # Categories section
        categories_label = QLabel("Categories")
        categories_label.setFont(QFont("Arial", 16, QFont.Bold))
        left_layout.addWidget(categories_label)
        
        categories_grid = QGridLayout()
        categories = ["Food", "Drinks", "Snacks", "Desserts"]
        for i, category in enumerate(categories):
            btn = QPushButton(category)
            categories_grid.addWidget(btn, i // 2, i % 2)
        left_layout.addLayout(categories_grid)
        
        # Products section
        products_label = QLabel("Products")
        products_label.setFont(QFont("Arial", 16, QFont.Bold))
        left_layout.addWidget(products_label)
        
        products_scroll = QScrollArea()
        products_widget = QWidget()
        products_layout = QGridLayout(products_widget)
        
        # Sample products
        products = ["Product 1", "Product 2", "Product 3", "Product 4", 
                   "Product 5", "Product 6", "Product 7", "Product 8"]
        for i, product in enumerate(products):
            btn = QPushButton(product)
            products_layout.addWidget(btn, i // 2, i % 2)
        
        products_scroll.setWidget(products_widget)
        products_scroll.setWidgetResizable(True)
        left_layout.addWidget(products_scroll)
        
        # Right panel for current order
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        
        # Order section
        order_label = QLabel("Current Order")
        order_label.setFont(QFont("Arial", 16, QFont.Bold))
        right_layout.addWidget(order_label)
        
        # Order items area
        order_items = QScrollArea()
        order_widget = QWidget()
        order_items_layout = QVBoxLayout(order_widget)
        order_items.setWidget(order_widget)
        order_items.setWidgetResizable(True)
        right_layout.addWidget(order_items)
        
        # Total and payment section
        total_frame = QFrame()
        total_layout = QVBoxLayout(total_frame)
        
        total_label = QLabel("Total: €0.00")
        total_label.setFont(QFont("Arial", 20, QFont.Bold))
        total_layout.addWidget(total_label)
        
        payment_buttons = QHBoxLayout()
        pay_button = QPushButton("Pay")
        pay_button.setMinimumHeight(50)
        cancel_button = QPushButton("Cancel")
        cancel_button.setMinimumHeight(50)
        payment_buttons.addWidget(pay_button)
        payment_buttons.addWidget(cancel_button)
        total_layout.addLayout(payment_buttons)
        
        right_layout.addWidget(total_frame)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel, 2)
        main_layout.addWidget(right_panel, 1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = POSSystem()
    window.show()
    sys.exit(app.exec_()) 