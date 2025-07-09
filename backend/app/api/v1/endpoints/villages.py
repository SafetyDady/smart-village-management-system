"""
Villages Endpoints - Smart Village Management System
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user, get_super_admin, get_village_admin
from app.schemas.village import VillageCreate, VillageUpdate, VillageResponse, VillageList
from app.services.village_service import VillageService
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=VillageList)
async def read_villages(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    is_active: bool = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Retrieve villages
    """
    village_service = VillageService(db)
    
    # Super admin can see all villages
    if current_user.is_super_admin:
        villages, total = await village_service.get_villages(
            skip=skip,
            limit=limit,
            search=search,
            is_active=is_active
        )
    else:
        # Other users can only see villages they have access to
        villages, total = await village_service.get_user_villages(
            user_id=current_user.id,
            skip=skip,
            limit=limit,
            search=search,
            is_active=is_active
        )
    
    return {
        "villages": villages,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.post("/", response_model=VillageResponse)
async def create_village(
    village_in: VillageCreate,
    current_user: User = Depends(get_super_admin),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create new village (Super Admin only)
    """
    village_service = VillageService(db)
    
    # Check if village code already exists
    existing_village = await village_service.get_village_by_code(village_in.code)
    if existing_village:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Village with this code already exists"
        )
    
    village = await village_service.create_village(village_in, created_by=current_user.id)
    return village


@router.get("/{village_id}", response_model=VillageResponse)
async def read_village(
    village_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get village by ID
    """
    village_service = VillageService(db)
    
    village = await village_service.get_village(village_id)
    if not village:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Village not found"
        )
    
    # Check permissions
    if not current_user.can_access_village(village_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this village"
        )
    
    return village


@router.put("/{village_id}", response_model=VillageResponse)
async def update_village(
    village_id: int,
    village_in: VillageUpdate,
    current_user: User = Depends(get_village_admin),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update village
    """
    village_service = VillageService(db)
    
    village = await village_service.get_village(village_id)
    if not village:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Village not found"
        )
    
    # Check permissions
    if not current_user.can_access_village(village_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this village"
        )
    
    updated_village = await village_service.update_village(
        village_id, 
        village_in, 
        updated_by=current_user.id
    )
    return updated_village


@router.delete("/{village_id}")
async def delete_village(
    village_id: int,
    current_user: User = Depends(get_super_admin),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete village (Super Admin only)
    """
    village_service = VillageService(db)
    
    village = await village_service.get_village(village_id)
    if not village:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Village not found"
        )
    
    await village_service.delete_village(village_id)
    return {"message": "Village deleted successfully"}


@router.get("/{village_id}/properties")
async def get_village_properties(
    village_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    property_type: str = Query(None),
    is_occupied: bool = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get properties in village
    """
    village_service = VillageService(db)
    
    # Check permissions
    if not current_user.can_access_village(village_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this village"
        )
    
    properties, total = await village_service.get_village_properties(
        village_id=village_id,
        skip=skip,
        limit=limit,
        search=search,
        property_type=property_type,
        is_occupied=is_occupied
    )
    
    return {
        "properties": properties,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{village_id}/stats")
async def get_village_stats(
    village_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get village statistics
    """
    village_service = VillageService(db)
    
    # Check permissions
    if not current_user.can_access_village(village_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this village"
        )
    
    stats = await village_service.get_village_stats(village_id)
    return stats


@router.post("/{village_id}/activate")
async def activate_village(
    village_id: int,
    current_user: User = Depends(get_super_admin),
    db: Session = Depends(get_db)
) -> Any:
    """
    Activate village (Super Admin only)
    """
    village_service = VillageService(db)
    
    village = await village_service.get_village(village_id)
    if not village:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Village not found"
        )
    
    await village_service.activate_village(village_id, updated_by=current_user.id)
    return {"message": "Village activated successfully"}


@router.post("/{village_id}/deactivate")
async def deactivate_village(
    village_id: int,
    current_user: User = Depends(get_super_admin),
    db: Session = Depends(get_db)
) -> Any:
    """
    Deactivate village (Super Admin only)
    """
    village_service = VillageService(db)
    
    village = await village_service.get_village(village_id)
    if not village:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Village not found"
        )
    
    await village_service.deactivate_village(village_id, updated_by=current_user.id)
    return {"message": "Village deactivated successfully"}

