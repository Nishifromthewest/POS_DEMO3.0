from PyQt5.QtWidgets import QApplication
from login import LoginScreen
from tablemanager import RestaurantView
from admin_dashboard import AdminDashboard
from logger import pos_logger
import sys

class POSSystem:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login_screen = LoginScreen()
        self.login_screen.login_successful.connect(self.handle_login)
        pos_logger.log_info("POS System initialized")
        
    def handle_login(self, user_data):
        # user_data contains (id, name, role)
        user_id, user_name, role = user_data
        pos_logger.log_audit(
            user=f"{user_name} (ID: {user_id})",
            action="Login",
            details=f"Role: {role}"
        )
        
        if role == 'admin':
            # Show admin dashboard for admin users
            self.admin_dashboard = AdminDashboard(user_data)
            self.admin_dashboard.show()
            pos_logger.log_info(f"Admin dashboard opened for user: {user_name}")
        else:
            # Show restaurant view for staff users
            self.restaurant_view = RestaurantView(user_data)
            self.restaurant_view.show()
            pos_logger.log_info(f"Restaurant view opened for user: {user_name}")
        
        # Close login screen
        self.login_screen.close()
    
    def run(self):
        self.login_screen.show()
        pos_logger.log_info("POS System started")
        return self.app.exec_()

if __name__ == '__main__':
    try:
        pos = POSSystem()
        sys.exit(pos.run())
    except Exception as e:
        pos_logger.log_error(f"Critical error in POS System: {str(e)}")
        raise 