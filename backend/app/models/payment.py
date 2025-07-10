"""
Payment Model - Smart Village Management System
"""

import uuid
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from app.core.database import Base


class PaymentMethod(PyEnum):
    """Payment method enumeration"""
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"
    QR_CODE = "qr"
    CREDIT_CARD = "credit_card"
    MOBILE_BANKING = "mobile_banking"


class Payment(Base):
    """Payment model for tracking payments"""
    
    __tablename__ = "payments"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Property relationship
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False, index=True)
    
    # Payment details
    amount = Column(Numeric(12, 2), nullable=False)
    payment_date = Column(DateTime, nullable=False)
    method = Column(Enum(PaymentMethod), nullable=False)
    note = Column(Text, nullable=True)
    
    # Reference information
    reference_number = Column(String(100), nullable=True)
    bank_reference = Column(String(100), nullable=True)
    
    # Audit fields
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Soft delete
    archived = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    property_obj = relationship("Property", back_populates="payments")
    created_by_user = relationship("User", foreign_keys=[created_by])
    
    # Many-to-many relationship with invoices
    payment_invoices = relationship("PaymentInvoice", back_populates="payment")
    
    # One-to-one relationship with receipt
    receipt = relationship("Receipt", back_populates="payment", uselist=False)
    
    def __repr__(self):
        return f"<Payment(id={self.id}, property_id={self.property_id}, amount={self.amount}, method={self.method})>"
    
    @property
    def allocated_amount(self) -> float:
        """Calculate total allocated amount to invoices"""
        total = 0
        for payment_invoice in self.payment_invoices:
            total += float(payment_invoice.amount)
        return total
    
    @property
    def unallocated_amount(self) -> float:
        """Calculate unallocated amount"""
        return float(self.amount) - self.allocated_amount
    
    @property
    def fully_allocated(self) -> bool:
        """Check if payment is fully allocated to invoices"""
        return self.unallocated_amount <= 0

