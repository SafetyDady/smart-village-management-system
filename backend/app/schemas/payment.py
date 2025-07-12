"""
Payment Schemas - Smart Village Management System
"""
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from uuid import UUID

from app.models.payment import PaymentMethod, PaymentStatus


class PaymentBase(BaseModel):
    """Base payment schema"""
    property_id: int
    amount: Decimal = Field(..., gt=0, description="Payment amount must be positive")
    payment_method: PaymentMethod
    reference_number: Optional[str] = None
    notes: Optional[str] = None


class PaymentCreate(PaymentBase):
    """Schema for creating a payment"""
    auto_allocate: bool = True
    payment_date: Optional[datetime] = None


class PaymentUpdate(BaseModel):
    """Schema for updating a payment"""
    amount: Optional[Decimal] = Field(None, gt=0)
    payment_method: Optional[PaymentMethod] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None


class PaymentApproval(BaseModel):
    """Schema for payment approval/rejection"""
    notes: Optional[str] = None


class PaymentResponse(PaymentBase):
    """Schema for payment response"""
    id: UUID
    status: PaymentStatus
    payment_date: datetime
    bank_reference: Optional[str] = None
    
    # Audit fields
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    # Approval fields
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    rejected_by_id: Optional[int] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    # Calculated fields
    allocated_amount: Decimal
    unallocated_amount: Decimal
    fully_allocated: bool
    
    archived: bool = False

    class Config:
        from_attributes = True


class PaymentAllocation(BaseModel):
    """Schema for payment allocation"""
    invoice_id: UUID
    amount: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentSummary(BaseModel):
    """Schema for payment summary"""
    total_payments: int
    total_amount: Decimal
    total_allocated: Decimal
    total_unallocated: Decimal
    payment_methods: dict


class PaymentListResponse(BaseModel):
    """Schema for paginated payment list"""
    payments: List[PaymentResponse]
    total: int
    limit: int
    offset: int

