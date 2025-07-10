"""
Village and Property Models - Smart Village Management System
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Village(Base):
    """Village model for managing village communities"""
    
    __tablename__ = "villages"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic information
    name = Column(String(200), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Contact information
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(100), default="Thailand")
    
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Geographic information
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    
    # Village settings
    timezone = Column(String(50), default="Asia/Bangkok")
    currency = Column(String(3), default="THB")
    language = Column(String(5), default="th")
    
    # Financial settings
    default_monthly_fee = Column(Numeric(10, 2), nullable=True)
    late_fee_percentage = Column(Numeric(5, 2), default=5.0)
    grace_period_days = Column(Integer, default=7)
    
    # Access control settings
    gate_system_enabled = Column(Boolean, default=False)
    visitor_approval_required = Column(Boolean, default=True)
    qr_code_enabled = Column(Boolean, default=True)
    lpr_enabled = Column(Boolean, default=False)
    
    # Notification settings
    line_notify_enabled = Column(Boolean, default=False)
    line_notify_token = Column(String(255), nullable=True)
    email_notifications_enabled = Column(Boolean, default=True)
    sms_notifications_enabled = Column(Boolean, default=False)
    
    # Status and configuration
    is_active = Column(Boolean, default=True)
    subscription_plan = Column(String(50), default="basic")  # basic, premium, enterprise
    subscription_expires = Column(DateTime, nullable=True)
    
    # Branding
    logo_url = Column(Text, nullable=True)
    primary_color = Column(String(7), default="#3B82F6")  # Hex color
    secondary_color = Column(String(7), default="#10B981")  # Hex color
    
    # Additional settings (JSON field for flexibility)
    settings = Column(JSON, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    properties = relationship("Property", back_populates="village", cascade="all, delete-orphan")
    admins = relationship("Admin", back_populates="village", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="village")
    access_logs = relationship("AccessLog", back_populates="village")
    visitor_passes = relationship("VisitorPass", back_populates="village")
    devices = relationship("Device", back_populates="village", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Village(id={self.id}, name='{self.name}', code='{self.code}')>"
    
    @property
    def total_properties(self):
        """Get total number of properties in village"""
        return len(self.properties)
    
    @property
    def occupied_properties(self):
        """Get number of occupied properties"""
        return len([p for p in self.properties if p.is_occupied])
    
    @property
    def occupancy_rate(self):
        """Get occupancy rate percentage"""
        if self.total_properties == 0:
            return 0
        return (self.occupied_properties / self.total_properties) * 100


class Property(Base):
    """Property model for individual units within villages"""
    
    __tablename__ = "properties"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Village relationship
    village_id = Column(Integer, ForeignKey("villages.id"), nullable=False, index=True)
    
    # Property identification
    unit_number = Column(String(50), nullable=False, index=True)
    building = Column(String(50), nullable=True)
    floor = Column(String(10), nullable=True)
    
    # Property details
    property_type = Column(String(50), nullable=False)  # house, condo, townhouse, etc.
    size_sqm = Column(Numeric(8, 2), nullable=True)
    bedrooms = Column(Integer, nullable=True)
    bathrooms = Column(Integer, nullable=True)
    parking_spaces = Column(Integer, default=0)
    
    # Financial information
    monthly_fee = Column(Numeric(10, 2), nullable=True)
    deposit_amount = Column(Numeric(10, 2), nullable=True)
    purchase_price = Column(Numeric(12, 2), nullable=True)
    market_value = Column(Numeric(12, 2), nullable=True)
    
    # Ownership information
    ownership_type = Column(String(20), nullable=False, default="owned")  # owned, rented
    owner_name = Column(String(200), nullable=True)
    owner_phone = Column(String(20), nullable=True)
    owner_email = Column(String(255), nullable=True)
    
    # Property status
    is_occupied = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    
    # Lease information (for rental properties)
    lease_start_date = Column(DateTime, nullable=True)
    lease_end_date = Column(DateTime, nullable=True)
    lease_monthly_rent = Column(Numeric(10, 2), nullable=True)
    
    # Utility information
    electricity_meter = Column(String(50), nullable=True)
    water_meter = Column(String(50), nullable=True)
    gas_meter = Column(String(50), nullable=True)
    internet_enabled = Column(Boolean, default=False)
    
    # Access control
    access_codes = Column(JSON, nullable=True)  # Array of access codes
    key_cards = Column(JSON, nullable=True)  # Array of key card IDs
    
    # Additional information
    description = Column(Text, nullable=True)
    amenities = Column(JSON, nullable=True)  # Array of amenities
    restrictions = Column(JSON, nullable=True)  # Array of restrictions
    
    # Maintenance
    last_maintenance_date = Column(DateTime, nullable=True)
    next_maintenance_date = Column(DateTime, nullable=True)
    maintenance_notes = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    village = relationship("Village", back_populates="properties")
    residents = relationship("Resident", back_populates="property", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="property")
    access_logs = relationship("AccessLog", back_populates="property")
    visitor_passes = relationship("VisitorPass", back_populates="property")
    
    def __repr__(self):
        return f"<Property(id={self.id}, unit='{self.unit_number}', village_id={self.village_id})>"
    
    @property
    def full_address(self):
        """Get full property address"""
        parts = [self.unit_number]
        if self.building:
            parts.append(f"Building {self.building}")
        if self.floor:
            parts.append(f"Floor {self.floor}")
        return ", ".join(parts)
    
    @property
    def current_residents(self):
        """Get current active residents"""
        return [r for r in self.residents if r.is_active and not r.move_out_date]
    
    @property
    def primary_resident(self):
        """Get primary resident (owner or main tenant)"""
        primary = [r for r in self.current_residents if r.is_primary]
        return primary[0] if primary else None
    
    @property
    def effective_monthly_fee(self):
        """Get effective monthly fee (property-specific or village default)"""
        return self.monthly_fee or self.village.default_monthly_fee

