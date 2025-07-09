"""
Properties Endpoints - Smart Village Management System
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user, get_village_admin
from app.schemas.property import PropertyCreate, PropertyUpdate, PropertyResponse, PropertyList
from app.services.property_service import PropertyService
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=PropertyList)
async def read_properties(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    village_id: int = Query(None),
    property_type: str = Query(None),
    is_occupied: bool = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Retrieve properties
    """
    property_service = PropertyService(db)
    
    # Filter by user's accessible villages if not super admin
    accessible_village_ids = None
    if not current_user.is_super_admin:
        accessible_village_ids = [
            admin.village_id for admin in current_user.admin_villages
        ] if current_user.is_admin else [
            resident.property.village_id for resident in current_user.resident_properties
        ]
    
    properties, total = await property_service.get_properties(
        skip=skip,
        limit=limit,
        search=search,
        village_id=village_id,
        property_type=property_type,
        is_occupied=is_occupied,
        accessible_village_ids=accessible_village_ids
    )
    
    return {
        "properties": properties,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.post("/", response_model=PropertyResponse)
async def create_property(
    property_in: PropertyCreate,
    current_user: User = Depends(get_village_admin),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create new property
    """
    property_service = PropertyService(db)
    
    # Check permissions for the village
    if not current_user.can_access_village(property_in.village_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create property in this village"
        )
    
    # Check if property unit number already exists in village
    existing_property = await property_service.get_property_by_unit(
        village_id=property_in.village_id,
        unit_number=property_in.unit_number
    )
    if existing_property:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Property with this unit number already exists in the village"
        )
    
    property_obj = await property_service.create_property(
        property_in, 
        created_by=current_user.id
    )
    return property_obj


@router.get("/{property_id}", response_model=PropertyResponse)
async def read_property(
    property_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get property by ID
    """
    property_service = PropertyService(db)
    
    property_obj = await property_service.get_property(property_id)
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check permissions
    if not current_user.can_access_village(property_obj.village_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this property"
        )
    
    return property_obj


@router.put("/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: int,
    property_in: PropertyUpdate,
    current_user: User = Depends(get_village_admin),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update property
    """
    property_service = PropertyService(db)
    
    property_obj = await property_service.get_property(property_id)
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check permissions
    if not current_user.can_access_village(property_obj.village_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this property"
        )
    
    updated_property = await property_service.update_property(
        property_id, 
        property_in, 
        updated_by=current_user.id
    )
    return updated_property


@router.delete("/{property_id}")
async def delete_property(
    property_id: int,
    current_user: User = Depends(get_village_admin),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete property
    """
    property_service = PropertyService(db)
    
    property_obj = await property_service.get_property(property_id)
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check permissions
    if not current_user.can_access_village(property_obj.village_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this property"
        )
    
    await property_service.delete_property(property_id)
    return {"message": "Property deleted successfully"}


@router.get("/{property_id}/residents")
async def get_property_residents(
    property_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get residents of property
    """
    property_service = PropertyService(db)
    
    property_obj = await property_service.get_property(property_id)
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check permissions
    if not current_user.can_access_village(property_obj.village_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this property"
        )
    
    residents = await property_service.get_property_residents(property_id)
    return {"residents": residents}


@router.get("/{property_id}/invoices")
async def get_property_invoices(
    property_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get invoices for property
    """
    property_service = PropertyService(db)
    
    property_obj = await property_service.get_property(property_id)
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check permissions
    if not current_user.can_access_village(property_obj.village_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this property"
        )
    
    invoices, total = await property_service.get_property_invoices(
        property_id=property_id,
        skip=skip,
        limit=limit,
        status=status
    )
    
    return {
        "invoices": invoices,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.post("/{property_id}/activate")
async def activate_property(
    property_id: int,
    current_user: User = Depends(get_village_admin),
    db: Session = Depends(get_db)
) -> Any:
    """
    Activate property
    """
    property_service = PropertyService(db)
    
    property_obj = await property_service.get_property(property_id)
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check permissions
    if not current_user.can_access_village(property_obj.village_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to activate this property"
        )
    
    await property_service.activate_property(property_id, updated_by=current_user.id)
    return {"message": "Property activated successfully"}


@router.post("/{property_id}/deactivate")
async def deactivate_property(
    property_id: int,
    current_user: User = Depends(get_village_admin),
    db: Session = Depends(get_db)
) -> Any:
    """
    Deactivate property
    """
    property_service = PropertyService(db)
    
    property_obj = await property_service.get_property(property_id)
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check permissions
    if not current_user.can_access_village(property_obj.village_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to deactivate this property"
        )
    
    await property_service.deactivate_property(property_id, updated_by=current_user.id)
    return {"message": "Property deactivated successfully"}

