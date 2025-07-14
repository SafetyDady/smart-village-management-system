"""
Main API Router - Smart Village Management System
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, villages, properties, admin, invoices, payments, receipts, dashboard, accounting, config, debug

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(villages.router, prefix="/villages", tags=["Villages"])
api_router.include_router(properties.router, prefix="/properties", tags=["Properties"])

api_router.include_router(
    admin.router,
    tags=["Admin"]
)

# Accounting endpoints
api_router.include_router(
    invoices.router,
    prefix="/invoices",
    tags=["Invoices"]
)

api_router.include_router(
    payments.router,
    prefix="/payments",
    tags=["Payments"]
)

api_router.include_router(
    receipts.router,
    prefix="/receipts",
    tags=["Receipts"]
)

# Legacy accounting and config endpoints
api_router.include_router(accounting.router, prefix="/accounting", tags=["Accounting"])
api_router.include_router(config.router, prefix="/config", tags=["Configuration"])

# Dashboard endpoints
api_router.include_router(
    dashboard.router,
    tags=["Dashboard"]
)

# Debug endpoints (temporary)
api_router.include_router(
    debug.router,
    tags=["Debug"]
)

