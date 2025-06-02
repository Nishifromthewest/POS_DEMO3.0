import logging
import os
from datetime import datetime
import json
import traceback
import sys

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
        error_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - File: %(filename)s - Line: %(lineno)d - Function: %(funcName)s - Error: %(message)s\nStack Trace: %(stack_trace)s'
        )
        performance_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - Operation: %(operation)s - Duration: %(duration)s - Details: %(details)s'
        )

        # Create handlers
        system_handler = logging.FileHandler('logs/system.log')
        system_handler.setFormatter(system_formatter)

        audit_handler = logging.FileHandler('logs/audit.log')
        audit_handler.setFormatter(audit_formatter)

        security_handler = logging.FileHandler('logs/security.log')
        security_handler.setFormatter(security_formatter)

        error_handler = logging.FileHandler('logs/error.log')
        error_handler.setFormatter(error_formatter)

        performance_handler = logging.FileHandler('logs/performance.log')
        performance_handler.setFormatter(performance_formatter)

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

        self.error_logger = logging.getLogger('error')
        self.error_logger.setLevel(logging.ERROR)
        self.error_logger.addHandler(error_handler)

        self.performance_logger = logging.getLogger('performance')
        self.performance_logger.setLevel(logging.INFO)
        self.performance_logger.addHandler(performance_handler)

    def log_info(self, message: str):
        """Log general system information"""
        self.system_logger.info(message)

    def log_error(self, message: str, exc_info=None):
        """Log system errors with stack trace"""
        if exc_info:
            stack_trace = ''.join(traceback.format_exception(*exc_info))
        else:
            stack_trace = ''.join(traceback.format_stack())
        
        self.error_logger.error(
            message,
            extra={
                'stack_trace': stack_trace
            }
        )

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

    def log_performance(self, operation: str, duration: float, details: str = ""):
        """Log performance metrics"""
        self.performance_logger.info(
            "",
            extra={
                'operation': operation,
                'duration': f"{duration:.2f}s",
                'details': details
            }
        )

    def log_database_operation(self, operation: str, table: str, details: str = ""):
        """Log database operations"""
        self.system_logger.info(
            f"Database {operation} on table {table}",
            extra={'details': details}
        )

    def log_api_call(self, endpoint: str, method: str, status: int, duration: float):
        """Log API calls"""
        self.performance_logger.info(
            "",
            extra={
                'operation': f"API {method} {endpoint}",
                'duration': f"{duration:.2f}s",
                'details': f"Status: {status}"
            }
        )

    def log_file_operation(self, operation: str, filename: str, details: str = ""):
        """Log file operations"""
        self.system_logger.info(
            f"File {operation}: {filename}",
            extra={'details': details}
        )

    def log_config_change(self, setting: str, old_value: str, new_value: str):
        """Log configuration changes"""
        self.audit_logger.info(
            "",
            extra={
                'user': 'system',
                'action': 'config_change',
                'details': f"Changed {setting} from {old_value} to {new_value}"
            }
        )

# Create singleton instance
pos_logger = POSLogger() 