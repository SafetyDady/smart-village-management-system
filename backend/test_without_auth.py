#!/usr/bin/env python3
"""
Test Script without Authentication - For Development Testing
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_public_endpoints():
    """Test public endpoints that don't require auth"""
    print("🧪 Testing Public Endpoints")
    print("-" * 40)
    
    # Health check
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Check: {response.status_code}")
    if response.status_code == 200:
        print(f"  Data: {response.json()}")
    
    # Config
    response = requests.get(f"{BASE_URL}/config")
    print(f"Config: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Accounting Enabled: {data.get('accounting_enabled')}")
        print(f"  Auto Journal Entry: {data.get('auto_journal_entry')}")
    
    # Root endpoint
    response = requests.get(f"{BASE_URL}/")
    print(f"Root: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Version: {data.get('version')}")
        print(f"  Features: {len(data.get('features', []))}")

def test_swagger_docs():
    """Test Swagger documentation"""
    print("\n📚 Testing Documentation")
    print("-" * 40)
    
    # Swagger UI
    response = requests.get(f"{BASE_URL}/docs")
    print(f"Swagger UI: {response.status_code}")
    
    # ReDoc
    response = requests.get(f"{BASE_URL}/redoc")
    print(f"ReDoc: {response.status_code}")
    
    # OpenAPI JSON
    response = requests.get(f"{BASE_URL}/openapi.json")
    print(f"OpenAPI JSON: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Title: {data.get('info', {}).get('title')}")
        print(f"  Version: {data.get('info', {}).get('version')}")
        print(f"  Paths: {len(data.get('paths', {}))}")

def test_database_connection():
    """Test database connectivity through health endpoint"""
    print("\n🗄️ Testing Database Connection")
    print("-" * 40)
    
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        data = response.json()
        db_status = data.get('database', 'unknown')
        print(f"Database Status: {db_status}")
        
        if db_status == 'connected':
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed")
    else:
        print("❌ Cannot check database status")

def test_accounting_system_status():
    """Test accounting system status"""
    print("\n💰 Testing Accounting System Status")
    print("-" * 40)
    
    response = requests.get(f"{BASE_URL}/config")
    if response.status_code == 200:
        data = response.json()
        
        accounting_enabled = data.get('accounting_enabled', False)
        auto_journal = data.get('auto_journal_entry', False)
        chart_initialized = data.get('chart_of_accounts_initialized', False)
        
        print(f"Accounting Enabled: {'✅' if accounting_enabled else '❌'}")
        print(f"Auto Journal Entry: {'✅' if auto_journal else '❌'}")
        print(f"Chart of Accounts: {'✅' if chart_initialized else '❌'}")
        print(f"Default Currency: {data.get('default_currency', 'N/A')}")
        print(f"Fiscal Year Start: {data.get('fiscal_year_start', 'N/A')}")
        
        if accounting_enabled and auto_journal:
            print("🎉 Accounting system is properly configured!")
        else:
            print("⚠️ Accounting system needs configuration")

def test_cors_and_headers():
    """Test CORS and security headers"""
    print("\n🔒 Testing CORS and Headers")
    print("-" * 40)
    
    # Test CORS preflight
    response = requests.options(f"{BASE_URL}/")
    print(f"OPTIONS Request: {response.status_code}")
    
    # Check headers
    response = requests.get(f"{BASE_URL}/health")
    headers = response.headers
    
    print("Response Headers:")
    for header in ['X-Process-Time', 'Access-Control-Allow-Origin', 'Content-Type']:
        value = headers.get(header, 'Not present')
        print(f"  {header}: {value}")

def main():
    """Run all tests"""
    print("🚀 Village Accounting ERP System - Development Tests")
    print("=" * 60)
    
    try:
        test_public_endpoints()
        test_swagger_docs()
        test_database_connection()
        test_accounting_system_status()
        test_cors_and_headers()
        
        print("\n" + "=" * 60)
        print("✅ Development tests completed successfully!")
        print("🔗 Public API URL: https://8000-ilz5cj354gz2af8ztnznh-5b92cd07.manusvm.computer")
        print("📚 Swagger Docs: https://8000-ilz5cj354gz2af8ztnznh-5b92cd07.manusvm.computer/docs")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()
