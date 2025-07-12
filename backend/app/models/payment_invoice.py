"""
PaymentInvoice Model - Smart Village Management System
Many-to-many relationship between payments and invoices
"""

import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class PaymentInvoice(Base):
    """Payment-Invoice association model for many-to-many relationship"""
    
    __tablename__ = "payment_invoices"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign keys
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"), nullable=False, index=True)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False, index=True)
    
    # Allocation amount (partial payment support)
    amount = Column(Numeric(12, 2), nullable=False)
    
    # Timestamps
    allocated_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    payment = relationship("Payment", back_populates="payment_invoices")
    invoice = relationship("Invoice", back_populates="payment_invoices")
    
    def __repr__(self):
        return f"<PaymentInvoice(payment_id={self.payment_id}, invoice_id={self.invoice_id}, amount={self.amount})>"

