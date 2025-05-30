import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

class POSLogger:
    def __init__(self):
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        # Set up the logger
        self.logger = logging.getLogger('POS_System')
        self.logger.setLevel(logging.INFO)
        
        # Create formatters
        general_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        audit_formatter = logging.Formatter(
            '%(asctime)s - User: %(user)s - Action: %(action)s - Details: %(details)s'
        )
        
        # Set up file handler for general logs
        general_handler = RotatingFileHandler(
            'logs/pos_system.log',
            maxBytes=1024*1024,  # 1MB
            backupCount=5
        )
        general_handler.setFormatter(general_formatter)
        
        # Set up file handler for audit logs
        audit_handler = RotatingFileHandler(
            'logs/audit.log',
            maxBytes=1024*1024,  # 1MB
            backupCount=5
        )
        audit_handler.setFormatter(audit_formatter)
        
        # Add handlers to logger
        self.logger.addHandler(general_handler)
        self.logger.addHandler(audit_handler)
    
    def log_info(self, message):
        """Log general information"""
        self.logger.info(message, extra={'user': 'SYSTEM', 'action': 'INFO', 'details': ''})
    
    def log_error(self, message):
        """Log error messages"""
        self.logger.error(message, extra={'user': 'SYSTEM', 'action': 'ERROR', 'details': ''})
    
    def log_warning(self, message):
        """Log warning messages"""
        self.logger.warning(message, extra={'user': 'SYSTEM', 'action': 'WARNING', 'details': ''})
    
    def log_audit(self, user, action, details=""):
        """Log audit events with user information"""
        self.logger.info(
            "Audit Event",
            extra={
                'user': user,
                'action': action,
                'details': details
            }
        )

# Create a singleton instance
pos_logger = POSLogger() 