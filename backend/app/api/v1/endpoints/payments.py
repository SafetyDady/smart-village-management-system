"""
Payment API Endpoints - Smart Village Management System
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.services.payment_service import PaymentService
from app.models.payment import Payment, PaymentStatus
from app.schemas.payment import (
    PaymentCreate,
    PaymentResponse,
    PaymentUpdate,
    PaymentApproval
)
from app.core.auth import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new payment"""
    try:
        payment_service = PaymentService(db)
        payment = payment_service.create_payment(
            property_id=payment_data.property_id,
            amount=float(payment_data.amount),
            payment_method=payment_data.payment_method,
            reference_number=payment_data.reference_number,
            notes=payment_data.notes,
            received_by_id=current_user.id,
            auto_allocate=payment_data.auto_allocate
        )
        
        logger.info(f"Payment {payment.id} created by user {current_user.id}")
        return payment
        
    except Exception as e:
        logger.error(f"Failed to create payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payment by ID"""
    payment_service = PaymentService(db)
    payment = payment_service.get_payment_by_id(payment_id)
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return payment


@router.get("/", response_model=List[PaymentResponse])
async def list_payments(
    property_id: Optional[str] = None,
    status_filter: Optional[PaymentStatus] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List payments with optional filters"""
    payment_service = PaymentService(db)
    
    if property_id:
        payments = payment_service.get_payments_by_property(
            property_id=property_id,
            limit=limit,
            offset=offset
        )
    else:
        # Get all payments (admin only)
        payments = payment_service.get_all_payments(limit=limit, offset=offset)
    
    # Filter by status if provided
    if status_filter:
        payments = [p for p in payments if p.status == status_filter]
    
    return payments


@router.post("/{payment_id}/approve", response_model=PaymentResponse)
async def approve_payment(
    payment_id: str,
    approval_data: PaymentApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Approve a pending payment
    
    This endpoint will:
    1. Update payment status to CONFIRMED
    2. Create journal entry automatically (if accounting is enabled)
    3. Auto-allocate to invoices using FIFO
    """
    try:
        payment_service = PaymentService(db)
        payment = payment_service.approve_payment(
            payment_id=payment_id,
            approved_by_id=current_user.id
        )
        
        logger.info(f"Payment {payment_id} approved by user {current_user.id}")
        return payment
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to approve payment {payment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve payment"
        )


@router.post("/{payment_id}/reject", response_model=PaymentResponse)
async def reject_payment(
    payment_id: str,
    rejection_data: PaymentApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reject a pending payment"""
    try:
        payment_service = PaymentService(db)
        payment = payment_service.reject_payment(
            payment_id=payment_id,
            rejected_by_id=current_user.id,
            reason=rejection_data.notes
        )
        
        logger.info(f"Payment {payment_id} rejected by user {current_user.id}")
        return payment
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to reject payment {payment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reject payment"
        )


@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: str,
    payment_data: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update payment details (only for pending payments)"""
    payment_service = PaymentService(db)
    payment = payment_service.get_payment_by_id(payment_id)
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    if payment.status != PaymentStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only update pending payments"
        )
    
    # Update payment fields
    for field, value in payment_data.dict(exclude_unset=True).items():
        setattr(payment, field, value)
    
    db.commit()
    db.refresh(payment)
    
    logger.info(f"Payment {payment_id} updated by user {current_user.id}")
    return payment


@router.delete("/{payment_id}")
async def delete_payment(
    payment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete payment (only for pending payments)"""
    payment_service = PaymentService(db)
    payment = payment_service.get_payment_by_id(payment_id)
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    if payment.status != PaymentStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only delete pending payments"
        )
    
    payment.archived = True
    db.commit()
    
    logger.info(f"Payment {payment_id} deleted by user {current_user.id}")
    return {"message": "Payment deleted successfully"}


@router.get("/{payment_id}/allocations")
async def get_payment_allocations(
    payment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payment allocations to invoices"""
    payment_service = PaymentService(db)
    payment = payment_service.get_payment_by_id(payment_id)
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return {
        "payment_id": payment_id,
        "total_amount": payment.amount,
        "allocated_amount": payment.allocated_amount,
        "unallocated_amount": payment.unallocated_amount,
        "allocations": [
            {
                "invoice_id": alloc.invoice_id,
                "amount": alloc.amount,
                "created_at": alloc.created_at
            }
            for alloc in payment.payment_invoices
        ]
    }


@router.post("/{payment_id}/allocate")
async def manual_allocate_payment(
    payment_id: str,
    allocation_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually allocate payment to specific invoice"""
    try:
        payment_service = PaymentService(db)
        allocation = payment_service.allocate_payment_to_invoice(
            payment_id=payment_id,
            invoice_id=allocation_data["invoice_id"],
            amount=allocation_data["amount"]
        )
        
        logger.info(f"Manual allocation created for payment {payment_id} by user {current_user.id}")
        return allocation
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to allocate payment {payment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to allocate payment"
        )

