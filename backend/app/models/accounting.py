"""
Village Accounting ERP System - SQLAlchemy Models
=================================================

This module contains SQLAlchemy models for the Village Accounting ERP System.
These models implement double-entry bookkeeping principles while maintaining
integration with existing payment and spending management systems.

Author: Manus AI
Date: January 7, 2025
Version: 1.0
"""

from sqlalchemy import (
    Column, String, Integer, Numeric, DateTime, Boolean, Text, 
    ForeignKey, CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from enum import Enum
from datetime import datetime
from typing import Optional
from app.core.database import Base


class AccountType(str, Enum):
    """Account types following standard accounting principles"""
    ASSET = "ASSET"
    LIABILITY = "LIABILITY" 
    EQUITY = "EQUITY"
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"


class BalanceType(str, Enum):
    """Normal balance types for accounts"""
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class JournalEntryStatus(str, Enum):
    """Journal entry status for workflow management"""
    DRAFT = "DRAFT"
    POSTED = "POSTED"
    REVERSED = "REVERSED"


class PeriodType(str, Enum):
    """Accounting period types"""
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUAL = "ANNUAL"


class ChartOfAccounts(Base):
    """
    Chart of Accounts - Master table for all accounting accounts
    
    Implements hierarchical account structure supporting the village's
    accounting requirements with proper account categorization.
    """
    __tablename__ = "chart_of_accounts"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Account identification
    account_code = Column(String(10), unique=True, nullable=False, index=True)
    account_name = Column(String(255), nullable=False)
    account_name_en = Column(String(255), nullable=True)  # English translation
    
    # Account classification
    account_type = Column(String(20), nullable=False)
    balance_type = Column(String(10), nullable=False)
    
    # Hierarchical structure
    parent_account_id = Column(UUID(as_uuid=True), ForeignKey('chart_of_accounts.id'), nullable=True)
    level = Column(Integer, nullable=False, default=1)
    
    # Account properties
    is_active = Column(Boolean, nullable=False, default=True)
    is_system_account = Column(Boolean, nullable=False, default=False)
    allow_manual_entry = Column(Boolean, nullable=False, default=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    parent_account = relationship("ChartOfAccounts", remote_side=[id], backref="sub_accounts")
    journal_entry_lines = relationship("JournalEntryLine", back_populates="account")
    general_ledger_entries = relationship("GeneralLedger", back_populates="account")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            account_type.in_(['ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE']),
            name='check_account_type'
        ),
        CheckConstraint(
            balance_type.in_(['DEBIT', 'CREDIT']),
            name='check_balance_type'
        ),
        CheckConstraint(
            "level >= 1 AND level <= 5",
            name='check_account_level'
        ),
        Index('idx_account_code', 'account_code'),
        Index('idx_account_type', 'account_type'),
        Index('idx_parent_account', 'parent_account_id'),
    )
    
    def __repr__(self):
        return f"<ChartOfAccounts(code='{self.account_code}', name='{self.account_name}')>"


class AccountingPeriod(Base):
    """
    Accounting Periods - Manages financial reporting periods
    
    Supports period-end closing procedures and comparative analysis
    across multiple time periods.
    """
    __tablename__ = "accounting_periods"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Period identification
    period_name = Column(String(50), nullable=False)
    period_type = Column(String(20), nullable=False)
    fiscal_year = Column(Integer, nullable=False)
    
    # Period dates
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    
    # Period status
    is_closed = Column(Boolean, nullable=False, default=False)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    closed_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    journal_entries = relationship("JournalEntry", back_populates="accounting_period")
    general_ledger_entries = relationship("GeneralLedger", back_populates="period")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            period_type.in_(['MONTHLY', 'QUARTERLY', 'ANNUAL']),
            name='check_period_type'
        ),
        CheckConstraint(
            "start_date < end_date",
            name='check_period_dates'
        ),
        UniqueConstraint('period_name', 'fiscal_year', name='unique_period_name_year'),
        Index('idx_period_dates', 'start_date', 'end_date'),
        Index('idx_fiscal_year', 'fiscal_year'),
    )
    
    def __repr__(self):
        return f"<AccountingPeriod(name='{self.period_name}', year={self.fiscal_year})>"


class JournalEntry(Base):
    """
    Journal Entries - Core transaction recording for double-entry bookkeeping
    
    Each journal entry represents a complete accounting transaction with
    balanced debit and credit entries.
    """
    __tablename__ = "journal_entries"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Entry identification
    entry_number = Column(String(20), unique=True, nullable=False, index=True)
    
    # Transaction details
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    description = Column(Text, nullable=False)
    reference_number = Column(String(50), nullable=True)
    
    # Polymorphic relationship to source transactions
    reference_type = Column(String(50), nullable=True)  # 'payment', 'spending', 'adjustment'
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Entry totals (for validation)
    total_debit = Column(Numeric(15, 2), nullable=False, default=0)
    total_credit = Column(Numeric(15, 2), nullable=False, default=0)
    
    # Entry status and workflow
    status = Column(String(20), nullable=False, default='DRAFT')
    posted_at = Column(DateTime(timezone=True), nullable=True)
    posted_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Period assignment
    period_id = Column(UUID(as_uuid=True), ForeignKey('accounting_periods.id'), nullable=False)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    accounting_period = relationship("AccountingPeriod", back_populates="journal_entries")
    journal_entry_lines = relationship("JournalEntryLine", back_populates="journal_entry", cascade="all, delete-orphan")
    
    # Integration relationships
    payment_journal_entries = relationship("PaymentJournalEntry", back_populates="journal_entry")
    spending_journal_entries = relationship("SpendingJournalEntry", back_populates="journal_entry")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            status.in_(['DRAFT', 'POSTED', 'REVERSED']),
            name='check_journal_entry_status'
        ),
        CheckConstraint(
            "total_debit = total_credit",
            name='check_balanced_entry'
        ),
        CheckConstraint(
            "total_debit >= 0 AND total_credit >= 0",
            name='check_positive_totals'
        ),
        Index('idx_entry_number', 'entry_number'),
        Index('idx_transaction_date', 'transaction_date'),
        Index('idx_reference', 'reference_type', 'reference_id'),
        Index('idx_period_status', 'period_id', 'status'),
    )
    
    def __repr__(self):
        return f"<JournalEntry(number='{self.entry_number}', amount={self.total_debit})>"


class JournalEntryLine(Base):
    """
    Journal Entry Lines - Individual debit and credit entries
    
    Implements the line items that comprise each journal entry,
    ensuring proper double-entry bookkeeping principles.
    """
    __tablename__ = "journal_entry_lines"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Parent journal entry
    journal_entry_id = Column(UUID(as_uuid=True), ForeignKey('journal_entries.id'), nullable=False)
    
    # Line details
    line_number = Column(Integer, nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey('chart_of_accounts.id'), nullable=False)
    
    # Amounts (exactly one should be non-zero)
    debit_amount = Column(Numeric(15, 2), nullable=True, default=0)
    credit_amount = Column(Numeric(15, 2), nullable=True, default=0)
    
    # Line description
    line_description = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    journal_entry = relationship("JournalEntry", back_populates="journal_entry_lines")
    account = relationship("ChartOfAccounts", back_populates="journal_entry_lines")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "(debit_amount > 0 AND credit_amount = 0) OR (debit_amount = 0 AND credit_amount > 0)",
            name='check_debit_or_credit'
        ),
        CheckConstraint(
            "debit_amount >= 0 AND credit_amount >= 0",
            name='check_positive_amounts'
        ),
        UniqueConstraint('journal_entry_id', 'line_number', name='unique_line_number'),
        Index('idx_journal_entry_line', 'journal_entry_id', 'line_number'),
        Index('idx_account_line', 'account_id'),
    )
    
    def __repr__(self):
        amount = self.debit_amount if self.debit_amount > 0 else self.credit_amount
        return f"<JournalEntryLine(account={self.account_id}, amount={amount})>"


class GeneralLedger(Base):
    """
    General Ledger - Account balance tracking and history
    
    Maintains running balances for each account and supports
    real-time financial reporting and analysis.
    """
    __tablename__ = "general_ledger"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Account and period
    account_id = Column(UUID(as_uuid=True), ForeignKey('chart_of_accounts.id'), nullable=False)
    period_id = Column(UUID(as_uuid=True), ForeignKey('accounting_periods.id'), nullable=False)
    
    # Balance tracking
    beginning_balance = Column(Numeric(15, 2), nullable=False, default=0)
    ending_balance = Column(Numeric(15, 2), nullable=False, default=0)
    
    # Period activity
    debit_total = Column(Numeric(15, 2), nullable=False, default=0)
    credit_total = Column(Numeric(15, 2), nullable=False, default=0)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    account = relationship("ChartOfAccounts", back_populates="general_ledger_entries")
    period = relationship("AccountingPeriod", back_populates="general_ledger_entries")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('account_id', 'period_id', name='unique_account_period'),
        CheckConstraint(
            "debit_total >= 0 AND credit_total >= 0",
            name='check_positive_totals'
        ),
        Index('idx_account_period', 'account_id', 'period_id'),
        Index('idx_period_balance', 'period_id', 'ending_balance'),
    )
    
    def __repr__(self):
        return f"<GeneralLedger(account={self.account_id}, balance={self.ending_balance})>"


# Integration Bridge Tables

class PaymentJournalEntry(Base):
    """
    Payment Journal Entry Bridge - Links payments to journal entries
    
    Maintains the relationship between payment transactions and
    their corresponding accounting entries.
    """
    __tablename__ = "payment_journal_entries"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    payment_id = Column(UUID(as_uuid=True), nullable=False)  # References existing payments table
    journal_entry_id = Column(UUID(as_uuid=True), ForeignKey('journal_entries.id'), nullable=False)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    journal_entry = relationship("JournalEntry", back_populates="payment_journal_entries")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('payment_id', 'journal_entry_id', name='unique_payment_journal'),
        Index('idx_payment_journal', 'payment_id'),
        Index('idx_journal_payment', 'journal_entry_id'),
    )
    
    def __repr__(self):
        return f"<PaymentJournalEntry(payment={self.payment_id}, journal={self.journal_entry_id})>"


# Spending Records (New table for expense management)

class ExpenseCategory(Base):
    """
    Expense Categories - Master data for expense classification
    
    Provides categorization for spending records and links to
    appropriate expense accounts in the chart of accounts.
    """
    __tablename__ = "expense_categories"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Category details
    category_code = Column(String(10), unique=True, nullable=False, index=True)
    category_name = Column(String(255), nullable=False)
    category_name_en = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    # Account mapping
    default_account_id = Column(UUID(as_uuid=True), ForeignKey('chart_of_accounts.id'), nullable=False)
    
    # Category properties
    is_active = Column(Boolean, nullable=False, default=True)
    requires_approval = Column(Boolean, nullable=False, default=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    default_account = relationship("ChartOfAccounts")
    spending_records = relationship("SpendingRecord", back_populates="expense_category")
    
    # Constraints
    __table_args__ = (
        Index('idx_category_code', 'category_code'),
        Index('idx_category_active', 'is_active'),
    )
    
    def __repr__(self):
        return f"<ExpenseCategory(code='{self.category_code}', name='{self.category_name}')>"


class SpendingRecord(Base):
    """
    Spending Records - Expense transaction management
    
    Tracks all spending/expense transactions with proper approval
    workflow and integration with the accounting system.
    """
    __tablename__ = "spending_records"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Spending details
    amount = Column(Numeric(12, 2), nullable=False)
    spending_date = Column(DateTime(timezone=True), nullable=False)
    description = Column(Text, nullable=False)
    reference_number = Column(String(100), nullable=True)
    
    # Category and account
    expense_category_id = Column(UUID(as_uuid=True), ForeignKey('expense_categories.id'), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey('chart_of_accounts.id'), nullable=True)  # Override default
    
    # Approval workflow
    status = Column(String(20), nullable=False, default='PENDING')  # PENDING, APPROVED, REJECTED
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Payment details
    payment_method = Column(String(50), nullable=True)
    bank_reference = Column(String(100), nullable=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Soft delete
    archived = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    expense_category = relationship("ExpenseCategory", back_populates="spending_records")
    account = relationship("ChartOfAccounts")
    spending_journal_entries = relationship("SpendingJournalEntry", back_populates="spending_record")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            status.in_(['PENDING', 'APPROVED', 'REJECTED']),
            name='check_spending_status'
        ),
        CheckConstraint(
            "amount > 0",
            name='check_positive_amount'
        ),
        Index('idx_spending_date', 'spending_date'),
        Index('idx_spending_status', 'status'),
        Index('idx_spending_category', 'expense_category_id'),
        Index('idx_spending_created_by', 'created_by'),
    )
    
    def __repr__(self):
        return f"<SpendingRecord(id={self.id}, amount={self.amount}, status='{self.status}')>"


class SpendingJournalEntry(Base):
    """
    Spending Journal Entry Bridge - Links spending records to journal entries
    
    Maintains the relationship between spending transactions and
    their corresponding accounting entries.
    """
    __tablename__ = "spending_journal_entries"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    spending_record_id = Column(UUID(as_uuid=True), ForeignKey('spending_records.id'), nullable=False)
    journal_entry_id = Column(UUID(as_uuid=True), ForeignKey('journal_entries.id'), nullable=False)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    spending_record = relationship("SpendingRecord", back_populates="spending_journal_entries")
    journal_entry = relationship("JournalEntry", back_populates="spending_journal_entries")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('spending_record_id', 'journal_entry_id', name='unique_spending_journal'),
        Index('idx_spending_journal', 'spending_record_id'),
        Index('idx_journal_spending', 'journal_entry_id'),
    )
    
    def __repr__(self):
        return f"<SpendingJournalEntry(spending={self.spending_record_id}, journal={self.journal_entry_id})>"


# Enhanced Bank Reconciliation (extends existing table)

class BankReconciliationGL(Base):
    """
    Bank Reconciliation General Ledger Bridge
    
    Connects bank reconciliation records with general ledger accounts
    for enhanced reconciliation capabilities.
    """
    __tablename__ = "bank_reconciliation_gl"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    bank_reconciliation_id = Column(UUID(as_uuid=True), nullable=False)  # References existing bank_reconciliation table
    gl_account_id = Column(UUID(as_uuid=True), ForeignKey('chart_of_accounts.id'), nullable=False)
    journal_entry_id = Column(UUID(as_uuid=True), ForeignKey('journal_entries.id'), nullable=True)
    
    # Reconciliation details
    reconciled_amount = Column(Numeric(15, 2), nullable=False)
    reconciliation_date = Column(DateTime(timezone=True), nullable=False)
    reconciliation_status = Column(String(20), nullable=False, default='MATCHED')
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    reconciled_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    gl_account = relationship("ChartOfAccounts")
    journal_entry = relationship("JournalEntry")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            reconciliation_status.in_(['MATCHED', 'UNMATCHED', 'DISPUTED', 'ADJUSTED']),
            name='check_reconciliation_status'
        ),
        Index('idx_bank_recon_gl', 'bank_reconciliation_id'),
        Index('idx_gl_recon', 'gl_account_id'),
        Index('idx_recon_status', 'reconciliation_status'),
    )
    
    def __repr__(self):
        return f"<BankReconciliationGL(amount={self.reconciled_amount}, status='{self.reconciliation_status}')>"

