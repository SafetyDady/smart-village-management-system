"""
Payment API Endpoints - Smart Village Management System
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.payment import Payment, PaymentMethod
from app.models.property import Property
from app.models.payment_invoice import PaymentInvoice
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
import uuid

router = APIRouter()

# Pydantic schemas
class PaymentBase(BaseModel):
    property_id: int
    amount: Decimal = Field(..., gt=0, description="Payment amount must be positive")
    payment_date: datetime
    method: PaymentMethod
    note: Optional[str] = None
    reference_number: Optional[str] = None
    bank_reference: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0)
    payment_date: Optional[datetime] = None
    method: Optional[PaymentMethod] = None
    note: Optional[str] = None
    reference_number: Optional[str] = None
    bank_reference: Optional[str] = None

class PaymentResponse(PaymentBase):
    id: uuid.UUID
    created_by: int
    created_at: datetime
    updated_at: datetime
    archived: bool
    
    # Computed properties
    allocated_amount: float
    unallocated_amount: float
    fully_allocated: bool
    
    class Config:
        from_attributes = True

class PaymentListResponse(BaseModel):
    payments: List[PaymentResponse]
    total: int
    page: int
    per_page: int

class PaymentAllocationRequest(BaseModel):
    invoice_id: uuid.UUID
    amount: Decimal = Field(..., gt=0, description="Allocation amount must be positive")

# API Endpoints
@router.get("/", response_model=PaymentListResponse)
async def get_payments(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    property_id: Optional[int] = Query(None, description="Filter by property ID"),
    method: Optional[PaymentMethod] = Query(None, description="Filter by payment method"),
    unallocated_only: bool = Query(False, description="Show only unallocated payments"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of payments with filtering and pagination"""
    
    query = db.query(Payment).filter(Payment.archived == False)
    
    # Apply filters
    if property_id:
        query = query.filter(Payment.property_id == property_id)
    
    if method:
        query = query.filter(Payment.method == method)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    payments = query.offset(skip).limit(limit).all()
    
    # Filter unallocated if requested (done in Python due to computed property)
    if unallocated_only:
        payments = [p for p in payments if p.unallocated_amount > 0]
        total = len(payments)
    
    return PaymentListResponse(
        payments=payments,
        total=total,
        page=(skip // limit) + 1,
        per_page=limit
    )

@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific payment by ID"""
    
    payment = db.query(Payment).filter(
        and_(Payment.id == payment_id, Payment.archived == False)
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return payment

@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new payment"""
    
    # Verify property exists
    property_obj = db.query(Property).filter(Property.id == payment_data.property_id).first()
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Create payment
    payment = Payment(
        **payment_data.dict(),
        created_by=current_user.id
    )
    
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    return payment

@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: uuid.UUID,
    payment_data: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing payment"""
    
    payment = db.query(Payment).filter(
        and_(Payment.id == payment_id, Payment.archived == False)
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Update fields
    update_data = payment_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(payment, field, value)
    
    db.commit()
    db.refresh(payment)
    
    return payment

@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(
    payment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a payment (archive it)"""
    
    payment = db.query(Payment).filter(
        and_(Payment.id == payment_id, Payment.archived == False)
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Check if payment has allocations
    if payment.payment_invoices:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete payment with invoice allocations"
        )
    
    # Soft delete
    payment.archived = True
    
    db.commit()
    
    return None

@router.post("/{payment_id}/allocate", response_model=PaymentResponse)
async def allocate_payment_to_invoice(
    payment_id: uuid.UUID,
    allocation: PaymentAllocationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Allocate payment amount to a specific invoice"""
    
    payment = db.query(Payment).filter(
        and_(Payment.id == payment_id, Payment.archived == False)
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Check if payment has enough unallocated amount
    if payment.unallocated_amount < float(allocation.amount):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Allocation amount exceeds unallocated payment amount"
        )
    
    # Verify invoice exists and belongs to same property
    from app.models.invoice import Invoice
    invoice = db.query(Invoice).filter(Invoice.id == allocation.invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    if invoice.property_id != payment.property_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice and payment must belong to the same property"
        )
    
    # Check if invoice needs this amount
    if invoice.remaining_amount < float(allocation.amount):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Allocation amount exceeds invoice remaining amount"
        )
    
    # Create payment-invoice allocation
    payment_invoice = PaymentInvoice(
        payment_id=payment.id,
        invoice_id=allocation.invoice_id,
        amount=allocation.amount,
        created_by=current_user.id
    )
    
    db.add(payment_invoice)
    db.commit()
    db.refresh(payment)
    
    return payment

@router.get("/property/{property_id}", response_model=List[PaymentResponse])
async def get_payments_by_property(
    property_id: int,
    method: Optional[PaymentMethod] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all payments for a specific property"""
    
    # Verify property exists
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    query = db.query(Payment).filter(
        and_(
            Payment.property_id == property_id,
            Payment.archived == False
        )
    )
    
    if method:
        query = query.filter(Payment.method == method)
    
    payments = query.all()
    return payments

@router.get("/{payment_id}/allocations")
async def get_payment_allocations(
    payment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all invoice allocations for a payment"""
    
    payment = db.query(Payment).filter(
        and_(Payment.id == payment_id, Payment.archived == False)
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    allocations = []
    for payment_invoice in payment.payment_invoices:
        allocations.append({
            "invoice_id": payment_invoice.invoice_id,
            "amount": float(payment_invoice.amount),
            "allocated_at": payment_invoice.created_at
        })
    
    return {
        "payment_id": payment.id,
        "total_amount": float(payment.amount),
        "allocated_amount": payment.allocated_amount,
        "unallocated_amount": payment.unallocated_amount,
        "allocations": allocations
    }

