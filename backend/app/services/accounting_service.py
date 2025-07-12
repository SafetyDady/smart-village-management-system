"""
Village Accounting ERP System - Service Layer
============================================

This module contains service classes for the Village Accounting ERP System.
Implements automated journal entry generation and general ledger management.

Author: Manus AI
Date: January 7, 2025
Version: 1.0
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.accounting import (
    ChartOfAccounts, AccountingPeriod, JournalEntry, JournalEntryLine,
    GeneralLedger, PaymentJournalEntry, SpendingJournalEntry,
    ExpenseCategory, SpendingRecord, AccountType, BalanceType, JournalEntryStatus
)
from app.models.payment import Payment
from app.core.database import get_db


class AccountingService:
    """
    Core accounting service for managing journal entries and general ledger
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_current_period(self, transaction_date: datetime = None) -> Optional[AccountingPeriod]:
        """Get current accounting period for a given date"""
        if transaction_date is None:
            transaction_date = datetime.now()
        
        period = self.db.query(AccountingPeriod).filter(
            and_(
                AccountingPeriod.start_date <= transaction_date,
                AccountingPeriod.end_date >= transaction_date,
                AccountingPeriod.is_closed == False
            )
        ).first()
        
        if not period:
            # Auto-create monthly period if not exists
            period = self._create_monthly_period(transaction_date)
        
        return period
    
    def _create_monthly_period(self, transaction_date: datetime) -> AccountingPeriod:
        """Auto-create monthly accounting period"""
        year = transaction_date.year
        month = transaction_date.month
        
        # Calculate period dates
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        period = AccountingPeriod(
            period_name=f"{year}-{month:02d}",
            period_type="MONTHLY",
            fiscal_year=year,
            start_date=start_date,
            end_date=end_date,
            is_closed=False
        )
        
        self.db.add(period)
        self.db.commit()
        self.db.refresh(period)
        
        return period
    
    def generate_entry_number(self, transaction_date: datetime = None) -> str:
        """Generate unique journal entry number"""
        if transaction_date is None:
            transaction_date = datetime.now()
        
        # Format: JE-YYYY-MM-NNNN
        year_month = transaction_date.strftime("%Y-%m")
        
        # Get next sequence number for the month
        last_entry = self.db.query(JournalEntry).filter(
            JournalEntry.entry_number.like(f"JE-{year_month}-%")
        ).order_by(JournalEntry.entry_number.desc()).first()
        
        if last_entry:
            last_seq = int(last_entry.entry_number.split("-")[-1])
            next_seq = last_seq + 1
        else:
            next_seq = 1
        
        return f"JE-{year_month}-{next_seq:04d}"
    
    def create_journal_entry(
        self,
        description: str,
        transaction_date: datetime,
        lines: List[Dict[str, Any]],
        reference_type: str = None,
        reference_id: UUID = None,
        reference_number: str = None,
        auto_post: bool = True
    ) -> JournalEntry:
        """
        Create a new journal entry with validation
        
        Args:
            description: Entry description
            transaction_date: Transaction date
            lines: List of line items with account_id, debit_amount, credit_amount, description
            reference_type: Type of source transaction (payment, spending, etc.)
            reference_id: ID of source transaction
            reference_number: Reference number
            auto_post: Whether to automatically post the entry
        
        Returns:
            Created JournalEntry
        """
        
        # Validate lines
        if len(lines) < 2:
            raise ValueError("Journal entry must have at least 2 lines")
        
        total_debits = Decimal('0')
        total_credits = Decimal('0')
        
        for line in lines:
            debit = Decimal(str(line.get('debit_amount', 0)))
            credit = Decimal(str(line.get('credit_amount', 0)))
            
            if debit > 0 and credit > 0:
                raise ValueError("Line cannot have both debit and credit amounts")
            
            if debit == 0 and credit == 0:
                raise ValueError("Line must have either debit or credit amount")
            
            total_debits += debit
            total_credits += credit
        
        if total_debits != total_credits:
            raise ValueError(f"Debits ({total_debits}) must equal credits ({total_credits})")
        
        # Get current period
        period = self.get_current_period(transaction_date)
        if not period:
            raise ValueError("No accounting period found for transaction date")
        
        # Create journal entry
        entry = JournalEntry(
            entry_number=self.generate_entry_number(transaction_date),
            transaction_date=transaction_date,
            description=description,
            reference_type=reference_type,
            reference_id=reference_id,
            reference_number=reference_number,
            total_debit=total_debits,
            total_credit=total_credits,
            status=JournalEntryStatus.DRAFT,
            period_id=period.id
        )
        
        self.db.add(entry)
        self.db.flush()  # Get the ID
        
        # Create journal entry lines
        for i, line_data in enumerate(lines, 1):
            line = JournalEntryLine(
                journal_entry_id=entry.id,
                line_number=i,
                account_id=line_data['account_id'],
                debit_amount=Decimal(str(line_data.get('debit_amount', 0))),
                credit_amount=Decimal(str(line_data.get('credit_amount', 0))),
                line_description=line_data.get('description', '')
            )
            self.db.add(line)
        
        self.db.commit()
        self.db.refresh(entry)
        
        # Auto-post if requested
        if auto_post:
            self.post_journal_entry(entry.id)
        
        return entry
    
    def post_journal_entry(self, entry_id: UUID) -> JournalEntry:
        """Post a journal entry and update general ledger"""
        entry = self.db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
        if not entry:
            raise ValueError("Journal entry not found")
        
        if entry.status != JournalEntryStatus.DRAFT:
            raise ValueError("Only draft entries can be posted")
        
        # Update entry status
        entry.status = JournalEntryStatus.POSTED
        entry.posted_at = datetime.now()
        
        # Update general ledger for each line
        for line in entry.journal_entry_lines:
            self._update_general_ledger(
                account_id=line.account_id,
                period_id=entry.period_id,
                debit_amount=line.debit_amount,
                credit_amount=line.credit_amount
            )
        
        self.db.commit()
        self.db.refresh(entry)
        
        return entry
    
    def _update_general_ledger(
        self,
        account_id: UUID,
        period_id: UUID,
        debit_amount: Decimal,
        credit_amount: Decimal
    ):
        """Update general ledger balances"""
        
        # Get or create general ledger record
        gl_record = self.db.query(GeneralLedger).filter(
            and_(
                GeneralLedger.account_id == account_id,
                GeneralLedger.period_id == period_id
            )
        ).first()
        
        if not gl_record:
            # Get account info for balance calculation
            account = self.db.query(ChartOfAccounts).filter(
                ChartOfAccounts.id == account_id
            ).first()
            
            gl_record = GeneralLedger(
                account_id=account_id,
                period_id=period_id,
                beginning_balance=Decimal('0'),
                ending_balance=Decimal('0'),
                debit_total=Decimal('0'),
                credit_total=Decimal('0')
            )
            self.db.add(gl_record)
        
        # Update totals
        gl_record.debit_total += debit_amount
        gl_record.credit_total += credit_amount
        
        # Calculate ending balance based on account type
        account = self.db.query(ChartOfAccounts).filter(
            ChartOfAccounts.id == account_id
        ).first()
        
        if account.balance_type == BalanceType.DEBIT:
            # Assets and Expenses: Debit increases, Credit decreases
            gl_record.ending_balance = (
                gl_record.beginning_balance + 
                gl_record.debit_total - 
                gl_record.credit_total
            )
        else:
            # Liabilities, Equity, Revenue: Credit increases, Debit decreases
            gl_record.ending_balance = (
                gl_record.beginning_balance + 
                gl_record.credit_total - 
                gl_record.debit_total
            )
        
        self.db.commit()


class PaymentAccountingService:
    """
    Service for handling payment-related accounting entries
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.accounting_service = AccountingService(db)
    
    def create_journal_entry_for_payment(self, payment_id: UUID) -> JournalEntry:
        """
        Create journal entry for approved payment
        
        Standard entry:
        Dr. 1112-01 ธนาคารกสิกรไทย CA    [payment_amount]
            Cr. 4100-01 รายรับค่าส่วนกลาง        [payment_amount]
        """
        
        # Get payment details
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise ValueError("Payment not found")
        
        # Check if journal entry already exists
        existing_bridge = self.db.query(PaymentJournalEntry).filter(
            PaymentJournalEntry.payment_id == payment_id
        ).first()
        
        if existing_bridge:
            raise ValueError("Journal entry already exists for this payment")
        
        # Get chart of accounts
        bank_account = self._get_account_by_code("1112-01")  # ธนาคารกสิกรไทย CA
        revenue_account = self._get_account_by_code("4100-01")  # รายรับค่าส่วนกลาง
        
        if not bank_account or not revenue_account:
            raise ValueError("Required accounts not found in chart of accounts")
        
        # Prepare journal entry lines
        lines = [
            {
                'account_id': bank_account.id,
                'debit_amount': payment.amount,
                'credit_amount': 0,
                'description': f"รับชำระค่าส่วนกลาง - {payment.reference_number or ''}"
            },
            {
                'account_id': revenue_account.id,
                'debit_amount': 0,
                'credit_amount': payment.amount,
                'description': f"รายรับค่าส่วนกลาง - {payment.reference_number or ''}"
            }
        ]
        
        # Create journal entry
        journal_entry = self.accounting_service.create_journal_entry(
            description=f"รับชำระเงินค่าส่วนกลาง - Payment ID: {payment_id}",
            transaction_date=payment.payment_date,
            lines=lines,
            reference_type="payment",
            reference_id=payment_id,
            reference_number=payment.reference_number,
            auto_post=True
        )
        
        # Create bridge record
        bridge = PaymentJournalEntry(
            payment_id=payment_id,
            journal_entry_id=journal_entry.id
        )
        self.db.add(bridge)
        self.db.commit()
        
        return journal_entry
    
    def _get_account_by_code(self, account_code: str) -> Optional[ChartOfAccounts]:
        """Get account by account code"""
        return self.db.query(ChartOfAccounts).filter(
            ChartOfAccounts.account_code == account_code
        ).first()


class SpendingAccountingService:
    """
    Service for handling spending-related accounting entries
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.accounting_service = AccountingService(db)
    
    def create_journal_entry_for_spending(self, spending_id: UUID) -> JournalEntry:
        """
        Create journal entry for approved spending
        
        Standard entry:
        Dr. 5320-05 ค่าดูแลส่วนกลาง        [spending_amount]
            Cr. 1112-01 ธนาคารกสิกรไทย CA        [spending_amount]
        """
        
        # Get spending details
        spending = self.db.query(SpendingRecord).filter(SpendingRecord.id == spending_id).first()
        if not spending:
            raise ValueError("Spending record not found")
        
        if spending.status != "APPROVED":
            raise ValueError("Only approved spending records can generate journal entries")
        
        # Check if journal entry already exists
        existing_bridge = self.db.query(SpendingJournalEntry).filter(
            SpendingJournalEntry.spending_record_id == spending_id
        ).first()
        
        if existing_bridge:
            raise ValueError("Journal entry already exists for this spending")
        
        # Get expense account (from category or override)
        expense_account_id = spending.account_id or spending.expense_category.default_account_id
        expense_account = self.db.query(ChartOfAccounts).filter(
            ChartOfAccounts.id == expense_account_id
        ).first()
        
        # Get bank account
        bank_account = self._get_account_by_code("1112-01")  # ธนาคารกสิกรไทย CA
        
        if not expense_account or not bank_account:
            raise ValueError("Required accounts not found")
        
        # Prepare journal entry lines
        lines = [
            {
                'account_id': expense_account.id,
                'debit_amount': spending.amount,
                'credit_amount': 0,
                'description': f"{spending.description} - {spending.reference_number or ''}"
            },
            {
                'account_id': bank_account.id,
                'debit_amount': 0,
                'credit_amount': spending.amount,
                'description': f"จ่ายเงิน - {spending.description}"
            }
        ]
        
        # Create journal entry
        journal_entry = self.accounting_service.create_journal_entry(
            description=f"รายจ่าย - {spending.description}",
            transaction_date=spending.spending_date,
            lines=lines,
            reference_type="spending",
            reference_id=spending_id,
            reference_number=spending.reference_number,
            auto_post=True
        )
        
        # Create bridge record
        bridge = SpendingJournalEntry(
            spending_record_id=spending_id,
            journal_entry_id=journal_entry.id
        )
        self.db.add(bridge)
        self.db.commit()
        
        return journal_entry
    
    def _get_account_by_code(self, account_code: str) -> Optional[ChartOfAccounts]:
        """Get account by account code"""
        return self.db.query(ChartOfAccounts).filter(
            ChartOfAccounts.account_code == account_code
        ).first()


class ChartOfAccountsService:
    """
    Service for managing chart of accounts
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_account(
        self,
        account_code: str,
        account_name: str,
        account_type: AccountType,
        balance_type: BalanceType,
        account_name_en: str = None,
        parent_account_id: UUID = None,
        level: int = 1
    ) -> ChartOfAccounts:
        """Create new account in chart of accounts"""
        
        # Validate account code uniqueness
        existing = self.db.query(ChartOfAccounts).filter(
            ChartOfAccounts.account_code == account_code
        ).first()
        
        if existing:
            raise ValueError(f"Account code {account_code} already exists")
        
        account = ChartOfAccounts(
            account_code=account_code,
            account_name=account_name,
            account_name_en=account_name_en,
            account_type=account_type,
            balance_type=balance_type,
            parent_account_id=parent_account_id,
            level=level,
            is_active=True,
            is_system_account=False,
            allow_manual_entry=True
        )
        
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        
        return account
    
    def get_account_by_code(self, account_code: str) -> Optional[ChartOfAccounts]:
        """Get account by code"""
        return self.db.query(ChartOfAccounts).filter(
            ChartOfAccounts.account_code == account_code
        ).first()
    
    def get_accounts_by_type(self, account_type: AccountType) -> List[ChartOfAccounts]:
        """Get all accounts of specific type"""
        return self.db.query(ChartOfAccounts).filter(
            and_(
                ChartOfAccounts.account_type == account_type,
                ChartOfAccounts.is_active == True
            )
        ).order_by(ChartOfAccounts.account_code).all()


class ReportingService:
    """
    Service for generating financial reports
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_trial_balance(self, period_id: UUID = None) -> List[Dict[str, Any]]:
        """Generate trial balance report"""
        
        if period_id is None:
            # Get current period
            current_date = datetime.now()
            period = self.db.query(AccountingPeriod).filter(
                and_(
                    AccountingPeriod.start_date <= current_date,
                    AccountingPeriod.end_date >= current_date
                )
            ).first()
            
            if not period:
                return []
            
            period_id = period.id
        
        # Get general ledger balances
        query = self.db.query(
            ChartOfAccounts.account_code,
            ChartOfAccounts.account_name,
            ChartOfAccounts.account_type,
            ChartOfAccounts.balance_type,
            GeneralLedger.ending_balance
        ).join(
            GeneralLedger, ChartOfAccounts.id == GeneralLedger.account_id
        ).filter(
            GeneralLedger.period_id == period_id
        ).order_by(ChartOfAccounts.account_code)
        
        results = []
        total_debits = Decimal('0')
        total_credits = Decimal('0')
        
        for row in query.all():
            balance = row.ending_balance
            
            if row.balance_type == BalanceType.DEBIT and balance > 0:
                debit_balance = balance
                credit_balance = None
                total_debits += balance
            elif row.balance_type == BalanceType.CREDIT and balance > 0:
                debit_balance = None
                credit_balance = balance
                total_credits += balance
            else:
                debit_balance = None
                credit_balance = None
            
            results.append({
                'account_code': row.account_code,
                'account_name': row.account_name,
                'account_type': row.account_type,
                'debit_balance': debit_balance,
                'credit_balance': credit_balance
            })
        
        return {
            'items': results,
            'total_debits': total_debits,
            'total_credits': total_credits,
            'is_balanced': total_debits == total_credits
        }


# Utility functions for easy access

def create_journal_entry_for_payment(payment_id: UUID, db: Session = None) -> JournalEntry:
    """Utility function to create journal entry for payment"""
    if db is None:
        db = next(get_db())
    
    service = PaymentAccountingService(db)
    return service.create_journal_entry_for_payment(payment_id)


def create_journal_entry_for_spending(spending_id: UUID, db: Session = None) -> JournalEntry:
    """Utility function to create journal entry for spending"""
    if db is None:
        db = next(get_db())
    
    service = SpendingAccountingService(db)
    return service.create_journal_entry_for_spending(spending_id)

