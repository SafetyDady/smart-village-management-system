"""
Bank Statement OCR Service - AI OCR for Reading Bank Statements
"""
import re
import hashlib
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date
from decimal import Decimal
import json
from pathlib import Path

from app.services.ocr_service import OCRService


class BankStatementOCRService(OCRService):
    """Service for extracting transaction data from bank statement files using AI OCR"""
    
    def __init__(self):
        super().__init__()
        self.statement_patterns = {
            'kasikorn': {
                'bank_name': 'กสิกรไทย|Kasikorn|KBANK',
                'account_pattern': r'เลขที่บัญชี[:\s]*([0-9\-]+)',
                'balance_pattern': r'ยอดคงเหลือ[:\s]*([0-9,]+\.?[0-9]*)',
                'transaction_pattern': r'(\d{2}/\d{2}/\d{4})\s+([^\d]+)\s+([0-9,]+\.?[0-9]*)'
            },
            'scb': {
                'bank_name': 'ไทยพาณิชย์|SCB|Siam Commercial',
                'account_pattern': r'Account No[:\s]*([0-9\-]+)',
                'balance_pattern': r'Balance[:\s]*([0-9,]+\.?[0-9]*)',
                'transaction_pattern': r'(\d{2}/\d{2}/\d{4})\s+([^\d]+)\s+([0-9,]+\.?[0-9]*)'
            },
            'bbl': {
                'bank_name': 'กรุงเทพ|Bangkok Bank|BBL',
                'account_pattern': r'บัญชีเลขที่[:\s]*([0-9\-]+)',
                'balance_pattern': r'ยอดยกมา[:\s]*([0-9,]+\.?[0-9]*)',
                'transaction_pattern': r'(\d{2}/\d{2}/\d{4})\s+([^\d]+)\s+([0-9,]+\.?[0-9]*)'
            }
        }
    
    def extract_bank_statement_data(self, file_path: str) -> Dict:
        """
        Extract complete bank statement data including all transactions
        
        Args:
            file_path: Path to the bank statement file
            
        Returns:
            Dictionary containing statement info and transactions
        """
        # Basic file validation and OCR
        basic_result = self.extract_payment_info(file_path)
        
        # Get raw OCR text
        raw_text = basic_result['raw_text']
        
        # Detect bank type
        bank_type = self._detect_bank_type(raw_text)
        
        # Extract statement header information
        statement_info = self._extract_statement_info(raw_text, bank_type)
        
        # Extract all transactions
        transactions = self._extract_transactions(raw_text, bank_type)
        
        # Validate extracted data
        validation_result = self._validate_statement_data(statement_info, transactions)
        
        return {
            'file_hash': basic_result['file_hash'],
            'file_size': basic_result['file_size'],
            'raw_text': raw_text,
            'confidence_score': basic_result['confidence_score'],
            'bank_type': bank_type,
            'statement_info': statement_info,
            'transactions': transactions,
            'validation': validation_result,
            'processing_time': basic_result['processing_time']
        }
    
    def _detect_bank_type(self, raw_text: str) -> str:
        """Detect bank type from OCR text"""
        for bank_code, patterns in self.statement_patterns.items():
            if re.search(patterns['bank_name'], raw_text, re.IGNORECASE):
                return bank_code
        return 'unknown'
    
    def _extract_statement_info(self, raw_text: str, bank_type: str) -> Dict:
        """Extract statement header information"""
        info = {
            'bank_name': None,
            'account_number': None,
            'account_name': None,
            'statement_date': None,
            'period_start': None,
            'period_end': None,
            'opening_balance': None,
            'closing_balance': None
        }
        
        # Extract bank name
        if bank_type in self.statement_patterns:
            bank_pattern = self.statement_patterns[bank_type]['bank_name']
            bank_match = re.search(bank_pattern, raw_text, re.IGNORECASE)
            if bank_match:
                info['bank_name'] = bank_match.group(0)
        
        # Extract account number
        if bank_type in self.statement_patterns:
            account_pattern = self.statement_patterns[bank_type]['account_pattern']
            account_match = re.search(account_pattern, raw_text, re.IGNORECASE)
            if account_match:
                info['account_number'] = account_match.group(1).replace('-', '')
        
        # Extract account name
        name_patterns = [
            r'ชื่อบัญชี[:\s]*([^\n]+)',
            r'Account Name[:\s]*([^\n]+)',
            r'Name[:\s]*([^\n]+)'
        ]
        for pattern in name_patterns:
            match = re.search(pattern, raw_text, re.IGNORECASE)
            if match:
                info['account_name'] = match.group(1).strip()
                break
        
        # Extract statement period
        period_patterns = [
            r'ระหว่างวันที่[:\s]*(\d{2}/\d{2}/\d{4})\s*ถึง\s*(\d{2}/\d{2}/\d{4})',
            r'Period[:\s]*(\d{2}/\d{2}/\d{4})\s*to\s*(\d{2}/\d{2}/\d{4})',
            r'From[:\s]*(\d{2}/\d{2}/\d{4})\s*To[:\s]*(\d{2}/\d{2}/\d{4})'
        ]
        
        for pattern in period_patterns:
            match = re.search(pattern, raw_text, re.IGNORECASE)
            if match:
                try:
                    info['period_start'] = datetime.strptime(match.group(1), '%d/%m/%Y').date()
                    info['period_end'] = datetime.strptime(match.group(2), '%d/%m/%Y').date()
                    break
                except ValueError:
                    continue
        
        # Extract balances
        balance_patterns = [
            r'ยอดยกมา[:\s]*([0-9,]+\.?[0-9]*)',
            r'Opening Balance[:\s]*([0-9,]+\.?[0-9]*)',
            r'ยอดคงเหลือ[:\s]*([0-9,]+\.?[0-9]*)',
            r'Closing Balance[:\s]*([0-9,]+\.?[0-9]*)'
        ]
        
        for i, pattern in enumerate(balance_patterns):
            match = re.search(pattern, raw_text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = float(amount_str)
                    if i < 2:  # Opening balance patterns
                        info['opening_balance'] = amount
                    else:  # Closing balance patterns
                        info['closing_balance'] = amount
                except ValueError:
                    continue
        
        return info
    
    def _extract_transactions(self, raw_text: str, bank_type: str) -> List[Dict]:
        """Extract all transactions from statement"""
        transactions = []
        
        # Common transaction patterns
        transaction_patterns = [
            # Date + Description + Amount
            r'(\d{2}/\d{2}/\d{4})\s+([^0-9\n]+?)\s+([0-9,]+\.?[0-9]*)',
            # Date + Time + Description + Amount
            r'(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2})\s+([^0-9\n]+?)\s+([0-9,]+\.?[0-9]*)',
            # More complex pattern with reference
            r'(\d{2}/\d{2}/\d{4})\s+([^0-9\n]+?)\s+([A-Z0-9]+)\s+([0-9,]+\.?[0-9]*)'
        ]
        
        lines = raw_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Try each pattern
            for pattern in transaction_patterns:
                match = re.search(pattern, line)
                if match:
                    try:
                        transaction = self._parse_transaction_match(match, pattern)
                        if transaction:
                            transactions.append(transaction)
                            break
                    except Exception:
                        continue
        
        # Remove duplicates and sort by date
        unique_transactions = []
        seen_transactions = set()
        
        for trans in transactions:
            # Create a unique key for deduplication
            key = f"{trans['date']}_{trans['description']}_{trans['amount']}"
            if key not in seen_transactions:
                seen_transactions.add(key)
                unique_transactions.append(trans)
        
        # Sort by date
        unique_transactions.sort(key=lambda x: x['date'])
        
        return unique_transactions
    
    def _parse_transaction_match(self, match, pattern: str) -> Optional[Dict]:
        """Parse a regex match into transaction data"""
        groups = match.groups()
        
        try:
            # Parse date
            date_str = groups[0]
            trans_date = datetime.strptime(date_str, '%d/%m/%Y').date()
            
            # Determine if pattern includes time
            if len(groups) == 4 and ':' in groups[1]:
                # Pattern with time
                time_str = groups[1]
                description = groups[2].strip()
                amount_str = groups[3]
            else:
                # Pattern without time
                time_str = None
                description = groups[1].strip()
                amount_str = groups[-1]  # Last group is always amount
            
            # Parse amount
            amount = float(amount_str.replace(',', ''))
            
            # Determine if credit or debit based on description keywords
            is_credit = self._is_credit_transaction(description)
            
            # Extract reference if present
            reference = self._extract_reference_from_description(description)
            
            return {
                'date': trans_date,
                'time': time_str,
                'description': description,
                'reference': reference,
                'amount': amount,
                'is_credit': is_credit,
                'credit_amount': amount if is_credit else None,
                'debit_amount': amount if not is_credit else None,
                'raw_text': match.group(0)
            }
            
        except (ValueError, IndexError):
            return None
    
    def _is_credit_transaction(self, description: str) -> bool:
        """Determine if transaction is credit (money in) based on description"""
        credit_keywords = [
            'โอนเข้า', 'ฝาก', 'รับโอน', 'เงินเข้า', 'Transfer In', 'Deposit',
            'Credit', 'Received', 'Income', 'Payment Received'
        ]
        
        debit_keywords = [
            'โอนออก', 'ถอน', 'จ่าย', 'เงินออก', 'Transfer Out', 'Withdrawal',
            'Debit', 'Payment', 'Fee', 'Charge'
        ]
        
        description_lower = description.lower()
        
        # Check for credit keywords
        for keyword in credit_keywords:
            if keyword.lower() in description_lower:
                return True
        
        # Check for debit keywords
        for keyword in debit_keywords:
            if keyword.lower() in description_lower:
                return False
        
        # Default assumption based on common patterns
        # If description contains account numbers or names, likely a transfer in
        if re.search(r'[0-9]{3,}', description):
            return True
        
        return False  # Default to debit if uncertain
    
    def _extract_reference_from_description(self, description: str) -> Optional[str]:
        """Extract reference number from transaction description"""
        # Common reference patterns
        ref_patterns = [
            r'Ref[:\s]*([A-Z0-9]+)',
            r'อ้างอิง[:\s]*([A-Z0-9]+)',
            r'([A-Z0-9]{10,})',  # Long alphanumeric strings
            r'TXN[:\s]*([A-Z0-9]+)'
        ]
        
        for pattern in ref_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _validate_statement_data(self, statement_info: Dict, transactions: List[Dict]) -> Dict:
        """Validate extracted statement data"""
        errors = []
        warnings = []
        
        # Validate statement info
        if not statement_info.get('account_number'):
            errors.append("ไม่พบเลขที่บัญชี")
        
        if not statement_info.get('period_start') or not statement_info.get('period_end'):
            errors.append("ไม่พบช่วงเวลาของ statement")
        
        # Validate transactions
        if not transactions:
            errors.append("ไม่พบรายการธุรกรรม")
        else:
            # Check for reasonable transaction amounts
            for trans in transactions:
                if trans['amount'] <= 0:
                    warnings.append(f"พบจำนวนเงินผิดปกติ: {trans['amount']}")
                elif trans['amount'] > 10000000:  # 10 million
                    warnings.append(f"จำนวนเงินสูงมาก: {trans['amount']:,.2f}")
        
        # Validate balance consistency
        if statement_info.get('opening_balance') and statement_info.get('closing_balance'):
            calculated_balance = statement_info['opening_balance']
            for trans in transactions:
                if trans['is_credit']:
                    calculated_balance += trans['amount']
                else:
                    calculated_balance -= trans['amount']
            
            balance_diff = abs(calculated_balance - statement_info['closing_balance'])
            if balance_diff > 0.01:  # Allow small rounding differences
                warnings.append(f"ยอดคงเหลือไม่ตรงกัน: คำนวณได้ {calculated_balance:,.2f} แต่ statement แสดง {statement_info['closing_balance']:,.2f}")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'transaction_count': len(transactions),
            'date_range_valid': self._validate_date_range(statement_info, transactions)
        }
    
    def _validate_date_range(self, statement_info: Dict, transactions: List[Dict]) -> bool:
        """Validate that all transactions fall within statement period"""
        if not statement_info.get('period_start') or not statement_info.get('period_end'):
            return True  # Can't validate without period info
        
        start_date = statement_info['period_start']
        end_date = statement_info['period_end']
        
        for trans in transactions:
            trans_date = trans['date']
            if trans_date < start_date or trans_date > end_date:
                return False
        
        return True

