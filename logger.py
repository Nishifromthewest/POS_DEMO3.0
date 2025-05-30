import logging
import os
from datetime import datetime
import json

class POSLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(POSLogger, cls).__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance

    def _initialize_logger(self):
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)

        # Create formatters
        system_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        audit_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - User: %(user)s - Action: %(action)s - Details: %(details)s'
        )
        security_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - Event: %(event)s - Details: %(details)s - IP: %(ip)s'
        )

        # Create handlers
        system_handler = logging.FileHandler('logs/system.log')
        system_handler.setFormatter(system_formatter)

        audit_handler = logging.FileHandler('logs/audit.log')
        audit_handler.setFormatter(audit_formatter)

        security_handler = logging.FileHandler('logs/security.log')
        security_handler.setFormatter(security_formatter)

        # Create loggers
        self.system_logger = logging.getLogger('system')
        self.system_logger.setLevel(logging.INFO)
        self.system_logger.addHandler(system_handler)

        self.audit_logger = logging.getLogger('audit')
        self.audit_logger.setLevel(logging.INFO)
        self.audit_logger.addHandler(audit_handler)

        self.security_logger = logging.getLogger('security')
        self.security_logger.setLevel(logging.INFO)
        self.security_logger.addHandler(security_handler)

    def log_info(self, message: str):
        """Log general system information"""
        self.system_logger.info(message)

    def log_error(self, message: str):
        """Log system errors"""
        self.system_logger.error(message)

    def log_warning(self, message: str):
        """Log system warnings"""
        self.system_logger.warning(message)

    def log_audit(self, user: str, action: str, details: str = ""):
        """Log user actions for audit purposes"""
        self.audit_logger.info(
            "",
            extra={
                'user': user,
                'action': action,
                'details': details
            }
        )

    def log_failed_login(self, username: str, ip: str):
        """Log failed login attempts"""
        self.security_logger.warning(
            "",
            extra={
                'event': 'failed_login',
                'details': f"Failed login attempt for user: {username}",
                'ip': ip
            }
        )

    def log_account_locked(self, username: str, ip: str):
        """Log account lockout events"""
        self.security_logger.warning(
            "",
            extra={
                'event': 'account_locked',
                'details': f"Account locked for user: {username}",
                'ip': ip
            }
        )

    def log_suspicious_activity(self, event: str, details: str, ip: str):
        """Log suspicious activities"""
        self.security_logger.warning(
            "",
            extra={
                'event': event,
                'details': details,
                'ip': ip
            }
        )

# Create singleton instance
pos_logger = POSLogger() 