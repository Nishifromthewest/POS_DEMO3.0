import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                            QTableWidget, QTableWidgetItem, QComboBox,
                            QMessageBox, QDialog, QFormLayout, QGridLayout,
                            QFrame)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from database import Database
from tablemanager import RestaurantView

class PinDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Enter PIN for {username}")
        self.setMinimumWidth(300)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #ffffff;
                font-size: 16px;
            }
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 10px;
                color: #ffffff;
                font-size: 20px;
                text-align: center;
            }
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 10px;
                color: #ffffff;
                font-size: 14px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # PIN input
        self.pin_input = QLineEdit()
        self.pin_input.setEchoMode(QLineEdit.Password)
        self.pin_input.setMaxLength(4)
        self.pin_input.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.pin_input)
        
        # Number pad
        numpad = QGridLayout()
        numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'C', '0', 'OK']
        
        for i, num in enumerate(numbers):
            btn = QPushButton(num)
            if num == 'C':
                btn.clicked.connect(self.clear_pin)
            elif num == 'OK':
                btn.clicked.connect(self.accept)
            else:
                btn.clicked.connect(lambda checked, n=num: self.add_digit(n))
            numpad.addWidget(btn, i // 3, i % 3)
        
        layout.addLayout(numpad)
        
    def add_digit(self, digit):
        current = self.pin_input.text()
        if len(current) < 4:
            self.pin_input.setText(current + digit)
            
    def clear_pin(self):
        self.pin_input.clear()
        
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
        title = QLabel("Select User")
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
        add_user_btn = QPushButton("Add User")
        remove_user_btn = QPushButton("Remove User")
        
        add_user_btn.clicked.connect(self.add_user)
        remove_user_btn.clicked.connect(self.remove_user)
        
        admin_controls.addWidget(add_user_btn)
        admin_controls.addWidget(remove_user_btn)
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
        dialog = PinDialog(user_data[1], self)
        if dialog.exec_() == QDialog.Accepted:
            pin = dialog.get_pin()
            if self.db.verify_user(user_data[1], pin):
                self.current_user = user_data
                if user_data[2] == "admin":
                    self.show_user_management()
                else:
                    self.show_restaurant_view()
            else:
                QMessageBox.warning(self, "Error", "Invalid PIN!")
                
    def show_user_management(self):
        # TODO: Show user management interface
        QMessageBox.information(self, "Success", "Admin login successful!")
        
    def show_restaurant_view(self):
        self.restaurant_view = RestaurantView(self.current_user)
        self.restaurant_view.show()
        self.close()
        
    def add_user(self):
        dialog = AddUserDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name = dialog.name_input.text()
            role = dialog.role_combo.currentText()
            pin = dialog.pin_input.text()
            
            if self.db.add_user(name, role, pin):
                self.add_user_boxes()
                QMessageBox.information(self, "Success", "User added successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to add user!")
                
    def remove_user(self):
        # TODO: Implement user removal interface
        QMessageBox.information(self, "Info", "User removal will be implemented")

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password!")
            return
            
        user_data = self.db.verify_user(username, password)
        if user_data:
            self.login_successful.emit(user_data)  # Emit signal with user data
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password!")

class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New User")
        self.setMinimumWidth(300)
        
        layout = QFormLayout(self)
        
        self.name_input = QLineEdit()
        self.role_combo = QComboBox()
        self.role_combo.addItems(["admin", "staff"])
        self.pin_input = QLineEdit()
        self.pin_input.setEchoMode(QLineEdit.Password)
        
        layout.addRow("Name:", self.name_input)
        layout.addRow("Role:", self.role_combo)
        layout.addRow("PIN:", self.pin_input)
        
        buttons = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow(buttons)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginScreen()
    window.show()
    sys.exit(app.exec_()) 