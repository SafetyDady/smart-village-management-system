"""
Bank Account Model - จัดการบัญชีธนาคารของหมู่บ้าน
"""
import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Numeric, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class BankAccountStatus(Enum):
    """สถานะของบัญชีธนาคาร"""
    ACTIVE = "active"           # ใช้งานอยู่
    INACTIVE = "inactive"       # ไม่ใช้งาน
    CLOSED = "closed"          # ปิดบัญชีแล้ว


class BankAccountType(Enum):
    """ประเภทบัญชีธนาคาร"""
    SAVINGS = "savings"         # บัญชีออมทรัพย์
    CURRENT = "current"         # บัญชีกระแสรายวัน
    FIXED_DEPOSIT = "fixed_deposit"  # บัญชีเงินฝากประจำ


class BankAccount(Base):
    """
    Bank Account Model - บัญชีธนาคารของหมู่บ้าน
    จำกัดไม่เกิน 2 บัญชีต่อหมู่บ้าน
    """
    __tablename__ = "bank_accounts"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Account Information
    account_number = Column(String(50), nullable=False, unique=True, index=True)
    account_name = Column(String(200), nullable=False)
    bank_name = Column(String(100), nullable=False)
    bank_code = Column(String(10), nullable=True)  # ธกส, กสิกร, SCB, etc.
    branch_name = Column(String(200), nullable=True)
    branch_code = Column(String(10), nullable=True)
    
    # Account Details
    account_type = Column(String(20), nullable=False, default=BankAccountType.SAVINGS.value)
    currency = Column(String(3), nullable=False, default="THB")
    
    # Village Association
    village_id = Column(UUID(as_uuid=True), ForeignKey("villages.id"), nullable=False)
    
    # Account Status
    status = Column(String(20), nullable=False, default=BankAccountStatus.ACTIVE.value)
    is_primary = Column(Boolean, default=False, nullable=False)  # บัญชีหลัก
    
    # Balance Information (for reference only)
    last_known_balance = Column(Numeric(15, 2), nullable=True)
    balance_as_of = Column(DateTime, nullable=True)
    
    # Account Management
    opened_date = Column(DateTime, nullable=True)
    closed_date = Column(DateTime, nullable=True)
    
    # Contact Information
    contact_person = Column(String(200), nullable=True)  # ผู้ติดต่อ
    contact_phone = Column(String(20), nullable=True)
    
    # Additional Information
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Management
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # Relationships
    village = relationship("Village", back_populates="bank_accounts")
    created_by = relationship("User", back_populates="created_bank_accounts")
    bank_statements = relationship("BankStatement", back_populates="bank_account", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="bank_account")
    
    def __repr__(self):
        return f"<BankAccount {self.bank_name} {self.account_number}: {self.account_name}>"
    
    @property
    def masked_account_number(self) -> str:
        """Get masked account number for display"""
        if len(self.account_number) <= 4:
            return self.account_number
        return f"***{self.account_number[-4:]}"
    
    @property
    def display_name(self) -> str:
        """Get display name for account"""
        return f"{self.bank_name} {self.masked_account_number}"
    
    @property
    def is_active(self) -> bool:
        """Check if account is active"""
        return self.status == BankAccountStatus.ACTIVE.value
    
    @property
    def latest_statement(self):
        """Get latest bank statement for this account"""
        if self.bank_statements:
            return max(self.bank_statements, key=lambda s: s.period_end)
        return None
    
    @property
    def total_statements(self) -> int:
        """Get total number of statements uploaded"""
        return len(self.bank_statements)
    
    @property
    def reconciliation_summary(self) -> dict:
        """Get reconciliation summary for this account"""
        if not self.bank_statements:
            return {"total_statements": 0, "reconciled": 0, "pending": 0}
        
        reconciled = len([s for s in self.bank_statements if s.is_processed])
        pending = len(self.bank_statements) - reconciled
        
        return {
            "total_statements": len(self.bank_statements),
            "reconciled": reconciled,
            "pending": pending,
            "last_reconciled": self.latest_statement.period_end if self.latest_statement and self.latest_statement.is_processed else None
        }


# Update BankStatement model to include bank_account_id
# This would be added to the existing BankStatement model:
"""
class BankStatement(Base):
    # ... existing fields ...
    
    # Add this field:
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey("bank_accounts.id"), nullable=False)
    
    # Add this relationship:
    bank_account = relationship("BankAccount", back_populates="bank_statements")
"""

# Update Payment model to include bank_account_id  
# This would be added to the existing Payment model:
"""
class Payment(Base):
    # ... existing fields ...
    
    # Add this field:
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey("bank_accounts.id"), nullable=True)
    
    # Add this relationship:
    bank_account = relationship("BankAccount", back_populates="payments")
"""

