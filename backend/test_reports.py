#!/usr/bin/env python3
"""Financial Reports Testing"""
import psycopg2
import uuid
from datetime import datetime

DB_CONFIG = {
    'host': 'localhost',
    'database': 'smart_village',
    'user': 'postgres',
    'password': 'postgres123'
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def create_test_data():
    print("📝 Creating test data...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check existing data
        cursor.execute("SELECT COUNT(*) FROM journal_entries")
        if cursor.fetchone()[0] > 0:
            print("✅ Test data already exists")
            return True
        
        # Create accounting period
        period_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO accounting_periods (id, year, month, start_date, end_date, status)
            VALUES (%s, 2025, 1, '2025-01-01', '2025-01-31', 'OPEN')
        """, (period_id,))
        
        # Create journal entry
        entry_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO journal_entries 
            (id, entry_number, transaction_date, description, reference_type, 
             total_debit, total_credit, status, period_id)
            VALUES (%s, 'JE-001', '2025-01-01', 'Test Entry', 'MANUAL', 5000, 5000, 'POSTED', %s)
        """, (entry_id, period_id))
        
        # Create journal lines
        line1_id = str(uuid.uuid4())
        line2_id = str(uuid.uuid4())
        
        cursor.execute("""
            INSERT INTO journal_entry_lines
            (id, journal_entry_id, account_code, entry_type, amount, description)
            VALUES (%s, %s, '1112-01', 'DEBIT', 5000, 'Test Debit')
        """, (line1_id, entry_id))
        
        cursor.execute("""
            INSERT INTO journal_entry_lines
            (id, journal_entry_id, account_code, entry_type, amount, description)
            VALUES (%s, %s, '4100-01', 'CREDIT', 5000, 'Test Credit')
        """, (line2_id, entry_id))
        
        # Update general ledger
        gl1_id = str(uuid.uuid4())
        gl2_id = str(uuid.uuid4())
        
        cursor.execute("""
            INSERT INTO general_ledger
            (id, account_code, period_year, period_month, opening_balance, 
             total_debits, total_credits, closing_balance)
            VALUES (%s, '1112-01', 2025, 1, 0, 5000, 0, 5000)
        """, (gl1_id,))
        
        cursor.execute("""
            INSERT INTO general_ledger
            (id, account_code, period_year, period_month, opening_balance, 
             total_debits, total_credits, closing_balance)
            VALUES (%s, '4100-01', 2025, 1, 0, 0, 5000, 5000)
        """, (gl2_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Test data created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_trial_balance():
    print("\n⚖️ Testing Trial Balance...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                coa.account_code,
                coa.account_name,
                coa.balance_type,
                COALESCE(gl.closing_balance, 0) as balance
            FROM chart_of_accounts coa
            LEFT JOIN general_ledger gl ON coa.account_code = gl.account_code
            WHERE gl.closing_balance IS NOT NULL AND gl.closing_balance != 0
            ORDER BY coa.account_code
        """)
        
        accounts = cursor.fetchall()
        
        print("\n📋 Trial Balance Report")
        print("-" * 70)
        print(f"{'Code':<12} {'Name':<25} {'Debit':<12} {'Credit':<12}")
        print("-" * 70)
        
        total_debits = 0
        total_credits = 0
        
        for code, name, balance_type, balance in accounts:
            balance = float(balance)
            
            if balance_type == 'DEBIT' and balance > 0:
                debit_amount = balance
                credit_amount = 0
            elif balance_type == 'CREDIT' and balance > 0:
                debit_amount = 0
                credit_amount = balance
            else:
                debit_amount = 0
                credit_amount = 0
            
            total_debits += debit_amount
            total_credits += credit_amount
            
            print(f"{code:<12} {name:<25} {debit_amount:>11.2f} {credit_amount:>11.2f}")
        
        print("-" * 70)
        print(f"{'TOTAL':<38} {total_debits:>11.2f} {total_credits:>11.2f}")
        
        if abs(total_debits - total_credits) < 0.01:
            print("✅ Trial Balance is BALANCED!")
        else:
            print(f"❌ NOT balanced (diff: {total_debits - total_credits:.2f})")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def main():
    print("🚀 Financial Reports Testing")
    print("=" * 50)
    
    if create_test_data():
        test_trial_balance()
    
    print("\n✅ Testing completed!")

if __name__ == "__main__":
    main()
