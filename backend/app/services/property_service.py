"""
Property Service - Smart Village Management System
"""

from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.property import Property
from app.schemas.property import PropertyCreate, PropertyUpdate


class PropertyService:
    """Property service for handling property operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_properties(
        self,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        village_id: Optional[int] = None,
        property_type: Optional[str] = None,
        is_occupied: Optional[bool] = None,
        accessible_village_ids: Optional[List[int]] = None
    ) -> Tuple[List[Property], int]:
        """Get properties with filtering and pagination"""
        query = self.db.query(Property)
        
        # Apply access control filter
        if accessible_village_ids is not None:
            query = query.filter(Property.village_id.in_(accessible_village_ids))
        
        # Apply filters
        if search:
            search_filter = or_(
                Property.unit_number.ilike(f"%{search}%"),
                Property.building.ilike(f"%{search}%"),
                Property.owner_name.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if village_id:
            query = query.filter(Property.village_id == village_id)
        
        if property_type:
            query = query.filter(Property.property_type == property_type)
        
        if is_occupied is not None:
            query = query.filter(Property.is_occupied == is_occupied)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        properties = query.offset(skip).limit(limit).all()
        
        return properties, total
    
    async def get_property(self, property_id: int) -> Optional[Property]:
        """Get property by ID"""
        return self.db.query(Property).filter(Property.id == property_id).first()
    
    async def get_property_by_unit(self, village_id: int, unit_number: str) -> Optional[Property]:
        """Get property by village and unit number"""
        return self.db.query(Property).filter(
            and_(
                Property.village_id == village_id,
                Property.unit_number == unit_number
            )
        ).first()
    
    async def create_property(self, property_data: PropertyCreate, created_by: int) -> Property:
        """Create new property"""
        property_dict = property_data.dict()
        property_dict["created_by"] = created_by
        
        property_obj = Property(**property_dict)
        self.db.add(property_obj)
        self.db.commit()
        self.db.refresh(property_obj)
        
        return property_obj
    
    async def update_property(self, property_id: int, property_data: PropertyUpdate, updated_by: int) -> Property:
        """Update property"""
        property_obj = self.db.query(Property).filter(Property.id == property_id).first()
        if not property_obj:
            return None
        
        update_dict = property_data.dict(exclude_unset=True)
        update_dict["updated_by"] = updated_by
        update_dict["updated_at"] = datetime.utcnow()
        
        for field, value in update_dict.items():
            setattr(property_obj, field, value)
        
        self.db.commit()
        self.db.refresh(property_obj)
        
        return property_obj
    
    async def delete_property(self, property_id: int) -> bool:
        """Delete property"""
        property_obj = self.db.query(Property).filter(Property.id == property_id).first()
        if not property_obj:
            return False
        
        self.db.delete(property_obj)
        self.db.commit()
        
        return True
    
    async def activate_property(self, property_id: int, updated_by: int) -> bool:
        """Activate property"""
        property_obj = self.db.query(Property).filter(Property.id == property_id).first()
        if not property_obj:
            return False
        
        property_obj.is_active = True
        property_obj.updated_by = updated_by
        property_obj.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return True
    
    async def deactivate_property(self, property_id: int, updated_by: int) -> bool:
        """Deactivate property"""
        property_obj = self.db.query(Property).filter(Property.id == property_id).first()
        if not property_obj:
            return False
        
        property_obj.is_active = False
        property_obj.updated_by = updated_by
        property_obj.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return True
    
    async def get_property_residents(self, property_id: int) -> List[dict]:
        """Get residents of property"""
        property_obj = self.db.query(Property).filter(Property.id == property_id).first()
        if not property_obj:
            return []
        
        residents = []
        for resident in property_obj.current_residents:
            residents.append({
                "id": resident.id,
                "user_id": resident.user_id,
                "user": {
                    "id": resident.user.id,
                    "first_name": resident.user.first_name,
                    "last_name": resident.user.last_name,
                    "email": resident.user.email,
                    "phone": resident.user.phone
                },
                "is_primary": resident.is_primary,
                "relationship": resident.relationship,
                "move_in_date": resident.move_in_date,
                "is_active": resident.is_active
            })
        
        return residents
    
    async def get_property_invoices(
        self,
        property_id: int,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None
    ) -> Tuple[List[dict], int]:
        """Get invoices for property"""
        # TODO: Implement when Invoice model is available
        return [], 0

