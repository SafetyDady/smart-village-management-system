"""
Payment Report Model - รายงานการชำระเงินจากลูกบ้าน
"""
import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Numeric, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class PaymentReportStatus(Enum):
    """สถานะของรายงานการชำระเงิน"""
    PENDING = "pending"           # รอการตรวจสอบ
    OCR_PROCESSING = "ocr_processing"  # กำลังประมวลผล OCR
    OCR_SUCCESS = "ocr_success"   # OCR สำเร็จ
    OCR_FAILED = "ocr_failed"     # OCR ล้มเหลว
    UNDER_REVIEW = "under_review" # อยู่ระหว่างการตรวจสอบ
    APPROVED = "approved"         # อนุมัติแล้ว
    REJECTED = "rejected"         # ปฏิเสธ
    DUPLICATE = "duplicate"       # slip ซ้ำ
    PROCESSED = "processed"       # ประมวลผลเสร็จแล้ว


class PaymentReportType(Enum):
    """ประเภทของรายงานการชำระเงิน"""
    BANK_TRANSFER = "bank_transfer"
    MOBILE_BANKING = "mobile_banking"
    QR_PAYMENT = "qr_payment"
    CASH_DEPOSIT = "cash_deposit"
    OTHER = "other"


class PaymentReport(Base):
    """
    Payment Report Model - รายงานการชำระเงินจากลูกบ้าน
    
    ลูกบ้านสามารถอัปโหลด slip และระบบจะใช้ AI OCR อ่านข้อมูลอัตโนมัติ
    """
    __tablename__ = "payment_reports"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Report Information
    report_number = Column(String(50), unique=True, nullable=False, index=True)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"), nullable=False)
    reported_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Payment Information (from OCR or manual input)
    reported_amount = Column(Numeric(10, 2), nullable=False)
    reported_date = Column(DateTime, nullable=False)
    payment_type = Column(String(20), nullable=False)  # PaymentReportType enum
    
    # OCR Results
    ocr_extracted_data = Column(JSON, nullable=True)  # Raw OCR data
    ocr_amount = Column(Numeric(10, 2), nullable=True)  # Amount from OCR
    ocr_date = Column(DateTime, nullable=True)  # Date from OCR
    ocr_time = Column(String(10), nullable=True)  # Time from OCR (HH:MM format)
    ocr_bank_name = Column(String(100), nullable=True)  # Bank name from OCR
    ocr_reference = Column(String(100), nullable=True)  # Reference number from OCR
    ocr_confidence_score = Column(Numeric(3, 2), nullable=True)  # OCR confidence (0.00-1.00)
    
    # Slip Information
    slip_file_path = Column(String(500), nullable=False)  # Path to uploaded slip
    slip_file_hash = Column(String(64), nullable=False, index=True)  # SHA-256 hash for duplicate detection
    slip_file_size = Column(Numeric(10, 0), nullable=True)  # File size in bytes
    slip_mime_type = Column(String(100), nullable=True)  # MIME type (image/jpeg, etc.)
    
    # Status and Workflow
    status = Column(String(20), nullable=False, default=PaymentReportStatus.PENDING.value)
    notes = Column(Text, nullable=True)  # Notes from user or admin
    admin_notes = Column(Text, nullable=True)  # Internal admin notes
    
    # Approval Information
    reviewed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Processing Information
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"), nullable=True)  # Created payment after approval
    processed_at = Column(DateTime, nullable=True)
    
    # Duplicate Detection
    is_duplicate = Column(Boolean, default=False, nullable=False)
    duplicate_of_id = Column(UUID(as_uuid=True), ForeignKey("payment_reports.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # Relationships
    property_obj = relationship("Property", back_populates="payment_reports")
    reported_by = relationship("User", foreign_keys=[reported_by_id], back_populates="payment_reports")
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id], back_populates="reviewed_payment_reports")
    payment = relationship("Payment", back_populates="payment_report")
    
    # Self-referential relationship for duplicates
    duplicate_of = relationship("PaymentReport", remote_side=[id], back_populates="duplicates")
    duplicates = relationship("PaymentReport", back_populates="duplicate_of")
    
    def __repr__(self):
        return f"<PaymentReport {self.report_number}: ฿{self.reported_amount} - {self.status}>"
    
    @property
    def is_ocr_processed(self) -> bool:
        """Check if OCR processing is completed"""
        return self.status in [
            PaymentReportStatus.OCR_SUCCESS.value,
            PaymentReportStatus.OCR_FAILED.value,
            PaymentReportStatus.UNDER_REVIEW.value,
            PaymentReportStatus.APPROVED.value,
            PaymentReportStatus.REJECTED.value,
            PaymentReportStatus.PROCESSED.value
        ]
    
    @property
    def is_pending_review(self) -> bool:
        """Check if report is pending admin review"""
        return self.status in [
            PaymentReportStatus.OCR_SUCCESS.value,
            PaymentReportStatus.UNDER_REVIEW.value
        ]
    
    @property
    def is_approved(self) -> bool:
        """Check if report is approved"""
        return self.status == PaymentReportStatus.APPROVED.value
    
    @property
    def is_processed(self) -> bool:
        """Check if report is fully processed"""
        return self.status == PaymentReportStatus.PROCESSED.value
    
    @property
    def ocr_data_matches_reported(self) -> bool:
        """Check if OCR data matches reported data"""
        if not self.ocr_amount or not self.ocr_date:
            return False
        
        # Check amount (allow 1% tolerance)
        amount_diff = abs(float(self.ocr_amount) - float(self.reported_amount))
        amount_tolerance = float(self.reported_amount) * 0.01
        amount_matches = amount_diff <= amount_tolerance
        
        # Check date (same day)
        date_matches = (
            self.ocr_date.date() == self.reported_date.date()
            if self.ocr_date and self.reported_date else False
        )
        
        return amount_matches and date_matches
    
    @property
    def final_amount(self) -> float:
        """Get the final amount to use (OCR if available and matches, otherwise reported)"""
        if self.ocr_amount and self.ocr_data_matches_reported:
            return float(self.ocr_amount)
        return float(self.reported_amount)
    
    @property
    def final_date(self) -> datetime:
        """Get the final date to use (OCR if available and matches, otherwise reported)"""
        if self.ocr_date and self.ocr_data_matches_reported:
            return self.ocr_date
        return self.reported_date

