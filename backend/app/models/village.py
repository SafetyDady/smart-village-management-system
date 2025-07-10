"""
Village Model - Smart Village Management System
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
    
    # Relationships (commented out until models are created)
    properties = relationship("Property", back_populates="village", cascade="all, delete-orphan")
    # admins = relationship("Admin", back_populates="village", cascade="all, delete-orphan")
    # invoices = relationship("Invoice", back_populates="village")
    # access_logs = relationship("AccessLog", back_populates="village")
    # visitor_passes = relationship("VisitorPass", back_populates="village")
    # devices = relationship("Device", back_populates="village", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Village(id={self.id}, name='{self.name}', code='{self.code}')>"
    
    @property
    def total_properties(self):
        """Get total number of properties in village"""
        return len(self.properties)
    
    @property
    def occupied_properties(self):
        """Get number of occupied properties"""
        # Commented out until Resident model is created
        # return len([p for p in self.properties if p.is_occupied])
        return 0
    
    @property
    def occupancy_rate(self):
        """Get occupancy rate percentage"""
        if self.total_properties == 0:
            return 0
        return (self.occupied_properties / self.total_properties) * 100
