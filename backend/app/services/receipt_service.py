"""
Receipt Service - Business Logic for Receipt Auto-Generation
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.receipt import Receipt
from app.models.payment import Payment
from app.models.payment_invoice import PaymentInvoice
from app.models.property import Property


class ReceiptService:
    """Service class for Receipt business logic and auto-generation"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_receipt_for_payment(
        self,
        payment_id: str,
        issued_by_id: Optional[str] = None
    ) -> Receipt:
        """
        Auto-generate receipt for a payment
        
        Args:
            payment_id: Payment UUID
            issued_by_id: User who issued the receipt
            
        Returns:
            Generated Receipt object
        """
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        
        # Check if receipt already exists for this payment
        existing_receipt = self.db.query(Receipt).filter(
            Receipt.payment_id == payment_id
        ).first()
        
        if existing_receipt:
            return existing_receipt  # Return existing receipt
        
        # Generate receipt number
        receipt_number = self._generate_receipt_number()
        
        # Get payment allocations for receipt details
        allocations = self.db.query(PaymentInvoice).filter(
            PaymentInvoice.payment_id == payment_id
        ).all()
        
        # Create receipt details
        receipt_details = self._create_receipt_details(payment, allocations)
        
        receipt = Receipt(
            receipt_number=receipt_number,
            payment_id=payment_id,
            property_id=payment.property_id,
            amount=payment.amount,
            payment_method=payment.payment_method,
            details=receipt_details,
            issued_by_id=issued_by_id
        )
        
        self.db.add(receipt)
        self.db.commit()
        self.db.refresh(receipt)
        
        return receipt
    
    def generate_receipts_for_property(
        self,
        property_id: str,
        issued_by_id: Optional[str] = None
    ) -> List[Receipt]:
        """
        Generate receipts for all payments in a property that don't have receipts yet
        
        Args:
            property_id: Property UUID
            issued_by_id: User who issued the receipts
            
        Returns:
            List of generated Receipt objects
        """
        # Get payments without receipts
        payments_without_receipts = self.db.query(Payment).filter(
            Payment.property_id == property_id,
            ~Payment.id.in_(
                self.db.query(Receipt.payment_id).filter(Receipt.payment_id.isnot(None))
            )
        ).all()
        
        receipts = []
        for payment in payments_without_receipts:
            try:
                receipt = self.generate_receipt_for_payment(payment.id, issued_by_id)
                receipts.append(receipt)
            except Exception as e:
                # Log error but continue with other payments
                print(f"Error generating receipt for payment {payment.id}: {e}")
                continue
        
        return receipts
    
    def get_receipt_by_id(self, receipt_id: str) -> Optional[Receipt]:
        """Get receipt by ID"""
        return self.db.query(Receipt).filter(Receipt.id == receipt_id).first()
    
    def get_receipt_by_payment_id(self, payment_id: str) -> Optional[Receipt]:
        """Get receipt by payment ID"""
        return self.db.query(Receipt).filter(Receipt.payment_id == payment_id).first()
    
    def get_receipts_by_property(
        self,
        property_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Receipt]:
        """Get receipts for a specific property"""
        return self.db.query(Receipt).filter(
            Receipt.property_id == property_id
        ).order_by(desc(Receipt.created_at)).offset(offset).limit(limit).all()
    
    def get_receipts_by_date_range(
        self,
        property_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Receipt]:
        """Get receipts within a date range"""
        query = self.db.query(Receipt)
        
        if property_id:
            query = query.filter(Receipt.property_id == property_id)
        
        if start_date:
            query = query.filter(Receipt.created_at >= start_date)
        
        if end_date:
            query = query.filter(Receipt.created_at <= end_date)
        
        return query.order_by(desc(Receipt.created_at)).offset(offset).limit(limit).all()
    
    def update_receipt_details(self, receipt_id: str, details: str) -> Optional[Receipt]:
        """Update receipt details"""
        receipt = self.get_receipt_by_id(receipt_id)
        if not receipt:
            return None
        
        receipt.details = details
        self.db.commit()
        self.db.refresh(receipt)
        
        return receipt
    
    def _generate_receipt_number(self) -> str:
        """Generate unique receipt number"""
        # Get current year and month
        now = datetime.now()
        year_month = now.strftime("%Y%m")
        
        # Count receipts in current month
        count = self.db.query(Receipt).filter(
            Receipt.receipt_number.like(f"RCP{year_month}%")
        ).count()
        
        # Generate number: RCP202501001, RCP202501002, etc.
        receipt_number = f"RCP{year_month}{count + 1:03d}"
        
        return receipt_number
    
    def _create_receipt_details(
        self,
        payment: Payment,
        allocations: List[PaymentInvoice]
    ) -> str:
        """
        Create detailed receipt description
        
        Args:
            payment: Payment object
            allocations: List of PaymentInvoice allocations
            
        Returns:
            Formatted receipt details string
        """
        details_lines = [
            f"Payment Method: {payment.payment_method.value}",
            f"Amount: ฿{payment.amount:,.2f}",
            f"Date: {payment.created_at.strftime('%d/%m/%Y %H:%M')}"
        ]
        
        if payment.reference_number:
            details_lines.append(f"Reference: {payment.reference_number}")
        
        if allocations:
            details_lines.append("\nAllocated to:")
            for allocation in allocations:
                invoice = allocation.invoice
                details_lines.append(
                    f"- Invoice {invoice.invoice_number}: ฿{allocation.amount:,.2f}"
                )
        
        if payment.notes:
            details_lines.append(f"\nNotes: {payment.notes}")
        
        return "\n".join(details_lines)
    
    def get_receipt_summary_by_property(self, property_id: str) -> dict:
        """Get receipt summary for a property"""
        receipts = self.get_receipts_by_property(property_id, limit=1000)
        
        total_amount = sum(receipt.amount for receipt in receipts)
        
        # Group by payment method
        method_breakdown = {}
        for receipt in receipts:
            method = receipt.payment_method.value
            if method not in method_breakdown:
                method_breakdown[method] = {"count": 0, "amount": 0.0}
            method_breakdown[method]["count"] += 1
            method_breakdown[method]["amount"] += receipt.amount
        
        # Group by month
        monthly_breakdown = {}
        for receipt in receipts:
            month_key = receipt.created_at.strftime("%Y-%m")
            if month_key not in monthly_breakdown:
                monthly_breakdown[month_key] = {"count": 0, "amount": 0.0}
            monthly_breakdown[month_key]["count"] += 1
            monthly_breakdown[month_key]["amount"] += receipt.amount
        
        return {
            "total_receipts": len(receipts),
            "total_amount": total_amount,
            "payment_method_breakdown": method_breakdown,
            "monthly_breakdown": monthly_breakdown
        }
    
    def generate_receipt_pdf_data(self, receipt_id: str) -> dict:
        """
        Generate data structure for PDF receipt generation
        
        Args:
            receipt_id: Receipt UUID
            
        Returns:
            Dictionary with receipt data for PDF generation
        """
        receipt = self.get_receipt_by_id(receipt_id)
        if not receipt:
            raise ValueError(f"Receipt {receipt_id} not found")
        
        # Get related data
        payment = receipt.payment
        property_obj = receipt.property_obj
        village = property_obj.village if property_obj else None
        
        # Get payment allocations
        allocations = self.db.query(PaymentInvoice).filter(
            PaymentInvoice.payment_id == receipt.payment_id
        ).all()
        
        allocation_details = []
        for allocation in allocations:
            invoice = allocation.invoice
            allocation_details.append({
                "invoice_number": invoice.invoice_number,
                "invoice_type": invoice.invoice_type.value,
                "amount": allocation.amount,
                "invoice_date": invoice.created_at.strftime("%d/%m/%Y")
            })
        
        return {
            "receipt": {
                "number": receipt.receipt_number,
                "date": receipt.created_at.strftime("%d/%m/%Y"),
                "time": receipt.created_at.strftime("%H:%M"),
                "amount": receipt.amount
            },
            "payment": {
                "method": payment.payment_method.value,
                "reference": payment.reference_number,
                "notes": payment.notes
            },
            "property": {
                "address": property_obj.address if property_obj else "N/A",
                "unit_number": property_obj.unit_number if property_obj else "N/A"
            },
            "village": {
                "name": village.name if village else "N/A",
                "address": village.address if village else "N/A"
            },
            "allocations": allocation_details,
            "issued_by": receipt.issued_by.full_name if receipt.issued_by else "System"
        }

