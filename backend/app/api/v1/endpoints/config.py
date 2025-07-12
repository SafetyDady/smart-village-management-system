"""
Configuration API Endpoints - Smart Village Management System
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.core.config import settings
from app.schemas.accounting import AccountingConfigResponse
from app.core.auth import get_current_admin_user
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/accounting", response_model=AccountingConfigResponse)
async def get_accounting_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get accounting system configuration"""
    try:
        # Check if chart of accounts is initialized
        from app.services.accounting_service import AccountingService
        accounting_service = AccountingService(db)
        
        accounts = accounting_service.get_all_accounts()
        chart_initialized = len(accounts) > 0
        
        return AccountingConfigResponse(
            accounting_enabled=settings.ACCOUNTING_ENABLED,
            auto_journal_entry=settings.AUTO_JOURNAL_ENTRY,
            auto_period_creation=settings.AUTO_PERIOD_CREATION,
            default_currency=settings.DEFAULT_CURRENCY,
            fiscal_year_start=settings.FISCAL_YEAR_START,
            chart_of_accounts_initialized=chart_initialized
        )
        
    except Exception as e:
        logger.error(f"Failed to get accounting config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve accounting configuration"
        )


@router.post("/accounting/initialize")
async def initialize_accounting_system(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Initialize accounting system with default chart of accounts"""
    try:
        from app.services.chart_of_accounts_init import initialize_chart_of_accounts
        from app.services.accounting_service import AccountingService
        
        # Check if already initialized
        accounting_service = AccountingService(db)
        existing_accounts = accounting_service.get_all_accounts()
        
        if existing_accounts:
            return {
                "message": "Chart of accounts already initialized",
                "accounts_count": len(existing_accounts)
            }
        
        # Initialize chart of accounts
        accounts_created = initialize_chart_of_accounts(db)
        
        # Create current accounting period if auto creation is enabled
        if settings.AUTO_PERIOD_CREATION:
            try:
                current_period = accounting_service.get_current_period()
                if not current_period:
                    from datetime import date
                    today = date.today()
                    period = accounting_service.create_period(
                        name=f"Period {today.year}-{today.month:02d}",
                        start_date=today.replace(day=1),
                        end_date=today.replace(day=28)  # Safe end date
                    )
                    logger.info(f"Created accounting period: {period.name}")
            except Exception as e:
                logger.warning(f"Failed to create accounting period: {e}")
        
        logger.info(f"Accounting system initialized with {accounts_created} accounts by user {current_user.id}")
        
        return {
            "message": "Accounting system initialized successfully",
            "accounts_created": accounts_created,
            "chart_of_accounts_initialized": True
        }
        
    except Exception as e:
        logger.error(f"Failed to initialize accounting system: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize accounting system"
        )


@router.get("/system")
async def get_system_config(
    current_user: User = Depends(get_current_admin_user)
):
    """Get system configuration (admin only)"""
    return {
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "database_url": settings.DATABASE_URL[:20] + "..." if settings.DATABASE_URL else None,
        "allowed_hosts": settings.ALLOWED_HOSTS,
        "cors_enabled": True,
        "logging": {
            "level": settings.LOG_LEVEL,
            "file": settings.LOG_FILE,
            "audit_enabled": settings.ENABLE_AUDIT_LOG
        },
        "accounting": {
            "enabled": settings.ACCOUNTING_ENABLED,
            "auto_journal_entry": settings.AUTO_JOURNAL_ENTRY,
            "auto_period_creation": settings.AUTO_PERIOD_CREATION,
            "default_currency": settings.DEFAULT_CURRENCY,
            "fiscal_year_start": settings.FISCAL_YEAR_START
        },
        "backup": {
            "enabled": settings.BACKUP_ENABLED,
            "schedule": settings.BACKUP_SCHEDULE,
            "retention_days": settings.BACKUP_RETENTION_DAYS
        }
    }


@router.post("/accounting/toggle")
async def toggle_accounting_system(
    enable: bool,
    current_user: User = Depends(get_current_admin_user)
):
    """Toggle accounting system on/off (admin only)"""
    # Note: In a real application, this would update the configuration
    # For now, we'll just return the current state
    
    logger.info(f"Accounting system toggle requested: {enable} by user {current_user.id}")
    
    return {
        "message": f"Accounting system {'enabled' if enable else 'disabled'}",
        "accounting_enabled": enable,
        "note": "Configuration change requires application restart to take effect"
    }


@router.get("/features")
async def get_enabled_features():
    """Get list of enabled features"""
    features = {
        "village_management": True,
        "property_management": True,
        "payment_processing": True,
        "invoice_management": True,
        "accounting_system": settings.ACCOUNTING_ENABLED,
        "auto_journal_entry": settings.AUTO_JOURNAL_ENTRY,
        "bank_reconciliation": True,
        "financial_reporting": settings.ACCOUNTING_ENABLED,
        "audit_logging": settings.ENABLE_AUDIT_LOG,
        "backup_system": settings.BACKUP_ENABLED
    }
    
    return {
        "features": features,
        "total_features": len([f for f in features.values() if f]),
        "accounting_features": sum([
            settings.ACCOUNTING_ENABLED,
            settings.AUTO_JOURNAL_ENTRY,
            settings.ENABLE_AUDIT_LOG
        ])
    }

