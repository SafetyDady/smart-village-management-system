"""
Property Schemas - Smart Village Management System
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, validator


class PropertyBase(BaseModel):
    """Base property schema"""
    village_id: int
    unit_number: str
    building: Optional[str] = None
    floor: Optional[str] = None
    property_type: str
    size_sqm: Optional[Decimal] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    parking_spaces: int = 0


class PropertyCreate(PropertyBase):
    """Property creation schema"""
    monthly_fee: Optional[Decimal] = None
    deposit_amount: Optional[Decimal] = None
    purchase_price: Optional[Decimal] = None
    market_value: Optional[Decimal] = None
    ownership_type: str = "owned"
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    owner_email: Optional[str] = None
    electricity_meter: Optional[str] = None
    water_meter: Optional[str] = None
    gas_meter: Optional[str] = None
    internet_enabled: bool = False
    description: Optional[str] = None
    amenities: Optional[List[str]] = None
    restrictions: Optional[List[str]] = None
    
    @validator('unit_number')
    def validate_unit_number(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Unit number is required')
        return v.strip()
    
    @validator('property_type')
    def validate_property_type(cls, v):
        allowed_types = ['house', 'condo', 'townhouse', 'apartment', 'villa', 'studio']
        if v.lower() not in allowed_types:
            raise ValueError(f'Property type must be one of: {", ".join(allowed_types)}')
        return v.lower()
    
    @validator('ownership_type')
    def validate_ownership_type(cls, v):
        allowed_types = ['owned', 'rented']
        if v.lower() not in allowed_types:
            raise ValueError(f'Ownership type must be one of: {", ".join(allowed_types)}')
        return v.lower()


class PropertyUpdate(BaseModel):
    """Property update schema"""
    unit_number: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[str] = None
    property_type: Optional[str] = None
    size_sqm: Optional[Decimal] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    parking_spaces: Optional[int] = None
    monthly_fee: Optional[Decimal] = None
    deposit_amount: Optional[Decimal] = None
    purchase_price: Optional[Decimal] = None
    market_value: Optional[Decimal] = None
    ownership_type: Optional[str] = None
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    owner_email: Optional[str] = None
    is_occupied: Optional[bool] = None
    is_available: Optional[bool] = None
    lease_start_date: Optional[datetime] = None
    lease_end_date: Optional[datetime] = None
    lease_monthly_rent: Optional[Decimal] = None
    electricity_meter: Optional[str] = None
    water_meter: Optional[str] = None
    gas_meter: Optional[str] = None
    internet_enabled: Optional[bool] = None
    description: Optional[str] = None
    amenities: Optional[List[str]] = None
    restrictions: Optional[List[str]] = None
    last_maintenance_date: Optional[datetime] = None
    next_maintenance_date: Optional[datetime] = None
    maintenance_notes: Optional[str] = None


class PropertyResponse(PropertyBase):
    """Property response schema"""
    id: int
    monthly_fee: Optional[Decimal] = None
    deposit_amount: Optional[Decimal] = None
    purchase_price: Optional[Decimal] = None
    market_value: Optional[Decimal] = None
    ownership_type: str
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    owner_email: Optional[str] = None
    is_occupied: bool
    is_available: bool
    is_active: bool
    lease_start_date: Optional[datetime] = None
    lease_end_date: Optional[datetime] = None
    lease_monthly_rent: Optional[Decimal] = None
    electricity_meter: Optional[str] = None
    water_meter: Optional[str] = None
    gas_meter: Optional[str] = None
    internet_enabled: bool
    access_codes: Optional[List[str]] = None
    key_cards: Optional[List[str]] = None
    description: Optional[str] = None
    amenities: Optional[List[str]] = None
    restrictions: Optional[List[str]] = None
    last_maintenance_date: Optional[datetime] = None
    next_maintenance_date: Optional[datetime] = None
    maintenance_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Computed fields
    full_address: Optional[str] = None
    effective_monthly_fee: Optional[Decimal] = None
    
    class Config:
        from_attributes = True


class PropertyList(BaseModel):
    """Property list response schema"""
    properties: List[PropertyResponse]
    total: int
    skip: int
    limit: int


class PropertySummary(BaseModel):
    """Property summary schema for references"""
    id: int
    village_id: int
    unit_number: str
    building: Optional[str] = None
    property_type: str
    is_occupied: bool
    is_active: bool
    
    class Config:
        from_attributes = True


class PropertyStats(BaseModel):
    """Property statistics schema"""
    total_properties: int
    occupied_properties: int
    vacant_properties: int
    occupancy_rate: float
    properties_by_type: Dict[str, int]
    average_size_sqm: Optional[Decimal] = None
    average_monthly_fee: Optional[Decimal] = None
    total_monthly_revenue: Decimal


class PropertyWithResidents(PropertyResponse):
    """Property with residents schema"""
    current_residents: List[Dict[str, Any]] = []
    primary_resident: Optional[Dict[str, Any]] = None


class PropertyMaintenance(BaseModel):
    """Property maintenance schema"""
    property_id: int
    maintenance_type: str
    description: str
    scheduled_date: datetime
    completed_date: Optional[datetime] = None
    cost: Optional[Decimal] = None
    notes: Optional[str] = None
    status: str = "scheduled"  # scheduled, in_progress, completed, cancelled

