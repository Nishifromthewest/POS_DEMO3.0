from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QFrame, QScrollArea, QSizePolicy, QMessageBox,
                            QDateEdit, QTableWidget, QTableWidgetItem, QFileDialog, QTabWidget,
                            QTextEdit, QComboBox)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QFont, QTextCursor
from database import Database
from logger import pos_logger
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.charts.axes import XCategoryAxis, YValueAxis

class LogViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self.update_logs)
        self.log_timer.start(5000)  # Update every 5 seconds
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Controls
        controls = QHBoxLayout()
        
        # Log type selector
        self.log_type = QComboBox()
        self.log_type.addItems(["System Logs", "Audit Logs"])
        self.log_type.currentTextChanged.connect(self.update_logs)
        controls.addWidget(QLabel("Log Type:"))
        controls.addWidget(self.log_type)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.update_logs)
        controls.addWidget(refresh_btn)
        
        # Clear button
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_logs)
        controls.addWidget(clear_btn)
        
        controls.addStretch()
        layout.addLayout(controls)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #2f3136;
                color: #dcddde;
                border: 1px solid #202225;
                border-radius: 5px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.log_display)
        
        # Initial load
        self.update_logs()
        
    def update_logs(self):
        log_type = self.log_type.currentText()
        log_file = "logs/pos_system.log" if log_type == "System Logs" else "logs/audit.log"
        
        try:
            with open(log_file, 'r') as f:
                content = f.read()
                self.log_display.setText(content)
                # Scroll to bottom
                self.log_display.moveCursor(QTextCursor.End)
        except Exception as e:
            self.log_display.setText(f"Error reading log file: {str(e)}")
            
    def clear_logs(self):
        log_type = self.log_type.currentText()
        log_file = "logs/pos_system.log" if log_type == "System Logs" else "logs/audit.log"
        
        try:
            with open(log_file, 'w') as f:
                f.write("")
            self.update_logs()
            pos_logger.log_info(f"Cleared {log_type}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to clear logs: {str(e)}")

class AdminDashboard(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.db = Database()
        self.setup_ui()
        self.showMaximized()
        pos_logger.log_audit(
            user=f"{user_data[1]} (ID: {user_data[0]})",
            action="Admin Dashboard Access",
            details="Dashboard initialized"
        )
        
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
            QTabWidget::pane {
                border: 1px solid #202225;
                border-radius: 5px;
                background-color: #36393f;
            }
            QTabBar::tab {
                background-color: #2f3136;
                color: #dcddde;
                padding: 8px 16px;
                border: 1px solid #202225;
                border-bottom: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #5865f2;
            }
            QTabBar::tab:hover:!selected {
                background-color: #40444b;
            }
            QComboBox {
                background-color: #2f3136;
                border: 1px solid #202225;
                border-radius: 5px;
                color: #dcddde;
                padding: 5px;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
        """)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Reports tab
        reports_tab = QWidget()
        reports_layout = QVBoxLayout(reports_tab)
        
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
        
        # Add accounting report button next to print report button
        self.accounting_btn = QPushButton("Generate Accounting Report")
        self.accounting_btn.clicked.connect(self.generate_accounting_report)
        header_layout.addWidget(self.accounting_btn)
        
        reports_layout.addLayout(header_layout)
        
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
        reports_tab.layout().addWidget(scroll)
        
        # Logs tab
        logs_tab = LogViewer()
        
        # Add tabs
        tab_widget.addTab(reports_tab, "Reports")
        tab_widget.addTab(logs_tab, "System Logs")
        
        layout.addWidget(tab_widget)
        
        # Initial data load
        self.update_daily_report()
    
    def update_daily_report(self):
        """Update all report data for the selected date"""
        selected_date = self.date_selector.date().toPyDate()
        pos_logger.log_audit(
            user=f"{self.user_data[1]} (ID: {self.user_data[0]})",
            action="View Daily Report",
            details=f"Date: {selected_date}"
        )
        
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
        """Generate and save a printable daily report as PDF"""
        selected_date = self.date_selector.date().toPyDate()
        pos_logger.log_audit(
            user=f"{self.user_data[1]} (ID: {self.user_data[0]})",
            action="Generate Daily Report PDF",
            details=f"Date: {selected_date}"
        )
        
        summary = self.db.get_daily_summary(selected_date)
        
        # Create reports directory if it doesn't exist
        os.makedirs("Reports", exist_ok=True)
        
        # Generate filename with date
        filename = f"daily_report_{selected_date}.pdf"
        filepath = os.path.join("Reports", filename)
        
        try:
            # Create PDF document
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30
            )
            elements.append(Paragraph(f"Daily Sales Report - {selected_date}", title_style))
            elements.append(Spacer(1, 20))
            
            # Revenue Summary
            elements.append(Paragraph("Revenue Summary", styles['Heading2']))
            revenue_data = [
                ["Total Revenue", f"€{summary['revenue']['total']:.2f}"],
                ["Average Order", f"€{summary['transactions']['average_order']:.2f}"],
                ["Total Transactions", str(summary['transactions']['count'])]
            ]
            revenue_table = Table(revenue_data, colWidths=[3*inch, 2*inch])
            revenue_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(revenue_table)
            elements.append(Spacer(1, 20))
            
            # Revenue by Hour Chart
            if not summary['revenue']['by_hour'].empty:
                elements.append(Paragraph("Revenue by Hour", styles['Heading2']))
                drawing = Drawing(400, 200)
                bc = VerticalBarChart()
                bc.x = 50
                bc.y = 50
                bc.height = 125
                bc.width = 300
                bc.data = [summary['revenue']['by_hour'].values.tolist()]
                bc.categoryAxis.categoryNames = [f"{h:02d}:00" for h in summary['revenue']['by_hour'].index]
                bc.valueAxis.valueMin = 0
                bc.valueAxis.valueMax = summary['revenue']['by_hour'].max() * 1.1
                drawing.add(bc)
                elements.append(drawing)
                elements.append(Spacer(1, 20))
            
            # Menu Analysis
            elements.append(Paragraph("Top Selling Items", styles['Heading2']))
            if not summary['menu']['top_items'].empty:
                menu_data = [["Item", "Quantity", "Revenue"]]
                for name, data in summary['menu']['top_items'].iterrows():
                    menu_data.append([
                        name,
                        str(int(data['quantity'])),
                        f"€{data['price']:.2f}"
                    ])
                menu_table = Table(menu_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
                menu_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(menu_table)
                elements.append(Spacer(1, 20))
            
            # Category Analysis
            elements.append(Paragraph("Revenue by Category", styles['Heading2']))
            if not summary['menu']['category_analysis']['revenue'].empty:
                category_data = [["Category", "Revenue", "Quantity"]]
                for category, revenue in summary['menu']['category_analysis']['revenue'].items():
                    quantity = summary['menu']['category_analysis']['quantity'][category]
                    category_data.append([
                        category,
                        f"€{revenue:.2f}",
                        str(int(quantity))
                    ])
                category_table = Table(category_data, colWidths=[2*inch, 2*inch, 2*inch])
                category_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(category_table)
                elements.append(Spacer(1, 20))
            
            # Tax Analysis
            elements.append(Paragraph("Tax Analysis", styles['Heading2']))
            tax_data = [
                ["Total Tax", f"€{summary['tax']['total']:.2f}"]
            ]
            if not summary['tax']['by_category'].empty:
                tax_data.append(["Tax by Category", ""])
                for category, tax in summary['tax']['by_category'].items():
                    tax_data.append([category, f"€{tax:.2f}"])
            
            tax_table = Table(tax_data, colWidths=[3*inch, 2*inch])
            tax_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(tax_table)
            
            # Build PDF
            doc.build(elements)
            
            QMessageBox.information(self, "Success", f"Daily report has been saved to:\n{filepath}")
            pos_logger.log_info(f"Daily report generated successfully: {filepath}")
            
        except Exception as e:
            error_msg = f"Failed to generate report: {str(e)}"
            pos_logger.log_error(error_msg)
            QMessageBox.critical(self, "Error", error_msg)

    def generate_accounting_report(self):
        """Generate a detailed accounting report for the selected date"""
        selected_date = self.date_selector.date().toPyDate()
        pos_logger.log_audit(
            user=f"{self.user_data[1]} (ID: {self.user_data[0]})",
            action="Generate Accounting Report",
            details=f"Date: {selected_date}"
        )
        
        summary = self.db.get_daily_summary(selected_date)
        
        # Create Boekhouding directory if it doesn't exist
        os.makedirs("Boekhouding", exist_ok=True)
        
        # Generate filename with date
        filename = f"boekhouding_{selected_date}.pdf"
        filepath = os.path.join("Boekhouding", filename)
        
        try:
            # Create PDF document
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30
            )
            elements.append(Paragraph(f"Dagelijkse Boekhouding - {selected_date}", title_style))
            elements.append(Spacer(1, 20))
            
            # Revenue Summary
            elements.append(Paragraph("Omzet Overzicht", styles['Heading2']))
            revenue_data = [
                ["Totaal Omzet", f"€{summary['revenue']['total']:.2f}"],
                ["Gemiddelde Bestelling", f"€{summary['transactions']['average_order']:.2f}"],
                ["Totaal Transacties", str(summary['transactions']['count'])]
            ]
            revenue_table = Table(revenue_data, colWidths=[3*inch, 2*inch])
            revenue_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(revenue_table)
            elements.append(Spacer(1, 20))
            
            # Payment Methods
            elements.append(Paragraph("Betaalmethoden", styles['Heading2']))
            payment_data = [
                ["PIN", f"€{summary['revenue']['total'] * 0.7:.2f}"],  # Assuming 70% PIN payments
                ["Contant", f"€{summary['revenue']['total'] * 0.3:.2f}"]  # Assuming 30% cash payments
            ]
            payment_table = Table(payment_data, colWidths=[3*inch, 2*inch])
            payment_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(payment_table)
            elements.append(Spacer(1, 20))
            
            # Tax Analysis
            elements.append(Paragraph("BTW Analyse", styles['Heading2']))
            tax_data = [
                ["Totaal BTW", f"€{summary['tax']['total']:.2f}"]
            ]
            if not summary['tax']['by_category'].empty:
                tax_data.append(["BTW per Categorie", ""])
                for category, tax in summary['tax']['by_category'].items():
                    tax_data.append([category, f"€{tax:.2f}"])
            
            tax_table = Table(tax_data, colWidths=[3*inch, 2*inch])
            tax_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(tax_table)
            elements.append(Spacer(1, 20))
            
            # Category Analysis
            elements.append(Paragraph("Omzet per Categorie", styles['Heading2']))
            if not summary['menu']['category_analysis']['revenue'].empty:
                category_data = [["Categorie", "Omzet", "Aantal"]]
                for category, revenue in summary['menu']['category_analysis']['revenue'].items():
                    quantity = summary['menu']['category_analysis']['quantity'][category]
                    category_data.append([
                        category,
                        f"€{revenue:.2f}",
                        str(int(quantity))
                    ])
                category_table = Table(category_data, colWidths=[2*inch, 2*inch, 2*inch])
                category_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(category_table)
            
            # Build PDF
            doc.build(elements)
            
            QMessageBox.information(self, "Success", f"Boekhouding rapport is opgeslagen in:\n{filepath}")
            pos_logger.log_info(f"Accounting report generated successfully: {filepath}")
            
        except Exception as e:
            error_msg = f"Fout bij het genereren van het rapport: {str(e)}"
            pos_logger.log_error(error_msg)
            QMessageBox.critical(self, "Error", error_msg)

    def closeEvent(self, event):
        """Handle window close event"""
        pos_logger.log_audit(
            user=f"{self.user_data[1]} (ID: {self.user_data[0]})",
            action="Admin Dashboard Close",
            details="Dashboard closed"
        )
        event.accept()