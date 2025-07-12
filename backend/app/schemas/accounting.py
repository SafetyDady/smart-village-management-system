"""
Accounting Schemas - Smart Village Management System
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, validator
from uuid import UUID

from app.models.accounting import AccountType, BalanceType, JournalEntryStatus


class ChartOfAccountsBase(BaseModel):
    """Base schema for Chart of Accounts"""
    account_code: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="Account code format: XXXX-XX")
    account_name: str = Field(..., min_length=1, max_length=200)
    account_type: AccountType
    balance_type: BalanceType
    parent_account_code: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}$")
    description: Optional[str] = None
    is_active: bool = True


class ChartOfAccountsCreate(ChartOfAccountsBase):
    """Schema for creating a new account"""
    pass


class ChartOfAccountsResponse(ChartOfAccountsBase):
    """Schema for Chart of Accounts response"""
    id: UUID
    current_balance: Decimal = Field(default=Decimal('0.00'))
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JournalEntryLineBase(BaseModel):
    """Base schema for Journal Entry Line"""
    account_code: str = Field(..., pattern=r"^\d{4}-\d{2}$")
    description: str = Field(..., min_length=1, max_length=500)
    debit_amount: Optional[Decimal] = Field(None, ge=0)
    credit_amount: Optional[Decimal] = Field(None, ge=0)

    @validator('debit_amount', 'credit_amount')
    def validate_amounts(cls, v, values):
        """Ensure exactly one of debit or credit is provided"""
        debit = values.get('debit_amount')
        credit = values.get('credit_amount')
        
        if v is not None:
            if v <= 0:
                raise ValueError("Amount must be positive")
        
        # Check that exactly one amount is provided
        if (debit is None and credit is None) or (debit is not None and credit is not None):
            raise ValueError("Exactly one of debit_amount or credit_amount must be provided")
        
        return v


class JournalEntryLineCreate(JournalEntryLineBase):
    """Schema for creating journal entry line"""
    pass


class JournalEntryLineResponse(JournalEntryLineBase):
    """Schema for journal entry line response"""
    id: UUID
    journal_entry_id: UUID
    line_number: int
    created_at: datetime

    class Config:
        from_attributes = True


class JournalEntryBase(BaseModel):
    """Base schema for Journal Entry"""
    description: str = Field(..., min_length=1, max_length=500)
    reference_number: Optional[str] = Field(None, max_length=100)
    entry_type: str = Field(..., max_length=50)


class JournalEntryCreate(JournalEntryBase):
    """Schema for creating journal entry"""
    lines: List[JournalEntryLineCreate] = Field(..., min_items=2)

    @validator('lines')
    def validate_balanced_entry(cls, v):
        """Ensure journal entry is balanced (debits = credits)"""
        total_debits = sum(line.debit_amount or Decimal('0') for line in v)
        total_credits = sum(line.credit_amount or Decimal('0') for line in v)
        
        if total_debits != total_credits:
            raise ValueError(f"Journal entry must be balanced. Debits: {total_debits}, Credits: {total_credits}")
        
        if total_debits == 0:
            raise ValueError("Journal entry cannot have zero amounts")
        
        return v


class JournalEntryResponse(JournalEntryBase):
    """Schema for journal entry response"""
    id: UUID
    entry_number: str
    entry_date: date
    status: JournalEntryStatus
    total_amount: Decimal
    
    # Audit fields
    created_by_id: Optional[int] = None
    created_at: datetime
    posted_by_id: Optional[int] = None
    posted_at: Optional[datetime] = None
    
    # Related data
    lines: List[JournalEntryLineResponse] = []
    
    # Bridge table references
    payment_id: Optional[UUID] = None
    spending_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class GeneralLedgerResponse(BaseModel):
    """Schema for General Ledger response"""
    id: UUID
    account_code: str
    account_name: str
    transaction_date: date
    description: str
    reference_number: Optional[str] = None
    debit_amount: Optional[Decimal] = None
    credit_amount: Optional[Decimal] = None
    running_balance: Decimal
    journal_entry_id: UUID
    journal_entry_number: str

    class Config:
        from_attributes = True


class AccountBalanceResponse(BaseModel):
    """Schema for account balance"""
    account_code: str
    account_name: str
    account_type: AccountType
    balance_type: BalanceType
    current_balance: Decimal
    debit_total: Decimal
    credit_total: Decimal


class TrialBalanceResponse(BaseModel):
    """Schema for Trial Balance report"""
    as_of_date: date
    accounts: List[AccountBalanceResponse]
    total_debits: Decimal
    total_credits: Decimal
    is_balanced: bool
    generated_at: datetime

    class Config:
        from_attributes = True


class FinancialReportLineItem(BaseModel):
    """Schema for financial report line item"""
    account_code: str
    account_name: str
    amount: Decimal
    percentage: Optional[Decimal] = None


class FinancialReportSection(BaseModel):
    """Schema for financial report section"""
    section_name: str
    line_items: List[FinancialReportLineItem]
    section_total: Decimal


class FinancialReportResponse(BaseModel):
    """Schema for financial reports (Income Statement, Balance Sheet)"""
    report_type: str  # "income_statement" or "balance_sheet"
    report_period: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    as_of_date: Optional[date] = None
    
    sections: List[FinancialReportSection]
    
    # Summary totals
    total_revenue: Optional[Decimal] = None
    total_expenses: Optional[Decimal] = None
    net_income: Optional[Decimal] = None
    total_assets: Optional[Decimal] = None
    total_liabilities: Optional[Decimal] = None
    total_equity: Optional[Decimal] = None
    
    generated_at: datetime

    class Config:
        from_attributes = True


class AccountingPeriodResponse(BaseModel):
    """Schema for Accounting Period response"""
    id: UUID
    name: str
    start_date: date
    end_date: date
    is_closed: bool
    closed_by_id: Optional[int] = None
    closed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentJournalEntryResponse(BaseModel):
    """Schema for Payment Journal Entry bridge"""
    id: UUID
    payment_id: UUID
    journal_entry_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class SpendingJournalEntryResponse(BaseModel):
    """Schema for Spending Journal Entry bridge"""
    id: UUID
    spending_id: UUID
    journal_entry_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class AccountingHealthResponse(BaseModel):
    """Schema for accounting system health check"""
    status: str
    accounts_count: int
    current_period: Optional[str] = None
    timestamp: str


class AccountingStatsResponse(BaseModel):
    """Schema for accounting statistics"""
    total_accounts: int
    active_accounts: int
    total_journal_entries: int
    posted_entries: int
    pending_entries: int
    current_period: Optional[str] = None
    last_entry_date: Optional[date] = None


class ManualJournalEntryRequest(BaseModel):
    """Schema for manual journal entry request"""
    description: str = Field(..., min_length=1, max_length=500)
    reference_number: Optional[str] = Field(None, max_length=100)
    entry_date: Optional[date] = None
    lines: List[JournalEntryLineCreate] = Field(..., min_items=2)

    @validator('lines')
    def validate_balanced_entry(cls, v):
        """Ensure journal entry is balanced"""
        total_debits = sum(line.debit_amount or Decimal('0') for line in v)
        total_credits = sum(line.credit_amount or Decimal('0') for line in v)
        
        if total_debits != total_credits:
            raise ValueError(f"Journal entry must be balanced. Debits: {total_debits}, Credits: {total_credits}")
        
        return v


class AccountingConfigResponse(BaseModel):
    """Schema for accounting configuration"""
    accounting_enabled: bool
    auto_journal_entry: bool
    auto_period_creation: bool
    default_currency: str
    fiscal_year_start: str  # MM-DD format
    chart_of_accounts_initialized: bool



class AccountingConfigResponse(BaseModel):
    """Accounting configuration response schema"""
    accounting_enabled: bool
    auto_journal_entry: bool
    auto_period_creation: bool
    default_currency: str
    fiscal_year_start: str
    chart_of_accounts_initialized: bool
    
    class Config:
        from_attributes = True

