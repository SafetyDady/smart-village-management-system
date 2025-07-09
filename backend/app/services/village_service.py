"""
Village Service - Smart Village Management System
"""

from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.village import Village
from app.schemas.village import VillageCreate, VillageUpdate


class VillageService:
    """Village service for handling village operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_villages(
        self,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Village], int]:
        """Get villages with filtering and pagination"""
        query = self.db.query(Village)
        
        # Apply filters
        if search:
            search_filter = or_(
                Village.name.ilike(f"%{search}%"),
                Village.code.ilike(f"%{search}%"),
                Village.city.ilike(f"%{search}%"),
                Village.state.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if is_active is not None:
            query = query.filter(Village.is_active == is_active)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        villages = query.offset(skip).limit(limit).all()
        
        return villages, total
    
    async def get_user_villages(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Village], int]:
        """Get villages accessible by user"""
        # TODO: Implement user-specific village filtering
        # For now, return empty list as placeholder
        return [], 0
    
    async def get_village(self, village_id: int) -> Optional[Village]:
        """Get village by ID"""
        return self.db.query(Village).filter(Village.id == village_id).first()
    
    async def get_village_by_code(self, code: str) -> Optional[Village]:
        """Get village by code"""
        return self.db.query(Village).filter(Village.code == code.upper()).first()
    
    async def create_village(self, village_data: VillageCreate, created_by: int) -> Village:
        """Create new village"""
        village_dict = village_data.dict()
        village_dict["created_by"] = created_by
        
        village = Village(**village_dict)
        self.db.add(village)
        self.db.commit()
        self.db.refresh(village)
        
        return village
    
    async def update_village(self, village_id: int, village_data: VillageUpdate, updated_by: int) -> Village:
        """Update village"""
        village = self.db.query(Village).filter(Village.id == village_id).first()
        if not village:
            return None
        
        update_dict = village_data.dict(exclude_unset=True)
        update_dict["updated_by"] = updated_by
        update_dict["updated_at"] = datetime.utcnow()
        
        for field, value in update_dict.items():
            setattr(village, field, value)
        
        self.db.commit()
        self.db.refresh(village)
        
        return village
    
    async def delete_village(self, village_id: int) -> bool:
        """Delete village"""
        village = self.db.query(Village).filter(Village.id == village_id).first()
        if not village:
            return False
        
        self.db.delete(village)
        self.db.commit()
        
        return True
    
    async def activate_village(self, village_id: int, updated_by: int) -> bool:
        """Activate village"""
        village = self.db.query(Village).filter(Village.id == village_id).first()
        if not village:
            return False
        
        village.is_active = True
        village.updated_by = updated_by
        village.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return True
    
    async def deactivate_village(self, village_id: int, updated_by: int) -> bool:
        """Deactivate village"""
        village = self.db.query(Village).filter(Village.id == village_id).first()
        if not village:
            return False
        
        village.is_active = False
        village.updated_by = updated_by
        village.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return True
    
    async def get_village_properties(
        self,
        village_id: int,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        property_type: Optional[str] = None,
        is_occupied: Optional[bool] = None
    ) -> Tuple[List[dict], int]:
        """Get properties in village"""
        # TODO: Implement when Property model is imported
        return [], 0
    
    async def get_village_stats(self, village_id: int) -> Dict[str, Any]:
        """Get village statistics"""
        village = self.db.query(Village).filter(Village.id == village_id).first()
        if not village:
            return {}
        
        # TODO: Implement comprehensive village statistics
        stats = {
            "total_properties": len(village.properties),
            "occupied_properties": len([p for p in village.properties if p.is_occupied]),
            "vacant_properties": len([p for p in village.properties if not p.is_occupied]),
            "occupancy_rate": village.occupancy_rate,
            "total_residents": 0,  # TODO: Calculate from residents
            "active_residents": 0,  # TODO: Calculate from active residents
            "pending_invoices": 0,  # TODO: Calculate from invoices
            "overdue_invoices": 0,  # TODO: Calculate from overdue invoices
            "total_revenue_this_month": 0,  # TODO: Calculate from payments
            "total_revenue_this_year": 0,  # TODO: Calculate from payments
        }
        
        return stats

