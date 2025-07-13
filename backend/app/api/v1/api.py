"""
Main API Router - Smart Village Management System
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, villages, properties, admin

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

api_router.include_router(
    villages.router,
    prefix="/villages",
    tags=["Villages"]
)

api_router.include_router(
    properties.router,
    prefix="/properties",
    tags=["Properties"]
)

api_router.include_router(
    admin.router,
    tags=["Admin"]
)

