"""fix_enum_values_to_lowercase

Revision ID: 366ac69e1786
Revises: 75f14addced2
Create Date: 2025-07-14 02:15:32.627899

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '366ac69e1786'
down_revision: Union[str, Sequence[str], None] = '75f14addced2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix enum values to lowercase to match Python model definitions."""
    
    # Step 1: Create new enum types with lowercase values
    op.execute("CREATE TYPE invoicestatus_new AS ENUM ('pending', 'paid', 'overdue', 'canceled')")
    op.execute("CREATE TYPE invoicetype_new AS ENUM ('monthly_fee', 'penalty', 'custom')")
    op.execute("CREATE TYPE paymentmethod_new AS ENUM ('bank_transfer', 'cash', 'qr_code', 'credit_card', 'mobile_banking')")
    
    # Step 2: Update existing data to lowercase values
    op.execute("""
        UPDATE invoices 
        SET status = CASE 
            WHEN status = 'PENDING' THEN 'pending'
            WHEN status = 'PAID' THEN 'paid'
            WHEN status = 'OVERDUE' THEN 'overdue'
            WHEN status = 'CANCELED' THEN 'canceled'
            ELSE status
        END
    """)
    
    op.execute("""
        UPDATE invoices 
        SET invoice_type = CASE 
            WHEN invoice_type = 'MONTHLY_FEE' THEN 'monthly_fee'
            WHEN invoice_type = 'PENALTY' THEN 'penalty'
            WHEN invoice_type = 'CUSTOM' THEN 'custom'
            ELSE invoice_type
        END
    """)
    
    op.execute("""
        UPDATE payments 
        SET method = CASE 
            WHEN method = 'BANK_TRANSFER' THEN 'bank_transfer'
            WHEN method = 'CASH' THEN 'cash'
            WHEN method = 'QR_CODE' THEN 'qr_code'
            WHEN method = 'CREDIT_CARD' THEN 'credit_card'
            WHEN method = 'MOBILE_BANKING' THEN 'mobile_banking'
            ELSE method
        END
    """)
    
    # Step 3: Alter columns to use new enum types
    op.execute("ALTER TABLE invoices ALTER COLUMN status TYPE invoicestatus_new USING status::text::invoicestatus_new")
    op.execute("ALTER TABLE invoices ALTER COLUMN invoice_type TYPE invoicetype_new USING invoice_type::text::invoicetype_new")
    op.execute("ALTER TABLE payments ALTER COLUMN method TYPE paymentmethod_new USING method::text::paymentmethod_new")
    
    # Step 4: Drop old enum types
    op.execute("DROP TYPE invoicestatus")
    op.execute("DROP TYPE invoicetype")
    op.execute("DROP TYPE paymentmethod")
    
    # Step 5: Rename new enum types to original names
    op.execute("ALTER TYPE invoicestatus_new RENAME TO invoicestatus")
    op.execute("ALTER TYPE invoicetype_new RENAME TO invoicetype")
    op.execute("ALTER TYPE paymentmethod_new RENAME TO paymentmethod")


def downgrade() -> None:
    """Revert enum values back to uppercase."""
    
    # Step 1: Create old enum types with uppercase values
    op.execute("CREATE TYPE invoicestatus_old AS ENUM ('PENDING', 'PAID', 'OVERDUE', 'CANCELED')")
    op.execute("CREATE TYPE invoicetype_old AS ENUM ('MONTHLY_FEE', 'PENALTY', 'CUSTOM')")
    op.execute("CREATE TYPE paymentmethod_old AS ENUM ('BANK_TRANSFER', 'CASH', 'QR_CODE', 'CREDIT_CARD', 'MOBILE_BANKING')")
    
    # Step 2: Update existing data to uppercase values
    op.execute("""
        UPDATE invoices 
        SET status = CASE 
            WHEN status = 'pending' THEN 'PENDING'
            WHEN status = 'paid' THEN 'PAID'
            WHEN status = 'overdue' THEN 'OVERDUE'
            WHEN status = 'canceled' THEN 'CANCELED'
            ELSE status
        END
    """)
    
    op.execute("""
        UPDATE invoices 
        SET invoice_type = CASE 
            WHEN invoice_type = 'monthly_fee' THEN 'MONTHLY_FEE'
            WHEN invoice_type = 'penalty' THEN 'PENALTY'
            WHEN invoice_type = 'custom' THEN 'CUSTOM'
            ELSE invoice_type
        END
    """)
    
    op.execute("""
        UPDATE payments 
        SET method = CASE 
            WHEN method = 'bank_transfer' THEN 'BANK_TRANSFER'
            WHEN method = 'cash' THEN 'CASH'
            WHEN method = 'qr_code' THEN 'QR_CODE'
            WHEN method = 'credit_card' THEN 'CREDIT_CARD'
            WHEN method = 'mobile_banking' THEN 'MOBILE_BANKING'
            ELSE method
        END
    """)
    
    # Step 3: Alter columns to use old enum types
    op.execute("ALTER TABLE invoices ALTER COLUMN status TYPE invoicestatus_old USING status::text::invoicestatus_old")
    op.execute("ALTER TABLE invoices ALTER COLUMN invoice_type TYPE invoicetype_old USING invoice_type::text::invoicetype_old")
    op.execute("ALTER TABLE payments ALTER COLUMN method TYPE paymentmethod_old USING method::text::paymentmethod_old")
    
    # Step 4: Drop current enum types
    op.execute("DROP TYPE invoicestatus")
    op.execute("DROP TYPE invoicetype")
    op.execute("DROP TYPE paymentmethod")
    
    # Step 5: Rename old enum types to original names
    op.execute("ALTER TYPE invoicestatus_old RENAME TO invoicestatus")
    op.execute("ALTER TYPE invoicetype_old RENAME TO invoicetype")
    op.execute("ALTER TYPE paymentmethod_old RENAME TO paymentmethod")
