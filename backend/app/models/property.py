"""
Property Model - Smart Village Management System
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


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
    
    # Accounting relationships
    invoices = relationship("Invoice", back_populates="property_obj")
    payments = relationship("Payment", back_populates="property_obj")
    
    # Commented out relationships to models that don't exist yet
    # residents = relationship("Resident", back_populates="property", cascade="all, delete-orphan")
    # access_logs = relationship("AccessLog", back_populates="property")
    # visitor_passes = relationship("VisitorPass", back_populates="property")
    
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
        # TODO: Implement when Resident model is created
        return []
    
    @property
    def primary_resident(self):
        """Get primary resident (owner or main tenant)"""
        # TODO: Implement when Resident model is created
        return None
    
    @property
    def effective_monthly_fee(self):
        """Get effective monthly fee (property-specific or village default)"""
        if self.monthly_fee:
            return self.monthly_fee
        # TODO: Implement when village.default_monthly_fee is available
        return self.monthly_fee or 0
