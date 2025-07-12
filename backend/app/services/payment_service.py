"""
Payment Service - Business Logic for Payment Management with FIFO Allocation
"""
from typing import List, Optional, Tuple
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import logging

from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.invoice import Invoice, InvoiceStatus
from app.models.payment_invoice import PaymentInvoice
from app.models.property import Property
from app.services.invoice_service import InvoiceService

# Import accounting service for journal entry creation
try:
    from app.services.accounting_service import AccountingService
except ImportError:
    AccountingService = None

# Import logging and audit trail
from app.core.logging import accounting_logger, audit_logger

logger = logging.getLogger(__name__)


class PaymentService:
    """Service class for Payment business logic with FIFO allocation"""
    
    def __init__(self, db: Session):
        self.db = db
        self.invoice_service = InvoiceService(db)
        # Initialize accounting service if available
        self.accounting_service = AccountingService(db) if AccountingService else None
    
    def create_payment(
        self,
        property_id: str,
        amount: float,
        payment_method: PaymentMethod,
        reference_number: Optional[str] = None,
        notes: Optional[str] = None,
        received_by_id: Optional[str] = None,
        auto_allocate: bool = True
    ) -> Payment:
        """
        Create a new payment and optionally auto-allocate to invoices using FIFO
        
        Args:
            property_id: Property UUID
            amount: Payment amount
            payment_method: Payment method (CASH, BANK_TRANSFER, etc.)
            reference_number: Payment reference (bank transfer ref, etc.)
            notes: Additional notes
            received_by_id: User who received the payment
            auto_allocate: Whether to automatically allocate to invoices using FIFO
            
        Returns:
            Created Payment object
        """
        # Generate payment number
        payment_number = self._generate_payment_number()
        
        payment = Payment(
            payment_number=payment_number,
            property_id=property_id,
            amount=amount,
            payment_method=payment_method,
            reference_number=reference_number,
            notes=notes,
            status=PaymentStatus.CONFIRMED,
            received_by_id=received_by_id
        )
        
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        
        # Auto-allocate to invoices using FIFO if requested
        if auto_allocate:
            self.allocate_payment_fifo(payment.id)
        
        return payment
    
    def allocate_payment_fifo(self, payment_id: str) -> List[PaymentInvoice]:
        """
        Allocate payment to invoices using FIFO (First In, First Out) logic
        
        Args:
            payment_id: Payment UUID
            
        Returns:
            List of PaymentInvoice allocations created
        """
        payment = self.get_payment_by_id(payment_id)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        
        # Get pending invoices for this property (FIFO order: oldest first)
        pending_invoices = self.invoice_service.get_pending_invoices_by_property(
            payment.property_id
        )
        
        remaining_amount = float(payment.amount)
        allocations = []
        
        for invoice in pending_invoices:
            if remaining_amount <= 0:
                break
            
            # Calculate how much this invoice still needs
            outstanding = self.invoice_service.calculate_outstanding_amount(invoice.id)
            
            if outstanding <= 0:
                continue  # Invoice already fully paid
            
            # Allocate the minimum of remaining payment or outstanding invoice amount
            allocation_amount = min(remaining_amount, outstanding)
            
            # Create payment-invoice allocation
            payment_invoice = PaymentInvoice(
                payment_id=payment.id,
                invoice_id=invoice.id,
                amount=allocation_amount
            )
            
            self.db.add(payment_invoice)
            allocations.append(payment_invoice)
            
            remaining_amount -= allocation_amount
            
            # Check if invoice is now fully paid
            self.invoice_service.mark_invoice_as_paid_if_fully_allocated(invoice.id)
        
        # Update payment status
        if remaining_amount > 0:
            payment.status = PaymentStatus.PARTIALLY_ALLOCATED
        else:
            payment.status = PaymentStatus.FULLY_ALLOCATED
        
        self.db.commit()
        
        # Refresh all objects
        for allocation in allocations:
            self.db.refresh(allocation)
        
        return allocations
    
    def create_manual_allocation(
        self,
        payment_id: str,
        invoice_id: str,
        amount: float
    ) -> PaymentInvoice:
        """
        Manually allocate payment to specific invoice
        
        Args:
            payment_id: Payment UUID
            invoice_id: Invoice UUID
            amount: Amount to allocate
            
        Returns:
            PaymentInvoice allocation created
        """
        payment = self.get_payment_by_id(payment_id)
        invoice = self.invoice_service.get_invoice_by_id(invoice_id)
        
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        if not invoice:
            raise ValueError(f"Invoice {invoice_id} not found")
        
        # Validate allocation amount
        payment_unallocated = self.get_unallocated_amount(payment_id)
        invoice_outstanding = self.invoice_service.calculate_outstanding_amount(invoice_id)
        
        if amount > payment_unallocated:
            raise ValueError(f"Amount {amount} exceeds unallocated payment amount {payment_unallocated}")
        if amount > invoice_outstanding:
            raise ValueError(f"Amount {amount} exceeds invoice outstanding amount {invoice_outstanding}")
        
        # Create allocation
        payment_invoice = PaymentInvoice(
            payment_id=payment_id,
            invoice_id=invoice_id,
            amount=amount
        )
        
        self.db.add(payment_invoice)
        
        # Update statuses
        self._update_payment_status(payment_id)
        self.invoice_service.mark_invoice_as_paid_if_fully_allocated(invoice_id)
        
        self.db.commit()
        self.db.refresh(payment_invoice)
        
        return payment_invoice
    
    def get_payment_by_id(self, payment_id: str) -> Optional[Payment]:
        """Get payment by ID"""
        return self.db.query(Payment).filter(Payment.id == payment_id).first()
    
    def get_payments_by_property(
        self,
        property_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Payment]:
        """Get payments for a specific property"""
        return self.db.query(Payment).filter(
            Payment.property_id == property_id
        ).order_by(desc(Payment.created_at)).offset(offset).limit(limit).all()
    
    def get_unallocated_amount(self, payment_id: str) -> float:
        """Calculate unallocated amount for a payment"""
        payment = self.get_payment_by_id(payment_id)
        if not payment:
            return 0.0
        
        # Calculate total allocated amount
        total_allocated = sum(
            allocation.amount for allocation in payment.invoice_allocations
        )
        
        unallocated = payment.amount - total_allocated
        return max(0.0, unallocated)  # Never negative
    
    def get_unallocated_payments(self, property_id: Optional[str] = None) -> List[Payment]:
        """Get payments that have unallocated amounts"""
        query = self.db.query(Payment).filter(
            Payment.status.in_([PaymentStatus.CONFIRMED, PaymentStatus.PARTIALLY_ALLOCATED])
        )
        
        if property_id:
            query = query.filter(Payment.property_id == property_id)
        
        payments = query.all()
        
        # Filter payments that actually have unallocated amounts
        unallocated_payments = []
        for payment in payments:
            if self.get_unallocated_amount(payment.id) > 0:
                unallocated_payments.append(payment)
        
        return unallocated_payments
    
    def _update_payment_status(self, payment_id: str) -> None:
        """Update payment status based on allocation"""
        payment = self.get_payment_by_id(payment_id)
        if not payment:
            return
        
        unallocated = self.get_unallocated_amount(payment_id)
        
        if unallocated <= 0.01:  # Fully allocated (considering rounding)
            payment.status = PaymentStatus.FULLY_ALLOCATED
        elif unallocated < payment.amount:  # Partially allocated
            payment.status = PaymentStatus.PARTIALLY_ALLOCATED
        else:  # Not allocated
            payment.status = PaymentStatus.CONFIRMED
    
    def _generate_payment_number(self) -> str:
        """Generate unique payment number"""
        # Get current year and month
        now = datetime.now()
        year_month = now.strftime("%Y%m")
        
        # Count payments in current month
        count = self.db.query(Payment).filter(
            Payment.payment_number.like(f"PAY{year_month}%")
        ).count()
        
        # Generate number: PAY202501001, PAY202501002, etc.
        payment_number = f"PAY{year_month}{count + 1:03d}"
        
        return payment_number
    
    def get_payment_summary_by_property(self, property_id: str) -> dict:
        """Get payment summary for a property"""
        payments = self.get_payments_by_property(property_id, limit=1000)
        
        total_amount = sum(payment.amount for payment in payments)
        total_allocated = sum(
            sum(allocation.amount for allocation in payment.invoice_allocations)
            for payment in payments
        )
        total_unallocated = total_amount - total_allocated
        
        return {
            "total_payments": len(payments),
            "total_amount": total_amount,
            "total_allocated": total_allocated,
            "total_unallocated": total_unallocated,
            "payment_methods": self._get_payment_method_breakdown(payments)
        }
    
    def _get_payment_method_breakdown(self, payments: List[Payment]) -> dict:
        """Get breakdown of payments by method"""
        breakdown = {}
        for payment in payments:
            method = payment.payment_method.value
            if method not in breakdown:
                breakdown[method] = {"count": 0, "amount": 0.0}
            breakdown[method]["count"] += 1
            breakdown[method]["amount"] += payment.amount
        
        return breakdown
    
    def process_bulk_fifo_allocation(self, property_id: str) -> dict:
        """
        Process FIFO allocation for all unallocated payments in a property
        
        Args:
            property_id: Property UUID
            
        Returns:
            Summary of allocations processed
        """
        unallocated_payments = self.get_unallocated_payments(property_id)
        
        total_processed = 0
        total_amount = 0.0
        allocations_created = 0
        
        for payment in unallocated_payments:
            allocations = self.allocate_payment_fifo(payment.id)
            if allocations:
                total_processed += 1
                total_amount += sum(alloc.amount for alloc in allocations)
                allocations_created += len(allocations)
        
        return {
            "payments_processed": total_processed,
            "total_amount_allocated": total_amount,
            "allocations_created": allocations_created
        }


    def approve_payment(self, payment_id: str, approved_by_id: Optional[str] = None) -> Payment:
        """
        Approve a pending payment and create journal entry
        
        Args:
            payment_id: Payment UUID
            approved_by_id: User who approved the payment
            
        Returns:
            Approved Payment object
        """
        payment = self.get_payment_by_id(payment_id)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        
        if payment.status != PaymentStatus.PENDING:
            raise ValueError(f"Payment {payment_id} is not in pending status")
        
        # Update payment status
        payment.status = PaymentStatus.CONFIRMED
        if approved_by_id:
            payment.approved_by_id = approved_by_id
            payment.approved_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(payment)
        
        # Log payment approval
        logger.info(f"Payment {payment_id} approved by user {approved_by_id}")
        if approved_by_id:
            audit_logger.log_payment_approval(
                user_id=int(approved_by_id),
                payment_id=payment_id,
                amount=float(payment.amount)
            )
        
        # Create journal entry for accounting
        if self.accounting_service:
            try:
                journal_entry = self.accounting_service.create_journal_entry_for_payment(payment_id)
                accounting_logger.log_payment_journal_entry(
                    payment_id=payment_id,
                    journal_entry_id=str(journal_entry.id),
                    user_id=int(approved_by_id) if approved_by_id else 0
                )
                logger.info(f"Journal entry {journal_entry.id} created for payment {payment_id}")
            except Exception as e:
                logger.error(f"Failed to create journal entry for payment {payment_id}: {e}")
                accounting_logger.log_error(
                    message=f"Failed to create journal entry for payment {payment_id}",
                    error=e,
                    payment_id=payment_id,
                    user_id=int(approved_by_id) if approved_by_id else 0
                )
                # Don't rollback payment approval, just log the error
        
        # Auto-allocate to invoices using FIFO
        try:
            self.allocate_payment_fifo(payment_id)
            logger.info(f"Payment {payment_id} auto-allocated using FIFO")
        except Exception as e:
            logger.error(f"Failed to auto-allocate payment {payment_id}: {e}")
        
        return payment
    
    def reject_payment(self, payment_id: str, rejected_by_id: Optional[str] = None, reason: Optional[str] = None) -> Payment:
        """
        Reject a pending payment
        
        Args:
            payment_id: Payment UUID
            rejected_by_id: User who rejected the payment
            reason: Rejection reason
            
        Returns:
            Rejected Payment object
        """
        payment = self.get_payment_by_id(payment_id)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        
        if payment.status != PaymentStatus.PENDING:
            raise ValueError(f"Payment {payment_id} is not in pending status")
        
        # Update payment status
        payment.status = PaymentStatus.CANCELLED
        if rejected_by_id:
            payment.rejected_by_id = rejected_by_id
            payment.rejected_at = datetime.now()
        if reason:
            payment.rejection_reason = reason
        
        self.db.commit()
        self.db.refresh(payment)
        
        # Log payment rejection
        logger.info(f"Payment {payment_id} rejected by user {rejected_by_id}")
        if rejected_by_id:
            audit_logger.log_payment_rejection(
                user_id=int(rejected_by_id),
                payment_id=payment_id,
                reason=reason
            )
        
        return payment

