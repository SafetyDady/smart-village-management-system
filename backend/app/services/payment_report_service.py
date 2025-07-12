"""
Payment Report Service - Business Logic for Payment Reports with OCR Integration
"""
import os
from typing import List, Optional, Dict, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from app.models.payment_report import PaymentReport, PaymentReportStatus, PaymentReportType
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.services.ocr_service import OCRService
from app.services.payment_service import PaymentService


class PaymentReportService:
    """Service for managing payment reports with OCR integration"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ocr_service = OCRService()
        self.payment_service = PaymentService(db)
    
    def create_payment_report(
        self,
        property_id: str,
        reported_by_id: str,
        reported_amount: float,
        reported_date: datetime,
        payment_type: PaymentReportType,
        slip_file_path: str,
        notes: Optional[str] = None
    ) -> PaymentReport:
        """
        Create a new payment report with slip upload
        
        Args:
            property_id: Property UUID
            reported_by_id: User who reported the payment
            reported_amount: Amount reported by user
            reported_date: Date reported by user
            payment_type: Type of payment
            slip_file_path: Path to uploaded slip file
            notes: Optional notes from user
            
        Returns:
            Created PaymentReport object
        """
        # Calculate file hash for duplicate detection
        file_hash = self.ocr_service.calculate_file_hash(slip_file_path)
        
        # Check for duplicate slips
        if self._is_duplicate_slip(file_hash):
            duplicate_report = self._get_report_by_hash(file_hash)
            raise ValueError(f"Slip ซ้ำกับรายงาน {duplicate_report.report_number}")
        
        # Generate report number
        report_number = self._generate_report_number()
        
        # Get file info
        file_size = os.path.getsize(slip_file_path)
        
        # Create payment report
        payment_report = PaymentReport(
            report_number=report_number,
            property_id=property_id,
            reported_by_id=reported_by_id,
            reported_amount=reported_amount,
            reported_date=reported_date,
            payment_type=payment_type.value,
            slip_file_path=slip_file_path,
            slip_file_hash=file_hash,
            slip_file_size=file_size,
            notes=notes,
            status=PaymentReportStatus.PENDING.value
        )
        
        self.db.add(payment_report)
        self.db.commit()
        self.db.refresh(payment_report)
        
        # Start OCR processing asynchronously
        self._process_ocr_async(payment_report.id)
        
        return payment_report
    
    def process_ocr(self, report_id: str) -> PaymentReport:
        """
        Process OCR for a payment report
        
        Args:
            report_id: PaymentReport UUID
            
        Returns:
            Updated PaymentReport object
        """
        report = self.get_report_by_id(report_id)
        if not report:
            raise ValueError(f"Payment report {report_id} not found")
        
        # Update status to processing
        report.status = PaymentReportStatus.OCR_PROCESSING.value
        self.db.commit()
        
        try:
            # Extract payment info using OCR
            ocr_result = self.ocr_service.extract_payment_info(report.slip_file_path)
            
            # Update report with OCR results
            report.ocr_extracted_data = ocr_result['extracted_data']
            report.ocr_confidence_score = ocr_result['confidence_score']
            
            # Extract specific fields
            extracted = ocr_result['extracted_data']
            if extracted.get('amount'):
                report.ocr_amount = extracted['amount']
            if extracted.get('date'):
                report.ocr_date = extracted['date']
            if extracted.get('time'):
                report.ocr_time = extracted['time']
            if extracted.get('bank_name'):
                report.ocr_bank_name = extracted['bank_name']
            if extracted.get('reference_number'):
                report.ocr_reference = extracted['reference_number']
            
            # Validate OCR results
            is_valid, errors = self.ocr_service.validate_extracted_data(extracted)
            
            if is_valid and report.ocr_confidence_score >= 0.8:
                report.status = PaymentReportStatus.OCR_SUCCESS.value
                
                # If OCR data matches reported data, auto-approve
                if report.ocr_data_matches_reported:
                    report.status = PaymentReportStatus.UNDER_REVIEW.value
                
            else:
                report.status = PaymentReportStatus.OCR_FAILED.value
                report.admin_notes = f"OCR validation failed: {', '.join(errors)}"
            
        except Exception as e:
            report.status = PaymentReportStatus.OCR_FAILED.value
            report.admin_notes = f"OCR processing error: {str(e)}"
        
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    def approve_payment_report(
        self,
        report_id: str,
        reviewed_by_id: str,
        admin_notes: Optional[str] = None
    ) -> Payment:
        """
        Approve payment report and create actual payment
        
        Args:
            report_id: PaymentReport UUID
            reviewed_by_id: Admin who approved the report
            admin_notes: Optional admin notes
            
        Returns:
            Created Payment object
        """
        report = self.get_report_by_id(report_id)
        if not report:
            raise ValueError(f"Payment report {report_id} not found")
        
        if report.status != PaymentReportStatus.UNDER_REVIEW.value:
            raise ValueError(f"Report {report.report_number} is not ready for approval")
        
        # Update report status
        report.status = PaymentReportStatus.APPROVED.value
        report.reviewed_by_id = reviewed_by_id
        report.reviewed_at = datetime.now()
        if admin_notes:
            report.admin_notes = admin_notes
        
        # Create payment using final data (OCR if available and accurate, otherwise reported)
        payment_method = self._map_payment_type_to_method(report.payment_type)
        
        payment = self.payment_service.create_payment(
            property_id=report.property_id,
            amount=report.final_amount,
            payment_method=payment_method,
            reference_number=report.ocr_reference or f"RPT-{report.report_number}",
            notes=f"From payment report {report.report_number}",
            received_by_id=reviewed_by_id,
            auto_allocate=True  # Auto-allocate using FIFO
        )
        
        # Link payment to report
        report.payment_id = payment.id
        report.status = PaymentReportStatus.PROCESSED.value
        report.processed_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(report)
        
        return payment
    
    def reject_payment_report(
        self,
        report_id: str,
        reviewed_by_id: str,
        rejection_reason: str
    ) -> PaymentReport:
        """
        Reject payment report
        
        Args:
            report_id: PaymentReport UUID
            reviewed_by_id: Admin who rejected the report
            rejection_reason: Reason for rejection
            
        Returns:
            Updated PaymentReport object
        """
        report = self.get_report_by_id(report_id)
        if not report:
            raise ValueError(f"Payment report {report_id} not found")
        
        report.status = PaymentReportStatus.REJECTED.value
        report.reviewed_by_id = reviewed_by_id
        report.reviewed_at = datetime.now()
        report.rejection_reason = rejection_reason
        
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    def get_report_by_id(self, report_id: str) -> Optional[PaymentReport]:
        """Get payment report by ID"""
        return self.db.query(PaymentReport).filter(PaymentReport.id == report_id).first()
    
    def get_reports_by_property(
        self,
        property_id: str,
        status: Optional[PaymentReportStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[PaymentReport]:
        """Get payment reports for a property"""
        query = self.db.query(PaymentReport).filter(PaymentReport.property_id == property_id)
        
        if status:
            query = query.filter(PaymentReport.status == status.value)
        
        return query.order_by(desc(PaymentReport.created_at)).offset(offset).limit(limit).all()
    
    def get_pending_reports(self, limit: int = 100, offset: int = 0) -> List[PaymentReport]:
        """Get reports pending review"""
        return self.db.query(PaymentReport).filter(
            PaymentReport.status.in_([
                PaymentReportStatus.OCR_SUCCESS.value,
                PaymentReportStatus.UNDER_REVIEW.value
            ])
        ).order_by(PaymentReport.created_at.asc()).offset(offset).limit(limit).all()
    
    def get_reports_by_user(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[PaymentReport]:
        """Get payment reports by user"""
        return self.db.query(PaymentReport).filter(
            PaymentReport.reported_by_id == user_id
        ).order_by(desc(PaymentReport.created_at)).offset(offset).limit(limit).all()
    
    def _process_ocr_async(self, report_id: str) -> None:
        """
        Process OCR asynchronously (in production, use Celery or similar)
        For now, process immediately
        """
        # In production, this would be a background task
        self.process_ocr(report_id)
    
    def _is_duplicate_slip(self, file_hash: str) -> bool:
        """Check if slip is duplicate based on file hash"""
        existing = self.db.query(PaymentReport).filter(
            PaymentReport.slip_file_hash == file_hash
        ).first()
        return existing is not None
    
    def _get_report_by_hash(self, file_hash: str) -> Optional[PaymentReport]:
        """Get report by file hash"""
        return self.db.query(PaymentReport).filter(
            PaymentReport.slip_file_hash == file_hash
        ).first()
    
    def _generate_report_number(self) -> str:
        """Generate unique report number"""
        now = datetime.now()
        year_month = now.strftime("%Y%m")
        
        count = self.db.query(PaymentReport).filter(
            PaymentReport.report_number.like(f"RPT{year_month}%")
        ).count()
        
        return f"RPT{year_month}{count + 1:03d}"
    
    def _map_payment_type_to_method(self, payment_type: str) -> PaymentMethod:
        """Map payment report type to payment method"""
        mapping = {
            PaymentReportType.BANK_TRANSFER.value: PaymentMethod.BANK_TRANSFER,
            PaymentReportType.MOBILE_BANKING.value: PaymentMethod.BANK_TRANSFER,
            PaymentReportType.QR_PAYMENT.value: PaymentMethod.QR_CODE,
            PaymentReportType.CASH_DEPOSIT.value: PaymentMethod.CASH,
            PaymentReportType.OTHER.value: PaymentMethod.BANK_TRANSFER
        }
        return mapping.get(payment_type, PaymentMethod.BANK_TRANSFER)
    
    def get_report_summary(self) -> Dict:
        """Get summary of all payment reports"""
        total_reports = self.db.query(PaymentReport).count()
        
        status_counts = {}
        for status in PaymentReportStatus:
            count = self.db.query(PaymentReport).filter(
                PaymentReport.status == status.value
            ).count()
            status_counts[status.value] = count
        
        return {
            "total_reports": total_reports,
            "status_breakdown": status_counts,
            "pending_review": status_counts.get(PaymentReportStatus.UNDER_REVIEW.value, 0),
            "ocr_processing": status_counts.get(PaymentReportStatus.OCR_PROCESSING.value, 0)
        }

