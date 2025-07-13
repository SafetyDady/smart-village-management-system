"""
Invoice API Endpoints - Smart Village Management System
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.invoice import Invoice, InvoiceStatus, InvoiceType
from app.models.property import Property
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
import uuid

router = APIRouter()

# Pydantic schemas
class InvoiceBase(BaseModel):
    property_id: int
    amount: Decimal = Field(..., gt=0, description="Invoice amount must be positive")
    due_date: datetime
    invoice_type: InvoiceType = InvoiceType.MONTHLY_FEE
    description: Optional[str] = None
    reference_number: Optional[str] = None

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0)
    due_date: Optional[datetime] = None
    status: Optional[InvoiceStatus] = None
    invoice_type: Optional[InvoiceType] = None
    description: Optional[str] = None
    reference_number: Optional[str] = None

class InvoiceResponse(InvoiceBase):
    id: uuid.UUID
    status: InvoiceStatus
    issued_at: datetime
    paid_at: Optional[datetime] = None
    archived: bool
    created_by: int
    updated_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    # Computed properties
    overdue_status: bool
    paid_amount: float
    remaining_amount: float
    fully_paid: bool
    
    class Config:
        from_attributes = True

class InvoiceListResponse(BaseModel):
    invoices: List[InvoiceResponse]
    total: int
    page: int
    per_page: int

# API Endpoints
@router.get("/", response_model=InvoiceListResponse)
async def get_invoices(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    status: Optional[InvoiceStatus] = Query(None, description="Filter by invoice status"),
    property_id: Optional[int] = Query(None, description="Filter by property ID"),
    overdue_only: bool = Query(False, description="Show only overdue invoices"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of invoices with filtering and pagination"""
    
    query = db.query(Invoice).filter(Invoice.archived == False)
    
    # Apply filters
    if status:
        query = query.filter(Invoice.status == status)
    
    if property_id:
        query = query.filter(Invoice.property_id == property_id)
    
    if overdue_only:
        query = query.filter(
            and_(
                Invoice.due_date < datetime.now(),
                Invoice.status == InvoiceStatus.PENDING
            )
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    invoices = query.offset(skip).limit(limit).all()
    
    return InvoiceListResponse(
        invoices=invoices,
        total=total,
        page=(skip // limit) + 1,
        per_page=limit
    )

@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific invoice by ID"""
    
    invoice = db.query(Invoice).filter(
        and_(Invoice.id == invoice_id, Invoice.archived == False)
    ).first()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    return invoice

@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new invoice"""
    
    # Verify property exists
    property_obj = db.query(Property).filter(Property.id == invoice_data.property_id).first()
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check for duplicate reference number
    if invoice_data.reference_number:
        existing = db.query(Invoice).filter(
            Invoice.reference_number == invoice_data.reference_number
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reference number already exists"
            )
    
    # Create invoice
    invoice = Invoice(
        **invoice_data.dict(),
        created_by=current_user.id,
        status=InvoiceStatus.PENDING
    )
    
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    
    return invoice

@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: uuid.UUID,
    invoice_data: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing invoice"""
    
    invoice = db.query(Invoice).filter(
        and_(Invoice.id == invoice_id, Invoice.archived == False)
    ).first()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    # Check for duplicate reference number
    if invoice_data.reference_number and invoice_data.reference_number != invoice.reference_number:
        existing = db.query(Invoice).filter(
            Invoice.reference_number == invoice_data.reference_number
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reference number already exists"
            )
    
    # Update fields
    update_data = invoice_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(invoice, field, value)
    
    invoice.updated_by = current_user.id
    
    db.commit()
    db.refresh(invoice)
    
    return invoice

@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete an invoice (archive it)"""
    
    invoice = db.query(Invoice).filter(
        and_(Invoice.id == invoice_id, Invoice.archived == False)
    ).first()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    # Check if invoice has payments
    if invoice.payment_invoices:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete invoice with associated payments"
        )
    
    # Soft delete
    invoice.archived = True
    invoice.updated_by = current_user.id
    
    db.commit()
    
    return None

@router.patch("/{invoice_id}/status", response_model=InvoiceResponse)
async def update_invoice_status(
    invoice_id: uuid.UUID,
    status: InvoiceStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update invoice status"""
    
    invoice = db.query(Invoice).filter(
        and_(Invoice.id == invoice_id, Invoice.archived == False)
    ).first()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    invoice.status = status
    if status == InvoiceStatus.PAID:
        invoice.paid_at = datetime.now()
    
    invoice.updated_by = current_user.id
    
    db.commit()
    db.refresh(invoice)
    
    return invoice

@router.get("/property/{property_id}", response_model=List[InvoiceResponse])
async def get_invoices_by_property(
    property_id: int,
    status: Optional[InvoiceStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all invoices for a specific property"""
    
    # Verify property exists
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    query = db.query(Invoice).filter(
        and_(
            Invoice.property_id == property_id,
            Invoice.archived == False
        )
    )
    
    if status:
        query = query.filter(Invoice.status == status)
    
    invoices = query.all()
    return invoices

