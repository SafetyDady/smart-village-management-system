from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.village import Village
from app.models.invoice import Invoice, InvoiceStatus
from app.models.payment import Payment
from typing import Dict, Any

router = APIRouter()

@router.get("/dashboard-summary")
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get dashboard summary data for Super Admin
    Returns total villages, revenue, active users, and pending invoices
    """
    try:
        # Total Villages
        total_villages = db.query(Village).count()
        
        # Total Revenue (sum of all paid invoices)
        total_revenue_result = db.query(func.sum(Invoice.amount)).filter(
            Invoice.status == InvoiceStatus.PAID
        ).scalar()
        total_revenue = float(total_revenue_result) if total_revenue_result else 0.0
        
        # Active Users (users who logged in within last 30 days)
        # For now, we'll count all users as active
        active_users = db.query(User).count()
        
        # Pending Invoices
        pending_invoices = db.query(Invoice).filter(
            Invoice.status == InvoiceStatus.PENDING
        ).count()
        
        # Calculate growth percentages (mock for now, can be enhanced later)
        # In real implementation, you would compare with previous period
        village_growth = "+2 this month"  # Mock data
        revenue_growth = "+15% from last month"  # Mock data  
        user_growth = "+8% from last month"  # Mock data
        invoice_growth = "-12% from last month"  # Mock data
        
        return {
            "total_villages": total_villages,
            "total_revenue": total_revenue,
            "active_users": active_users,
            "pending_invoices": pending_invoices,
            "growth": {
                "villages": village_growth,
                "revenue": revenue_growth,
                "users": user_growth,
                "invoices": invoice_growth
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard summary: {str(e)}")

@router.get("/recent-activities")
async def get_recent_activities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 10
) -> Dict[str, Any]:
    """
    Get recent activities for dashboard
    """
    try:
        # Get recent invoices
        recent_invoices = db.query(Invoice).order_by(
            Invoice.created_at.desc()
        ).limit(limit//2).all()
        
        # Get recent payments
        recent_payments = db.query(Payment).order_by(
            Payment.created_at.desc()
        ).limit(limit//2).all()
        
        activities = []
        
        # Add invoice activities
        for invoice in recent_invoices:
            activities.append({
                "type": "invoice",
                "message": f"New invoice #{invoice.invoice_number} created",
                "amount": invoice.amount,
                "timestamp": invoice.created_at.isoformat(),
                "icon": "receipt"
            })
        
        # Add payment activities
        for payment in recent_payments:
            activities.append({
                "type": "payment", 
                "message": f"Payment received for invoice #{payment.invoice_id}",
                "amount": payment.amount,
                "timestamp": payment.created_at.isoformat(),
                "icon": "credit-card"
            })
        
        # Sort by timestamp (most recent first)
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {
            "activities": activities[:limit]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch recent activities: {str(e)}")

