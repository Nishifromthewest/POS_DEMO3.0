import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFrame, QGridLayout, QMessageBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QBrush
from ordermenu import OrderMenu
from database import Database
from logger import POSLogger



logger = POSLogger()

class TableWidget(QFrame):
    def __init__(self, table_number, user_data, parent=None):
        super().__init__(parent)
        self.table_number = table_number
        self.user_data = user_data
        self.status = "empty"  # empty, occupied, reserved
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            TableWidget {
                background-color: #2d2d2d;
                border: 2px solid #3d3d3d;
                border-radius: 10px;
            }
            TableWidget:hover {
                border: 2px solid #4d4d4d;
            }
        """)
        
        self.setFixedSize(120, 120)
        self.setCursor(Qt.PointingHandCursor)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw table
        painter.setPen(QPen(QColor("#3d3d3d"), 2))
        painter.setBrush(QBrush(QColor("#2d2d2d")))
        painter.drawRoundedRect(10, 10, 100, 100, 10, 10)
        
        # Draw table number
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Arial", 16, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, f"Table {self.table_number}")
        
        # Draw status indicator
        status_color = {
            "empty": "#4CAF50",    # Green
            "occupied": "#f44336",  # Red
            "reserved": "#FFC107"   # Yellow
        }
        painter.setBrush(QBrush(QColor(status_color[self.status])))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(15, 15, 10, 10)
        
    def mousePressEvent(self, event):
        # Show order menu
        menu = OrderMenu(self.table_number, self.user_data, self)
        if menu.exec_() == OrderMenu.Accepted:
            # Update table status based on order status
            if menu.current_order_id:
                self.status = "occupied"
            else:
                self.status = "empty"
            self.update()

class RestaurantView(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.setup_ui()
        self.showMaximized()  # Show maximized by default
        
    def setup_ui(self):
        self.setWindowTitle("Restaurant View")
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
                border-radius: 10px;
                padding: 15px;
                color: #ffffff;
                font-size: 16px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            QLabel {
                color: #ffffff;
                font-size: 16px;
            }
        """)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add user info and controls at top
        top_bar = QHBoxLayout()
        
        # User info
        user_info = QLabel(f"Logged in as: {self.user_data[1]} ({self.user_data[2]})")
        user_info.setFont(QFont("Arial", 12))
        top_bar.addWidget(user_info)
        
        # Add admin controls if user is admin
        if self.user_data[2] == 'admin':
            admin_btn = QPushButton("Admin Dashboard")
            admin_btn.setStyleSheet("""
                QPushButton {
                    background-color: #5865f2;
                    border: none;
                    border-radius: 5px;
                    color: #ffffff;
                    text-align: center;
                    padding: 10px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #4752c4;
                }
            """)
            admin_btn.clicked.connect(self.switch_to_admin_dashboard)
            top_bar.addWidget(admin_btn)
        
        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #ed4245;
                border: none;
                border-radius: 5px;
                color: #ffffff;
                text-align: center;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c03537;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        top_bar.addWidget(logout_btn)
        
        layout.addLayout(top_bar)
        
        # Title
        title = QLabel("Restaurant Floor")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Legend
        legend = QWidget()
        legend_layout = QHBoxLayout(legend)
        legend_layout.setAlignment(Qt.AlignCenter)
        
        for status, color in [("Empty", "#4CAF50"), ("Occupied", "#f44336"), ("Reserved", "#FFC107")]:
            status_widget = QWidget()
            status_layout = QHBoxLayout(status_widget)
            
            indicator = QFrame()
            indicator.setFixedSize(15, 15)
            indicator.setStyleSheet(f"background-color: {color}; border-radius: 7px;")
            
            label = QLabel(status)
            label.setStyleSheet("color: #ffffff;")
            
            status_layout.addWidget(indicator)
            status_layout.addWidget(label)
            legend_layout.addWidget(status_widget)
        
        layout.addWidget(legend)
        
        # Tables layout
        tables_container = QWidget()
        tables_layout = QGridLayout(tables_container)
        tables_layout.setSpacing(30)
        
        # Create tables in a restaurant-like arrangement
        # Tables 1-4: Window side
        for i in range(4):
            table = TableWidget(i + 1, self.user_data)
            tables_layout.addWidget(table, 0, i)
            
        # Tables 5-6: Center
        for i in range(2):
            table = TableWidget(i + 5, self.user_data)
            tables_layout.addWidget(table, 1, i + 1)
            
        # Tables 7-10: Bar side
        for i in range(4):
            table = TableWidget(i + 7, self.user_data)
            tables_layout.addWidget(table, 2, i)
        
        layout.addWidget(tables_container)

    def switch_to_admin_dashboard(self):
        """Switch back to admin dashboard"""
        from admin_dashboard import AdminDashboard
        self.admin_dashboard = AdminDashboard(self.user_data)
        self.admin_dashboard.show()
        self.close()
    
    def logout(self):
        """Handle logout"""
        from login import LoginScreen
        self.login_screen = LoginScreen()
        self.login_screen.show()
        self.close()
    
    def closeEvent(self, event):
        """Handle window close event"""
        # If closing restaurant view, show login screen
        if not hasattr(self, 'admin_dashboard') or not self.admin_dashboard.isVisible():
            from login import LoginScreen
            self.login_screen = LoginScreen()
            self.login_screen.show()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # For testing purposes, create a dummy user
    user_data = (1, "Test User", "staff")
    window = RestaurantView(user_data)
    window.show()
    sys.exit(app.exec_()) 