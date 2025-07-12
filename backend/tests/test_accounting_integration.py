"""
Integration Tests for Village Accounting ERP System
"""
import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db
from app.models.village import Village
from app.models.property import Property
from app.models.user import User
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.accounting import (
    ChartOfAccounts, JournalEntry, JournalEntryLine, 
    GeneralLedger, PaymentJournalEntry, AccountingPeriod
)
from app.services.payment_service import PaymentService
from app.services.accounting_service import AccountingService


class TestPaymentAccountingIntegration:
    """Test integration between Payment and Accounting systems"""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)
    
    @pytest.fixture
    def db_session(self):
        """Database session for testing"""
        db = next(get_db())
        yield db
        db.close()
    
    @pytest.fixture
    def sample_village(self, db_session: Session):
        """Create sample village"""
        village = Village(
            name="Test Village",
            code="TV001",
            address="123 Test Street",
            city="Test City",
            postal_code="12345",
            phone="123-456-7890"
        )
        db_session.add(village)
        db_session.commit()
        db_session.refresh(village)
        return village
    
    @pytest.fixture
    def sample_user(self, db_session: Session):
        """Create sample user"""
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            hashed_password="hashedpassword123",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    
    @pytest.fixture
    def sample_property(self, db_session: Session, sample_village: Village):
        """Create sample property"""
        property_obj = Property(
            property_number="P001",
            owner_name="John Doe",
            owner_phone="123-456-7890",
            village_id=sample_village.id,
            area_sqm=Decimal('100.00'),
            monthly_fee=Decimal('500.00')
        )
        db_session.add(property_obj)
        db_session.commit()
        db_session.refresh(property_obj)
        return property_obj
    
    @pytest.fixture
    def accounting_service(self, db_session: Session):
        """Accounting service instance"""
        return AccountingService(db_session)
    
    @pytest.fixture
    def payment_service(self, db_session: Session):
        """Payment service instance"""
        return PaymentService(db_session)
    
    def test_payment_approval_creates_journal_entry(
        self, 
        db_session: Session, 
        sample_property: Property, 
        sample_user: User,
        payment_service: PaymentService,
        accounting_service: AccountingService
    ):
        """Test that approving a payment creates a journal entry"""
        
        # Create a pending payment
        payment = Payment(
            property_id=sample_property.id,
            amount=Decimal('1000.00'),
            payment_date=datetime.now(),
            method=PaymentMethod.BANK_TRANSFER,
            status=PaymentStatus.PENDING,
            reference_number="PAY001",
            created_by=sample_user.id
        )
        db_session.add(payment)
        db_session.commit()
        db_session.refresh(payment)
        
        # Count journal entries before approval
        initial_entry_count = db_session.query(JournalEntry).count()
        
        # Approve the payment
        approved_payment = payment_service.approve_payment(
            payment_id=str(payment.id),
            approved_by_id=str(sample_user.id)
        )
        
        # Verify payment status changed
        assert approved_payment.status == PaymentStatus.CONFIRMED
        assert approved_payment.approved_by_id == sample_user.id
        assert approved_payment.approved_at is not None
        
        # Verify journal entry was created
        final_entry_count = db_session.query(JournalEntry).count()
        assert final_entry_count == initial_entry_count + 1
        
        # Get the created journal entry
        journal_entry = db_session.query(JournalEntry).filter(
            JournalEntry.entry_type == "PAYMENT"
        ).first()
        
        assert journal_entry is not None
        assert journal_entry.total_amount == Decimal('1000.00')
        assert len(journal_entry.lines) == 2  # Debit and Credit
        
        # Verify journal entry lines
        debit_line = next((line for line in journal_entry.lines if line.debit_amount), None)
        credit_line = next((line for line in journal_entry.lines if line.credit_amount), None)
        
        assert debit_line is not None
        assert credit_line is not None
        assert debit_line.debit_amount == Decimal('1000.00')
        assert credit_line.credit_amount == Decimal('1000.00')
        
        # Verify bridge table entry
        bridge_entry = db_session.query(PaymentJournalEntry).filter(
            PaymentJournalEntry.payment_id == payment.id
        ).first()
        
        assert bridge_entry is not None
        assert bridge_entry.journal_entry_id == journal_entry.id
    
    def test_payment_rejection_no_journal_entry(
        self,
        db_session: Session,
        sample_property: Property,
        sample_user: User,
        payment_service: PaymentService
    ):
        """Test that rejecting a payment does not create a journal entry"""
        
        # Create a pending payment
        payment = Payment(
            property_id=sample_property.id,
            amount=Decimal('1000.00'),
            payment_date=datetime.now(),
            method=PaymentMethod.BANK_TRANSFER,
            status=PaymentStatus.PENDING,
            reference_number="PAY002",
            created_by=sample_user.id
        )
        db_session.add(payment)
        db_session.commit()
        db_session.refresh(payment)
        
        # Count journal entries before rejection
        initial_entry_count = db_session.query(JournalEntry).count()
        
        # Reject the payment
        rejected_payment = payment_service.reject_payment(
            payment_id=str(payment.id),
            rejected_by_id=str(sample_user.id),
            reason="Invalid payment"
        )
        
        # Verify payment status changed
        assert rejected_payment.status == PaymentStatus.CANCELLED
        assert rejected_payment.rejected_by_id == sample_user.id
        assert rejected_payment.rejection_reason == "Invalid payment"
        
        # Verify no journal entry was created
        final_entry_count = db_session.query(JournalEntry).count()
        assert final_entry_count == initial_entry_count
    
    def test_general_ledger_updated_after_journal_entry(
        self,
        db_session: Session,
        sample_property: Property,
        sample_user: User,
        payment_service: PaymentService,
        accounting_service: AccountingService
    ):
        """Test that general ledger is updated after journal entry creation"""
        
        # Create and approve a payment
        payment = Payment(
            property_id=sample_property.id,
            amount=Decimal('1500.00'),
            payment_date=datetime.now(),
            method=PaymentMethod.BANK_TRANSFER,
            status=PaymentStatus.PENDING,
            reference_number="PAY003",
            created_by=sample_user.id
        )
        db_session.add(payment)
        db_session.commit()
        db_session.refresh(payment)
        
        # Count general ledger entries before
        initial_gl_count = db_session.query(GeneralLedger).count()
        
        # Approve payment (should create journal entry and update GL)
        payment_service.approve_payment(
            payment_id=str(payment.id),
            approved_by_id=str(sample_user.id)
        )
        
        # Verify general ledger entries were created
        final_gl_count = db_session.query(GeneralLedger).count()
        assert final_gl_count >= initial_gl_count + 2  # At least 2 GL entries (Dr/Cr)
        
        # Get GL entries for this transaction
        journal_entry = db_session.query(JournalEntry).filter(
            JournalEntry.entry_type == "PAYMENT"
        ).first()
        
        gl_entries = db_session.query(GeneralLedger).filter(
            GeneralLedger.journal_entry_id == journal_entry.id
        ).all()
        
        assert len(gl_entries) == 2
        
        # Verify GL entry amounts
        total_debits = sum(entry.debit_amount or Decimal('0') for entry in gl_entries)
        total_credits = sum(entry.credit_amount or Decimal('0') for entry in gl_entries)
        
        assert total_debits == Decimal('1500.00')
        assert total_credits == Decimal('1500.00')
    
    def test_trial_balance_reflects_payment_transactions(
        self,
        db_session: Session,
        sample_property: Property,
        sample_user: User,
        payment_service: PaymentService,
        accounting_service: AccountingService
    ):
        """Test that trial balance reflects payment transactions"""
        
        # Create multiple payments
        payments = []
        amounts = [Decimal('1000.00'), Decimal('1500.00'), Decimal('2000.00')]
        
        for i, amount in enumerate(amounts):
            payment = Payment(
                property_id=sample_property.id,
                amount=amount,
                payment_date=datetime.now(),
                method=PaymentMethod.BANK_TRANSFER,
                status=PaymentStatus.PENDING,
                reference_number=f"PAY00{i+4}",
                created_by=sample_user.id
            )
            db_session.add(payment)
            db_session.commit()
            db_session.refresh(payment)
            payments.append(payment)
        
        # Approve all payments
        for payment in payments:
            payment_service.approve_payment(
                payment_id=str(payment.id),
                approved_by_id=str(sample_user.id)
            )
        
        # Generate trial balance
        trial_balance = accounting_service.generate_trial_balance(date.today())
        
        # Verify trial balance is balanced
        assert trial_balance.is_balanced
        assert trial_balance.total_debits == trial_balance.total_credits
        
        # Verify total amount matches our payments
        total_payment_amount = sum(amounts)
        assert trial_balance.total_debits >= total_payment_amount
    
    def test_multiple_payments_journal_entries_sequence(
        self,
        db_session: Session,
        sample_property: Property,
        sample_user: User,
        payment_service: PaymentService
    ):
        """Test sequence of multiple payment approvals"""
        
        # Create multiple payments
        payment_amounts = [Decimal('500.00'), Decimal('750.00'), Decimal('1000.00')]
        payments = []
        
        for i, amount in enumerate(payment_amounts):
            payment = Payment(
                property_id=sample_property.id,
                amount=amount,
                payment_date=datetime.now() - timedelta(days=i),
                method=PaymentMethod.BANK_TRANSFER,
                status=PaymentStatus.PENDING,
                reference_number=f"SEQ00{i+1}",
                created_by=sample_user.id
            )
            db_session.add(payment)
            db_session.commit()
            db_session.refresh(payment)
            payments.append(payment)
        
        # Approve payments in sequence
        journal_entries = []
        for payment in payments:
            initial_count = db_session.query(JournalEntry).count()
            
            payment_service.approve_payment(
                payment_id=str(payment.id),
                approved_by_id=str(sample_user.id)
            )
            
            final_count = db_session.query(JournalEntry).count()
            assert final_count == initial_count + 1
            
            # Get the latest journal entry
            latest_entry = db_session.query(JournalEntry).order_by(
                JournalEntry.created_at.desc()
            ).first()
            journal_entries.append(latest_entry)
        
        # Verify all journal entries were created
        assert len(journal_entries) == len(payments)
        
        # Verify journal entry amounts match payment amounts
        for i, entry in enumerate(journal_entries):
            assert entry.total_amount == payment_amounts[i]
    
    def test_accounting_period_integration(
        self,
        db_session: Session,
        sample_property: Property,
        sample_user: User,
        payment_service: PaymentService,
        accounting_service: AccountingService
    ):
        """Test integration with accounting periods"""
        
        # Ensure current period exists
        current_period = accounting_service.get_current_period()
        if not current_period:
            current_period = accounting_service.create_period(
                name="Test Period",
                start_date=date.today().replace(day=1),
                end_date=date.today().replace(day=28)
            )
        
        # Create and approve payment
        payment = Payment(
            property_id=sample_property.id,
            amount=Decimal('2000.00'),
            payment_date=datetime.now(),
            method=PaymentMethod.BANK_TRANSFER,
            status=PaymentStatus.PENDING,
            reference_number="PERIOD001",
            created_by=sample_user.id
        )
        db_session.add(payment)
        db_session.commit()
        db_session.refresh(payment)
        
        # Approve payment
        payment_service.approve_payment(
            payment_id=str(payment.id),
            approved_by_id=str(sample_user.id)
        )
        
        # Verify journal entry is in current period
        journal_entry = db_session.query(JournalEntry).filter(
            JournalEntry.entry_type == "PAYMENT"
        ).order_by(JournalEntry.created_at.desc()).first()
        
        assert journal_entry is not None
        assert current_period.start_date <= journal_entry.entry_date <= current_period.end_date


class TestAccountingAPIIntegration:
    """Test Accounting API endpoints integration"""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)
    
    def test_chart_of_accounts_api(self, client: TestClient):
        """Test Chart of Accounts API endpoint"""
        response = client.get("/api/v1/accounting/accounts")
        
        # Should return 200 even if no accounts exist
        assert response.status_code in [200, 401]  # 401 if auth required
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_journal_entries_api(self, client: TestClient):
        """Test Journal Entries API endpoint"""
        response = client.get("/api/v1/accounting/journal-entries")
        
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_trial_balance_api(self, client: TestClient):
        """Test Trial Balance API endpoint"""
        response = client.get("/api/v1/accounting/trial-balance")
        
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            data = response.json()
            assert "as_of_date" in data
            assert "accounts" in data
            assert "total_debits" in data
            assert "total_credits" in data
            assert "is_balanced" in data
    
    def test_accounting_health_check(self, client: TestClient):
        """Test accounting health check endpoint"""
        response = client.get("/api/v1/accounting/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data


class TestAccountingDataIntegrity:
    """Test accounting data integrity"""
    
    @pytest.fixture
    def db_session(self):
        """Database session for testing"""
        db = next(get_db())
        yield db
        db.close()
    
    @pytest.fixture
    def accounting_service(self, db_session: Session):
        """Accounting service instance"""
        return AccountingService(db_session)
    
    def test_journal_entry_balance_validation(
        self,
        db_session: Session,
        accounting_service: AccountingService
    ):
        """Test that journal entries must be balanced"""
        
        # Try to create unbalanced journal entry
        with pytest.raises(ValueError, match="balanced"):
            accounting_service.create_journal_entry(
                description="Unbalanced entry",
                entry_type="MANUAL",
                lines=[
                    {
                        "account_code": "1111-00",
                        "description": "Debit entry",
                        "debit_amount": Decimal('1000.00'),
                        "credit_amount": None
                    },
                    {
                        "account_code": "4100-01",
                        "description": "Credit entry",
                        "debit_amount": None,
                        "credit_amount": Decimal('500.00')  # Unbalanced!
                    }
                ]
            )
    
    def test_duplicate_account_code_prevention(
        self,
        db_session: Session,
        accounting_service: AccountingService
    ):
        """Test that duplicate account codes are prevented"""
        
        # This should work (assuming account doesn't exist)
        try:
            accounting_service.create_account(
                account_code="9999-99",
                account_name="Test Account",
                account_type="ASSET",
                balance_type="DEBIT"
            )
        except ValueError:
            pass  # Account might already exist
        
        # This should fail (duplicate)
        with pytest.raises(ValueError, match="already exists"):
            accounting_service.create_account(
                account_code="9999-99",
                account_name="Duplicate Account",
                account_type="ASSET",
                balance_type="DEBIT"
            )

