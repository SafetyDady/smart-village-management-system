"""
Village Schemas - Smart Village Management System
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, validator


class VillageBase(BaseModel):
    """Base village schema"""
    name: str
    code: str
    description: Optional[str] = None
    address: str
    city: str
    state: str
    postal_code: str
    country: str = "Thailand"
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None


class VillageCreate(VillageBase):
    """Village creation schema"""
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    timezone: str = "Asia/Bangkok"
    currency: str = "THB"
    language: str = "th"
    default_monthly_fee: Optional[Decimal] = None
    late_fee_percentage: Decimal = Decimal("5.0")
    grace_period_days: int = 7
    subscription_plan: str = "basic"
    
    @validator('code')
    def validate_code(cls, v):
        if not v.isalnum():
            raise ValueError('Village code must be alphanumeric')
        if len(v) < 3 or len(v) > 20:
            raise ValueError('Village code must be between 3 and 20 characters')
        return v.upper()


class VillageUpdate(BaseModel):
    """Village update schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    timezone: Optional[str] = None
    currency: Optional[str] = None
    language: Optional[str] = None
    default_monthly_fee: Optional[Decimal] = None
    late_fee_percentage: Optional[Decimal] = None
    grace_period_days: Optional[int] = None
    gate_system_enabled: Optional[bool] = None
    visitor_approval_required: Optional[bool] = None
    qr_code_enabled: Optional[bool] = None
    lpr_enabled: Optional[bool] = None
    line_notify_enabled: Optional[bool] = None
    line_notify_token: Optional[str] = None
    email_notifications_enabled: Optional[bool] = None
    sms_notifications_enabled: Optional[bool] = None
    subscription_plan: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class VillageResponse(VillageBase):
    """Village response schema"""
    id: int
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    timezone: str
    currency: str
    language: str
    default_monthly_fee: Optional[Decimal] = None
    late_fee_percentage: Decimal
    grace_period_days: int
    gate_system_enabled: bool
    visitor_approval_required: bool
    qr_code_enabled: bool
    lpr_enabled: bool
    line_notify_enabled: bool
    email_notifications_enabled: bool
    sms_notifications_enabled: bool
    is_active: bool
    subscription_plan: str
    subscription_expires: Optional[datetime] = None
    logo_url: Optional[str] = None
    primary_color: str
    secondary_color: str
    settings: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class VillageList(BaseModel):
    """Village list response schema"""
    villages: List[VillageResponse]
    total: int
    skip: int
    limit: int


class VillageSummary(BaseModel):
    """Village summary schema for references"""
    id: int
    name: str
    code: str
    city: str
    state: str
    is_active: bool
    
    class Config:
        from_attributes = True


class VillageStats(BaseModel):
    """Village statistics schema"""
    total_properties: int
    occupied_properties: int
    vacant_properties: int
    occupancy_rate: float
    total_residents: int
    active_residents: int
    pending_invoices: int
    overdue_invoices: int
    total_revenue_this_month: Decimal
    total_revenue_this_year: Decimal
    
    class Config:
        from_attributes = True


class VillageSettings(BaseModel):
    """Village settings schema"""
    gate_system_enabled: bool
    visitor_approval_required: bool
    qr_code_enabled: bool
    lpr_enabled: bool
    line_notify_enabled: bool
    email_notifications_enabled: bool
    sms_notifications_enabled: bool
    default_monthly_fee: Optional[Decimal] = None
    late_fee_percentage: Decimal
    grace_period_days: int
    primary_color: str
    secondary_color: str

