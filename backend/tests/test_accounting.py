"""
Unit Tests for Village Accounting ERP System
===========================================

This module contains comprehensive unit tests for the accounting system,
including journal entry automation, general ledger updates, and validation.

Author: Manus AI
Date: January 7, 2025
Version: 1.0
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.accounting import (
    ChartOfAccounts, AccountingPeriod, JournalEntry, JournalEntryLine,
    GeneralLedger, PaymentJournalEntry, SpendingJournalEntry,
    ExpenseCategory, SpendingRecord, AccountType, BalanceType, JournalEntryStatus
)
from app.models.payment import Payment, PaymentMethod
from app.models.property import Property
from app.models.user import User
from app.models.village import Village
from app.services.accounting_service import (
    AccountingService, PaymentAccountingService, SpendingAccountingService,
    ChartOfAccountsService, ReportingService
)


# Test Database Setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_accounting.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_accounts(db_session):
    """Create sample chart of accounts for testing"""
    accounts = [
        ChartOfAccounts(
            account_code="1112-01",
            account_name="ธนาคารกสิกรไทย CA",
            account_type=AccountType.ASSET,
            balance_type=BalanceType.DEBIT,
            level=1,
            is_system_account=True
        ),
        ChartOfAccounts(
            account_code="4100-01",
            account_name="รายรับค่าส่วนกลาง",
            account_type=AccountType.REVENUE,
            balance_type=BalanceType.CREDIT,
            level=1,
            is_system_account=True
        ),
        ChartOfAccounts(
            account_code="5320-05",
            account_name="ค่าดูแลส่วนกลาง",
            account_type=AccountType.EXPENSE,
            balance_type=BalanceType.DEBIT,
            level=1,
            is_system_account=True
        )
    ]
    
    for account in accounts:
        db_session.add(account)
    db_session.commit()
    
    return {account.account_code: account for account in accounts}


@pytest.fixture
def sample_period(db_session):
    """Create sample accounting period for testing"""
    period = AccountingPeriod(
        period_name="2025-01",
        period_type="MONTHLY",
        fiscal_year=2025,
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2025, 1, 31),
        is_closed=False
    )
    db_session.add(period)
    db_session.commit()
    return period


@pytest.fixture
def sample_expense_category(db_session, sample_accounts):
    """Create sample expense category for testing"""
    category = ExpenseCategory(
        category_code="MAINT-01",
        category_name="ค่าดูแลส่วนกลาง",
        default_account_id=sample_accounts["5320-05"].id,
        is_active=True,
        requires_approval=True
    )
    db_session.add(category)
    db_session.commit()
    return category


@pytest.fixture
def sample_village(db_session):
    """Create sample village for testing"""
    village = Village(
        name="Test Village",
        code="TV001",
        address="123 Test Street",
        city="Bangkok",
        state="Bangkok",
        postal_code="10100",
        phone="02-123-4567"
    )
    db_session.add(village)
    db_session.commit()
    return village


@pytest.fixture
def sample_user(db_session):
    """Create sample user for testing"""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        first_name="Test",
        last_name="User",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def sample_property(db_session, sample_village):
    """Create sample property for testing"""
    property_obj = Property(
        village_id=sample_village.id,
        unit_number="A101",
        property_type="condo",
        owner_name="Test Owner",
        owner_phone="081-234-5678",
        size_sqm=100.0,
        monthly_fee=Decimal("2000.00")
    )
    db_session.add(property_obj)
    db_session.commit()
    return property_obj


@pytest.fixture
def sample_payment(db_session, sample_property, sample_user):
    """Create sample payment for testing"""
    payment = Payment(
        property_id=sample_property.id,
        amount=Decimal("2000.00"),
        payment_date=datetime.now(),
        method=PaymentMethod.BANK_TRANSFER,
        reference_number="PAY-001",
        created_by=sample_user.id
    )
    db_session.add(payment)
    db_session.commit()
    return payment


class TestAccountingService:
    """Test cases for AccountingService"""
    
    def test_get_current_period_existing(self, db_session, sample_period):
        """Test getting existing current period"""
        service = AccountingService(db_session)
        
        # Test with date within period
        test_date = datetime(2025, 1, 15)
        period = service.get_current_period(test_date)
        
        assert period is not None
        assert period.id == sample_period.id
        assert period.period_name == "2025-01"
    
    def test_get_current_period_auto_create(self, db_session):
        """Test auto-creation of period when none exists"""
        service = AccountingService(db_session)
        
        # Test with date that has no existing period
        test_date = datetime(2025, 2, 15)
        period = service.get_current_period(test_date)
        
        assert period is not None
        assert period.period_name == "2025-02"
        assert period.fiscal_year == 2025
        assert period.period_type == "MONTHLY"
    
    def test_generate_entry_number(self, db_session, sample_period):
        """Test journal entry number generation"""
        service = AccountingService(db_session)
        
        # Test first entry
        test_date = datetime(2025, 1, 15)
        entry_number = service.generate_entry_number(test_date)
        assert entry_number == "JE-2025-01-0001"
        
        # Create an entry to test sequence
        entry = JournalEntry(
            entry_number=entry_number,
            transaction_date=test_date,
            description="Test Entry",
            total_debit=Decimal("100.00"),
            total_credit=Decimal("100.00"),
            period_id=sample_period.id
        )
        db_session.add(entry)
        db_session.commit()
        
        # Test next entry number
        next_number = service.generate_entry_number(test_date)
        assert next_number == "JE-2025-01-0002"
    
    def test_create_journal_entry_valid(self, db_session, sample_accounts, sample_period):
        """Test creating valid journal entry"""
        service = AccountingService(db_session)
        
        lines = [
            {
                'account_id': sample_accounts["1112-01"].id,
                'debit_amount': Decimal("1000.00"),
                'credit_amount': Decimal("0.00"),
                'description': "Test debit"
            },
            {
                'account_id': sample_accounts["4100-01"].id,
                'debit_amount': Decimal("0.00"),
                'credit_amount': Decimal("1000.00"),
                'description': "Test credit"
            }
        ]
        
        entry = service.create_journal_entry(
            description="Test Journal Entry",
            transaction_date=datetime(2025, 1, 15),
            lines=lines,
            auto_post=False
        )
        
        assert entry is not None
        assert entry.description == "Test Journal Entry"
        assert entry.total_debit == Decimal("1000.00")
        assert entry.total_credit == Decimal("1000.00")
        assert entry.status == JournalEntryStatus.DRAFT
        assert len(entry.journal_entry_lines) == 2
    
    def test_create_journal_entry_unbalanced(self, db_session, sample_accounts):
        """Test creating unbalanced journal entry should fail"""
        service = AccountingService(db_session)
        
        lines = [
            {
                'account_id': sample_accounts["1112-01"].id,
                'debit_amount': Decimal("1000.00"),
                'credit_amount': Decimal("0.00"),
                'description': "Test debit"
            },
            {
                'account_id': sample_accounts["4100-01"].id,
                'debit_amount': Decimal("0.00"),
                'credit_amount': Decimal("500.00"),  # Unbalanced!
                'description': "Test credit"
            }
        ]
        
        with pytest.raises(ValueError, match="Debits .* must equal credits"):
            service.create_journal_entry(
                description="Unbalanced Entry",
                transaction_date=datetime(2025, 1, 15),
                lines=lines
            )
    
    def test_post_journal_entry(self, db_session, sample_accounts, sample_period):
        """Test posting journal entry and updating general ledger"""
        service = AccountingService(db_session)
        
        lines = [
            {
                'account_id': sample_accounts["1112-01"].id,
                'debit_amount': Decimal("1000.00"),
                'credit_amount': Decimal("0.00"),
                'description': "Test debit"
            },
            {
                'account_id': sample_accounts["4100-01"].id,
                'debit_amount': Decimal("0.00"),
                'credit_amount': Decimal("1000.00"),
                'description': "Test credit"
            }
        ]
        
        # Create draft entry
        entry = service.create_journal_entry(
            description="Test Journal Entry",
            transaction_date=datetime(2025, 1, 15),
            lines=lines,
            auto_post=False
        )
        
        assert entry.status == JournalEntryStatus.DRAFT
        
        # Post the entry
        posted_entry = service.post_journal_entry(entry.id)
        
        assert posted_entry.status == JournalEntryStatus.POSTED
        assert posted_entry.posted_at is not None
        
        # Check general ledger updates
        bank_gl = db_session.query(GeneralLedger).filter(
            GeneralLedger.account_id == sample_accounts["1112-01"].id
        ).first()
        
        revenue_gl = db_session.query(GeneralLedger).filter(
            GeneralLedger.account_id == sample_accounts["4100-01"].id
        ).first()
        
        assert bank_gl is not None
        assert bank_gl.debit_total == Decimal("1000.00")
        assert bank_gl.ending_balance == Decimal("1000.00")  # Asset account: debit increases
        
        assert revenue_gl is not None
        assert revenue_gl.credit_total == Decimal("1000.00")
        assert revenue_gl.ending_balance == Decimal("1000.00")  # Revenue account: credit increases


class TestPaymentAccountingService:
    """Test cases for PaymentAccountingService"""
    
    def test_create_journal_entry_for_payment(self, db_session, sample_accounts, sample_payment):
        """Test creating journal entry for payment"""
        service = PaymentAccountingService(db_session)
        
        # Create journal entry for payment
        journal_entry = service.create_journal_entry_for_payment(sample_payment.id)
        
        assert journal_entry is not None
        assert journal_entry.status == JournalEntryStatus.POSTED
        assert journal_entry.total_debit == sample_payment.amount
        assert journal_entry.total_credit == sample_payment.amount
        assert journal_entry.reference_type == "payment"
        assert journal_entry.reference_id == sample_payment.id
        
        # Check bridge record
        bridge = db_session.query(PaymentJournalEntry).filter(
            PaymentJournalEntry.payment_id == sample_payment.id
        ).first()
        
        assert bridge is not None
        assert bridge.journal_entry_id == journal_entry.id
        
        # Check journal entry lines
        lines = journal_entry.journal_entry_lines
        assert len(lines) == 2
        
        # Find debit and credit lines
        debit_line = next(line for line in lines if line.debit_amount > 0)
        credit_line = next(line for line in lines if line.credit_amount > 0)
        
        assert debit_line.account.account_code == "1112-01"  # Bank account
        assert credit_line.account.account_code == "4100-01"  # Revenue account
        assert debit_line.debit_amount == sample_payment.amount
        assert credit_line.credit_amount == sample_payment.amount
    
    def test_create_journal_entry_duplicate_payment(self, db_session, sample_accounts, sample_payment):
        """Test creating journal entry for payment that already has one"""
        service = PaymentAccountingService(db_session)
        
        # Create first journal entry
        service.create_journal_entry_for_payment(sample_payment.id)
        
        # Try to create second journal entry for same payment
        with pytest.raises(ValueError, match="Journal entry already exists"):
            service.create_journal_entry_for_payment(sample_payment.id)


class TestSpendingAccountingService:
    """Test cases for SpendingAccountingService"""
    
    def test_create_journal_entry_for_spending(self, db_session, sample_accounts, sample_expense_category):
        """Test creating journal entry for spending"""
        service = SpendingAccountingService(db_session)
        
        # Create spending record
        spending = SpendingRecord(
            amount=Decimal("500.00"),
            spending_date=datetime.now(),
            description="Test maintenance expense",
            expense_category_id=sample_expense_category.id,
            status="APPROVED",
            created_by=uuid4()
        )
        db_session.add(spending)
        db_session.commit()
        
        # Create journal entry for spending
        journal_entry = service.create_journal_entry_for_spending(spending.id)
        
        assert journal_entry is not None
        assert journal_entry.status == JournalEntryStatus.POSTED
        assert journal_entry.total_debit == spending.amount
        assert journal_entry.total_credit == spending.amount
        assert journal_entry.reference_type == "spending"
        assert journal_entry.reference_id == spending.id
        
        # Check bridge record
        bridge = db_session.query(SpendingJournalEntry).filter(
            SpendingJournalEntry.spending_record_id == spending.id
        ).first()
        
        assert bridge is not None
        assert bridge.journal_entry_id == journal_entry.id
        
        # Check journal entry lines
        lines = journal_entry.journal_entry_lines
        assert len(lines) == 2
        
        # Find debit and credit lines
        debit_line = next(line for line in lines if line.debit_amount > 0)
        credit_line = next(line for line in lines if line.credit_amount > 0)
        
        assert debit_line.account.account_code == "5320-05"  # Expense account
        assert credit_line.account.account_code == "1112-01"  # Bank account
        assert debit_line.debit_amount == spending.amount
        assert credit_line.credit_amount == spending.amount
    
    def test_create_journal_entry_unapproved_spending(self, db_session, sample_expense_category):
        """Test creating journal entry for unapproved spending should fail"""
        service = SpendingAccountingService(db_session)
        
        # Create unapproved spending record
        spending = SpendingRecord(
            amount=Decimal("500.00"),
            spending_date=datetime.now(),
            description="Test maintenance expense",
            expense_category_id=sample_expense_category.id,
            status="PENDING",  # Not approved
            created_by=uuid4()
        )
        db_session.add(spending)
        db_session.commit()
        
        # Try to create journal entry
        with pytest.raises(ValueError, match="Only approved spending records"):
            service.create_journal_entry_for_spending(spending.id)


class TestChartOfAccountsService:
    """Test cases for ChartOfAccountsService"""
    
    def test_create_account(self, db_session):
        """Test creating new account"""
        service = ChartOfAccountsService(db_session)
        
        account = service.create_account(
            account_code="1234-56",
            account_name="Test Account",
            account_type=AccountType.ASSET,
            balance_type=BalanceType.DEBIT,
            account_name_en="Test Account EN"
        )
        
        assert account is not None
        assert account.account_code == "1234-56"
        assert account.account_name == "Test Account"
        assert account.account_type == AccountType.ASSET
        assert account.balance_type == BalanceType.DEBIT
        assert account.is_active == True
    
    def test_create_duplicate_account_code(self, db_session, sample_accounts):
        """Test creating account with duplicate code should fail"""
        service = ChartOfAccountsService(db_session)
        
        with pytest.raises(ValueError, match="Account code .* already exists"):
            service.create_account(
                account_code="1112-01",  # Already exists
                account_name="Duplicate Account",
                account_type=AccountType.ASSET,
                balance_type=BalanceType.DEBIT
            )
    
    def test_get_account_by_code(self, db_session, sample_accounts):
        """Test getting account by code"""
        service = ChartOfAccountsService(db_session)
        
        account = service.get_account_by_code("1112-01")
        assert account is not None
        assert account.account_code == "1112-01"
        
        # Test non-existent account
        account = service.get_account_by_code("9999-99")
        assert account is None
    
    def test_get_accounts_by_type(self, db_session, sample_accounts):
        """Test getting accounts by type"""
        service = ChartOfAccountsService(db_session)
        
        asset_accounts = service.get_accounts_by_type(AccountType.ASSET)
        assert len(asset_accounts) == 1
        assert asset_accounts[0].account_code == "1112-01"
        
        revenue_accounts = service.get_accounts_by_type(AccountType.REVENUE)
        assert len(revenue_accounts) == 1
        assert revenue_accounts[0].account_code == "4100-01"


class TestReportingService:
    """Test cases for ReportingService"""
    
    def test_trial_balance_empty(self, db_session, sample_period):
        """Test trial balance with no transactions"""
        service = ReportingService(db_session)
        
        trial_balance = service.get_trial_balance(sample_period.id)
        
        assert trial_balance is not None
        assert trial_balance['items'] == []
        assert trial_balance['total_debits'] == Decimal('0')
        assert trial_balance['total_credits'] == Decimal('0')
        assert trial_balance['is_balanced'] == True
    
    def test_trial_balance_with_transactions(self, db_session, sample_accounts, sample_period):
        """Test trial balance with transactions"""
        # Create general ledger entries
        bank_gl = GeneralLedger(
            account_id=sample_accounts["1112-01"].id,
            period_id=sample_period.id,
            beginning_balance=Decimal("0"),
            ending_balance=Decimal("1000.00"),
            debit_total=Decimal("1000.00"),
            credit_total=Decimal("0")
        )
        
        revenue_gl = GeneralLedger(
            account_id=sample_accounts["4100-01"].id,
            period_id=sample_period.id,
            beginning_balance=Decimal("0"),
            ending_balance=Decimal("1000.00"),
            debit_total=Decimal("0"),
            credit_total=Decimal("1000.00")
        )
        
        db_session.add(bank_gl)
        db_session.add(revenue_gl)
        db_session.commit()
        
        service = ReportingService(db_session)
        trial_balance = service.get_trial_balance(sample_period.id)
        
        assert len(trial_balance['items']) == 2
        assert trial_balance['total_debits'] == Decimal('1000.00')
        assert trial_balance['total_credits'] == Decimal('1000.00')
        assert trial_balance['is_balanced'] == True
        
        # Check individual items
        items = {item['account_code']: item for item in trial_balance['items']}
        
        assert items['1112-01']['debit_balance'] == Decimal('1000.00')
        assert items['1112-01']['credit_balance'] is None
        
        assert items['4100-01']['credit_balance'] == Decimal('1000.00')
        assert items['4100-01']['debit_balance'] is None


class TestIntegrationScenarios:
    """Integration test scenarios"""
    
    def test_complete_payment_to_journal_flow(self, db_session, sample_accounts, sample_payment):
        """Test complete flow from payment to journal entry to general ledger"""
        # Create journal entry for payment
        payment_service = PaymentAccountingService(db_session)
        journal_entry = payment_service.create_journal_entry_for_payment(sample_payment.id)
        
        # Verify journal entry is posted
        assert journal_entry.status == JournalEntryStatus.POSTED
        
        # Verify general ledger is updated
        bank_gl = db_session.query(GeneralLedger).filter(
            GeneralLedger.account_id == sample_accounts["1112-01"].id
        ).first()
        
        revenue_gl = db_session.query(GeneralLedger).filter(
            GeneralLedger.account_id == sample_accounts["4100-01"].id
        ).first()
        
        assert bank_gl.ending_balance == sample_payment.amount
        assert revenue_gl.ending_balance == sample_payment.amount
        
        # Verify trial balance is balanced
        reporting_service = ReportingService(db_session)
        trial_balance = reporting_service.get_trial_balance()
        
        assert trial_balance['is_balanced'] == True
        assert trial_balance['total_debits'] == trial_balance['total_credits']
    
    def test_multiple_transactions_balance(self, db_session, sample_accounts, sample_payment, sample_expense_category):
        """Test multiple transactions maintain balance"""
        # Create payment journal entry
        payment_service = PaymentAccountingService(db_session)
        payment_service.create_journal_entry_for_payment(sample_payment.id)
        
        # Create spending record and journal entry
        spending = SpendingRecord(
            amount=Decimal("300.00"),
            spending_date=datetime.now(),
            description="Test expense",
            expense_category_id=sample_expense_category.id,
            status="APPROVED",
            created_by=uuid4()
        )
        db_session.add(spending)
        db_session.commit()
        
        spending_service = SpendingAccountingService(db_session)
        spending_service.create_journal_entry_for_spending(spending.id)
        
        # Check final balances
        reporting_service = ReportingService(db_session)
        trial_balance = reporting_service.get_trial_balance()
        
        assert trial_balance['is_balanced'] == True
        
        # Bank account should have: +2000 (payment) -300 (spending) = 1700
        bank_item = next(item for item in trial_balance['items'] if item['account_code'] == '1112-01')
        assert bank_item['debit_balance'] == Decimal('1700.00')
        
        # Revenue account should have: +2000 (payment) = 2000
        revenue_item = next(item for item in trial_balance['items'] if item['account_code'] == '4100-01')
        assert revenue_item['credit_balance'] == Decimal('2000.00')
        
        # Expense account should have: +300 (spending) = 300
        expense_item = next(item for item in trial_balance['items'] if item['account_code'] == '5320-05')
        assert expense_item['debit_balance'] == Decimal('300.00')


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v"])

