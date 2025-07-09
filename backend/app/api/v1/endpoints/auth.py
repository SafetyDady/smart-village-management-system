"""
Authentication Endpoints - Smart Village Management System
"""

from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_user,
    get_current_active_user
)
from app.schemas.auth import Token, TokenRefresh, LineLogin, UserLogin
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.services.line_service import LineService

router = APIRouter()


@router.post("/login", response_model=Token)
async def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    auth_service = AuthService(db)
    
    user = await auth_service.authenticate_user(
        email=form_data.username,
        password=form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token = create_access_token(
        subject=user.email,
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        subject=user.email,
        expires_delta=refresh_token_expires
    )
    
    # Store refresh token in database
    await auth_service.store_refresh_token(user.id, refresh_token)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/line/login", response_model=Token)
async def line_login(
    line_data: LineLogin,
    db: Session = Depends(get_db)
) -> Any:
    """
    LINE LIFF login endpoint
    """
    line_service = LineService()
    auth_service = AuthService(db)
    
    try:
        # Verify LINE ID token
        line_profile = await line_service.verify_id_token(line_data.id_token)
        
        if not line_profile or "sub" not in line_profile:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid LINE token"
            )
        
        # Get or create user from LINE profile
        user = await auth_service.get_or_create_line_user(line_profile)
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        access_token = create_access_token(
            subject=user.email,
            expires_delta=access_token_expires
        )
        
        refresh_token = create_refresh_token(
            subject=user.email,
            expires_delta=refresh_token_expires
        )
        
        # Store refresh token in database
        await auth_service.store_refresh_token(user.id, refresh_token)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"LINE authentication failed: {str(e)}"
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
) -> Any:
    """
    Refresh access token using refresh token
    """
    auth_service = AuthService(db)
    
    # Verify refresh token
    email = verify_token(token_data.refresh_token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Check if refresh token exists in database
    if not await auth_service.verify_refresh_token(email, token_data.refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found or expired"
        )
    
    # Get user
    user = await auth_service.get_user_by_email(email)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    new_access_token = create_access_token(
        subject=user.email,
        expires_delta=access_token_expires
    )
    
    new_refresh_token = create_refresh_token(
        subject=user.email,
        expires_delta=refresh_token_expires
    )
    
    # Replace old refresh token with new one
    await auth_service.replace_refresh_token(
        user.id,
        token_data.refresh_token,
        new_refresh_token
    )
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/logout")
async def logout(
    refresh_token: str = Body(..., embed=True),
    current_user: Any = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Logout user by invalidating refresh token
    """
    auth_service = AuthService(db)
    
    await auth_service.revoke_refresh_token(current_user.id, refresh_token)
    
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: Any = Depends(get_current_active_user)
) -> Any:
    """
    Get current user information
    """
    return current_user


@router.post("/verify-email")
async def verify_email(
    token: str = Body(..., embed=True),
    db: Session = Depends(get_db)
) -> Any:
    """
    Verify user email address
    """
    auth_service = AuthService(db)
    
    success = await auth_service.verify_email_token(token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    return {"message": "Email verified successfully"}


@router.post("/forgot-password")
async def forgot_password(
    email: str = Body(..., embed=True),
    db: Session = Depends(get_db)
) -> Any:
    """
    Send password reset email
    """
    auth_service = AuthService(db)
    
    await auth_service.send_password_reset_email(email)
    
    return {"message": "Password reset email sent if account exists"}


@router.post("/reset-password")
async def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(get_db)
) -> Any:
    """
    Reset password using reset token
    """
    auth_service = AuthService(db)
    
    success = await auth_service.reset_password(token, new_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    return {"message": "Password reset successfully"}

