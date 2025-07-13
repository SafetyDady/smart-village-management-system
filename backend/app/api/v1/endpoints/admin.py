"""
Database Migration Router
Provides endpoints to run database migrations and check database status
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import get_db
import subprocess
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/migrate")
async def run_migrations():
    """Run database migrations"""
    try:
        logger.info("Starting database migrations...")
        
        # Run Alembic migrations
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd="/app"
        )
        
        if result.returncode == 0:
            logger.info("Migrations completed successfully")
            return {
                "status": "success",
                "message": "Migrations completed successfully",
                "output": result.stdout,
                "timestamp": "2025-07-13T07:30:00Z"
            }
        else:
            logger.error(f"Migration failed: {result.stderr}")
            return {
                "status": "error", 
                "message": "Migration failed",
                "error": result.stderr,
                "output": result.stdout,
                "timestamp": "2025-07-13T07:30:00Z"
            }
            
    except Exception as e:
        logger.error(f"Migration exception: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Migration error: {str(e)}")

@router.get("/tables")
async def check_tables(db: Session = Depends(get_db)):
    """Check what tables exist in the database"""
    try:
        logger.info("Checking database tables...")
        
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """))
        
        tables = [row[0] for row in result.fetchall()]
        
        logger.info(f"Found {len(tables)} tables")
        
        return {
            "status": "success",
            "tables": tables,
            "count": len(tables),
            "timestamp": "2025-07-13T07:30:00Z"
        }
        
    except Exception as e:
        logger.error(f"Database check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/seed-data")
async def seed_initial_data(db: Session = Depends(get_db)):
    """Create initial data (Super Admin user and sample villages)"""
    try:
        from app.models.user import User
        from app.models.village import Village
        from app.services.auth_service import AuthService
        from sqlalchemy.exc import IntegrityError
        import bcrypt
        
        logger.info("Starting data seeding...")
        
        # Create Super Admin user
        auth_service = AuthService(db)
        
        # Check if admin user already exists
        existing_admin = db.query(User).filter(User.email == "admin@smartvillage.com").first()
        
        if not existing_admin:
            # Hash password
            hashed_password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            admin_user = User(
                email="admin@smartvillage.com",
                hashed_password=hashed_password,
                first_name="Super",
                last_name="Admin",
                phone="+66123456789",
                role="super_admin",
                is_active=True,
                is_verified=True,
                is_email_verified=True
            )
            
            db.add(admin_user)
            db.commit()
            logger.info("Super Admin user created")
        else:
            logger.info("Super Admin user already exists")
        
        # Create sample villages
        sample_villages = [
            {
                "name": "Green Valley Village",
                "description": "A peaceful village surrounded by green hills",
                "address": "123 Green Valley Road, Chiang Mai",
                "city": "Chiang Mai",
                "state": "Chiang Mai",
                "postal_code": "50000",
                "country": "Thailand",
                "is_active": True
            },
            {
                "name": "Sunset Beach Village", 
                "description": "Beautiful beachfront community",
                "address": "456 Beach Road, Phuket",
                "city": "Phuket",
                "state": "Phuket", 
                "postal_code": "83000",
                "country": "Thailand",
                "is_active": True
            },
            {
                "name": "Mountain View Village",
                "description": "Village with stunning mountain views", 
                "address": "789 Mountain Road, Chiang Rai",
                "city": "Chiang Rai",
                "state": "Chiang Rai",
                "postal_code": "57000", 
                "country": "Thailand",
                "is_active": True
            }
        ]
        
        villages_created = 0
        for village_data in sample_villages:
            existing_village = db.query(Village).filter(Village.name == village_data["name"]).first()
            if not existing_village:
                village = Village(**village_data)
                db.add(village)
                villages_created += 1
        
        db.commit()
        logger.info(f"Created {villages_created} new villages")
        
        return {
            "status": "success",
            "message": f"Data seeding completed. Created {villages_created} villages.",
            "admin_user": "admin@smartvillage.com / admin123",
            "villages_created": villages_created,
            "timestamp": "2025-07-13T07:30:00Z"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Data seeding error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Data seeding error: {str(e)}")

@router.get("/database-status")
async def get_database_status(db: Session = Depends(get_db)):
    """Get comprehensive database status"""
    try:
        # Check tables
        tables_result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """))
        tables = [row[0] for row in tables_result.fetchall()]
        
        # Count records in main tables
        counts = {}
        main_tables = ["users", "villages", "properties", "invoices", "payments", "receipts"]
        
        for table in main_tables:
            if table in tables:
                try:
                    count_result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    counts[table] = count_result.fetchone()[0]
                except:
                    counts[table] = "Error"
            else:
                counts[table] = "Table not found"
        
        return {
            "status": "success",
            "database_connected": True,
            "tables": tables,
            "table_count": len(tables),
            "record_counts": counts,
            "timestamp": "2025-07-13T07:30:00Z"
        }
        
    except Exception as e:
        logger.error(f"Database status error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database status error: {str(e)}")

