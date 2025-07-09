"""
User Service - Smart Village Management System
"""

from typing import Optional, List, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class UserService:
    """User service for handling user operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_users(
        self,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[User], int]:
        """Get users with filtering and pagination"""
        query = self.db.query(User)
        
        # Apply filters
        if search:
            search_filter = or_(
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if role:
            query = query.filter(User.role == role)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        users = query.offset(skip).limit(limit).all()
        
        return users, total
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    async def create_user(self, user_data: UserCreate, created_by: int) -> User:
        """Create new user"""
        user_dict = user_data.dict()
        
        # Hash password if provided
        if user_dict.get("password"):
            user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
        else:
            user_dict.pop("password", None)
        
        user_dict["created_by"] = created_by
        
        user = User(**user_dict)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    async def update_user(self, user_id: int, user_data: UserUpdate, updated_by: int) -> User:
        """Update user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        update_dict = user_data.dict(exclude_unset=True)
        update_dict["updated_by"] = updated_by
        update_dict["updated_at"] = datetime.utcnow()
        
        for field, value in update_dict.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    async def delete_user(self, user_id: int) -> bool:
        """Delete user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        
        return True
    
    async def activate_user(self, user_id: int, updated_by: int) -> bool:
        """Activate user account"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        user.is_active = True
        user.updated_by = updated_by
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return True
    
    async def deactivate_user(self, user_id: int, updated_by: int) -> bool:
        """Deactivate user account"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        user.is_active = False
        user.updated_by = updated_by
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return True
    
    async def get_user_villages(self, user_id: int) -> List[dict]:
        """Get villages associated with user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        villages = []
        
        if user.is_super_admin:
            # Super admin can access all villages
            # TODO: Implement when Village model is imported
            pass
        elif user.is_admin:
            # Get villages where user is admin
            for admin in user.admin_villages:
                villages.append({
                    "id": admin.village.id,
                    "name": admin.village.name,
                    "code": admin.village.code,
                    "role": admin.role
                })
        elif user.is_resident:
            # Get villages where user is resident
            for resident in user.resident_properties:
                village = resident.property.village
                if village not in [v["id"] for v in villages]:
                    villages.append({
                        "id": village.id,
                        "name": village.name,
                        "code": village.code,
                        "role": "resident"
                    })
        
        return villages
    
    async def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.hashed_password:
            return False
        
        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            return False
        
        # Update password
        user.hashed_password = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return True

