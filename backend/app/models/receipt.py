"""
Receipt Model - Smart Village Management System
"""

import uuid
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Receipt(Base):
    """Receipt model for payment receipts"""
    
    __tablename__ = "receipts"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Payment relationship (one-to-one)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"), nullable=False, unique=True, index=True)
    
    # Receipt details
    receipt_number = Column(String(100), nullable=False, unique=True, index=True)
    issued_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Audit fields
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Additional information
    notes = Column(Text, nullable=True)
    
    # Soft delete
    archived = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    payment = relationship("Payment", back_populates="receipt")
    created_by_user = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<Receipt(id={self.id}, receipt_number={self.receipt_number}, payment_id={self.payment_id})>"
    
    @property
    def property_id(self) -> int:
        """Get property ID from related payment"""
        return self.payment.property_id if self.payment else None
    
    @property
    def amount(self) -> float:
        """Get payment amount from related payment"""
        return float(self.payment.amount) if self.payment else 0.0
    
    @property
    def payment_method(self) -> str:
        """Get payment method from related payment"""
        return self.payment.method.value if self.payment else None

