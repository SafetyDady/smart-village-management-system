"""
Auto-migration utility for Railway deployment
"""

import logging
from alembic.config import Config
from alembic import command
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine
from app.core.config import settings

logger = logging.getLogger(__name__)

def get_current_revision(engine):
    """Get current database revision"""
    try:
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            return context.get_current_revision()
    except Exception as e:
        logger.warning(f"Could not get current revision: {e}")
        return None

def get_head_revision():
    """Get head revision from migration scripts"""
    try:
        alembic_cfg = Config("alembic.ini")
        script = ScriptDirectory.from_config(alembic_cfg)
        return script.get_current_head()
    except Exception as e:
        logger.warning(f"Could not get head revision: {e}")
        return None

def run_migrations():
    """Run database migrations if needed"""
    try:
        logger.info("🔄 Checking database migration status...")
        
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        # Get current and head revisions
        current_rev = get_current_revision(engine)
        head_rev = get_head_revision()
        
        logger.info(f"Current revision: {current_rev}")
        logger.info(f"Head revision: {head_rev}")
        
        if current_rev == head_rev:
            logger.info("✅ Database is up to date, no migrations needed")
            return True
        
        logger.info("🚀 Running database migrations...")
        
        # Configure Alembic
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
        
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        
        logger.info("✅ Database migrations completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False

def check_enum_compatibility():
    """Check if enum values are compatible with current schema"""
    try:
        from app.models.invoice import InvoiceStatus
        from app.core.database import get_db
        from sqlalchemy import text
        
        # Test enum values
        test_values = [status.value for status in InvoiceStatus]
        logger.info(f"Testing enum values: {test_values}")
        
        db = next(get_db())
        
        for value in test_values:
            try:
                # Test if enum value is valid
                result = db.execute(text(f"SELECT '{value}'::invoicestatus"))
                logger.info(f"✅ Enum value '{value}' is valid")
            except Exception as e:
                logger.error(f"❌ Enum value '{value}' is invalid: {e}")
                return False
        
        logger.info("✅ All enum values are compatible")
        return True
        
    except Exception as e:
        logger.error(f"❌ Enum compatibility check failed: {e}")
        return False

if __name__ == "__main__":
    # For testing
    logging.basicConfig(level=logging.INFO)
    run_migrations()
    check_enum_compatibility()

