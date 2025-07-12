from logging.config import fileConfig
import os
import sys

# ✅ โหลด .env เพื่อให้สามารถใช้ DATABASE_URL จากไฟล์ .env ได้
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# ✅ เพิ่ม path ให้สามารถ import จาก app ได้
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# ✅ Import Base และ Models ทั้งหมดที่ใช้ใน metadata
from app.core.database import Base
from app.models.user import User
from app.models.village import Village
from app.models.property import Property
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.models.receipt import Receipt
from app.models.payment_invoice import PaymentInvoice

# ✅ อ่าน Alembic config object
config = context.config

# ✅ อ่าน DATABASE_URL จาก environment หรือใช้ fallback (กรณียังไม่มี .env)
database_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/smart_village")
config.set_main_option("sqlalchemy.url", database_url)

# ✅ ตั้งค่าการ log จากไฟล์ alembic.ini ถ้ามี
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ✅ ระบุ metadata สำหรับ autogenerate
target_metadata = Base.metadata

# -------------------------------
# 🚀 โหมด offline: generate SQL script
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# 🚀 โหมด online: connect DB และ migrate จริง
def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

# ✅ เลือกโหมด run
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
