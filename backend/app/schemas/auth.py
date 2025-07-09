"""
Authentication Schemas - Smart Village Management System
"""

from typing import Optional
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class TokenRefresh(BaseModel):
    """Token refresh request schema"""
    refresh_token: str


class UserLogin(BaseModel):
    """User login request schema"""
    email: EmailStr
    password: str


class LineLogin(BaseModel):
    """LINE login request schema"""
    id_token: str
    access_token: Optional[str] = None


class PasswordReset(BaseModel):
    """Password reset request schema"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str
    new_password: str


class ChangePassword(BaseModel):
    """Change password request schema"""
    current_password: str
    new_password: str


class EmailVerification(BaseModel):
    """Email verification schema"""
    token: str

