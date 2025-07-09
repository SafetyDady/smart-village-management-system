"""
Authentication Service - Smart Village Management System
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.user import User
from app.core.security import verify_password, get_password_hash
from app.core.config import settings


class AuthService:
    """Authentication service for handling user authentication"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            return None
        
        if not user.hashed_password:
            # User registered via LINE only
            return None
        
        if not verify_password(password, user.hashed_password):
            # Increment failed login attempts
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                # Lock account for 30 minutes
                user.locked_until = datetime.utcnow() + timedelta(minutes=30)
            self.db.commit()
            return None
        
        # Reset failed login attempts on successful login
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        return user
    
    async def get_or_create_line_user(self, line_profile: Dict[str, Any]) -> User:
        """Get or create user from LINE profile"""
        line_user_id = line_profile.get("sub")
        email = line_profile.get("email")
        name = line_profile.get("name", "")
        picture = line_profile.get("picture")
        
        # Try to find existing user by LINE ID
        user = self.db.query(User).filter(User.line_user_id == line_user_id).first()
        
        if user:
            # Update LINE profile information
            user.line_display_name = name
            user.line_picture_url = picture
            user.last_login = datetime.utcnow()
            self.db.commit()
            return user
        
        # Try to find existing user by email
        if email:
            user = self.db.query(User).filter(User.email == email).first()
            if user:
                # Link LINE account to existing user
                user.line_user_id = line_user_id
                user.line_display_name = name
                user.line_picture_url = picture
                user.last_login = datetime.utcnow()
                self.db.commit()
                return user
        
        # Create new user
        # Parse name
        name_parts = name.split(" ", 1) if name else ["", ""]
        first_name = name_parts[0] or "LINE"
        last_name = name_parts[1] if len(name_parts) > 1 else "User"
        
        # Generate email if not provided
        if not email:
            email = f"line_{line_user_id}@smartvillage.local"
        
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            line_user_id=line_user_id,
            line_display_name=name,
            line_picture_url=picture,
            role="resident",
            is_active=True,
            is_verified=True,  # LINE users are considered verified
            last_login=datetime.utcnow()
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    async def store_refresh_token(self, user_id: int, refresh_token: str) -> None:
        """Store refresh token in database"""
        # TODO: Implement refresh token storage
        # For now, we'll skip this as we haven't created the RefreshToken model yet
        pass
    
    async def verify_refresh_token(self, email: str, refresh_token: str) -> bool:
        """Verify refresh token"""
        # TODO: Implement refresh token verification
        # For now, we'll return True as a placeholder
        return True
    
    async def replace_refresh_token(self, user_id: int, old_token: str, new_token: str) -> None:
        """Replace old refresh token with new one"""
        # TODO: Implement refresh token replacement
        pass
    
    async def revoke_refresh_token(self, user_id: int, refresh_token: str) -> None:
        """Revoke refresh token"""
        # TODO: Implement refresh token revocation
        pass
    
    async def verify_email_token(self, token: str) -> bool:
        """Verify email verification token"""
        # TODO: Implement email verification
        return True
    
    async def send_password_reset_email(self, email: str) -> None:
        """Send password reset email"""
        # TODO: Implement password reset email
        pass
    
    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password using reset token"""
        # TODO: Implement password reset
        return True

