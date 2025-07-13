#!/usr/bin/env python3
"""
Script to run Alembic migrations on production database
"""

import os
import subprocess
import sys
from sqlalchemy import create_engine, text
from app.core.config import settings

def check_database_connection():
    """Check if database is accessible"""
    try:
        # Use the DATABASE_URL from Railway environment
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL environment variable not found")
            return False
            
        print(f"🔗 Connecting to database...")
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def run_migrations():
    """Run Alembic migrations"""
    try:
        print("🚀 Running Alembic migrations...")
        
        # Set the DATABASE_URL environment variable for Alembic
        env = os.environ.copy()
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            env["DATABASE_URL"] = database_url
        
        # Run alembic upgrade head
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            env=env,
            cwd="/home/ubuntu/smart-village-management-system/backend"
        )
        
        if result.returncode == 0:
            print("✅ Migrations completed successfully!")
            print("Output:", result.stdout)
            return True
        else:
            print("❌ Migration failed!")
            print("Error:", result.stderr)
            print("Output:", result.stdout)
            return False
            
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False

def check_tables_created():
    """Check if tables were created successfully"""
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            return False
            
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check for main tables
            tables_to_check = [
                "users", "villages", "properties", 
                "invoices", "payments", "receipts"
            ]
            
            existing_tables = []
            for table in tables_to_check:
                result = conn.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = '{table}'
                    );
                """))
                
                if result.fetchone()[0]:
                    existing_tables.append(table)
            
            print(f"✅ Found {len(existing_tables)} tables: {', '.join(existing_tables)}")
            return len(existing_tables) > 0
            
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return False

def main():
    print("🔧 Production Database Migration Script")
    print("=" * 50)
    
    # Step 1: Check database connection
    if not check_database_connection():
        print("❌ Cannot connect to database. Exiting...")
        sys.exit(1)
    
    # Step 2: Run migrations
    if not run_migrations():
        print("❌ Migration failed. Exiting...")
        sys.exit(1)
    
    # Step 3: Verify tables were created
    if not check_tables_created():
        print("❌ Tables were not created properly. Exiting...")
        sys.exit(1)
    
    print("=" * 50)
    print("🎉 Database migration completed successfully!")
    print("✅ Production database is ready for use!")

if __name__ == "__main__":
    main()
