"""
OCR Service - AI OCR for Reading Payment Slips
"""
import re
import hashlib
from typing import Dict, Optional, Tuple, List
from datetime import datetime
from decimal import Decimal
import json
from pathlib import Path

# Note: In production, you would use actual OCR libraries like:
# - Google Cloud Vision API
# - AWS Textract
# - Azure Computer Vision
# - Tesseract OCR
# For now, we'll create a mock implementation that can be replaced


class OCRService:
    """Service for extracting payment information from slip images using AI OCR"""
    
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.pdf']
        self.thai_banks = [
            'กสิกรไทย', 'ไทยพาณิชย์', 'กรุงเทพ', 'กรุงไทย', 'ทหารไทยธนชาต',
            'ธนาคารออมสิน', 'อาคารสงเคราะห์', 'เกียรตินาคินภัทร', 'ซีไอเอ็มบี',
            'ยูโอบี', 'สแตนดาร์ดชาร์เตอร์ด', 'ดอยซ์แบงก์', 'ไอซีบีซี',
            'Kasikorn', 'SCB', 'BBL', 'KTB', 'TMB', 'GSB', 'BAY', 'KKP',
            'CIMB', 'UOB', 'SCBT', 'ICBC'
        ]
    
    def calculate_file_hash(self, file_path: str) -> str:
        """
        Calculate SHA-256 hash of file for duplicate detection
        
        Args:
            file_path: Path to the file
            
        Returns:
            SHA-256 hash string
        """
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                # Read file in chunks to handle large files
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            raise ValueError(f"Error calculating file hash: {e}")
    
    def extract_payment_info(self, file_path: str) -> Dict:
        """
        Extract payment information from slip image using OCR
        
        Args:
            file_path: Path to the slip image file
            
        Returns:
            Dictionary containing extracted information
        """
        # Validate file
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = Path(file_path).suffix.lower()
        if file_extension not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        # Calculate file hash for duplicate detection
        file_hash = self.calculate_file_hash(file_path)
        
        # Mock OCR processing (replace with actual OCR service)
        ocr_result = self._mock_ocr_processing(file_path)
        
        # Extract structured data from OCR text
        extracted_data = self._extract_structured_data(ocr_result['raw_text'])
        
        return {
            'file_hash': file_hash,
            'file_size': Path(file_path).stat().st_size,
            'raw_text': ocr_result['raw_text'],
            'confidence_score': ocr_result['confidence'],
            'extracted_data': extracted_data,
            'processing_time': ocr_result['processing_time']
        }
    
    def _mock_ocr_processing(self, file_path: str) -> Dict:
        """
        Mock OCR processing (replace with actual OCR service)
        
        In production, this would call:
        - Google Cloud Vision API
        - AWS Textract
        - Azure Computer Vision
        - Or local Tesseract OCR
        """
        # Simulate OCR processing time
        import time
        time.sleep(0.5)  # Simulate processing delay
        
        # Mock OCR text result (this would come from actual OCR)
        mock_text = """
        ธนาคารกสิกรไทย
        K PLUS
        โอนเงิน
        วันที่: 15/01/2025
        เวลา: 14:30:25
        จำนวนเงิน: 2,500.00 บาท
        ค่าธรรมเนียม: 0.00 บาท
        หมายเลขอ้างอิง: 202501151430001
        จาก: นายสมชาย ใจดี
        ไปยัง: บริษัท สมาร์ทวิลเลจ จำกัด
        เลขที่บัญชี: 123-4-56789-0
        """
        
        return {
            'raw_text': mock_text.strip(),
            'confidence': 0.95,  # 95% confidence
            'processing_time': 0.5
        }
    
    def _extract_structured_data(self, raw_text: str) -> Dict:
        """
        Extract structured data from OCR raw text
        
        Args:
            raw_text: Raw text from OCR
            
        Returns:
            Dictionary with extracted structured data
        """
        extracted = {
            'amount': None,
            'date': None,
            'time': None,
            'bank_name': None,
            'reference_number': None,
            'account_number': None,
            'sender_name': None,
            'receiver_name': None
        }
        
        # Extract amount (support various formats)
        amount_patterns = [
            r'จำนวนเงิน[:\s]*([0-9,]+\.?[0-9]*)\s*บาท',
            r'Amount[:\s]*([0-9,]+\.?[0-9]*)',
            r'([0-9,]+\.?[0-9]*)\s*บาท',
            r'฿\s*([0-9,]+\.?[0-9]*)',
            r'THB\s*([0-9,]+\.?[0-9]*)'
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, raw_text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    extracted['amount'] = float(amount_str)
                    break
                except ValueError:
                    continue
        
        # Extract date (support various formats)
        date_patterns = [
            r'วันที่[:\s]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
            r'Date[:\s]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
            r'(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, raw_text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                try:
                    # Try different date formats
                    for date_format in ['%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%m-%d-%Y']:
                        try:
                            extracted['date'] = datetime.strptime(date_str, date_format)
                            break
                        except ValueError:
                            continue
                    if extracted['date']:
                        break
                except ValueError:
                    continue
        
        # Extract time
        time_patterns = [
            r'เวลา[:\s]*(\d{1,2}:\d{2}(?::\d{2})?)',
            r'Time[:\s]*(\d{1,2}:\d{2}(?::\d{2})?)',
            r'(\d{1,2}:\d{2}(?::\d{2})?)'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, raw_text, re.IGNORECASE)
            if match:
                extracted['time'] = match.group(1)
                break
        
        # Extract bank name
        for bank in self.thai_banks:
            if bank in raw_text:
                extracted['bank_name'] = bank
                break
        
        # Extract reference number
        ref_patterns = [
            r'หมายเลขอ้างอิง[:\s]*([A-Z0-9]+)',
            r'Reference[:\s]*([A-Z0-9]+)',
            r'Ref[:\s]*([A-Z0-9]+)',
            r'อ้างอิง[:\s]*([A-Z0-9]+)'
        ]
        
        for pattern in ref_patterns:
            match = re.search(pattern, raw_text, re.IGNORECASE)
            if match:
                extracted['reference_number'] = match.group(1)
                break
        
        # Extract account number
        account_patterns = [
            r'เลขที่บัญชี[:\s]*([0-9\-]+)',
            r'Account[:\s]*([0-9\-]+)',
            r'A/C[:\s]*([0-9\-]+)'
        ]
        
        for pattern in account_patterns:
            match = re.search(pattern, raw_text, re.IGNORECASE)
            if match:
                extracted['account_number'] = match.group(1)
                break
        
        # Extract sender name
        sender_patterns = [
            r'จาก[:\s]*([^\n]+)',
            r'From[:\s]*([^\n]+)',
            r'ผู้โอน[:\s]*([^\n]+)'
        ]
        
        for pattern in sender_patterns:
            match = re.search(pattern, raw_text, re.IGNORECASE)
            if match:
                extracted['sender_name'] = match.group(1).strip()
                break
        
        # Extract receiver name
        receiver_patterns = [
            r'ไปยัง[:\s]*([^\n]+)',
            r'To[:\s]*([^\n]+)',
            r'ผู้รับ[:\s]*([^\n]+)'
        ]
        
        for pattern in receiver_patterns:
            match = re.search(pattern, raw_text, re.IGNORECASE)
            if match:
                extracted['receiver_name'] = match.group(1).strip()
                break
        
        return extracted
    
    def validate_extracted_data(self, extracted_data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate extracted data quality
        
        Args:
            extracted_data: Dictionary with extracted data
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        if not extracted_data.get('amount'):
            errors.append("ไม่พบจำนวนเงิน")
        elif extracted_data['amount'] <= 0:
            errors.append("จำนวนเงินไม่ถูกต้อง")
        
        if not extracted_data.get('date'):
            errors.append("ไม่พบวันที่")
        elif isinstance(extracted_data['date'], datetime):
            # Check if date is reasonable (not too old or in future)
            days_diff = (datetime.now() - extracted_data['date']).days
            if days_diff > 365:
                errors.append("วันที่เก่าเกินไป (เกิน 1 ปี)")
            elif days_diff < -7:
                errors.append("วันที่ในอนาคต")
        
        if not extracted_data.get('time'):
            errors.append("ไม่พบเวลา")
        
        # Check data consistency
        if extracted_data.get('amount') and extracted_data['amount'] > 1000000:
            errors.append("จำนวนเงินสูงผิดปกติ (เกิน 1 ล้านบาท)")
        
        return len(errors) == 0, errors
    
    def is_duplicate_slip(self, file_hash: str, existing_hashes: List[str]) -> bool:
        """
        Check if slip is duplicate based on file hash
        
        Args:
            file_hash: Hash of current file
            existing_hashes: List of existing file hashes in database
            
        Returns:
            True if duplicate, False otherwise
        """
        return file_hash in existing_hashes

