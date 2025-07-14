"""
Test enum validation to prevent enum errors in dev/staging
"""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.invoice import InvoiceStatus, InvoiceType
from app.models.payment import PaymentMethod
from app.core.database import Base

class TestEnumValidation:
    """Test enum validation against database schema"""
    
    @pytest.fixture(scope="class")
    def db_engine(self):
        """Create test database engine"""
        engine = create_engine(settings.DATABASE_URL)
        return engine
    
    @pytest.fixture(scope="class")
    def db_session(self, db_engine):
        """Create test database session"""
        SessionLocal = sessionmaker(bind=db_engine)
        session = SessionLocal()
        yield session
        session.close()
    
    def test_invoice_status_enum_values(self, db_session):
        """Test that all InvoiceStatus enum values are valid in database"""
        for status in InvoiceStatus:
            try:
                # Test if enum value can be cast to database enum type
                result = db_session.execute(text(f"SELECT '{status.value}'::invoicestatus"))
                assert result is not None, f"InvoiceStatus.{status.name} ('{status.value}') is not valid in database"
                print(f"✅ InvoiceStatus.{status.name} = '{status.value}' is valid")
            except Exception as e:
                pytest.fail(f"❌ InvoiceStatus.{status.name} ('{status.value}') failed: {e}")
    
    def test_invoice_type_enum_values(self, db_session):
        """Test that all InvoiceType enum values are valid in database"""
        for invoice_type in InvoiceType:
            try:
                # Test if enum value can be cast to database enum type
                result = db_session.execute(text(f"SELECT '{invoice_type.value}'::invoicetype"))
                assert result is not None, f"InvoiceType.{invoice_type.name} ('{invoice_type.value}') is not valid in database"
                print(f"✅ InvoiceType.{invoice_type.name} = '{invoice_type.value}' is valid")
            except Exception as e:
                pytest.fail(f"❌ InvoiceType.{invoice_type.name} ('{invoice_type.value}') failed: {e}")
    
    def test_payment_method_enum_values(self, db_session):
        """Test that all PaymentMethod enum values are valid in database"""
        for method in PaymentMethod:
            try:
                # Test if enum value can be cast to database enum type
                result = db_session.execute(text(f"SELECT '{method.value}'::paymentmethod"))
                assert result is not None, f"PaymentMethod.{method.name} ('{method.value}') is not valid in database"
                print(f"✅ PaymentMethod.{method.name} = '{method.value}' is valid")
            except Exception as e:
                pytest.fail(f"❌ PaymentMethod.{method.name} ('{method.value}') failed: {e}")
    
    def test_enum_case_consistency(self):
        """Test that enum values follow consistent case convention"""
        # All enum values should be lowercase
        for status in InvoiceStatus:
            assert status.value.islower(), f"InvoiceStatus.{status.name} value '{status.value}' should be lowercase"
        
        for invoice_type in InvoiceType:
            assert invoice_type.value.islower(), f"InvoiceType.{invoice_type.name} value '{invoice_type.value}' should be lowercase"
        
        for method in PaymentMethod:
            assert method.value.islower(), f"PaymentMethod.{method.name} value '{method.value}' should be lowercase"
    
    def test_enum_no_spaces(self):
        """Test that enum values don't contain spaces"""
        for status in InvoiceStatus:
            assert ' ' not in status.value, f"InvoiceStatus.{status.name} value '{status.value}' should not contain spaces"
        
        for invoice_type in InvoiceType:
            assert ' ' not in invoice_type.value, f"InvoiceType.{invoice_type.name} value '{invoice_type.value}' should not contain spaces"
        
        for method in PaymentMethod:
            assert ' ' not in method.value, f"PaymentMethod.{method.name} value '{method.value}' should not contain spaces"

class TestDashboardAPIEnumUsage:
    """Test that dashboard API uses enum values correctly"""
    
    def test_dashboard_uses_enum_constants(self):
        """Test that dashboard API uses enum constants instead of string literals"""
        # Read dashboard.py file
        with open('/home/ubuntu/smart-village-management-system/backend/app/api/v1/endpoints/dashboard.py', 'r') as f:
            content = f.read()
        
        # Check that InvoiceStatus enum is imported
        assert 'from app.models.invoice import Invoice, InvoiceStatus' in content, "InvoiceStatus should be imported"
        
        # Check that enum constants are used instead of string literals
        assert 'InvoiceStatus.PAID' in content, "Should use InvoiceStatus.PAID instead of string literal"
        assert 'InvoiceStatus.PENDING' in content, "Should use InvoiceStatus.PENDING instead of string literal"
        
        # Check that string literals are NOT used
        assert 'status == "paid"' not in content, "Should not use string literal 'paid'"
        assert 'status == "pending"' not in content, "Should not use string literal 'pending'"

if __name__ == "__main__":
    # Run tests manually for debugging
    import sys
    sys.path.append('/home/ubuntu/smart-village-management-system/backend')
    
    test_instance = TestEnumValidation()
    
    # Mock session for manual testing
    class MockSession:
        def execute(self, query):
            print(f"Would execute: {query}")
            return True
    
    mock_session = MockSession()
    
    print("Testing enum case consistency...")
    test_instance.test_enum_case_consistency()
    print("✅ Enum case consistency test passed")
    
    print("\nTesting enum no spaces...")
    test_instance.test_enum_no_spaces()
    print("✅ Enum no spaces test passed")
    
    print("\nTesting dashboard API enum usage...")
    dashboard_test = TestDashboardAPIEnumUsage()
    dashboard_test.test_dashboard_uses_enum_constants()
    print("✅ Dashboard API enum usage test passed")

