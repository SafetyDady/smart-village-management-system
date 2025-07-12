"""
Accounting API Endpoints - Smart Village Management System
"""
from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.services.accounting_service import AccountingService
from app.schemas.accounting import (
    ChartOfAccountsResponse,
    JournalEntryResponse,
    JournalEntryCreate,
    GeneralLedgerResponse,
    TrialBalanceResponse,
    FinancialReportResponse,
    AccountingPeriodResponse
)
from app.core.auth import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/accounts", response_model=List[ChartOfAccountsResponse])
async def get_chart_of_accounts(
    account_type: Optional[str] = Query(None, description="Filter by account type"),
    active_only: bool = Query(True, description="Show only active accounts"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get Chart of Accounts"""
    try:
        accounting_service = AccountingService(db)
        
        if account_type:
            accounts = accounting_service.get_accounts_by_type(account_type)
        else:
            accounts = accounting_service.get_all_accounts()
        
        # Filter active accounts if requested
        if active_only:
            accounts = [acc for acc in accounts if acc.is_active]
        
        return accounts
        
    except Exception as e:
        logger.error(f"Failed to get chart of accounts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chart of accounts"
        )


@router.get("/accounts/{account_code}", response_model=ChartOfAccountsResponse)
async def get_account_by_code(
    account_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific account by code"""
    accounting_service = AccountingService(db)
    account = accounting_service.get_account_by_code(account_code)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account {account_code} not found"
        )
    
    return account


@router.get("/journal-entries", response_model=List[JournalEntryResponse])
async def get_journal_entries(
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    account_code: Optional[str] = Query(None, description="Filter by account code"),
    entry_type: Optional[str] = Query(None, description="Filter by entry type"),
    limit: int = Query(100, le=1000, description="Maximum number of entries"),
    offset: int = Query(0, ge=0, description="Number of entries to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get journal entries with optional filters"""
    try:
        accounting_service = AccountingService(db)
        
        # Build filters
        filters = {}
        if start_date:
            filters['start_date'] = start_date
        if end_date:
            filters['end_date'] = end_date
        if account_code:
            filters['account_code'] = account_code
        if entry_type:
            filters['entry_type'] = entry_type
        
        entries = accounting_service.get_journal_entries(
            filters=filters,
            limit=limit,
            offset=offset
        )
        
        return entries
        
    except Exception as e:
        logger.error(f"Failed to get journal entries: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve journal entries"
        )


@router.get("/journal-entries/{entry_id}", response_model=JournalEntryResponse)
async def get_journal_entry(
    entry_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific journal entry by ID"""
    accounting_service = AccountingService(db)
    entry = accounting_service.get_journal_entry_by_id(entry_id)
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found"
        )
    
    return entry


@router.post("/manual-entry", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_manual_journal_entry(
    entry_data: JournalEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create manual journal entry"""
    try:
        accounting_service = AccountingService(db)
        
        # Create journal entry
        entry = accounting_service.create_journal_entry(
            description=entry_data.description,
            reference_number=entry_data.reference_number,
            entry_type="MANUAL",
            lines=entry_data.lines,
            created_by_id=current_user.id
        )
        
        # Post the entry immediately
        accounting_service.post_journal_entry(entry.id)
        
        logger.info(f"Manual journal entry {entry.id} created by user {current_user.id}")
        return entry
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create manual journal entry: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create journal entry"
        )


@router.get("/ledger", response_model=List[GeneralLedgerResponse])
async def get_general_ledger(
    account_code: Optional[str] = Query(None, description="Filter by account code"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get general ledger entries"""
    try:
        accounting_service = AccountingService(db)
        
        filters = {}
        if account_code:
            filters['account_code'] = account_code
        if start_date:
            filters['start_date'] = start_date
        if end_date:
            filters['end_date'] = end_date
        
        ledger_entries = accounting_service.get_general_ledger(
            filters=filters,
            limit=limit,
            offset=offset
        )
        
        return ledger_entries
        
    except Exception as e:
        logger.error(f"Failed to get general ledger: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve general ledger"
        )


@router.get("/trial-balance", response_model=TrialBalanceResponse)
async def get_trial_balance(
    as_of_date: Optional[date] = Query(None, description="Trial balance as of date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get trial balance report"""
    try:
        accounting_service = AccountingService(db)
        
        if not as_of_date:
            as_of_date = datetime.now().date()
        
        trial_balance = accounting_service.generate_trial_balance(as_of_date)
        
        return trial_balance
        
    except Exception as e:
        logger.error(f"Failed to generate trial balance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate trial balance"
        )


@router.get("/reports/income-statement", response_model=FinancialReportResponse)
async def get_income_statement(
    start_date: date = Query(..., description="Report start date"),
    end_date: date = Query(..., description="Report end date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get income statement (profit & loss) report"""
    try:
        accounting_service = AccountingService(db)
        
        income_statement = accounting_service.generate_income_statement(
            start_date=start_date,
            end_date=end_date
        )
        
        return income_statement
        
    except Exception as e:
        logger.error(f"Failed to generate income statement: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate income statement"
        )


@router.get("/reports/balance-sheet", response_model=FinancialReportResponse)
async def get_balance_sheet(
    as_of_date: Optional[date] = Query(None, description="Balance sheet as of date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get balance sheet report"""
    try:
        accounting_service = AccountingService(db)
        
        if not as_of_date:
            as_of_date = datetime.now().date()
        
        balance_sheet = accounting_service.generate_balance_sheet(as_of_date)
        
        return balance_sheet
        
    except Exception as e:
        logger.error(f"Failed to generate balance sheet: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate balance sheet"
        )


@router.get("/periods", response_model=List[AccountingPeriodResponse])
async def get_accounting_periods(
    year: Optional[int] = Query(None, description="Filter by year"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get accounting periods"""
    try:
        accounting_service = AccountingService(db)
        periods = accounting_service.get_accounting_periods(year=year)
        
        return periods
        
    except Exception as e:
        logger.error(f"Failed to get accounting periods: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve accounting periods"
        )


@router.get("/periods/current", response_model=AccountingPeriodResponse)
async def get_current_period(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current accounting period"""
    try:
        accounting_service = AccountingService(db)
        period = accounting_service.get_current_period()
        
        return period
        
    except Exception as e:
        logger.error(f"Failed to get current period: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve current period"
        )


@router.post("/periods/{period_id}/close")
async def close_accounting_period(
    period_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Close an accounting period"""
    try:
        accounting_service = AccountingService(db)
        result = accounting_service.close_period(period_id, current_user.id)
        
        logger.info(f"Accounting period {period_id} closed by user {current_user.id}")
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to close period {period_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to close accounting period"
        )


@router.get("/health")
async def accounting_health_check(
    db: Session = Depends(get_db)
):
    """Health check for accounting system"""
    try:
        accounting_service = AccountingService(db)
        
        # Basic health checks
        account_count = len(accounting_service.get_all_accounts())
        current_period = accounting_service.get_current_period()
        
        return {
            "status": "healthy",
            "accounts_count": account_count,
            "current_period": current_period.name if current_period else None,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Accounting health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

