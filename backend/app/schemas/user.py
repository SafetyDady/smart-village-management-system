"""
User Schemas - Smart Village Management System
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, validator


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: str = "resident"
    is_active: bool = True


class UserCreate(UserBase):
    """User creation schema"""
    password: Optional[str] = None  # Optional for LINE-only users
    
    @validator('password')
    def validate_password(cls, v, values):
        if not v and 'line_user_id' not in values:
            raise ValueError('Password is required for non-LINE users')
        if v and len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserUpdate(BaseModel):
    """User update schema"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    profile_picture: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


class UserResponse(UserBase):
    """User response schema"""
    id: int
    is_verified: bool
    is_email_verified: bool
    is_phone_verified: bool
    line_user_id: Optional[str] = None
    line_display_name: Optional[str] = None
    profile_picture: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    last_login: Optional[datetime] = None
    mfa_enabled: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserList(BaseModel):
    """User list response schema"""
    users: List[UserResponse]
    total: int
    skip: int
    limit: int


class UserSummary(BaseModel):
    """User summary schema for references"""
    id: int
    email: str
    first_name: str
    last_name: str
    role: str
    
    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """User profile schema"""
    id: int
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    profile_picture: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    line_display_name: Optional[str] = None
    
    class Config:
        from_attributes = True

