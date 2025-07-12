"""
Main API Router - Smart Village Management System
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, villages, properties, payments, accounting, config

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(villages.router, prefix="/villages", tags=["Villages"])
api_router.include_router(properties.router, prefix="/properties", tags=["Properties"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(accounting.router, prefix="/accounting", tags=["Accounting"])
api_router.include_router(config.router, prefix="/config", tags=["Configuration"])

