from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QFrame, QScrollArea, QSizePolicy, QMessageBox,
                            QDateEdit, QTableWidget, QTableWidgetItem, QFileDialog)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from database import Database
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import os
import csv

class AdminDashboard(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.db = Database()
        self.setup_ui()
        self.showMaximized()
        
    def setup_ui(self):
        self.setWindowTitle("Admin Dashboard - Reports")
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
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #202225;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QPushButton {
                background-color: #5865f2;
                border: none;
                border-radius: 5px;
                color: #ffffff;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4752c4;
            }
        """)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title and date selection
        header_layout = QHBoxLayout()
        title = QLabel("Daily Reports")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        header_layout.addWidget(title)
        
        # Date selector
        self.date_selector = QDateEdit()
        self.date_selector.setDate(QDate.currentDate())
        self.date_selector.setCalendarPopup(True)
        self.date_selector.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.date_selector.setMinimumWidth(150)
        self.date_selector.setStyleSheet("""
            QDateEdit {
                background-color: #2f3136;
                border: 1px solid #202225;
                border-radius: 5px;
                color: #dcddde;
                padding: 8px;
                font-size: 14px;
            }
        """)
        self.date_selector.dateChanged.connect(self.update_daily_report)
        header_layout.addWidget(self.date_selector)
        
        # Add print report button
        self.print_btn = QPushButton("Print Daily Report")
        self.print_btn.clicked.connect(self.print_daily_report)
        header_layout.addWidget(self.print_btn)
        
        layout.addLayout(header_layout)
        
        # Create scroll area for reports
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #36393f;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #2f3136;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #202225;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        reports_widget = QWidget()
        reports_layout = QVBoxLayout(reports_widget)
        reports_layout.setSpacing(30)
        reports_layout.setContentsMargins(10, 10, 10, 10)
        
        # Revenue Overview with Chart
        revenue_frame = QFrame()
        revenue_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        revenue_frame.setStyleSheet("""
            QFrame {
                background-color: #2f3136;
                border-radius: 15px;
                padding: 25px;
            }
        """)
        revenue_layout = QVBoxLayout(revenue_frame)
        revenue_layout.setSpacing(15)
        
        revenue_title = QLabel("Revenue Overview")
        revenue_title.setFont(QFont("Arial", 18, QFont.Bold))
        revenue_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        revenue_layout.addWidget(revenue_title)
        
        # Revenue stats
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(30)
        
        total_revenue_container = QFrame()
        total_revenue_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        total_revenue_container.setStyleSheet("""
            QFrame {
                background-color: #40444b;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        total_revenue_layout = QVBoxLayout(total_revenue_container)
        total_revenue_label = QLabel("Total Revenue")
        total_revenue_label.setFont(QFont("Arial", 12))
        self.total_revenue_label = QLabel("€0.00")
        self.total_revenue_label.setFont(QFont("Arial", 24, QFont.Bold))
        total_revenue_layout.addWidget(total_revenue_label)
        total_revenue_layout.addWidget(self.total_revenue_label)
        
        avg_order_container = QFrame()
        avg_order_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        avg_order_container.setStyleSheet("""
            QFrame {
                background-color: #40444b;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        avg_order_layout = QVBoxLayout(avg_order_container)
        avg_order_label = QLabel("Average Order")
        avg_order_label.setFont(QFont("Arial", 12))
        self.avg_order_label = QLabel("€0.00")
        self.avg_order_label.setFont(QFont("Arial", 24, QFont.Bold))
        avg_order_layout.addWidget(avg_order_label)
        avg_order_layout.addWidget(self.avg_order_label)
        
        stats_layout.addWidget(total_revenue_container)
        stats_layout.addWidget(avg_order_container)
        revenue_layout.addLayout(stats_layout)
        
        # Revenue chart
        self.revenue_figure = Figure(figsize=(10, 5), facecolor='#2f3136')
        self.revenue_canvas = FigureCanvas(self.revenue_figure)
        self.revenue_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        revenue_layout.addWidget(self.revenue_canvas)
        
        reports_layout.addWidget(revenue_frame)
        
        # Transaction Analysis
        transaction_frame = QFrame()
        transaction_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        transaction_frame.setStyleSheet("""
            QFrame {
                background-color: #2f3136;
                border-radius: 15px;
                padding: 25px;
            }
        """)
        transaction_layout = QVBoxLayout(transaction_frame)
        transaction_layout.setSpacing(15)
        
        transaction_title = QLabel("Transaction Analysis")
        transaction_title.setFont(QFont("Arial", 18, QFont.Bold))
        transaction_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        transaction_layout.addWidget(transaction_title)
        
        # Transaction stats
        transaction_stats = QFrame()
        transaction_stats.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        transaction_stats.setStyleSheet("""
            QFrame {
                background-color: #40444b;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        transaction_stats_layout = QVBoxLayout(transaction_stats)
        transaction_count_label = QLabel("Total Transactions")
        transaction_count_label.setFont(QFont("Arial", 12))
        self.transaction_count_label = QLabel("0")
        self.transaction_count_label.setFont(QFont("Arial", 24, QFont.Bold))
        transaction_stats_layout.addWidget(transaction_count_label)
        transaction_stats_layout.addWidget(self.transaction_count_label)
        transaction_layout.addWidget(transaction_stats)
        
        # Transaction chart
        self.transaction_figure = Figure(figsize=(10, 5), facecolor='#2f3136')
        self.transaction_canvas = FigureCanvas(self.transaction_figure)
        self.transaction_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        transaction_layout.addWidget(self.transaction_canvas)
        
        reports_layout.addWidget(transaction_frame)
        
        # Menu Analysis
        menu_frame = QFrame()
        menu_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        menu_frame.setStyleSheet("""
            QFrame {
                background-color: #2f3136;
                border-radius: 15px;
                padding: 25px;
            }
        """)
        menu_layout = QVBoxLayout(menu_frame)
        menu_layout.setSpacing(15)
        
        menu_title = QLabel("Menu Analysis")
        menu_title.setFont(QFont("Arial", 18, QFont.Bold))
        menu_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        menu_layout.addWidget(menu_title)
        
        # Top items table
        self.top_items_table = QTableWidget()
        self.top_items_table.setColumnCount(3)
        self.top_items_table.setHorizontalHeaderLabels(["Item", "Quantity", "Revenue"])
        self.top_items_table.horizontalHeader().setStretchLastSection(True)
        self.top_items_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.top_items_table.setStyleSheet("""
            QTableWidget {
                background-color: #40444b;
                border: none;
                border-radius: 10px;
                gridline-color: #2f3136;
            }
            QHeaderView::section {
                background-color: #2f3136;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        menu_layout.addWidget(self.top_items_table)
        
        # Menu chart
        self.menu_figure = Figure(figsize=(10, 5), facecolor='#2f3136')
        self.menu_canvas = FigureCanvas(self.menu_figure)
        self.menu_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        menu_layout.addWidget(self.menu_canvas)
        
        reports_layout.addWidget(menu_frame)
        
        # Tax Analysis
        tax_frame = QFrame()
        tax_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        tax_frame.setStyleSheet("""
            QFrame {
                background-color: #2f3136;
                border-radius: 15px;
                padding: 25px;
            }
        """)
        tax_layout = QVBoxLayout(tax_frame)
        tax_layout.setSpacing(15)
        
        tax_title = QLabel("Tax Analysis")
        tax_title.setFont(QFont("Arial", 18, QFont.Bold))
        tax_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        tax_layout.addWidget(tax_title)
        
        # Tax stats
        tax_stats = QFrame()
        tax_stats.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        tax_stats.setStyleSheet("""
            QFrame {
                background-color: #40444b;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        tax_stats_layout = QVBoxLayout(tax_stats)
        tax_total_label = QLabel("Total Tax")
        tax_total_label.setFont(QFont("Arial", 12))
        self.total_tax_label = QLabel("€0.00")
        self.total_tax_label.setFont(QFont("Arial", 24, QFont.Bold))
        tax_stats_layout.addWidget(tax_total_label)
        tax_stats_layout.addWidget(self.total_tax_label)
        tax_layout.addWidget(tax_stats)
        
        # Tax chart
        self.tax_figure = Figure(figsize=(10, 5), facecolor='#2f3136')
        self.tax_canvas = FigureCanvas(self.tax_figure)
        self.tax_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        tax_layout.addWidget(self.tax_canvas)
        
        reports_layout.addWidget(tax_frame)
        
        scroll.setWidget(reports_widget)
        layout.addWidget(scroll)
        
        # Initial data load
        self.update_daily_report()
    
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
        if not summary['revenue']['by_hour'].empty:
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
        if not summary['transactions']['hourly_distribution'].empty:
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
            self.top_items_table.setItem(i, 2, QTableWidgetItem(f"€{data['price']:.2f}"))
        
        # Plot category analysis
        self.menu_figure.clear()
        ax = self.menu_figure.add_subplot(111)
        if not summary['menu']['category_analysis']['revenue'].empty:
            summary['menu']['category_analysis']['revenue'].plot(kind='pie', ax=ax, autopct='%1.1f%%')
        ax.set_title('Revenue by Category')
        ax.set_facecolor('#2f3136')
        self.menu_canvas.draw()
        
        # Update Tax Analysis
        self.total_tax_label.setText(f"€{summary['tax']['total']:.2f}")
        
        # Plot tax by category
        self.tax_figure.clear()
        ax = self.tax_figure.add_subplot(111)
        if not summary['tax']['by_category'].empty:
            summary['tax']['by_category'].plot(kind='bar', ax=ax, color='#5865f2')
        ax.set_title('Tax by Category')
        ax.set_xlabel('Category')
        ax.set_ylabel('Tax Amount (€)')
        ax.set_facecolor('#2f3136')
        ax.tick_params(colors='#dcddde')
        self.tax_canvas.draw()
    
    def print_daily_report(self):
        """Generate and save a printable daily report"""
        selected_date = self.date_selector.date().toPyDate()
        summary = self.db.get_daily_summary(selected_date)
        
        # Create reports directory if it doesn't exist
        os.makedirs("Reports", exist_ok=True)
        
        # Generate filename with date
        filename = f"daily_report_{selected_date}.csv"
        filepath = os.path.join("Reports", filename)
        
        try:
            with open(filepath, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(["Daily Sales Report"])
                writer.writerow([f"Date: {selected_date}"])
                writer.writerow([])
                
                # Revenue Summary
                writer.writerow(["Revenue Summary"])
                writer.writerow(["Total Revenue", f"€{summary['revenue']['total']:.2f}"])
                writer.writerow(["Average Order", f"€{summary['transactions']['average_order']:.2f}"])
                writer.writerow(["Total Transactions", str(summary['transactions']['count'])])
                writer.writerow([])
                
                # Revenue by Hour
                writer.writerow(["Revenue by Hour"])
                writer.writerow(["Hour", "Amount"])
                if not summary['revenue']['by_hour'].empty:
                    for hour, amount in summary['revenue']['by_hour'].items():
                        writer.writerow([f"{hour:02d}:00", f"€{amount:.2f}"])
                writer.writerow([])
                
                # Menu Analysis
                writer.writerow(["Top Selling Items"])
                writer.writerow(["Item", "Quantity", "Revenue"])
                if not summary['menu']['top_items'].empty:
                    for name, data in summary['menu']['top_items'].iterrows():
                        writer.writerow([name, str(int(data['quantity'])), f"€{data['price']:.2f}"])
                writer.writerow([])
                
                # Category Analysis
                writer.writerow(["Revenue by Category"])
                writer.writerow(["Category", "Revenue", "Quantity"])
                if not summary['menu']['category_analysis']['revenue'].empty:
                    for category, revenue in summary['menu']['category_analysis']['revenue'].items():
                        quantity = summary['menu']['category_analysis']['quantity'][category]
                        writer.writerow([category, f"€{revenue:.2f}", str(int(quantity))])
                writer.writerow([])
                
                # Tax Analysis
                writer.writerow(["Tax Analysis"])
                writer.writerow(["Total Tax", f"€{summary['tax']['total']:.2f}"])
                writer.writerow([])
                writer.writerow(["Tax by Category"])
                writer.writerow(["Category", "Tax Amount"])
                if not summary['tax']['by_category'].empty:
                    for category, tax in summary['tax']['by_category'].items():
                        writer.writerow([category, f"€{tax:.2f}"])
                
            QMessageBox.information(self, "Success", f"Daily report has been saved to:\n{filepath}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")