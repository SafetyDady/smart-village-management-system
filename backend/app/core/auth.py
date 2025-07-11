"""
Authentication utilities - Smart Village Management System
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.models.user import User

logger = logging.getLogger(__name__)
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user
    
    For testing purposes, this is a simplified implementation
    """
    # In a real implementation, you would validate the JWT token
    # For testing, we'll just return a mock user
    
    # Try to get user from database (for testing)
    user = db.query(User).first()
    
    if not user:
        # Create a test user if none exists
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            hashed_password="hashedpassword123",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current admin user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # In a real implementation, check for admin role
    # For testing, assume all users are admin
    return current_user

