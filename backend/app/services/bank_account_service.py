"""
Bank Account Service - Business Logic for Bank Account Management
"""
from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.models.bank_account import BankAccount, BankAccountStatus, BankAccountType


class BankAccountService:
    """Service for managing bank accounts (max 2 per village)"""
    
    def __init__(self, db: Session):
        self.db = db
        self.MAX_ACCOUNTS_PER_VILLAGE = 2
    
    def create_bank_account(
        self,
        village_id: str,
        account_number: str,
        account_name: str,
        bank_name: str,
        bank_code: str,
        account_type: BankAccountType,
        created_by_id: str,
        branch_name: Optional[str] = None,
        branch_code: Optional[str] = None,
        contact_person: Optional[str] = None,
        contact_phone: Optional[str] = None,
        description: Optional[str] = None,
        is_primary: bool = False
    ) -> BankAccount:
        """
        Create a new bank account for village
        
        Args:
            village_id: Village UUID
            account_number: Bank account number
            account_name: Account holder name
            bank_name: Bank name
            bank_code: Bank code (e.g., 'KBANK', 'SCB')
            account_type: Type of account
            created_by_id: User who created the account
            branch_name: Bank branch name
            branch_code: Bank branch code
            contact_person: Contact person for this account
            contact_phone: Contact phone number
            description: Account description
            is_primary: Whether this is the primary account
            
        Returns:
            Created BankAccount object
        """
        # Check village account limit
        existing_accounts = self.get_accounts_by_village(village_id)
        if len(existing_accounts) >= self.MAX_ACCOUNTS_PER_VILLAGE:
            raise ValueError(f"Village can have maximum {self.MAX_ACCOUNTS_PER_VILLAGE} bank accounts")
        
        # Check for duplicate account number
        existing_account = self.db.query(BankAccount).filter(
            BankAccount.account_number == account_number
        ).first()
        
        if existing_account:
            raise ValueError(f"Account number {account_number} already exists")
        
        # If this is the first account or explicitly set as primary, make it primary
        if not existing_accounts or is_primary:
            # Remove primary status from other accounts in the same village
            self.db.query(BankAccount).filter(
                and_(
                    BankAccount.village_id == village_id,
                    BankAccount.is_primary == True
                )
            ).update({"is_primary": False})
            is_primary = True
        
        # Create bank account
        bank_account = BankAccount(
            account_number=account_number,
            account_name=account_name,
            bank_name=bank_name,
            bank_code=bank_code,
            branch_name=branch_name,
            branch_code=branch_code,
            account_type=account_type.value,
            village_id=village_id,
            is_primary=is_primary,
            contact_person=contact_person,
            contact_phone=contact_phone,
            description=description,
            created_by_id=created_by_id,
            opened_date=datetime.now()
        )
        
        self.db.add(bank_account)
        self.db.commit()
        self.db.refresh(bank_account)
        
        return bank_account
    
    def update_bank_account(
        self,
        account_id: str,
        account_name: Optional[str] = None,
        contact_person: Optional[str] = None,
        contact_phone: Optional[str] = None,
        description: Optional[str] = None,
        notes: Optional[str] = None
    ) -> BankAccount:
        """
        Update bank account information
        
        Args:
            account_id: BankAccount UUID
            account_name: New account name
            contact_person: New contact person
            contact_phone: New contact phone
            description: New description
            notes: New notes
            
        Returns:
            Updated BankAccount object
        """
        account = self.get_account_by_id(account_id)
        if not account:
            raise ValueError(f"Bank account {account_id} not found")
        
        if account_name is not None:
            account.account_name = account_name
        if contact_person is not None:
            account.contact_person = contact_person
        if contact_phone is not None:
            account.contact_phone = contact_phone
        if description is not None:
            account.description = description
        if notes is not None:
            account.notes = notes
        
        self.db.commit()
        self.db.refresh(account)
        
        return account
    
    def set_primary_account(self, account_id: str, village_id: str) -> BankAccount:
        """
        Set an account as primary for the village
        
        Args:
            account_id: BankAccount UUID to set as primary
            village_id: Village UUID
            
        Returns:
            Updated BankAccount object
        """
        account = self.get_account_by_id(account_id)
        if not account:
            raise ValueError(f"Bank account {account_id} not found")
        
        if account.village_id != village_id:
            raise ValueError("Account does not belong to this village")
        
        # Remove primary status from other accounts
        self.db.query(BankAccount).filter(
            and_(
                BankAccount.village_id == village_id,
                BankAccount.id != account_id
            )
        ).update({"is_primary": False})
        
        # Set this account as primary
        account.is_primary = True
        
        self.db.commit()
        self.db.refresh(account)
        
        return account
    
    def deactivate_account(self, account_id: str, reason: str) -> BankAccount:
        """
        Deactivate a bank account
        
        Args:
            account_id: BankAccount UUID
            reason: Reason for deactivation
            
        Returns:
            Updated BankAccount object
        """
        account = self.get_account_by_id(account_id)
        if not account:
            raise ValueError(f"Bank account {account_id} not found")
        
        account.status = BankAccountStatus.INACTIVE.value
        account.notes = f"{account.notes or ''}\nDeactivated: {reason}".strip()
        
        # If this was the primary account, set another account as primary
        if account.is_primary:
            other_accounts = self.get_active_accounts_by_village(account.village_id)
            other_accounts = [a for a in other_accounts if a.id != account_id]
            
            if other_accounts:
                other_accounts[0].is_primary = True
            
            account.is_primary = False
        
        self.db.commit()
        self.db.refresh(account)
        
        return account
    
    def close_account(self, account_id: str, reason: str) -> BankAccount:
        """
        Close a bank account permanently
        
        Args:
            account_id: BankAccount UUID
            reason: Reason for closure
            
        Returns:
            Updated BankAccount object
        """
        account = self.get_account_by_id(account_id)
        if not account:
            raise ValueError(f"Bank account {account_id} not found")
        
        account.status = BankAccountStatus.CLOSED.value
        account.closed_date = datetime.now()
        account.notes = f"{account.notes or ''}\nClosed: {reason}".strip()
        
        # If this was the primary account, set another account as primary
        if account.is_primary:
            other_accounts = self.get_active_accounts_by_village(account.village_id)
            other_accounts = [a for a in other_accounts if a.id != account_id]
            
            if other_accounts:
                other_accounts[0].is_primary = True
            
            account.is_primary = False
        
        self.db.commit()
        self.db.refresh(account)
        
        return account
    
    def update_balance(
        self,
        account_id: str,
        balance: float,
        as_of_date: Optional[datetime] = None
    ) -> BankAccount:
        """
        Update account balance (for reference only)
        
        Args:
            account_id: BankAccount UUID
            balance: New balance amount
            as_of_date: Date of balance (defaults to now)
            
        Returns:
            Updated BankAccount object
        """
        account = self.get_account_by_id(account_id)
        if not account:
            raise ValueError(f"Bank account {account_id} not found")
        
        account.last_known_balance = balance
        account.balance_as_of = as_of_date or datetime.now()
        
        self.db.commit()
        self.db.refresh(account)
        
        return account
    
    def get_account_by_id(self, account_id: str) -> Optional[BankAccount]:
        """Get bank account by ID"""
        return self.db.query(BankAccount).filter(BankAccount.id == account_id).first()
    
    def get_account_by_number(self, account_number: str) -> Optional[BankAccount]:
        """Get bank account by account number"""
        return self.db.query(BankAccount).filter(
            BankAccount.account_number == account_number
        ).first()
    
    def get_accounts_by_village(self, village_id: str) -> List[BankAccount]:
        """Get all bank accounts for a village"""
        return self.db.query(BankAccount).filter(
            BankAccount.village_id == village_id
        ).order_by(desc(BankAccount.is_primary), BankAccount.created_at.asc()).all()
    
    def get_active_accounts_by_village(self, village_id: str) -> List[BankAccount]:
        """Get active bank accounts for a village"""
        return self.db.query(BankAccount).filter(
            and_(
                BankAccount.village_id == village_id,
                BankAccount.status == BankAccountStatus.ACTIVE.value
            )
        ).order_by(desc(BankAccount.is_primary), BankAccount.created_at.asc()).all()
    
    def get_primary_account(self, village_id: str) -> Optional[BankAccount]:
        """Get primary bank account for a village"""
        return self.db.query(BankAccount).filter(
            and_(
                BankAccount.village_id == village_id,
                BankAccount.is_primary == True,
                BankAccount.status == BankAccountStatus.ACTIVE.value
            )
        ).first()
    
    def can_add_account(self, village_id: str) -> bool:
        """Check if village can add more accounts"""
        existing_count = self.db.query(BankAccount).filter(
            and_(
                BankAccount.village_id == village_id,
                BankAccount.status.in_([
                    BankAccountStatus.ACTIVE.value,
                    BankAccountStatus.INACTIVE.value
                ])
            )
        ).count()
        
        return existing_count < self.MAX_ACCOUNTS_PER_VILLAGE
    
    def get_account_summary(self, village_id: str) -> Dict:
        """Get summary of bank accounts for a village"""
        accounts = self.get_accounts_by_village(village_id)
        
        active_accounts = [a for a in accounts if a.status == BankAccountStatus.ACTIVE.value]
        primary_account = next((a for a in accounts if a.is_primary), None)
        
        total_balance = sum(
            float(a.last_known_balance or 0) 
            for a in active_accounts 
            if a.last_known_balance is not None
        )
        
        return {
            "total_accounts": len(accounts),
            "active_accounts": len(active_accounts),
            "can_add_more": self.can_add_account(village_id),
            "primary_account": {
                "id": str(primary_account.id),
                "display_name": primary_account.display_name,
                "balance": float(primary_account.last_known_balance or 0)
            } if primary_account else None,
            "total_balance": total_balance,
            "accounts": [
                {
                    "id": str(a.id),
                    "display_name": a.display_name,
                    "bank_name": a.bank_name,
                    "status": a.status,
                    "is_primary": a.is_primary,
                    "balance": float(a.last_known_balance or 0),
                    "reconciliation_summary": a.reconciliation_summary
                }
                for a in accounts
            ]
        }

