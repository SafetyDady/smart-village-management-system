"""
Main FastAPI Application - Smart Village Management System
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.api import api_router

# Setup logging
setup_logging(
    log_level=settings.LOG_LEVEL,
    log_file=settings.LOG_FILE
)

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Smart Village Management System",
    description="A comprehensive ERP system for village management with integrated accounting",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add process time header to responses"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = time.time()
    
    # Log request
    logger.info(
        f"Request: {request.method} {request.url}",
        extra={
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else None
        }
    )
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(
        f"Response: {response.status_code} in {process_time:.4f}s",
        extra={
            "status_code": response.status_code,
            "process_time": process_time
        }
    )
    
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(
        f"Unhandled exception: {exc}",
        extra={
            "method": request.method,
            "url": str(request.url),
            "exception_type": type(exc).__name__
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_id": f"{int(time.time())}"
        }
    )


# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Smart Village Management System API",
        "version": "2.0.0",
        "features": [
            "Village Management",
            "Property Management", 
            "Payment Processing",
            "Invoice Management",
            "Accounting System",
            "Bank Reconciliation",
            "Financial Reporting"
        ],
        "accounting_enabled": settings.ACCOUNTING_ENABLED,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "accounting_enabled": settings.ACCOUNTING_ENABLED,
        "auto_journal_entry": settings.AUTO_JOURNAL_ENTRY,
        "database": "connected"  # In real app, check DB connection
    }


@app.get("/test")
async def test_endpoint():
    """Simple test endpoint to verify service is working"""
    return {
        "message": "Service is working!",
        "timestamp": time.time(),
        "status": "OK",
        "version": "2.0.0"
    }


@app.get("/env-debug")
def env_debug():
    """Environment debug endpoint to diagnose Railway configuration"""
    import os
    return {
        "port": os.environ.get("PORT"),
        "host": os.environ.get("HOST"),
        "all_env": dict(os.environ)
    }


@app.get("/config")
async def get_config():
    """Get application configuration (non-sensitive)"""
    return {
        "accounting_enabled": settings.ACCOUNTING_ENABLED,
        "auto_journal_entry": settings.AUTO_JOURNAL_ENTRY,
        "auto_period_creation": settings.AUTO_PERIOD_CREATION,
        "default_currency": settings.DEFAULT_CURRENCY,
        "fiscal_year_start": settings.FISCAL_YEAR_START,
        "chart_of_accounts_initialized": settings.CHART_OF_ACCOUNTS_INITIALIZED,
        "enable_audit_log": settings.ENABLE_AUDIT_LOG,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Smart Village Management System")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Accounting enabled: {settings.ACCOUNTING_ENABLED}")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

