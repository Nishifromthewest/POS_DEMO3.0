from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QStackedWidget, QTableWidget, 
                            QTableWidgetItem, QFrame, QScrollArea, QSizePolicy, QMessageBox,
                            QDateEdit, QComboBox)
from PyQt5.QtCore import Qt, QSize, QDate
from PyQt5.QtGui import QFont, QIcon, QColor
from database import Database
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class SidebarButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.setMinimumHeight(50)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2f3136;
                border: none;
                border-radius: 5px;
                color: #dcddde;
                text-align: left;
                padding: 10px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #36393f;
            }
            QPushButton:checked {
                background-color: #40444b;
            }
        """)
        self.setCheckable(True)

class AdminDashboard(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.db = Database()
        self.setup_ui()
        self.showMaximized()
        
    def setup_ui(self):
        self.setWindowTitle("Admin Dashboard")
        self.setStyleSheet("""
            QMainWindow {
                background-color: #36393f;
            }
            QWidget {
                background-color: #36393f;
                color: #dcddde;
            }
            QLabel {
                color: #dcddde;
                font-size: 14px;
            }
            QTableWidget {
                background-color: #2f3136;
                border: 1px solid #202225;
                border-radius: 5px;
                gridline-color: #202225;
                color: #dcddde;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #40444b;
            }
            QHeaderView::section {
                background-color: #2f3136;
                color: #dcddde;
                padding: 5px;
                border: 1px solid #202225;
            }
            QScrollArea {
                border: none;
                background-color: #36393f;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #2f3136;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #202225;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #2f3136;
                border-right: 1px solid #202225;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(5)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add user info at top of sidebar
        user_info = QLabel(f"Welcome, {self.user_data[1]}")
        user_info.setFont(QFont("Arial", 12, QFont.Bold))
        user_info.setStyleSheet("color: #ffffff; padding: 10px;")
        sidebar_layout.addWidget(user_info)
        
        # Add role info
        role_info = QLabel(f"Role: {self.user_data[2].capitalize()}")
        role_info.setFont(QFont("Arial", 10))
        role_info.setStyleSheet("color: #888888; padding: 5px 10px;")
        sidebar_layout.addWidget(role_info)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #202225;")
        sidebar_layout.addWidget(separator)
        
        # Add navigation buttons
        self.overview_btn = SidebarButton("Overview")
        self.orders_btn = SidebarButton("Orders")
        self.users_btn = SidebarButton("Users")
        self.menu_btn = SidebarButton("Menu Management")
        self.reports_btn = SidebarButton("Reports")
        
        sidebar_layout.addWidget(self.overview_btn)
        sidebar_layout.addWidget(self.orders_btn)
        sidebar_layout.addWidget(self.users_btn)
        sidebar_layout.addWidget(self.menu_btn)
        sidebar_layout.addWidget(self.reports_btn)
        
        # Add view switcher button for admins
        if self.user_data[2] == 'admin':
            self.view_switcher_btn = QPushButton("Switch to Restaurant View")
            self.view_switcher_btn.setStyleSheet("""
                QPushButton {
                    background-color: #5865f2;
                    border: none;
                    border-radius: 5px;
                    color: #ffffff;
                    text-align: center;
                    padding: 10px;
                    font-size: 14px;
                    margin-top: 20px;
                }
                QPushButton:hover {
                    background-color: #4752c4;
                }
            """)
            self.view_switcher_btn.clicked.connect(self.switch_to_restaurant_view)
            sidebar_layout.addWidget(self.view_switcher_btn)
        
        # Add logout button
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #ed4245;
                border: none;
                border-radius: 5px;
                color: #ffffff;
                text-align: center;
                padding: 10px;
                font-size: 14px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #c03537;
            }
        """)
        self.logout_btn.clicked.connect(self.logout)
        sidebar_layout.addWidget(self.logout_btn)
        
        # Add stretch to push buttons to top
        sidebar_layout.addStretch()
        
        # Create main content area
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet("""
            QStackedWidget {
                background-color: #36393f;
            }
        """)
        
        # Create pages
        self.overview_page = self.create_overview_page()
        self.orders_page = self.create_orders_page()
        self.users_page = self.create_users_page()
        self.menu_page = self.create_menu_page()
        self.reports_page = self.create_reports_page()
        
        # Add pages to stacked widget
        self.content_area.addWidget(self.overview_page)
        self.content_area.addWidget(self.orders_page)
        self.content_area.addWidget(self.users_page)
        self.content_area.addWidget(self.menu_page)
        self.content_area.addWidget(self.reports_page)
        
        # Connect buttons to page switching
        self.overview_btn.clicked.connect(lambda: self.switch_page(0))
        self.orders_btn.clicked.connect(lambda: self.switch_page(1))
        self.users_btn.clicked.connect(lambda: self.switch_page(2))
        self.menu_btn.clicked.connect(lambda: self.switch_page(3))
        self.reports_btn.clicked.connect(lambda: self.switch_page(4))
        
        # Add widgets to main layout
        layout.addWidget(sidebar)
        layout.addWidget(self.content_area)
        
        # Set initial page
        self.overview_btn.setChecked(True)
        self.switch_page(0)
    
    def switch_to_restaurant_view(self):
        """Switch to restaurant view while maintaining admin session"""
        from tablemanager import RestaurantView
        self.restaurant_view = RestaurantView(self.user_data)
        self.restaurant_view.show()
        self.hide()  # Hide instead of close to maintain session
    
    def logout(self):
        """Handle logout"""
        from login import LoginScreen
        self.login_screen = LoginScreen()
        self.login_screen.show()
        self.close()
    
    def closeEvent(self, event):
        """Handle window close event"""
        # If closing admin dashboard, show login screen
        if hasattr(self, 'restaurant_view') and self.restaurant_view.isVisible():
            event.accept()
        else:
            from login import LoginScreen
            self.login_screen = LoginScreen()
            self.login_screen.show()
            event.accept()
    
    def verify_admin_access(self):
        """Verify that the user still has admin access"""
        if not self.db.verify_user(self.user_data[1], self.user_data[3])[2] == 'admin':
            QMessageBox.warning(self, "Access Denied", "Your admin privileges have been revoked!")
            self.logout()
            return False
        return True
    
    def switch_page(self, index):
        """Switch pages with admin verification"""
        if not self.verify_admin_access():
            return
        self.content_area.setCurrentIndex(index)
        # Update button states
        for btn in [self.overview_btn, self.orders_btn, self.users_btn, 
                   self.menu_btn, self.reports_btn]:
            btn.setChecked(btn == self.content_area.currentWidget().property("button"))
    
    def create_overview_page(self):
        page = QWidget()
        page.setProperty("button", self.overview_btn)
        layout = QVBoxLayout(page)
        
        # Add overview content
        title = QLabel("Dashboard Overview")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(title)
        
        # Add some statistics widgets here
        stats_layout = QHBoxLayout()
        
        # Total Orders Today
        orders_frame = QFrame()
        orders_frame.setStyleSheet("""
            QFrame {
                background-color: #2f3136;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        orders_layout = QVBoxLayout(orders_frame)
        orders_title = QLabel("Total Orders Today")
        orders_title.setFont(QFont("Arial", 14, QFont.Bold))
        orders_count = QLabel("0")  # TODO: Get actual count
        orders_count.setFont(QFont("Arial", 24, QFont.Bold))
        orders_layout.addWidget(orders_title)
        orders_layout.addWidget(orders_count)
        
        # Total Revenue Today
        revenue_frame = QFrame()
        revenue_frame.setStyleSheet("""
            QFrame {
                background-color: #2f3136;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        revenue_layout = QVBoxLayout(revenue_frame)
        revenue_title = QLabel("Total Revenue Today")
        revenue_title.setFont(QFont("Arial", 14, QFont.Bold))
        revenue_amount = QLabel("€0.00")  # TODO: Get actual amount
        revenue_amount.setFont(QFont("Arial", 24, QFont.Bold))
        revenue_layout.addWidget(revenue_title)
        revenue_layout.addWidget(revenue_amount)
        
        stats_layout.addWidget(orders_frame)
        stats_layout.addWidget(revenue_frame)
        layout.addLayout(stats_layout)
        
        # Add recent activity table
        recent_activity = QLabel("Recent Activity")
        recent_activity.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(recent_activity)
        
        activity_table = QTableWidget()
        activity_table.setColumnCount(4)
        activity_table.setHorizontalHeaderLabels(["Time", "Table", "Action", "User"])
        activity_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(activity_table)
        
        return page
    
    def create_orders_page(self):
        page = QWidget()
        page.setProperty("button", self.orders_btn)
        layout = QVBoxLayout(page)
        
        title = QLabel("Order Management")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(title)
        
        # Add orders table
        orders_table = QTableWidget()
        orders_table.setColumnCount(5)
        orders_table.setHorizontalHeaderLabels(["Order ID", "Table", "Status", "Time", "User"])
        orders_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(orders_table)
        
        return page
    
    def create_users_page(self):
        page = QWidget()
        page.setProperty("button", self.users_btn)
        layout = QVBoxLayout(page)
        
        title = QLabel("User Management")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(title)
        
        # Add users table
        users_table = QTableWidget()
        users_table.setColumnCount(4)
        users_table.setHorizontalHeaderLabels(["ID", "Name", "Role", "Actions"])
        users_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(users_table)
        
        return page
    
    def create_menu_page(self):
        page = QWidget()
        page.setProperty("button", self.menu_btn)
        layout = QVBoxLayout(page)
        
        title = QLabel("Menu Management")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(title)
        
        # Add menu items table
        menu_table = QTableWidget()
        menu_table.setColumnCount(5)
        menu_table.setHorizontalHeaderLabels(["ID", "Name", "Category", "Price", "Actions"])
        menu_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(menu_table)
        
        return page
    
    def create_reports_page(self):
        page = QWidget()
        page.setProperty("button", self.reports_btn)
        layout = QVBoxLayout(page)
        
        # Title and date selection
        header_layout = QHBoxLayout()
        title = QLabel("Daily Reports")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        header_layout.addWidget(title)
        
        # Date selector
        self.date_selector = QDateEdit()
        self.date_selector.setDate(QDate.currentDate())
        self.date_selector.setCalendarPopup(True)
        self.date_selector.setStyleSheet("""
            QDateEdit {
                background-color: #2f3136;
                border: 1px solid #202225;
                border-radius: 5px;
                color: #dcddde;
                padding: 5px;
            }
        """)
        self.date_selector.dateChanged.connect(self.update_daily_report)
        header_layout.addWidget(self.date_selector)
        
        layout.addLayout(header_layout)
        
        # Create scroll area for reports
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #36393f;
            }
        """)
        
        reports_widget = QWidget()
        reports_layout = QVBoxLayout(reports_widget)
        
        # Revenue Overview with Chart
        revenue_frame = QFrame()
        revenue_frame.setStyleSheet("""
            QFrame {
                background-color: #2f3136;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        revenue_layout = QVBoxLayout(revenue_frame)
        
        revenue_title = QLabel("Revenue Overview")
        revenue_title.setFont(QFont("Arial", 14, QFont.Bold))
        revenue_layout.addWidget(revenue_title)
        
        # Revenue stats
        stats_layout = QHBoxLayout()
        self.total_revenue_label = QLabel("€0.00")
        self.total_revenue_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.avg_order_label = QLabel("€0.00")
        self.avg_order_label.setFont(QFont("Arial", 24, QFont.Bold))
        
        stats_layout.addWidget(QLabel("Total Revenue:"))
        stats_layout.addWidget(self.total_revenue_label)
        stats_layout.addWidget(QLabel("Average Order:"))
        stats_layout.addWidget(self.avg_order_label)
        revenue_layout.addLayout(stats_layout)
        
        # Revenue chart
        self.revenue_figure = Figure(figsize=(8, 4), facecolor='#2f3136')
        self.revenue_canvas = FigureCanvas(self.revenue_figure)
        revenue_layout.addWidget(self.revenue_canvas)
        
        reports_layout.addWidget(revenue_frame)
        
        # Transaction Analysis
        transaction_frame = QFrame()
        transaction_frame.setStyleSheet("""
            QFrame {
                background-color: #2f3136;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        transaction_layout = QVBoxLayout(transaction_frame)
        
        transaction_title = QLabel("Transaction Analysis")
        transaction_title.setFont(QFont("Arial", 14, QFont.Bold))
        transaction_layout.addWidget(transaction_title)
        
        # Transaction stats
        self.transaction_count_label = QLabel("0")
        self.transaction_count_label.setFont(QFont("Arial", 24, QFont.Bold))
        transaction_layout.addWidget(QLabel("Total Transactions:"))
        transaction_layout.addWidget(self.transaction_count_label)
        
        # Transaction chart
        self.transaction_figure = Figure(figsize=(8, 4), facecolor='#2f3136')
        self.transaction_canvas = FigureCanvas(self.transaction_figure)
        transaction_layout.addWidget(self.transaction_canvas)
        
        reports_layout.addWidget(transaction_frame)
        
        # Menu Analysis
        menu_frame = QFrame()
        menu_frame.setStyleSheet("""
            QFrame {
                background-color: #2f3136;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        menu_layout = QVBoxLayout(menu_frame)
        
        menu_title = QLabel("Menu Analysis")
        menu_title.setFont(QFont("Arial", 14, QFont.Bold))
        menu_layout.addWidget(menu_title)
        
        # Top items table
        self.top_items_table = QTableWidget()
        self.top_items_table.setColumnCount(3)
        self.top_items_table.setHorizontalHeaderLabels(["Item", "Quantity", "Revenue"])
        self.top_items_table.horizontalHeader().setStretchLastSection(True)
        menu_layout.addWidget(self.top_items_table)
        
        # Menu chart
        self.menu_figure = Figure(figsize=(8, 4), facecolor='#2f3136')
        self.menu_canvas = FigureCanvas(self.menu_figure)
        menu_layout.addWidget(self.menu_canvas)
        
        reports_layout.addWidget(menu_frame)
        
        # Tax Analysis
        tax_frame = QFrame()
        tax_frame.setStyleSheet("""
            QFrame {
                background-color: #2f3136;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        tax_layout = QVBoxLayout(tax_frame)
        
        tax_title = QLabel("Tax Analysis")
        tax_title.setFont(QFont("Arial", 14, QFont.Bold))
        tax_layout.addWidget(tax_title)
        
        # Tax stats
        self.total_tax_label = QLabel("€0.00")
        self.total_tax_label.setFont(QFont("Arial", 24, QFont.Bold))
        tax_layout.addWidget(QLabel("Total Tax:"))
        tax_layout.addWidget(self.total_tax_label)
        
        # Tax chart
        self.tax_figure = Figure(figsize=(8, 4), facecolor='#2f3136')
        self.tax_canvas = FigureCanvas(self.tax_figure)
        tax_layout.addWidget(self.tax_canvas)
        
        reports_layout.addWidget(tax_frame)
        
        # Add stretch to push everything to the top
        reports_layout.addStretch()
        
        scroll.setWidget(reports_widget)
        layout.addWidget(scroll)
        
        # Initial data load
        self.update_daily_report()
        
        return page
    
    def update_daily_report(self):
        """Update all report data for the selected date"""
        selected_date = self.date_selector.date().toPyDate()
        db = Database()
        summary = db.get_daily_summary(selected_date)
        
        # Update Revenue Overview
        self.total_revenue_label.setText(f"€{summary['revenue']['total']:.2f}")
        self.avg_order_label.setText(f"€{summary['transactions']['average_order']:.2f}")
        
        # Plot revenue by hour
        self.revenue_figure.clear()
        ax = self.revenue_figure.add_subplot(111)
        summary['revenue']['by_hour'].plot(kind='bar', ax=ax, color='#5865f2')
        ax.set_title('Revenue by Hour')
        ax.set_xlabel('Hour')
        ax.set_ylabel('Revenue (€)')
        ax.set_facecolor('#2f3136')
        ax.tick_params(colors='#dcddde')
        self.revenue_canvas.draw()
        
        # Update Transaction Analysis
        self.transaction_count_label.setText(str(summary['transactions']['count']))
        
        # Plot transaction distribution
        self.transaction_figure.clear()
        ax = self.transaction_figure.add_subplot(111)
        summary['transactions']['hourly_distribution'].plot(kind='line', ax=ax, color='#5865f2')
        ax.set_title('Transactions by Hour')
        ax.set_xlabel('Hour')
        ax.set_ylabel('Number of Transactions')
        ax.set_facecolor('#2f3136')
        ax.tick_params(colors='#dcddde')
        self.transaction_canvas.draw()
        
        # Update Menu Analysis
        top_items = summary['menu']['top_items']
        self.top_items_table.setRowCount(len(top_items))
        for i, (name, data) in enumerate(top_items.iterrows()):
            self.top_items_table.setItem(i, 0, QTableWidgetItem(name))
            self.top_items_table.setItem(i, 1, QTableWidgetItem(str(int(data['quantity']))))
            self.top_items_table.setItem(i, 2, QTableWidgetItem(f"€{data['revenue']:.2f}"))
        
        # Plot category analysis
        self.menu_figure.clear()
        ax = self.menu_figure.add_subplot(111)
        summary['menu']['category_analysis']['revenue'].plot(kind='pie', ax=ax, autopct='%1.1f%%')
        ax.set_title('Revenue by Category')
        ax.set_facecolor('#2f3136')
        self.menu_canvas.draw()
        
        # Update Tax Analysis
        self.total_tax_label.setText(f"€{summary['tax']['total']:.2f}")
        
        # Plot tax by category
        self.tax_figure.clear()
        ax = self.tax_figure.add_subplot(111)
        summary['tax']['by_category'].plot(kind='bar', ax=ax, color='#5865f2')
        ax.set_title('Tax by Category')
        ax.set_xlabel('Category')
        ax.set_ylabel('Tax Amount (€)')
        ax.set_facecolor('#2f3136')
        ax.tick_params(colors='#dcddde')
        self.tax_canvas.draw() 