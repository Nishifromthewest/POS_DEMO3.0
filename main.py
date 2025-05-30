from PyQt5.QtWidgets import QApplication
from login import LoginScreen
from tablemanager import RestaurantView
from admin_dashboard import AdminDashboard
import sys

class POSSystem:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login_screen = LoginScreen()
        self.login_screen.login_successful.connect(self.handle_login)
        
    def handle_login(self, user_data):
        # user_data contains (id, name, role)
        if user_data[2] == 'admin':
            # Show admin dashboard for admin users
            self.admin_dashboard = AdminDashboard(user_data)
            self.admin_dashboard.show()
        else:
            # Show restaurant view for staff users
            self.restaurant_view = RestaurantView(user_data)
            self.restaurant_view.show()
        
        # Close login screen
        self.login_screen.close()
    
    def run(self):
        self.login_screen.show()
        return self.app.exec_()

if __name__ == '__main__':
    pos = POSSystem()
    sys.exit(pos.run()) 