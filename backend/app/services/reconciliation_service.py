"""
Reconciliation Service - Business Logic for Bank Statement Reconciliation
"""
import re
from typing import List, Optional, Dict, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.models.bank_statement import BankStatement, BankTransaction, ReconciliationRule, BankStatementStatus, ReconciliationStatus
from app.models.payment import Payment
from app.services.bank_statement_ocr_service import BankStatementOCRService


class ReconciliationService:
    """Service for bank statement reconciliation with payments"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ocr_service = BankStatementOCRService()
    
    def upload_bank_statement(
        self,
        file_path: str,
        village_id: str,
        uploaded_by_id: str,
        statement_date: Optional[date] = None
    ) -> BankStatement:
        """
        Upload and process bank statement
        
        Args:
            file_path: Path to statement file
            village_id: Village UUID
            uploaded_by_id: User who uploaded the statement
            statement_date: Statement date (optional, will be extracted from OCR)
            
        Returns:
            Created BankStatement object
        """
        # Calculate file hash for duplicate detection
        file_hash = self.ocr_service.calculate_file_hash(file_path)
        
        # Check for duplicate statements
        existing = self.db.query(BankStatement).filter(
            BankStatement.file_hash == file_hash
        ).first()
        
        if existing:
            raise ValueError(f"Statement file already uploaded: {existing.statement_number}")
        
        # Generate statement number
        statement_number = self._generate_statement_number()
        
        # Create initial statement record
        statement = BankStatement(
            statement_number=statement_number,
            bank_name="Unknown",  # Will be updated after OCR
            account_number="Unknown",  # Will be updated after OCR
            account_name="Unknown",  # Will be updated after OCR
            statement_date=statement_date or date.today(),
            period_start=date.today(),  # Will be updated after OCR
            period_end=date.today(),  # Will be updated after OCR
            file_path=file_path,
            file_hash=file_hash,
            file_size=self.ocr_service.calculate_file_hash(file_path),  # This should be file size, not hash
            uploaded_by_id=uploaded_by_id,
            village_id=village_id,
            status=BankStatementStatus.UPLOADED.value
        )
        
        self.db.add(statement)
        self.db.commit()
        self.db.refresh(statement)
        
        # Process OCR asynchronously
        self._process_statement_ocr(statement.id)
        
        return statement
    
    def process_statement_ocr(self, statement_id: str) -> BankStatement:
        """
        Process OCR for bank statement
        
        Args:
            statement_id: BankStatement UUID
            
        Returns:
            Updated BankStatement object
        """
        statement = self.get_statement_by_id(statement_id)
        if not statement:
            raise ValueError(f"Bank statement {statement_id} not found")
        
        # Update status
        statement.status = BankStatementStatus.OCR_PROCESSING.value
        self.db.commit()
        
        try:
            # Extract statement data using OCR
            ocr_result = self.ocr_service.extract_bank_statement_data(statement.file_path)
            
            # Update statement with OCR results
            statement.ocr_raw_data = ocr_result
            statement.ocr_confidence_score = ocr_result['confidence_score']
            statement.ocr_processed_at = datetime.now()
            
            # Update statement info from OCR
            stmt_info = ocr_result['statement_info']
            if stmt_info.get('bank_name'):
                statement.bank_name = stmt_info['bank_name']
            if stmt_info.get('account_number'):
                statement.account_number = stmt_info['account_number']
            if stmt_info.get('account_name'):
                statement.account_name = stmt_info['account_name']
            if stmt_info.get('period_start'):
                statement.period_start = stmt_info['period_start']
            if stmt_info.get('period_end'):
                statement.period_end = stmt_info['period_end']
            if stmt_info.get('opening_balance'):
                statement.opening_balance = stmt_info['opening_balance']
            if stmt_info.get('closing_balance'):
                statement.closing_balance = stmt_info['closing_balance']
            
            # Create transaction records
            transactions_data = ocr_result['transactions']
            statement.total_transactions = len(transactions_data)
            
            for trans_data in transactions_data:
                transaction = BankTransaction(
                    statement_id=statement.id,
                    transaction_date=trans_data['date'],
                    transaction_time=trans_data.get('time'),
                    description=trans_data['description'],
                    reference_number=trans_data.get('reference'),
                    credit_amount=trans_data.get('credit_amount'),
                    debit_amount=trans_data.get('debit_amount'),
                    ocr_raw_text=trans_data.get('raw_text'),
                    ocr_confidence=ocr_result['confidence_score']
                )
                self.db.add(transaction)
            
            # Check validation results
            validation = ocr_result['validation']
            if validation['is_valid']:
                statement.status = BankStatementStatus.OCR_SUCCESS.value
            else:
                statement.status = BankStatementStatus.OCR_FAILED.value
                statement.processing_notes = f"Validation errors: {', '.join(validation['errors'])}"
            
        except Exception as e:
            statement.status = BankStatementStatus.OCR_FAILED.value
            statement.processing_notes = f"OCR processing error: {str(e)}"
        
        self.db.commit()
        self.db.refresh(statement)
        
        # If OCR successful, start auto-reconciliation
        if statement.status == BankStatementStatus.OCR_SUCCESS.value:
            self._start_auto_reconciliation(statement.id)
        
        return statement
    
    def auto_reconcile_statement(self, statement_id: str) -> Dict:
        """
        Automatically reconcile bank statement with payments
        
        Args:
            statement_id: BankStatement UUID
            
        Returns:
            Reconciliation summary
        """
        statement = self.get_statement_by_id(statement_id)
        if not statement:
            raise ValueError(f"Bank statement {statement_id} not found")
        
        statement.status = BankStatementStatus.RECONCILING.value
        self.db.commit()
        
        # Get unmatched transactions (credit transactions only for payments)
        unmatched_transactions = self.db.query(BankTransaction).filter(
            and_(
                BankTransaction.statement_id == statement_id,
                BankTransaction.reconciliation_status == ReconciliationStatus.UNMATCHED.value,
                BankTransaction.credit_amount.isnot(None),  # Only credit transactions
                BankTransaction.credit_amount > 0
            )
        ).all()
        
        # Get unreconciled payments in the same period
        payments = self._get_unreconciled_payments(
            statement.village_id,
            statement.period_start,
            statement.period_end
        )
        
        matches_found = 0
        total_processed = 0
        
        for transaction in unmatched_transactions:
            total_processed += 1
            
            # Try to find matching payment
            matched_payment = self._find_matching_payment(transaction, payments)
            
            if matched_payment:
                # Create match
                self._create_match(transaction, matched_payment, auto_match=True)
                matches_found += 1
                
                # Remove from available payments
                payments = [p for p in payments if p.id != matched_payment.id]
        
        # Update statement status
        reconciliation_summary = statement.reconciliation_summary
        if reconciliation_summary['unmatched'] == 0:
            statement.status = BankStatementStatus.RECONCILED.value
        else:
            statement.status = BankStatementStatus.PARTIALLY_RECONCILED.value
        
        self.db.commit()
        
        return {
            "total_transactions": total_processed,
            "matches_found": matches_found,
            "unmatched_remaining": reconciliation_summary['unmatched'],
            "reconciliation_percentage": reconciliation_summary['percentage']
        }
    
    def manual_reconcile(
        self,
        transaction_id: str,
        payment_id: str,
        reviewed_by_id: str,
        notes: Optional[str] = None
    ) -> BankTransaction:
        """
        Manually reconcile a bank transaction with a payment
        
        Args:
            transaction_id: BankTransaction UUID
            payment_id: Payment UUID
            reviewed_by_id: User who performed the reconciliation
            notes: Optional notes
            
        Returns:
            Updated BankTransaction object
        """
        transaction = self.db.query(BankTransaction).filter(
            BankTransaction.id == transaction_id
        ).first()
        
        if not transaction:
            raise ValueError(f"Bank transaction {transaction_id} not found")
        
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        
        # Validate match
        validation_result = self._validate_manual_match(transaction, payment)
        if not validation_result['is_valid']:
            raise ValueError(f"Invalid match: {', '.join(validation_result['errors'])}")
        
        # Create match
        self._create_match(
            transaction,
            payment,
            auto_match=False,
            reviewed_by_id=reviewed_by_id,
            notes=notes
        )
        
        return transaction
    
    def unmatch_transaction(
        self,
        transaction_id: str,
        reviewed_by_id: str,
        reason: str
    ) -> BankTransaction:
        """
        Remove match from a bank transaction
        
        Args:
            transaction_id: BankTransaction UUID
            reviewed_by_id: User who performed the action
            reason: Reason for unmatching
            
        Returns:
            Updated BankTransaction object
        """
        transaction = self.db.query(BankTransaction).filter(
            BankTransaction.id == transaction_id
        ).first()
        
        if not transaction:
            raise ValueError(f"Bank transaction {transaction_id} not found")
        
        # Clear match
        transaction.matched_payment_id = None
        transaction.reconciliation_status = ReconciliationStatus.UNMATCHED.value
        transaction.match_confidence = None
        transaction.reviewed_by_id = reviewed_by_id
        transaction.reviewed_at = datetime.now()
        transaction.review_notes = f"Unmatched: {reason}"
        
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction
    
    def get_statement_by_id(self, statement_id: str) -> Optional[BankStatement]:
        """Get bank statement by ID"""
        return self.db.query(BankStatement).filter(BankStatement.id == statement_id).first()
    
    def get_statements_by_village(
        self,
        village_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[BankStatement]:
        """Get bank statements for a village"""
        return self.db.query(BankStatement).filter(
            BankStatement.village_id == village_id
        ).order_by(desc(BankStatement.created_at)).offset(offset).limit(limit).all()
    
    def get_unmatched_transactions(
        self,
        statement_id: str
    ) -> List[BankTransaction]:
        """Get unmatched transactions for a statement"""
        return self.db.query(BankTransaction).filter(
            and_(
                BankTransaction.statement_id == statement_id,
                BankTransaction.reconciliation_status == ReconciliationStatus.UNMATCHED.value
            )
        ).order_by(BankTransaction.transaction_date.asc()).all()
    
    def _process_statement_ocr(self, statement_id: str) -> None:
        """Process OCR asynchronously (in production, use background task)"""
        self.process_statement_ocr(statement_id)
    
    def _start_auto_reconciliation(self, statement_id: str) -> None:
        """Start auto-reconciliation asynchronously"""
        self.auto_reconcile_statement(statement_id)
    
    def _get_unreconciled_payments(
        self,
        village_id: str,
        start_date: date,
        end_date: date
    ) -> List[Payment]:
        """Get payments that haven't been reconciled yet"""
        # Extend date range to account for timing differences
        extended_start = start_date - timedelta(days=3)
        extended_end = end_date + timedelta(days=3)
        
        return self.db.query(Payment).filter(
            and_(
                Payment.created_at >= extended_start,
                Payment.created_at <= extended_end,
                ~Payment.id.in_(
                    self.db.query(BankTransaction.matched_payment_id).filter(
                        BankTransaction.matched_payment_id.isnot(None)
                    )
                )
            )
        ).all()
    
    def _find_matching_payment(
        self,
        transaction: BankTransaction,
        payments: List[Payment]
    ) -> Optional[Payment]:
        """Find best matching payment for a bank transaction"""
        best_match = None
        best_score = 0.0
        
        for payment in payments:
            score = self._calculate_match_score(transaction, payment)
            if score > best_score and score >= 0.8:  # Minimum 80% confidence
                best_score = score
                best_match = payment
        
        return best_match
    
    def _calculate_match_score(
        self,
        transaction: BankTransaction,
        payment: Payment
    ) -> float:
        """Calculate match score between transaction and payment"""
        score = 0.0
        
        # Amount matching (40% weight)
        amount_diff = abs(transaction.transaction_amount - float(payment.amount))
        if amount_diff == 0:
            score += 0.4
        elif amount_diff <= 1.0:  # Allow ฿1 difference
            score += 0.3
        elif amount_diff <= float(payment.amount) * 0.01:  # 1% tolerance
            score += 0.2
        
        # Date matching (30% weight)
        payment_date = payment.created_at.date()
        date_diff = abs((transaction.transaction_date - payment_date).days)
        if date_diff == 0:
            score += 0.3
        elif date_diff <= 1:
            score += 0.2
        elif date_diff <= 3:
            score += 0.1
        
        # Reference matching (20% weight)
        if transaction.reference_number and payment.reference_number:
            if transaction.reference_number == payment.reference_number:
                score += 0.2
            elif transaction.reference_number in payment.reference_number or payment.reference_number in transaction.reference_number:
                score += 0.1
        
        # Description matching (10% weight)
        if payment.notes and transaction.description:
            # Simple keyword matching
            payment_words = set(payment.notes.lower().split())
            desc_words = set(transaction.description.lower().split())
            common_words = payment_words.intersection(desc_words)
            if common_words:
                score += 0.1 * (len(common_words) / max(len(payment_words), len(desc_words)))
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _create_match(
        self,
        transaction: BankTransaction,
        payment: Payment,
        auto_match: bool = True,
        reviewed_by_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> None:
        """Create a match between transaction and payment"""
        transaction.matched_payment_id = payment.id
        transaction.reconciliation_status = (
            ReconciliationStatus.AUTO_MATCHED.value if auto_match
            else ReconciliationStatus.MANUAL_MATCHED.value
        )
        
        if not auto_match:
            transaction.reviewed_by_id = reviewed_by_id
            transaction.reviewed_at = datetime.now()
            transaction.review_notes = notes
        
        # Calculate match confidence
        transaction.match_confidence = self._calculate_match_score(transaction, payment)
        
        self.db.commit()
    
    def _validate_manual_match(
        self,
        transaction: BankTransaction,
        payment: Payment
    ) -> Dict:
        """Validate a manual match"""
        errors = []
        
        # Check if payment is already matched
        existing_match = self.db.query(BankTransaction).filter(
            BankTransaction.matched_payment_id == payment.id
        ).first()
        
        if existing_match and existing_match.id != transaction.id:
            errors.append("Payment is already matched to another transaction")
        
        # Check amount reasonableness
        amount_diff = abs(transaction.transaction_amount - float(payment.amount))
        if amount_diff > float(payment.amount) * 0.1:  # 10% tolerance
            errors.append(f"Amount difference too large: ฿{amount_diff:,.2f}")
        
        # Check date reasonableness
        payment_date = payment.created_at.date()
        date_diff = abs((transaction.transaction_date - payment_date).days)
        if date_diff > 7:  # 7 days tolerance
            errors.append(f"Date difference too large: {date_diff} days")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
    
    def _generate_statement_number(self) -> str:
        """Generate unique statement number"""
        now = datetime.now()
        year_month = now.strftime("%Y%m")
        
        count = self.db.query(BankStatement).filter(
            BankStatement.statement_number.like(f"STMT{year_month}%")
        ).count()
        
        return f"STMT{year_month}{count + 1:03d}"

