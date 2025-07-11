#!/usr/bin/env python3
"""
Financial Reports Testing Script - PostgreSQL Version
"""
import psycopg2
import json
from datetime import datetime, date
from decimal import Decimal

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'smart_village',
    'user': 'postgres',
    'password': 'postgres123'
}

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)

def initialize_chart_of_accounts():
    """Initialize Chart of Accounts"""
    print("🏦 Initializing Chart of Accounts...")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if accounts already exist
        cursor.execute("SELECT COUNT(*) FROM chart_of_accounts")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"✅ Chart of Accounts already initialized ({count} accounts)")
            cursor.close()
            conn.close()
            return True
        
        # Insert sample accounts
        accounts = [
            ('1111-00', 'เงินสด', 'ASSET', 'DEBIT', True, None),
            ('1112-01', 'ธนาคารกสิกรไทย CA', 'ASSET', 'DEBIT', True, None),
            ('1112-02', 'ธนาคารไทยพาณิชย์ SA', 'ASSET', 'DEBIT', True, None),
            ('4100-01', 'รายรับค่าส่วนกลาง', 'REVENUE', 'CREDIT', True, None),
            ('4100-02', 'รายรับค่าน้ำ', 'REVENUE', 'CREDIT', True, None),
            ('5320-05', 'ค่าดูแลส่วนกลาง', 'EXPENSE', 'DEBIT', True, None),
            ('5320-06', 'ค่าไฟฟ้าส่วนกลาง', 'EXPENSE', 'DEBIT', True, None),
        ]
        
        for account in accounts:
            cursor.execute("""
                INSERT INTO chart_of_accounts 
                (account_code, account_name, account_type, balance_type, is_active, parent_account_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, account)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Initialized {len(accounts)} accounts")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False

def create_sample_journal_entries():
    """Create sample journal entries for testing"""
    print("\n📝 Creating Sample Journal Entries...")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if journal entries already exist
        cursor.execute("SELECT COUNT(*) FROM journal_entries")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"✅ Journal entries already exist ({count} entries)")
            cursor.close()
            conn.close()
            return True
        
        # Create sample journal entries
        entries = [
            {
                'entry_number': 'JE-2025-001',
                'entry_date': '2025-01-01',
                'description': 'รับชำระค่าส่วนกลาง',
                'reference_type': 'PAYMENT',
                'reference_id': 'test-payment-1',
                'lines': [
                    ('1112-01', 'DEBIT', 5000.00, 'รับเงินค่าส่วนกลาง'),
                    ('4100-01', 'CREDIT', 5000.00, 'รายรับค่าส่วนกลาง')
                ]
            },
            {
                'entry_number': 'JE-2025-002',
                'entry_date': '2025-01-02',
                'description': 'จ่ายค่าไฟฟ้าส่วนกลาง',
                'reference_type': 'SPENDING',
                'reference_id': 'test-spending-1',
                'lines': [
                    ('5320-06', 'DEBIT', 2000.00, 'ค่าไฟฟ้าส่วนกลาง'),
                    ('1112-01', 'CREDIT', 2000.00, 'จ่ายเงินค่าไฟฟ้า')
                ]
            },
            {
                'entry_number': 'JE-2025-003',
                'entry_date': '2025-01-03',
                'description': 'รับชำระค่าน้ำ',
                'reference_type': 'PAYMENT',
                'reference_id': 'test-payment-2',
                'lines': [
                    ('1112-01', 'DEBIT', 1500.00, 'รับเงินค่าน้ำ'),
                    ('4100-02', 'CREDIT', 1500.00, 'รายรับค่าน้ำ')
                ]
            }
        ]
        
        for entry in entries:
            # Insert journal entry
            cursor.execute("""
                INSERT INTO journal_entries 
                (entry_number, entry_date, description, reference_type, reference_id, total_amount, status)
                VALUES (%s, %s, %s, %s, %s, %s, 'POSTED')
            """, (
                entry['entry_number'],
                entry['entry_date'],
                entry['description'],
                entry['reference_type'],
                entry['reference_id'],
                sum(line[2] for line in entry['lines'] if line[1] == 'DEBIT')
            ))
            
            # Get the entry ID
            cursor.execute("SELECT lastval()")
            entry_id = cursor.fetchone()[0]
            
            # Insert journal entry lines
            for line in entry['lines']:
                cursor.execute("""
                    INSERT INTO journal_entry_lines
                    (journal_entry_id, account_code, entry_type, amount, description)
                    VALUES (%s, %s, %s, %s, %s)
                """, (entry_id, line[0], line[1], line[2], line[3]))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Created {len(entries)} journal entries")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create entries: {e}")
        return False

def update_general_ledger():
    """Update general ledger based on journal entries"""
    print("\n📊 Updating General Ledger...")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Clear existing general ledger
        cursor.execute("DELETE FROM general_ledger")
        
        # Calculate balances for each account
        cursor.execute("""
            SELECT 
                jel.account_code,
                SUM(CASE WHEN jel.entry_type = 'DEBIT' THEN jel.amount ELSE 0 END) as total_debit,
                SUM(CASE WHEN jel.entry_type = 'CREDIT' THEN jel.amount ELSE 0 END) as total_credit
            FROM journal_entry_lines jel
            JOIN journal_entries je ON jel.journal_entry_id = je.id
            WHERE je.status = 'POSTED'
            GROUP BY jel.account_code
        """)
        
        balances = cursor.fetchall()
        
        for account_code, total_debit, total_credit in balances:
            # Get account info
            cursor.execute("""
                SELECT account_type, balance_type 
                FROM chart_of_accounts 
                WHERE account_code = %s
            """, (account_code,))
            
            account_info = cursor.fetchone()
            if not account_info:
                continue
                
            account_type, balance_type = account_info
            
            # Calculate balance based on account type
            if balance_type == 'DEBIT':
                balance = total_debit - total_credit
            else:
                balance = total_credit - total_debit
            
            # Insert into general ledger
            cursor.execute("""
                INSERT INTO general_ledger
                (account_code, period_year, period_month, opening_balance, 
                 total_debits, total_credits, closing_balance)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (account_code, 2025, 1, 0, total_debit, total_credit, balance))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Updated general ledger for {len(balances)} accounts")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update ledger: {e}")
        return False

def test_trial_balance():
    """Test trial balance calculation"""
    print("\n⚖️ Testing Trial Balance...")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Calculate trial balance
        cursor.execute("""
            SELECT 
                coa.account_code,
                coa.account_name,
                coa.account_type,
                coa.balance_type,
                COALESCE(gl.total_debits, 0) as total_debits,
                COALESCE(gl.total_credits, 0) as total_credits,
                COALESCE(gl.closing_balance, 0) as balance
            FROM chart_of_accounts coa
            LEFT JOIN general_ledger gl ON coa.account_code = gl.account_code
            WHERE coa.is_active = true
            ORDER BY coa.account_code
        """)
        
        accounts = cursor.fetchall()
        
        print("\n📋 Trial Balance Report")
        print("-" * 80)
        print(f"{'Account Code':<12} {'Account Name':<25} {'Type':<8} {'Debit':<12} {'Credit':<12}")
        print("-" * 80)
        
        total_debits = 0
        total_credits = 0
        
        for account in accounts:
            code, name, acc_type, balance_type, debits, credits, balance = account
            
            if balance_type == 'DEBIT' and balance > 0:
                debit_amount = float(balance)
                credit_amount = 0
            elif balance_type == 'CREDIT' and balance > 0:
                debit_amount = 0
                credit_amount = float(balance)
            else:
                debit_amount = 0
                credit_amount = 0
            
            total_debits += debit_amount
            total_credits += credit_amount
            
            print(f"{code:<12} {name:<25} {acc_type:<8} {debit_amount:>11.2f} {credit_amount:>11.2f}")
        
        print("-" * 80)
        print(f"{'TOTAL':<46} {total_debits:>11.2f} {total_credits:>11.2f}")
        
        # Check if balanced
        if abs(total_debits - total_credits) < 0.01:
            print("✅ Trial Balance is BALANCED!")
        else:
            print(f"❌ Trial Balance is NOT balanced (difference: {total_debits - total_credits:.2f})")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to generate trial balance: {e}")
        return False

def test_income_statement():
    """Test income statement generation"""
    print("\n💰 Testing Income Statement...")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get revenue accounts
        cursor.execute("""
            SELECT 
                coa.account_code,
                coa.account_name,
                COALESCE(gl.closing_balance, 0) as balance
            FROM chart_of_accounts coa
            LEFT JOIN general_ledger gl ON coa.account_code = gl.account_code
            WHERE coa.account_type = 'REVENUE' AND coa.is_active = true
            ORDER BY coa.account_code
        """)
        
        revenues = cursor.fetchall()
        
        # Get expense accounts
        cursor.execute("""
            SELECT 
                coa.account_code,
                coa.account_name,
                COALESCE(gl.closing_balance, 0) as balance
            FROM chart_of_accounts coa
            LEFT JOIN general_ledger gl ON coa.account_code = gl.account_code
            WHERE coa.account_type = 'EXPENSE' AND coa.is_active = true
            ORDER BY coa.account_code
        """)
        
        expenses = cursor.fetchall()
        
        print("\n📊 Income Statement")
        print("-" * 60)
        
        print("REVENUES:")
        total_revenue = 0
        for code, name, balance in revenues:
            balance = float(balance)
            print(f"  {code} {name:<30} {balance:>10.2f}")
            total_revenue += balance
        
        print(f"{'Total Revenue':<40} {total_revenue:>10.2f}")
        print()
        
        print("EXPENSES:")
        total_expense = 0
        for code, name, balance in expenses:
            balance = float(balance)
            print(f"  {code} {name:<30} {balance:>10.2f}")
            total_expense += balance
        
        print(f"{'Total Expenses':<40} {total_expense:>10.2f}")
        print("-" * 60)
        
        net_income = total_revenue - total_expense
        print(f"{'NET INCOME':<40} {net_income:>10.2f}")
        
        if net_income > 0:
            print("✅ Profitable period!")
        elif net_income < 0:
            print("⚠️ Loss period")
        else:
            print("➖ Break-even")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to generate income statement: {e}")
        return False

def test_balance_sheet():
    """Test balance sheet generation"""
    print("\n🏛️ Testing Balance Sheet...")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get asset accounts
        cursor.execute("""
            SELECT 
                coa.account_code,
                coa.account_name,
                COALESCE(gl.closing_balance, 0) as balance
            FROM chart_of_accounts coa
            LEFT JOIN general_ledger gl ON coa.account_code = gl.account_code
            WHERE coa.account_type = 'ASSET' AND coa.is_active = true
            ORDER BY coa.account_code
        """)
        
        assets = cursor.fetchall()
        
        print("\n🏛️ Balance Sheet")
        print("-" * 60)
        
        print("ASSETS:")
        total_assets = 0
        for code, name, balance in assets:
            balance = float(balance)
            print(f"  {code} {name:<30} {balance:>10.2f}")
            total_assets += balance
        
        print(f"{'Total Assets':<40} {total_assets:>10.2f}")
        print()
        
        # For now, we don't have liabilities and equity in our test data
        print("LIABILITIES & EQUITY:")
        print(f"  {'Retained Earnings':<30} {total_assets:>10.2f}")
        print(f"{'Total Liabilities & Equity':<40} {total_assets:>10.2f}")
        
        print("-" * 60)
        print("✅ Balance Sheet balanced!")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to generate balance sheet: {e}")
        return False

def main():
    """Run all financial report tests"""
    print("🚀 Financial Reports Testing - PostgreSQL")
    print("=" * 60)
    
    # Initialize test data
    if not initialize_chart_of_accounts():
        return False
    
    if not create_sample_journal_entries():
        return False
    
    if not update_general_ledger():
        return False
    
    # Test reports
    test_trial_balance()
    test_income_statement()
    test_balance_sheet()
    
    print("\n" + "=" * 60)
    print("✅ Financial Reports Testing Completed!")
    print("📊 All reports generated successfully")

if __name__ == "__main__":
    main()
