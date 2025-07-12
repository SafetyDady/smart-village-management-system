"""
Background Tasks - Smart Village Management System
"""
from typing import Optional
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from app.core.database import get_db
from app.services.accounting_service import AccountingService
from app.core.logging import accounting_logger, audit_logger

logger = logging.getLogger(__name__)


class AccountingBackgroundTasks:
    """Background tasks for accounting operations"""
    
    @staticmethod
    def create_payment_journal_entry(
        payment_id: str,
        user_id: Optional[int] = None,
        db_session: Optional[Session] = None
    ):
        """
        Create journal entry for payment in background
        
        Args:
            payment_id: Payment UUID
            user_id: User who triggered the action
            db_session: Database session (optional, will create new if not provided)
        """
        db = db_session or next(get_db())
        
        try:
            accounting_service = AccountingService(db)
            
            # Create journal entry
            journal_entry = accounting_service.create_journal_entry_for_payment(payment_id)
            
            # Log the action
            accounting_logger.log_payment_journal_entry(
                payment_id=payment_id,
                journal_entry_id=str(journal_entry.id),
                user_id=user_id or 0
            )
            
            if user_id:
                audit_logger.log_user_action(
                    user_id=user_id,
                    action="AUTO_CREATE_PAYMENT_JOURNAL_ENTRY",
                    entity_type="PAYMENT",
                    entity_id=payment_id,
                    details={"journal_entry_id": str(journal_entry.id)}
                )
            
            logger.info(f"Background task completed: Payment journal entry created for {payment_id}")
            
        except Exception as e:
            logger.error(f"Background task failed: Payment journal entry for {payment_id}: {e}")
            accounting_logger.log_error(
                message=f"Failed to create payment journal entry for {payment_id}",
                error=e,
                payment_id=payment_id,
                user_id=user_id
            )
        finally:
            if not db_session:
                db.close()
    
    @staticmethod
    def create_spending_journal_entry(
        spending_id: str,
        user_id: Optional[int] = None,
        db_session: Optional[Session] = None
    ):
        """
        Create journal entry for spending in background
        
        Args:
            spending_id: Spending UUID
            user_id: User who triggered the action
            db_session: Database session (optional)
        """
        db = db_session or next(get_db())
        
        try:
            accounting_service = AccountingService(db)
            
            # Create journal entry
            journal_entry = accounting_service.create_journal_entry_for_spending(spending_id)
            
            # Log the action
            accounting_logger.log_spending_journal_entry(
                spending_id=spending_id,
                journal_entry_id=str(journal_entry.id),
                user_id=user_id or 0
            )
            
            if user_id:
                audit_logger.log_user_action(
                    user_id=user_id,
                    action="AUTO_CREATE_SPENDING_JOURNAL_ENTRY",
                    entity_type="SPENDING",
                    entity_id=spending_id,
                    details={"journal_entry_id": str(journal_entry.id)}
                )
            
            logger.info(f"Background task completed: Spending journal entry created for {spending_id}")
            
        except Exception as e:
            logger.error(f"Background task failed: Spending journal entry for {spending_id}: {e}")
            accounting_logger.log_error(
                message=f"Failed to create spending journal entry for {spending_id}",
                error=e,
                spending_id=spending_id,
                user_id=user_id
            )
        finally:
            if not db_session:
                db.close()
    
    @staticmethod
    def update_general_ledger(
        journal_entry_id: str,
        user_id: Optional[int] = None,
        db_session: Optional[Session] = None
    ):
        """
        Update general ledger after journal entry posting
        
        Args:
            journal_entry_id: Journal Entry UUID
            user_id: User who triggered the action
            db_session: Database session (optional)
        """
        db = db_session or next(get_db())
        
        try:
            accounting_service = AccountingService(db)
            
            # Update general ledger
            accounting_service.update_general_ledger_for_entry(journal_entry_id)
            
            logger.info(f"Background task completed: General ledger updated for journal entry {journal_entry_id}")
            
        except Exception as e:
            logger.error(f"Background task failed: General ledger update for {journal_entry_id}: {e}")
            accounting_logger.log_error(
                message=f"Failed to update general ledger for journal entry {journal_entry_id}",
                error=e,
                journal_entry_id=journal_entry_id,
                user_id=user_id
            )
        finally:
            if not db_session:
                db.close()
    
    @staticmethod
    def generate_period_end_reports(
        period_id: str,
        user_id: int,
        db_session: Optional[Session] = None
    ):
        """
        Generate period-end reports in background
        
        Args:
            period_id: Accounting Period UUID
            user_id: User who requested the reports
            db_session: Database session (optional)
        """
        db = db_session or next(get_db())
        
        try:
            accounting_service = AccountingService(db)
            
            # Generate trial balance
            period = accounting_service.get_period_by_id(period_id)
            trial_balance = accounting_service.generate_trial_balance(period.end_date)
            
            # Generate income statement
            income_statement = accounting_service.generate_income_statement(
                start_date=period.start_date,
                end_date=period.end_date
            )
            
            # Generate balance sheet
            balance_sheet = accounting_service.generate_balance_sheet(period.end_date)
            
            # Log the action
            audit_logger.log_user_action(
                user_id=user_id,
                action="GENERATE_PERIOD_END_REPORTS",
                entity_type="ACCOUNTING_PERIOD",
                entity_id=period_id,
                details={
                    "trial_balance_generated": True,
                    "income_statement_generated": True,
                    "balance_sheet_generated": True
                }
            )
            
            logger.info(f"Background task completed: Period-end reports generated for period {period_id}")
            
        except Exception as e:
            logger.error(f"Background task failed: Period-end reports for {period_id}: {e}")
            accounting_logger.log_error(
                message=f"Failed to generate period-end reports for period {period_id}",
                error=e,
                period_id=period_id,
                user_id=user_id
            )
        finally:
            if not db_session:
                db.close()
    
    @staticmethod
    def validate_accounting_integrity(
        user_id: Optional[int] = None,
        db_session: Optional[Session] = None
    ):
        """
        Validate accounting data integrity in background
        
        Args:
            user_id: User who triggered the validation
            db_session: Database session (optional)
        """
        db = db_session or next(get_db())
        
        try:
            accounting_service = AccountingService(db)
            
            # Validate trial balance
            today = datetime.now().date()
            trial_balance = accounting_service.generate_trial_balance(today)
            
            if not trial_balance.is_balanced:
                logger.warning("Accounting integrity check failed: Trial balance is not balanced")
                accounting_logger.log_error(
                    message="Trial balance is not balanced",
                    error=Exception("Trial balance validation failed"),
                    user_id=user_id
                )
            
            # Validate journal entries
            unbalanced_entries = accounting_service.find_unbalanced_journal_entries()
            if unbalanced_entries:
                logger.warning(f"Found {len(unbalanced_entries)} unbalanced journal entries")
                accounting_logger.log_error(
                    message=f"Found {len(unbalanced_entries)} unbalanced journal entries",
                    error=Exception("Journal entry validation failed"),
                    user_id=user_id
                )
            
            logger.info("Background task completed: Accounting integrity validation")
            
        except Exception as e:
            logger.error(f"Background task failed: Accounting integrity validation: {e}")
            accounting_logger.log_error(
                message="Failed to validate accounting integrity",
                error=e,
                user_id=user_id
            )
        finally:
            if not db_session:
                db.close()


def add_payment_journal_entry_task(
    background_tasks: BackgroundTasks,
    payment_id: str,
    user_id: Optional[int] = None
):
    """Add payment journal entry creation to background tasks"""
    background_tasks.add_task(
        AccountingBackgroundTasks.create_payment_journal_entry,
        payment_id=payment_id,
        user_id=user_id
    )


def add_spending_journal_entry_task(
    background_tasks: BackgroundTasks,
    spending_id: str,
    user_id: Optional[int] = None
):
    """Add spending journal entry creation to background tasks"""
    background_tasks.add_task(
        AccountingBackgroundTasks.create_spending_journal_entry,
        spending_id=spending_id,
        user_id=user_id
    )


def add_general_ledger_update_task(
    background_tasks: BackgroundTasks,
    journal_entry_id: str,
    user_id: Optional[int] = None
):
    """Add general ledger update to background tasks"""
    background_tasks.add_task(
        AccountingBackgroundTasks.update_general_ledger,
        journal_entry_id=journal_entry_id,
        user_id=user_id
    )


def add_period_end_reports_task(
    background_tasks: BackgroundTasks,
    period_id: str,
    user_id: int
):
    """Add period-end reports generation to background tasks"""
    background_tasks.add_task(
        AccountingBackgroundTasks.generate_period_end_reports,
        period_id=period_id,
        user_id=user_id
    )


def add_integrity_validation_task(
    background_tasks: BackgroundTasks,
    user_id: Optional[int] = None
):
    """Add accounting integrity validation to background tasks"""
    background_tasks.add_task(
        AccountingBackgroundTasks.validate_accounting_integrity,
        user_id=user_id
    )

