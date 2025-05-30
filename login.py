import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                            QTableWidget, QTableWidgetItem, QComboBox,
                            QMessageBox, QDialog, QFormLayout, QGridLayout,
                            QFrame)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap
from database import Database
from tablemanager import RestaurantView
from admin_dashboard import AdminDashboard
from logger import pos_logger
import re

class PinDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter PIN")
        self.setFixedSize(300, 150)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        layout = QVBoxLayout()
        
        # PIN input field
        self.pin_input = QLineEdit()
        self.pin_input.setEchoMode(QLineEdit.Password)
        self.pin_input.setMaxLength(4)
        self.pin_input.setAlignment(Qt.AlignCenter)
        self.pin_input.setFont(QFont("Arial", 14))
        self.pin_input.textChanged.connect(self.verify_pin)
        
        # Add to layout
        layout.addWidget(QLabel("Enter PIN:"))
        layout.addWidget(self.pin_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

    def verify_pin(self):
        """Verify if PIN is exactly 4 digits"""
        pin = self.pin_input.text()
        if not pin.isdigit() or len(pin) != 4:
            self.pin_input.setStyleSheet("background-color: #ffebee;")
            return False
        self.pin_input.setStyleSheet("")
        return True

    def get_pin(self):
        return self.pin_input.text()

class UserBox(QFrame):
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            UserBox {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 10px;
            }
            UserBox:hover {
                background-color: #3d3d3d;
                border: 1px solid #4d4d4d;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # User icon (first letter of name)
        icon = QLabel(self.user_data[1][0].upper())
        icon.setFont(QFont("Arial", 32, QFont.Bold))
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("color: #ffffff;")
        layout.addWidget(icon)
        
        # User name
        name = QLabel(self.user_data[1])
        name.setFont(QFont("Arial", 14))
        name.setAlignment(Qt.AlignCenter)
        name.setStyleSheet("color: #ffffff;")
        layout.addWidget(name)
        
        # Role
        role = QLabel(self.user_data[2].capitalize())
        role.setFont(QFont("Arial", 10))
        role.setAlignment(Qt.AlignCenter)
        role.setStyleSheet("color: #888888;")
        layout.addWidget(role)
        
        self.setFixedSize(150, 200)
        self.setCursor(Qt.PointingHandCursor)

class LoginScreen(QMainWindow):
    login_successful = pyqtSignal(tuple)  # Signal to emit user data on successful login
    
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.current_user = None
        self.setup_ui()
        self.showMaximized()  # Show maximized by default
        
    def setup_ui(self):
        self.setWindowTitle("POS System - Login")
        self.setMinimumSize(800, 600)
        
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
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Welcome to POS System")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # User grid
        self.user_grid = QGridLayout()
        self.user_grid.setSpacing(20)
        self.user_grid.setAlignment(Qt.AlignCenter)
        
        # Add user boxes
        self.add_user_boxes()
        
        layout.addLayout(self.user_grid)
        
        # Admin controls
        admin_controls = QHBoxLayout()
        self.add_user_btn = QPushButton("Add User")
        self.add_user_btn.setFixedWidth(200)
        self.add_user_btn.clicked.connect(self.add_user)
        
        admin_controls.addWidget(self.add_user_btn)
        layout.addLayout(admin_controls)
        
    def add_user_boxes(self):
        # Clear existing boxes
        while self.user_grid.count():
            item = self.user_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add new boxes
        users = self.db.get_all_users()
        for i, user in enumerate(users):
            box = UserBox(user, self)
            box.mousePressEvent = lambda e, u=user: self.user_selected(u)
            self.user_grid.addWidget(box, i // 4, i % 4)
            
    def user_selected(self, user_data):
        dialog = PinDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            pin = dialog.get_pin()
            if not pin.isdigit() or len(pin) != 4:
                QMessageBox.warning(self, "Error", "PIN must be exactly 4 digits")
                pos_logger.log_failed_login(user_data[1], "127.0.0.1")  # Log failed attempt
                return
                
            user = self.db.verify_user(user_data[1], pin)
            if user:
                pos_logger.log_audit(user[1], "login", "Successful login")
                self.current_user = user
                if user[2] == "admin":
                    self.show_user_management()
                else:
                    self.show_restaurant_view()
            else:
                QMessageBox.warning(self, "Error", "Invalid PIN")
                pos_logger.log_failed_login(user_data[1], "127.0.0.1")  # Log failed attempt
                
    def show_user_management(self):
        self.admin_dashboard = AdminDashboard(self.current_user)
        self.admin_dashboard.show()
        self.close()
        
    def show_restaurant_view(self):
        self.restaurant_view = RestaurantView(self.current_user)
        self.restaurant_view.show()
        self.close()
        
    def add_user(self):
        # Check if current user is admin
        current_user = self.db.get_all_users()[0]  # Assuming first user is admin
        if current_user[2] != "admin":
            QMessageBox.warning(self, "Error", "Only admin can add users")
            return
            
        # Create dialog for new user
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New User")
        dialog.setFixedSize(300, 200)
        
        layout = QVBoxLayout()
        
        # Username input
        username_input = QLineEdit()
        username_input.setPlaceholderText("Username")
        layout.addWidget(username_input)
        
        # Role selection
        role_input = QLineEdit()
        role_input.setPlaceholderText("Role (admin/staff)")
        layout.addWidget(role_input)
        
        # PIN input
        pin_input = QLineEdit()
        pin_input.setPlaceholderText("PIN (4 digits)")
        pin_input.setEchoMode(QLineEdit.Password)
        pin_input.setMaxLength(4)
        layout.addWidget(pin_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("Add")
        cancel_button = QPushButton("Cancel")
        
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            username = username_input.text()
            role = role_input.text().lower()
            pin = pin_input.text()
            
            # Validate inputs
            if not username or not role or not pin:
                QMessageBox.warning(self, "Error", "All fields are required")
                return
                
            if role not in ["admin", "staff"]:
                QMessageBox.warning(self, "Error", "Role must be 'admin' or 'staff'")
                return
                
            if not pin.isdigit() or len(pin) != 4:
                QMessageBox.warning(self, "Error", "PIN must be exactly 4 digits")
                return
                
            # Validate username format
            if not re.match("^[a-zA-Z0-9_]+$", username):
                QMessageBox.warning(self, "Error", "Username can only contain letters, numbers, and underscores")
                return
            
            # Add user to database
            if self.db.add_user(username, role, pin):
                QMessageBox.information(self, "Success", "User added successfully")
                pos_logger.log_audit(current_user[1], "add_user", f"Added new user: {username}")
                self.setup_ui()  # Refresh the UI
            else:
                QMessageBox.warning(self, "Error", "Failed to add user. Username might already exist.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginScreen()
    window.show()
    sys.exit(app.exec_()) 