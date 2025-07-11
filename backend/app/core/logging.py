"""
Logging Configuration - Smart Village Management System
"""
import logging
import logging.config
from typing import Dict, Any
from datetime import datetime
import json
import os


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'payment_id'):
            log_entry['payment_id'] = record.payment_id
        if hasattr(record, 'journal_entry_id'):
            log_entry['journal_entry_id'] = record.journal_entry_id
        if hasattr(record, 'action'):
            log_entry['action'] = record.action
        if hasattr(record, 'entity_type'):
            log_entry['entity_type'] = record.entity_type
        if hasattr(record, 'entity_id'):
            log_entry['entity_id'] = record.entity_id
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)


def setup_logging(log_level: str = "INFO", log_file: str = None) -> None:
    """Setup logging configuration"""
    
    # Create logs directory if it doesn't exist
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            },
            "json": {
                "()": JSONFormatter
            }
        },
        "handlers": {
            "console": {
                "level": log_level,
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "stream": "ext://sys.stdout"
            }
        },
        "loggers": {
            "app": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False
            },
            "app.services.accounting_service": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "app.services.payment_service": {
                "level": "INFO", 
                "handlers": ["console"],
                "propagate": False
            },
            "app.api": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            }
        },
        "root": {
            "level": log_level,
            "handlers": ["console"]
        }
    }
    
    # Add file handler if log_file is specified
    if log_file:
        config["handlers"]["file"] = {
            "level": log_level,
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json",
            "filename": log_file,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
        
        # Add file handler to all loggers
        for logger_name in config["loggers"]:
            config["loggers"][logger_name]["handlers"].append("file")
        config["root"]["handlers"].append("file")
    
    logging.config.dictConfig(config)


class AccountingLogger:
    """Specialized logger for accounting operations"""
    
    def __init__(self, name: str = "app.accounting"):
        self.logger = logging.getLogger(name)
    
    def log_journal_entry_created(self, journal_entry_id: str, user_id: int, entry_type: str, amount: float):
        """Log journal entry creation"""
        self.logger.info(
            f"Journal entry created: {journal_entry_id}",
            extra={
                "action": "CREATE_JOURNAL_ENTRY",
                "journal_entry_id": journal_entry_id,
                "user_id": user_id,
                "entity_type": "JOURNAL_ENTRY",
                "entity_id": journal_entry_id,
                "entry_type": entry_type,
                "amount": amount
            }
        )
    
    def log_journal_entry_posted(self, journal_entry_id: str, user_id: int):
        """Log journal entry posting"""
        self.logger.info(
            f"Journal entry posted: {journal_entry_id}",
            extra={
                "action": "POST_JOURNAL_ENTRY",
                "journal_entry_id": journal_entry_id,
                "user_id": user_id,
                "entity_type": "JOURNAL_ENTRY",
                "entity_id": journal_entry_id
            }
        )
    
    def log_payment_journal_entry(self, payment_id: str, journal_entry_id: str, user_id: int):
        """Log payment journal entry creation"""
        self.logger.info(
            f"Payment journal entry created: payment={payment_id}, journal={journal_entry_id}",
            extra={
                "action": "CREATE_PAYMENT_JOURNAL_ENTRY",
                "payment_id": payment_id,
                "journal_entry_id": journal_entry_id,
                "user_id": user_id,
                "entity_type": "PAYMENT",
                "entity_id": payment_id
            }
        )
    
    def log_spending_journal_entry(self, spending_id: str, journal_entry_id: str, user_id: int):
        """Log spending journal entry creation"""
        self.logger.info(
            f"Spending journal entry created: spending={spending_id}, journal={journal_entry_id}",
            extra={
                "action": "CREATE_SPENDING_JOURNAL_ENTRY",
                "spending_id": spending_id,
                "journal_entry_id": journal_entry_id,
                "user_id": user_id,
                "entity_type": "SPENDING",
                "entity_id": spending_id
            }
        )
    
    def log_period_closed(self, period_id: str, user_id: int):
        """Log accounting period closure"""
        self.logger.info(
            f"Accounting period closed: {period_id}",
            extra={
                "action": "CLOSE_ACCOUNTING_PERIOD",
                "period_id": period_id,
                "user_id": user_id,
                "entity_type": "ACCOUNTING_PERIOD",
                "entity_id": period_id
            }
        )
    
    def log_error(self, message: str, error: Exception, **kwargs):
        """Log accounting errors"""
        extra = {
            "action": "ERROR",
            "error_type": type(error).__name__,
            "error_message": str(error)
        }
        extra.update(kwargs)
        
        self.logger.error(message, extra=extra, exc_info=True)


class AuditLogger:
    """Audit trail logger for compliance and security"""
    
    def __init__(self, name: str = "app.audit"):
        self.logger = logging.getLogger(name)
    
    def log_user_action(self, user_id: int, action: str, entity_type: str, entity_id: str, details: Dict[str, Any] = None):
        """Log user actions for audit trail"""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "details": details or {}
        }
        
        self.logger.info(
            f"User action: {action} on {entity_type}:{entity_id}",
            extra=audit_entry
        )
    
    def log_payment_approval(self, user_id: int, payment_id: str, amount: float):
        """Log payment approval"""
        self.log_user_action(
            user_id=user_id,
            action="APPROVE_PAYMENT",
            entity_type="PAYMENT",
            entity_id=payment_id,
            details={"amount": amount}
        )
    
    def log_payment_rejection(self, user_id: int, payment_id: str, reason: str = None):
        """Log payment rejection"""
        self.log_user_action(
            user_id=user_id,
            action="REJECT_PAYMENT",
            entity_type="PAYMENT",
            entity_id=payment_id,
            details={"reason": reason}
        )
    
    def log_manual_journal_entry(self, user_id: int, journal_entry_id: str, amount: float):
        """Log manual journal entry creation"""
        self.log_user_action(
            user_id=user_id,
            action="CREATE_MANUAL_JOURNAL_ENTRY",
            entity_type="JOURNAL_ENTRY",
            entity_id=journal_entry_id,
            details={"amount": amount}
        )
    
    def log_financial_report_access(self, user_id: int, report_type: str, date_range: str):
        """Log financial report access"""
        self.log_user_action(
            user_id=user_id,
            action="ACCESS_FINANCIAL_REPORT",
            entity_type="FINANCIAL_REPORT",
            entity_id=f"{report_type}_{date_range}",
            details={"report_type": report_type, "date_range": date_range}
        )


# Global logger instances
accounting_logger = AccountingLogger()
audit_logger = AuditLogger()

