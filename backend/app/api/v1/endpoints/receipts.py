"""
Receipt API Endpoints - Smart Village Management System
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.receipt import Receipt
from app.models.payment import Payment
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

router = APIRouter()

# Pydantic schemas
class ReceiptBase(BaseModel):
    payment_id: uuid.UUID
    receipt_number: str = Field(..., min_length=1, max_length=100)
    notes: Optional[str] = None

class ReceiptCreate(ReceiptBase):
    pass

class ReceiptUpdate(BaseModel):
    receipt_number: Optional[str] = Field(None, min_length=1, max_length=100)
    notes: Optional[str] = None

class ReceiptResponse(ReceiptBase):
    id: uuid.UUID
    issued_at: datetime
    created_by: int
    created_at: datetime
    archived: bool
    
    # Computed properties from payment
    property_id: Optional[int]
    amount: float
    payment_method: Optional[str]
    
    class Config:
        from_attributes = True

class ReceiptListResponse(BaseModel):
    receipts: List[ReceiptResponse]
    total: int
    page: int
    per_page: int

# API Endpoints
@router.get("/", response_model=ReceiptListResponse)
async def get_receipts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    property_id: Optional[int] = Query(None, description="Filter by property ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of receipts with filtering and pagination"""
    
    query = db.query(Receipt).filter(Receipt.archived == False)
    
    # Apply property filter if specified
    if property_id:
        query = query.join(Payment).filter(Payment.property_id == property_id)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    receipts = query.offset(skip).limit(limit).all()
    
    return ReceiptListResponse(
        receipts=receipts,
        total=total,
        page=(skip // limit) + 1,
        per_page=limit
    )

@router.get("/{receipt_id}", response_model=ReceiptResponse)
async def get_receipt(
    receipt_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific receipt by ID"""
    
    receipt = db.query(Receipt).filter(
        and_(Receipt.id == receipt_id, Receipt.archived == False)
    ).first()
    
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found"
        )
    
    return receipt

@router.get("/number/{receipt_number}", response_model=ReceiptResponse)
async def get_receipt_by_number(
    receipt_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific receipt by receipt number"""
    
    receipt = db.query(Receipt).filter(
        and_(Receipt.receipt_number == receipt_number, Receipt.archived == False)
    ).first()
    
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found"
        )
    
    return receipt

@router.post("/", response_model=ReceiptResponse, status_code=status.HTTP_201_CREATED)
async def create_receipt(
    receipt_data: ReceiptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new receipt"""
    
    # Verify payment exists
    payment = db.query(Payment).filter(Payment.id == receipt_data.payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Check if receipt already exists for this payment
    existing_receipt = db.query(Receipt).filter(Receipt.payment_id == receipt_data.payment_id).first()
    if existing_receipt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Receipt already exists for this payment"
        )
    
    # Check for duplicate receipt number
    existing_number = db.query(Receipt).filter(
        Receipt.receipt_number == receipt_data.receipt_number
    ).first()
    if existing_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Receipt number already exists"
        )
    
    # Create receipt
    receipt = Receipt(
        **receipt_data.dict(),
        created_by=current_user.id
    )
    
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    
    return receipt

@router.put("/{receipt_id}", response_model=ReceiptResponse)
async def update_receipt(
    receipt_id: uuid.UUID,
    receipt_data: ReceiptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing receipt"""
    
    receipt = db.query(Receipt).filter(
        and_(Receipt.id == receipt_id, Receipt.archived == False)
    ).first()
    
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found"
        )
    
    # Check for duplicate receipt number
    if receipt_data.receipt_number and receipt_data.receipt_number != receipt.receipt_number:
        existing = db.query(Receipt).filter(
            Receipt.receipt_number == receipt_data.receipt_number
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Receipt number already exists"
            )
    
    # Update fields
    update_data = receipt_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(receipt, field, value)
    
    db.commit()
    db.refresh(receipt)
    
    return receipt

@router.delete("/{receipt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_receipt(
    receipt_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a receipt (archive it)"""
    
    receipt = db.query(Receipt).filter(
        and_(Receipt.id == receipt_id, Receipt.archived == False)
    ).first()
    
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found"
        )
    
    # Soft delete
    receipt.archived = True
    
    db.commit()
    
    return None

@router.get("/payment/{payment_id}", response_model=ReceiptResponse)
async def get_receipt_by_payment(
    payment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get receipt for a specific payment"""
    
    # Verify payment exists
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    receipt = db.query(Receipt).filter(
        and_(Receipt.payment_id == payment_id, Receipt.archived == False)
    ).first()
    
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found for this payment"
        )
    
    return receipt

@router.get("/property/{property_id}", response_model=List[ReceiptResponse])
async def get_receipts_by_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all receipts for a specific property"""
    
    receipts = db.query(Receipt).join(Payment).filter(
        and_(
            Payment.property_id == property_id,
            Receipt.archived == False
        )
    ).all()
    
    return receipts

@router.post("/generate-number")
async def generate_receipt_number(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a unique receipt number"""
    
    # Get current year and month
    now = datetime.now()
    year_month = now.strftime("%Y%m")
    
    # Find the highest receipt number for this month
    prefix = f"RCP-{year_month}-"
    latest_receipt = db.query(Receipt).filter(
        Receipt.receipt_number.like(f"{prefix}%")
    ).order_by(Receipt.receipt_number.desc()).first()
    
    if latest_receipt:
        # Extract sequence number and increment
        try:
            last_seq = int(latest_receipt.receipt_number.split("-")[-1])
            next_seq = last_seq + 1
        except (ValueError, IndexError):
            next_seq = 1
    else:
        next_seq = 1
    
    # Generate new receipt number
    receipt_number = f"{prefix}{next_seq:04d}"
    
    return {"receipt_number": receipt_number}

@router.get("/{receipt_id}/download")
async def download_receipt(
    receipt_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download receipt as PDF (placeholder for future implementation)"""
    
    receipt = db.query(Receipt).filter(
        and_(Receipt.id == receipt_id, Receipt.archived == False)
    ).first()
    
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found"
        )
    
    # TODO: Implement PDF generation
    return {
        "message": "PDF generation not implemented yet",
        "receipt_id": receipt.id,
        "receipt_number": receipt.receipt_number
    }

