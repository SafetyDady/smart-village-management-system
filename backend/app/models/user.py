"""
User Model - Smart Village Management System
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    """User model for authentication and user management"""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Authentication fields
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Nullable for LINE-only users
    
    # Personal information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    
    # Role and permissions
    role = Column(String(50), nullable=False, default="resident")
    # Roles: super_admin, village_admin, accounting_admin, resident
    
    # Status fields
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_email_verified = Column(Boolean, default=False)
    is_phone_verified = Column(Boolean, default=False)
    
    # LINE integration
    line_user_id = Column(String(100), unique=True, nullable=True, index=True)
    line_display_name = Column(String(100), nullable=True)
    line_picture_url = Column(Text, nullable=True)
    
    # Profile information
    profile_picture = Column(Text, nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    gender = Column(String(10), nullable=True)  # male, female, other
    
    # Address information
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), default="Thailand")
    
    # Security fields
    last_login = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    
    # MFA fields
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)
    backup_codes = Column(Text, nullable=True)  # JSON array of backup codes
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    social_accounts = relationship("SocialAccount", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", foreign_keys="AuditLog.user_id", back_populates="user")
    
    # Village relationships (for residents)
    resident_properties = relationship("Resident", back_populates="user")
    
    # Admin relationships
    admin_villages = relationship("Admin", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
    
    @property
    def full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_admin(self):
        """Check if user is any type of admin"""
        return self.role in ["super_admin", "village_admin", "accounting_admin"]
    
    @property
    def is_super_admin(self):
        """Check if user is super admin"""
        return self.role == "super_admin"
    
    @property
    def is_village_admin(self):
        """Check if user is village admin"""
        return self.role == "village_admin"
    
    @property
    def is_accounting_admin(self):
        """Check if user is accounting admin"""
        return self.role == "accounting_admin"
    
    @property
    def is_resident(self):
        """Check if user is resident"""
        return self.role == "resident"
    
    @property
    def is_locked(self):
        """Check if user account is locked"""
        if self.locked_until is None:
            return False
        from datetime import datetime
        return datetime.utcnow() < self.locked_until
    
    def can_access_village(self, village_id: int) -> bool:
        """Check if user can access specific village"""
        if self.is_super_admin:
            return True
        
        if self.is_village_admin or self.is_accounting_admin:
            # Check if user is admin of this village
            return any(admin.village_id == village_id for admin in self.admin_villages)
        
        if self.is_resident:
            # Check if user is resident of this village
            return any(
                resident.property.village_id == village_id 
                for resident in self.resident_properties
            )
        
        return False

