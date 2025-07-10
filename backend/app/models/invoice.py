"""
Invoice Model - Smart Village Management System
"""

import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Numeric, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from app.core.database import Base


class InvoiceStatus(PyEnum):
    """Invoice status enumeration"""
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELED = "canceled"


class InvoiceType(PyEnum):
    """Invoice type enumeration"""
    MONTHLY_FEE = "monthly_fee"
    PENALTY = "penalty"
    CUSTOM = "custom"


class Invoice(Base):
    """Invoice model for billing management"""
    
    __tablename__ = "invoices"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Property relationship
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False, index=True)
    
    # Invoice details
    amount = Column(Numeric(12, 2), nullable=False)
    due_date = Column(DateTime, nullable=False)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.PENDING, nullable=False)
    invoice_type = Column(Enum(InvoiceType), default=InvoiceType.MONTHLY_FEE, nullable=False)
    
    # Timestamps
    issued_at = Column(DateTime, default=func.now(), nullable=False)
    paid_at = Column(DateTime, nullable=True)
    
    # Soft delete
    archived = Column(Boolean, default=False, nullable=False)
    
    # Audit fields
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Additional fields
    description = Column(Text, nullable=True)
    reference_number = Column(String(100), nullable=True, unique=True)
    
    # Relationships
    property_obj = relationship("Property", back_populates="invoices")
    created_by_user = relationship("User", foreign_keys=[created_by])
    updated_by_user = relationship("User", foreign_keys=[updated_by])
    
    # Many-to-many relationship with payments
    payment_invoices = relationship("PaymentInvoice", back_populates="invoice")
    
    def __repr__(self):
        return f"<Invoice(id={self.id}, property_id={self.property_id}, amount={self.amount}, status={self.status})>"
    
    @property
    def overdue(self) -> bool:
        """Check if invoice is overdue"""
        from datetime import datetime
        return self.due_date < datetime.now() and self.status == InvoiceStatus.PENDING
    
    @property
    def paid_amount(self) -> float:
        """Calculate total paid amount for this invoice"""
        total = 0
        for payment_invoice in self.payment_invoices:
            total += float(payment_invoice.amount)
        return total
    
    @property
    def remaining_amount(self) -> float:
        """Calculate remaining amount to be paid"""
        return float(self.amount) - self.paid_amount
    
    @property
    def fully_paid(self) -> bool:
        """Check if invoice is fully paid"""
        return self.remaining_amount <= 0

