"""
Bank Statement Models - สำหรับการกระทบยอดธนาคาร
"""
import uuid
from datetime import datetime, date
from enum import Enum
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Numeric, Boolean, JSON, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class BankStatementStatus(Enum):
    """สถานะของ Bank Statement"""
    UPLOADED = "uploaded"           # อัปโหลดแล้ว
    OCR_PROCESSING = "ocr_processing"  # กำลังประมวลผล OCR
    OCR_SUCCESS = "ocr_success"     # OCR สำเร็จ
    OCR_FAILED = "ocr_failed"       # OCR ล้มเหลว
    RECONCILING = "reconciling"     # กำลังกระทบยอด
    RECONCILED = "reconciled"       # กระทบยอดเสร็จ
    PARTIALLY_RECONCILED = "partially_reconciled"  # กระทบยอดบางส่วน


class ReconciliationStatus(Enum):
    """สถานะการกระทบยอดแต่ละรายการ"""
    UNMATCHED = "unmatched"         # ยังไม่จับคู่
    AUTO_MATCHED = "auto_matched"   # จับคู่อัตโนมัติ
    MANUAL_MATCHED = "manual_matched"  # จับคู่ด้วยตนเอง
    DISPUTED = "disputed"           # มีข้อโต้แย้ง
    CONFIRMED = "confirmed"         # ยืนยันแล้ว


class BankStatement(Base):
    """
    Bank Statement Model - ไฟล์ statement ธนาคาร
    """
    __tablename__ = "bank_statements"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Statement Information
    statement_number = Column(String(50), unique=True, nullable=False, index=True)
    bank_name = Column(String(100), nullable=False)
    account_number = Column(String(50), nullable=False)
    account_name = Column(String(200), nullable=False)
    
    # Statement Period
    statement_date = Column(Date, nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    # Balance Information
    opening_balance = Column(Numeric(15, 2), nullable=True)
    closing_balance = Column(Numeric(15, 2), nullable=True)
    
    # File Information
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=False, index=True)  # SHA-256 for duplicate detection
    file_size = Column(Numeric(10, 0), nullable=True)
    file_mime_type = Column(String(100), nullable=True)
    
    # OCR Results
    ocr_raw_data = Column(JSON, nullable=True)  # Raw OCR output
    ocr_confidence_score = Column(Numeric(3, 2), nullable=True)
    ocr_processed_at = Column(DateTime, nullable=True)
    
    # Status and Processing
    status = Column(String(30), nullable=False, default=BankStatementStatus.UPLOADED.value)
    total_transactions = Column(Numeric(5, 0), nullable=True)  # Number of transactions found
    
    # Upload Information
    uploaded_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    village_id = Column(UUID(as_uuid=True), ForeignKey("villages.id"), nullable=False)
    
    # Processing Notes
    processing_notes = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # Relationships
    uploaded_by = relationship("User", back_populates="uploaded_bank_statements")
    village = relationship("Village", back_populates="bank_statements")
    transactions = relationship("BankTransaction", back_populates="statement", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<BankStatement {self.statement_number}: {self.bank_name} ({self.period_start} - {self.period_end})>"
    
    @property
    def is_processed(self) -> bool:
        """Check if statement is fully processed"""
        return self.status in [
            BankStatementStatus.RECONCILED.value,
            BankStatementStatus.PARTIALLY_RECONCILED.value
        ]
    
    @property
    def reconciliation_summary(self) -> dict:
        """Get reconciliation summary"""
        if not self.transactions:
            return {"total": 0, "matched": 0, "unmatched": 0, "percentage": 0}
        
        total = len(self.transactions)
        matched = len([t for t in self.transactions if t.is_reconciled])
        unmatched = total - matched
        percentage = (matched / total * 100) if total > 0 else 0
        
        return {
            "total": total,
            "matched": matched,
            "unmatched": unmatched,
            "percentage": round(percentage, 2)
        }


class BankTransaction(Base):
    """
    Bank Transaction Model - รายการธุรกรรมในแต่ละ statement
    """
    __tablename__ = "bank_transactions"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Statement Reference
    statement_id = Column(UUID(as_uuid=True), ForeignKey("bank_statements.id"), nullable=False)
    
    # Transaction Information
    transaction_date = Column(Date, nullable=False)
    transaction_time = Column(String(10), nullable=True)  # HH:MM format
    description = Column(Text, nullable=False)
    reference_number = Column(String(100), nullable=True)
    
    # Amount Information
    debit_amount = Column(Numeric(15, 2), nullable=True)   # เงินออก
    credit_amount = Column(Numeric(15, 2), nullable=True)  # เงินเข้า
    balance = Column(Numeric(15, 2), nullable=True)        # ยอดคงเหลือ
    
    # Transaction Details
    channel = Column(String(50), nullable=True)  # ATM, Internet Banking, etc.
    location = Column(String(200), nullable=True)
    
    # OCR Information
    ocr_confidence = Column(Numeric(3, 2), nullable=True)
    ocr_raw_text = Column(Text, nullable=True)
    
    # Reconciliation
    reconciliation_status = Column(String(20), nullable=False, default=ReconciliationStatus.UNMATCHED.value)
    matched_payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"), nullable=True)
    match_confidence = Column(Numeric(3, 2), nullable=True)  # Confidence of auto-match
    
    # Manual Review
    reviewed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # Relationships
    statement = relationship("BankStatement", back_populates="transactions")
    matched_payment = relationship("Payment", back_populates="bank_transaction")
    reviewed_by = relationship("User", back_populates="reviewed_bank_transactions")
    
    def __repr__(self):
        amount = self.credit_amount or self.debit_amount or 0
        return f"<BankTransaction {self.transaction_date}: ฿{amount} - {self.description[:50]}>"
    
    @property
    def transaction_amount(self) -> float:
        """Get transaction amount (credit or debit)"""
        return float(self.credit_amount or self.debit_amount or 0)
    
    @property
    def is_credit(self) -> bool:
        """Check if transaction is credit (money in)"""
        return self.credit_amount is not None and self.credit_amount > 0
    
    @property
    def is_debit(self) -> bool:
        """Check if transaction is debit (money out)"""
        return self.debit_amount is not None and self.debit_amount > 0
    
    @property
    def is_reconciled(self) -> bool:
        """Check if transaction is reconciled"""
        return self.reconciliation_status in [
            ReconciliationStatus.AUTO_MATCHED.value,
            ReconciliationStatus.MANUAL_MATCHED.value,
            ReconciliationStatus.CONFIRMED.value
        ]
    
    @property
    def display_amount(self) -> str:
        """Get formatted amount with +/- prefix"""
        if self.is_credit:
            return f"+฿{self.credit_amount:,.2f}"
        elif self.is_debit:
            return f"-฿{self.debit_amount:,.2f}"
        return "฿0.00"


class ReconciliationRule(Base):
    """
    Reconciliation Rule Model - กฎสำหรับการจับคู่อัตโนมัติ
    """
    __tablename__ = "reconciliation_rules"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Rule Information
    rule_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    priority = Column(Numeric(3, 0), default=100, nullable=False)  # Lower number = higher priority
    
    # Matching Criteria
    amount_tolerance = Column(Numeric(5, 2), default=0.00, nullable=False)  # Amount difference tolerance
    date_tolerance_days = Column(Numeric(3, 0), default=0, nullable=False)  # Date difference tolerance
    
    # Text Matching
    description_keywords = Column(JSON, nullable=True)  # Keywords to match in description
    reference_pattern = Column(String(200), nullable=True)  # Regex pattern for reference matching
    
    # Village and Bank Specific
    village_id = Column(UUID(as_uuid=True), ForeignKey("villages.id"), nullable=True)
    bank_name = Column(String(100), nullable=True)
    
    # Rule Statistics
    total_matches = Column(Numeric(10, 0), default=0, nullable=False)
    successful_matches = Column(Numeric(10, 0), default=0, nullable=False)
    
    # Management
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # Relationships
    village = relationship("Village", back_populates="reconciliation_rules")
    created_by = relationship("User", back_populates="created_reconciliation_rules")
    
    def __repr__(self):
        return f"<ReconciliationRule {self.rule_name}: {self.successful_matches}/{self.total_matches} matches>"
    
    @property
    def success_rate(self) -> float:
        """Calculate rule success rate"""
        if self.total_matches == 0:
            return 0.0
        return float(self.successful_matches) / float(self.total_matches) * 100

