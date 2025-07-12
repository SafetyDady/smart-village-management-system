"""
Invoice Service - Business Logic for Invoice Management
"""
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.invoice import Invoice, InvoiceStatus, InvoiceType
from app.models.property import Property
from app.models.user import User


class InvoiceService:
    """Service class for Invoice business logic"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_invoice(
        self,
        property_id: str,
        invoice_type: InvoiceType,
        amount: float,
        description: str,
        due_date: Optional[datetime] = None,
        created_by_id: Optional[str] = None
    ) -> Invoice:
        """
        Create a new invoice
        
        Args:
            property_id: Property UUID
            invoice_type: Type of invoice (MAINTENANCE, UTILITY, etc.)
            amount: Invoice amount
            description: Invoice description
            due_date: Due date (default: 30 days from now)
            created_by_id: User who created the invoice
            
        Returns:
            Created Invoice object
        """
        if due_date is None:
            due_date = datetime.now() + timedelta(days=30)
        
        # Generate invoice number
        invoice_number = self._generate_invoice_number()
        
        invoice = Invoice(
            invoice_number=invoice_number,
            property_id=property_id,
            invoice_type=invoice_type,
            amount=amount,
            description=description,
            due_date=due_date,
            status=InvoiceStatus.PENDING,
            created_by_id=created_by_id
        )
        
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        
        return invoice
    
    def get_invoice_by_id(self, invoice_id: str) -> Optional[Invoice]:
        """Get invoice by ID"""
        return self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
    
    def get_invoices_by_property(
        self,
        property_id: str,
        status: Optional[InvoiceStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Invoice]:
        """Get invoices for a specific property"""
        query = self.db.query(Invoice).filter(Invoice.property_id == property_id)
        
        if status:
            query = query.filter(Invoice.status == status)
        
        return query.order_by(Invoice.created_at.desc()).offset(offset).limit(limit).all()
    
    def get_pending_invoices_by_property(self, property_id: str) -> List[Invoice]:
        """Get all pending invoices for a property (for FIFO allocation)"""
        return self.db.query(Invoice).filter(
            and_(
                Invoice.property_id == property_id,
                Invoice.status == InvoiceStatus.PENDING
            )
        ).order_by(Invoice.created_at.asc()).all()  # FIFO: oldest first
    
    def get_overdue_invoices(self, property_id: Optional[str] = None) -> List[Invoice]:
        """Get overdue invoices"""
        query = self.db.query(Invoice).filter(
            and_(
                Invoice.status == InvoiceStatus.PENDING,
                Invoice.due_date < datetime.now()
            )
        )
        
        if property_id:
            query = query.filter(Invoice.property_id == property_id)
        
        return query.order_by(Invoice.due_date.asc()).all()
    
    def update_invoice_status(self, invoice_id: str, status: InvoiceStatus) -> Optional[Invoice]:
        """Update invoice status"""
        invoice = self.get_invoice_by_id(invoice_id)
        if not invoice:
            return None
        
        invoice.status = status
        if status == InvoiceStatus.PAID:
            invoice.paid_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(invoice)
        
        return invoice
    
    def calculate_outstanding_amount(self, invoice_id: str) -> float:
        """Calculate outstanding amount for an invoice"""
        invoice = self.get_invoice_by_id(invoice_id)
        if not invoice:
            return 0.0
        
        # Calculate total payments allocated to this invoice
        total_paid = sum(
            pi.amount for pi in invoice.payment_allocations
        )
        
        outstanding = invoice.amount - total_paid
        return max(0.0, outstanding)  # Never negative
    
    def mark_invoice_as_paid_if_fully_allocated(self, invoice_id: str) -> bool:
        """
        Check if invoice is fully paid and update status
        
        Returns:
            True if invoice was marked as paid, False otherwise
        """
        outstanding = self.calculate_outstanding_amount(invoice_id)
        
        if outstanding <= 0.01:  # Consider paid if outstanding is very small (rounding)
            self.update_invoice_status(invoice_id, InvoiceStatus.PAID)
            return True
        
        return False
    
    def _generate_invoice_number(self) -> str:
        """Generate unique invoice number"""
        # Get current year and month
        now = datetime.now()
        year_month = now.strftime("%Y%m")
        
        # Count invoices in current month
        count = self.db.query(Invoice).filter(
            Invoice.invoice_number.like(f"INV{year_month}%")
        ).count()
        
        # Generate number: INV202501001, INV202501002, etc.
        invoice_number = f"INV{year_month}{count + 1:03d}"
        
        return invoice_number
    
    def get_invoice_summary_by_property(self, property_id: str) -> dict:
        """Get invoice summary for a property"""
        invoices = self.db.query(Invoice).filter(Invoice.property_id == property_id).all()
        
        total_amount = sum(inv.amount for inv in invoices)
        total_paid = sum(
            sum(pi.amount for pi in inv.payment_allocations)
            for inv in invoices
        )
        total_outstanding = total_amount - total_paid
        
        pending_count = len([inv for inv in invoices if inv.status == InvoiceStatus.PENDING])
        overdue_count = len([
            inv for inv in invoices 
            if inv.status == InvoiceStatus.PENDING and inv.due_date < datetime.now()
        ])
        
        return {
            "total_invoices": len(invoices),
            "pending_invoices": pending_count,
            "overdue_invoices": overdue_count,
            "total_amount": total_amount,
            "total_paid": total_paid,
            "total_outstanding": total_outstanding
        }

