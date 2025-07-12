"""
Chart of Accounts Initialization Script
======================================

This script initializes the Chart of Accounts with the standard accounts
for the Village Management System based on the provided account structure.

Author: Manus AI
Date: January 7, 2025
Version: 1.0
"""

from sqlalchemy.orm import Session
from app.models.accounting import ChartOfAccounts, AccountType, BalanceType
from app.core.database import get_db


def initialize_chart_of_accounts(db: Session):
    """Initialize Chart of Accounts with standard village accounts"""
    
    accounts = [
        # Assets (1xxx)
        {
            'account_code': '1111-00',
            'account_name': 'เงินสด',
            'account_name_en': 'Cash',
            'account_type': AccountType.ASSET,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': True
        },
        {
            'account_code': '1112-01',
            'account_name': 'ธนาคารกสิกรไทย CA-040-1-57563-4',
            'account_name_en': 'Kasikorn Bank Current Account',
            'account_type': AccountType.ASSET,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': True
        },
        {
            'account_code': '1113-01',
            'account_name': 'ธนาคารกสิกรไทย SA-040-1-56500-0',
            'account_name_en': 'Kasikorn Bank Savings Account',
            'account_type': AccountType.ASSET,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': True
        },
        {
            'account_code': '1130-01',
            'account_name': 'ลูกหนี้ค่าส่วนกลาง',
            'account_name_en': 'Accounts Receivable - Common Area Fees',
            'account_type': AccountType.ASSET,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': True
        },
        {
            'account_code': '1130-02',
            'account_name': 'ลูกหนี้อื่นๆ',
            'account_name_en': 'Other Accounts Receivable',
            'account_type': AccountType.ASSET,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '1140-01',
            'account_name': 'เงินมัดจำและเงินประกัน',
            'account_name_en': 'Deposits and Guarantees',
            'account_type': AccountType.ASSET,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '1150-01',
            'account_name': 'วัสดุคงเหลือ',
            'account_name_en': 'Inventory',
            'account_type': AccountType.ASSET,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '1160-01',
            'account_name': 'ค่าใช้จ่ายจ่ายล่วงหน้า',
            'account_name_en': 'Prepaid Expenses',
            'account_type': AccountType.ASSET,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '1210-01',
            'account_name': 'อุปกรณ์และเครื่องใช้',
            'account_name_en': 'Equipment and Tools',
            'account_type': AccountType.ASSET,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '1220-01',
            'account_name': 'ส่วนปรับปรุงและตกแต่ง',
            'account_name_en': 'Improvements and Decorations',
            'account_type': AccountType.ASSET,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        
        # Liabilities (2xxx)
        {
            'account_code': '2110-01',
            'account_name': 'เจ้าหนี้การค้า',
            'account_name_en': 'Accounts Payable',
            'account_type': AccountType.LIABILITY,
            'balance_type': BalanceType.CREDIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '2120-01',
            'account_name': 'เจ้าหนี้อื่นๆ',
            'account_name_en': 'Other Payables',
            'account_type': AccountType.LIABILITY,
            'balance_type': BalanceType.CREDIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '2131-01',
            'account_name': 'ค่าไฟฟ้าค้างจ่าย',
            'account_name_en': 'Accrued Electricity Expenses',
            'account_type': AccountType.LIABILITY,
            'balance_type': BalanceType.CREDIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '2131-02',
            'account_name': 'ค่าเก็บขยะค้างจ่าย',
            'account_name_en': 'Accrued Garbage Collection Fees',
            'account_type': AccountType.LIABILITY,
            'balance_type': BalanceType.CREDIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '2131-03',
            'account_name': 'ค่าบริการดูแลสระว่ายน้ำค้างจ่าย',
            'account_name_en': 'Accrued Pool Maintenance Fees',
            'account_type': AccountType.LIABILITY,
            'balance_type': BalanceType.CREDIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '2131-04',
            'account_name': 'ค่าใช้จ่ายค้างจ่ายอื่นๆ',
            'account_name_en': 'Other Accrued Expenses',
            'account_type': AccountType.LIABILITY,
            'balance_type': BalanceType.CREDIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '2140-01',
            'account_name': 'เงินรับล่วงหน้า',
            'account_name_en': 'Advance Receipts',
            'account_type': AccountType.LIABILITY,
            'balance_type': BalanceType.CREDIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '2150-01',
            'account_name': 'เงินประกันผู้รับเหมา',
            'account_name_en': 'Contractor Deposits',
            'account_type': AccountType.LIABILITY,
            'balance_type': BalanceType.CREDIT,
            'level': 1,
            'is_system_account': False
        },
        
        # Equity (3xxx)
        {
            'account_code': '3110-01',
            'account_name': 'ทุนสำรองฉุกเฉิน',
            'account_name_en': 'Emergency Reserve Fund',
            'account_type': AccountType.EQUITY,
            'balance_type': BalanceType.CREDIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '3120-01',
            'account_name': 'ทุนสำรองซ่อมบำรุง',
            'account_name_en': 'Maintenance Reserve Fund',
            'account_type': AccountType.EQUITY,
            'balance_type': BalanceType.CREDIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '3130-01',
            'account_name': 'กำไรสะสม',
            'account_name_en': 'Retained Earnings',
            'account_type': AccountType.EQUITY,
            'balance_type': BalanceType.CREDIT,
            'level': 1,
            'is_system_account': True
        },
        {
            'account_code': '3140-01',
            'account_name': 'กำไร(ขาดทุน)ปีปัจจุบัน',
            'account_name_en': 'Current Year Profit (Loss)',
            'account_type': AccountType.EQUITY,
            'balance_type': BalanceType.CREDIT,
            'level': 1,
            'is_system_account': True
        },
        
        # Revenue (4xxx)
        {
            'account_code': '4100-01',
            'account_name': 'รายรับค่าส่วนกลาง',
            'account_name_en': 'Common Area Fee Revenue',
            'account_type': AccountType.REVENUE,
            'balance_type': BalanceType.CREDIT,
            'level': 1,
            'is_system_account': True
        },
        {
            'account_code': '4100-02',
            'account_name': 'รายรับอื่นๆ',
            'account_name_en': 'Other Revenue',
            'account_type': AccountType.REVENUE,
            'balance_type': BalanceType.CREDIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '4200-01',
            'account_name': 'ดอกเบี้ยรับ',
            'account_name_en': 'Interest Income',
            'account_type': AccountType.REVENUE,
            'balance_type': BalanceType.CREDIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '4300-01',
            'account_name': 'รายรับจากค่าปรับ',
            'account_name_en': 'Penalty Revenue',
            'account_type': AccountType.REVENUE,
            'balance_type': BalanceType.CREDIT,
            'level': 1,
            'is_system_account': False
        },
        
        # Expenses (5xxx)
        {
            'account_code': '5110-01',
            'account_name': 'เงินเดือนและค่าจ้าง',
            'account_name_en': 'Salaries and Wages',
            'account_type': AccountType.EXPENSE,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '5110-02',
            'account_name': 'ค่าล่วงเวลา',
            'account_name_en': 'Overtime Pay',
            'account_type': AccountType.EXPENSE,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '5110-03',
            'account_name': 'เบี้ยขยัน',
            'account_name_en': 'Attendance Bonus',
            'account_type': AccountType.EXPENSE,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '5120-01',
            'account_name': 'ค่าประกันสังคม',
            'account_name_en': 'Social Security Contributions',
            'account_type': AccountType.EXPENSE,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '5210-01',
            'account_name': 'ค่าเช่าและบริการ',
            'account_name_en': 'Rent and Service Fees',
            'account_type': AccountType.EXPENSE,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '5220-01',
            'account_name': 'ค่าที่ปรึกษา',
            'account_name_en': 'Consulting Fees',
            'account_type': AccountType.EXPENSE,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '5230-01',
            'account_name': 'ค่าธรรมเนียมธนาคาร',
            'account_name_en': 'Bank Fees',
            'account_type': AccountType.EXPENSE,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '5240-01',
            'account_name': 'ค่าประกันภัย',
            'account_name_en': 'Insurance Expenses',
            'account_type': AccountType.EXPENSE,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '5310-01',
            'account_name': 'ค่าเครื่องเขียนและอุปกรณ์สำนักงาน',
            'account_name_en': 'Office Supplies',
            'account_type': AccountType.EXPENSE,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '5310-02',
            'account_name': 'ค่าวัสดุทำความสะอาด',
            'account_name_en': 'Cleaning Supplies',
            'account_type': AccountType.EXPENSE,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '5320-01',
            'account_name': 'ค่าซ่อมบำรุงอาคาร',
            'account_name_en': 'Building Maintenance',
            'account_type': AccountType.EXPENSE,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '5320-02',
            'account_name': 'ค่าอะไหล่ซ่อมบำรุงและค่าซ่อมแซมอื่นๆ',
            'account_name_en': 'Spare Parts and Other Repairs',
            'account_type': AccountType.EXPENSE,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '5320-03',
            'account_name': 'ค่าซ่อมบำรุงลิฟต์',
            'account_name_en': 'Elevator Maintenance',
            'account_type': AccountType.EXPENSE,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '5320-04',
            'account_name': 'ค่าซ่อมบำรุงระบบไฟฟ้า',
            'account_name_en': 'Electrical System Maintenance',
            'account_type': AccountType.EXPENSE,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '5320-05',
            'account_name': 'ค่าดูแลส่วนกลาง',
            'account_name_en': 'Common Area Maintenance',
            'account_type': AccountType.EXPENSE,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': True
        },
        {
            'account_code': '5330-01',
            'account_name': 'ค่าไฟฟ้า',
            'account_name_en': 'Electricity Expenses',
            'account_type': AccountType.EXPENSE,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '5330-02',
            'account_name': 'ค่าน้ำประปา',
            'account_name_en': 'Water Expenses',
            'account_type': AccountType.EXPENSE,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '5330-03',
            'account_name': 'ค่าโทรศัพท์',
            'account_name_en': 'Telephone Expenses',
            'account_type': AccountType.EXPENSE,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '5330-04',
            'account_name': 'ค่าอินเทอร์เน็ต',
            'account_name_en': 'Internet Expenses',
            'account_type': AccountType.EXPENSE,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '5340-01',
            'account_name': 'ค่าเก็บขยะ',
            'account_name_en': 'Garbage Collection Fees',
            'account_type': AccountType.EXPENSE,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '5340-02',
            'account_name': 'ค่าบริการดูแลสระว่ายน้ำ',
            'account_name_en': 'Pool Maintenance Services',
            'account_type': AccountType.EXPENSE,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '5340-03',
            'account_name': 'ค่าบริการรักษาความปลอดภัย',
            'account_name_en': 'Security Services',
            'account_type': AccountType.EXPENSE,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '5340-04',
            'account_name': 'ค่าบริการทำความสะอาด',
            'account_name_en': 'Cleaning Services',
            'account_type': AccountType.EXPENSE,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '5340-05',
            'account_name': 'ค่าบริการดูแลต้นไม้',
            'account_name_en': 'Landscaping Services',
            'account_type': AccountType.EXPENSE,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '5410-01',
            'account_name': 'ค่าเสื่อมราคา',
            'account_name_en': 'Depreciation Expenses',
            'account_type': AccountType.EXPENSE,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        },
        {
            'account_code': '5510-01',
            'account_name': 'ค่าใช้จ่ายอื่นๆ',
            'account_name_en': 'Other Expenses',
            'account_type': AccountType.EXPENSE,
            'balance_type': BalanceType.DEBIT,
            'level': 1,
            'is_system_account': False
        }
    ]
    
    # Check if accounts already exist
    existing_count = db.query(ChartOfAccounts).count()
    if existing_count > 0:
        print(f"Chart of Accounts already initialized with {existing_count} accounts")
        return
    
    # Create accounts
    created_count = 0
    for account_data in accounts:
        # Check if account already exists
        existing = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.account_code == account_data['account_code']
        ).first()
        
        if not existing:
            account = ChartOfAccounts(**account_data)
            db.add(account)
            created_count += 1
    
    db.commit()
    print(f"Successfully created {created_count} accounts in Chart of Accounts")


def initialize_expense_categories(db: Session):
    """Initialize expense categories with default account mappings"""
    
    # Get expense accounts for mapping
    maintenance_account = db.query(ChartOfAccounts).filter(
        ChartOfAccounts.account_code == '5320-05'
    ).first()
    
    utilities_account = db.query(ChartOfAccounts).filter(
        ChartOfAccounts.account_code == '5330-01'
    ).first()
    
    services_account = db.query(ChartOfAccounts).filter(
        ChartOfAccounts.account_code == '5340-01'
    ).first()
    
    other_account = db.query(ChartOfAccounts).filter(
        ChartOfAccounts.account_code == '5510-01'
    ).first()
    
    if not all([maintenance_account, utilities_account, services_account, other_account]):
        print("Required expense accounts not found. Please initialize Chart of Accounts first.")
        return
    
    from app.models.accounting import ExpenseCategory
    
    categories = [
        {
            'category_code': 'MAINT-01',
            'category_name': 'ค่าดูแลส่วนกลาง',
            'category_name_en': 'Common Area Maintenance',
            'description': 'ค่าใช้จ่ายในการดูแลรักษาส่วนกลาง',
            'default_account_id': maintenance_account.id,
            'is_active': True,
            'requires_approval': True
        },
        {
            'category_code': 'UTIL-01',
            'category_name': 'ค่าสาธารณูปโภค',
            'category_name_en': 'Utilities',
            'description': 'ค่าไฟฟ้า น้ำประปา โทรศัพท์',
            'default_account_id': utilities_account.id,
            'is_active': True,
            'requires_approval': True
        },
        {
            'category_code': 'SERV-01',
            'category_name': 'ค่าบริการ',
            'category_name_en': 'Services',
            'description': 'ค่าบริการต่างๆ เช่น รักษาความปลอดภัย ทำความสะอาด',
            'default_account_id': services_account.id,
            'is_active': True,
            'requires_approval': True
        },
        {
            'category_code': 'OTHER-01',
            'category_name': 'ค่าใช้จ่ายอื่นๆ',
            'category_name_en': 'Other Expenses',
            'description': 'ค่าใช้จ่ายอื่นๆ ที่ไม่อยู่ในหมวดหมู่ข้างต้น',
            'default_account_id': other_account.id,
            'is_active': True,
            'requires_approval': True
        }
    ]
    
    # Check if categories already exist
    existing_count = db.query(ExpenseCategory).count()
    if existing_count > 0:
        print(f"Expense categories already initialized with {existing_count} categories")
        return
    
    # Create categories
    created_count = 0
    for category_data in categories:
        category = ExpenseCategory(**category_data)
        db.add(category)
        created_count += 1
    
    db.commit()
    print(f"Successfully created {created_count} expense categories")


if __name__ == "__main__":
    # Initialize when run directly
    db = next(get_db())
    try:
        print("Initializing Chart of Accounts...")
        initialize_chart_of_accounts(db)
        
        print("Initializing Expense Categories...")
        initialize_expense_categories(db)
        
        print("Initialization completed successfully!")
    except Exception as e:
        print(f"Error during initialization: {e}")
        db.rollback()
    finally:
        db.close()

