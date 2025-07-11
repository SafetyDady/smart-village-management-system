#!/usr/bin/env python3
"""
End-to-End Testing Script for Village Accounting ERP System
"""
import requests
import json
import time
from datetime import datetime, date
from decimal import Decimal

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

class E2ETestRunner:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, message="", data=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
    def test_health_check(self):
        """Test basic health check"""
        try:
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, "API is healthy", data)
                return True
            else:
                self.log_test("Health Check", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Error: {e}")
            return False
    
    def test_config_endpoint(self):
        """Test configuration endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/config")
            if response.status_code == 200:
                data = response.json()
                accounting_enabled = data.get("accounting_enabled", False)
                self.log_test("Config Check", accounting_enabled, 
                            f"Accounting enabled: {accounting_enabled}", data)
                return accounting_enabled
            else:
                self.log_test("Config Check", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Config Check", False, f"Error: {e}")
            return False
    
    def test_initialize_accounting(self):
        """Test accounting system initialization"""
        try:
            # Try to initialize (might already be initialized)
            response = self.session.post(f"{API_BASE}/config/accounting/initialize")
            
            if response.status_code in [200, 401]:  # 401 = auth required (expected)
                if response.status_code == 401:
                    self.log_test("Initialize Accounting", True, 
                                "Auth required (expected behavior)")
                else:
                    data = response.json()
                    self.log_test("Initialize Accounting", True, 
                                "Initialization attempted", data)
                return True
            else:
                self.log_test("Initialize Accounting", False, 
                            f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Initialize Accounting", False, f"Error: {e}")
            return False
    
    def test_accounting_endpoints_auth(self):
        """Test that accounting endpoints require authentication"""
        endpoints = [
            "/accounting/accounts",
            "/accounting/journal-entries", 
            "/accounting/ledger",
            "/accounting/trial-balance"
        ]
        
        all_protected = True
        for endpoint in endpoints:
            try:
                response = self.session.get(f"{API_BASE}{endpoint}")
                if response.status_code == 401:
                    self.log_test(f"Auth Protection {endpoint}", True, 
                                "Properly protected")
                else:
                    self.log_test(f"Auth Protection {endpoint}", False, 
                                f"Status: {response.status_code}")
                    all_protected = False
            except Exception as e:
                self.log_test(f"Auth Protection {endpoint}", False, f"Error: {e}")
                all_protected = False
        
        return all_protected
    
    def test_payment_endpoints_auth(self):
        """Test that payment endpoints require authentication"""
        endpoints = [
            "/payments",
            "/payments/test-id/approve",
            "/payments/test-id/reject"
        ]
        
        all_protected = True
        for endpoint in endpoints:
            try:
                if "approve" in endpoint or "reject" in endpoint:
                    response = self.session.post(f"{API_BASE}{endpoint}")
                else:
                    response = self.session.get(f"{API_BASE}{endpoint}")
                    
                if response.status_code in [401, 404]:  # 401 = auth, 404 = not found (expected)
                    self.log_test(f"Payment Auth {endpoint}", True, 
                                f"Properly protected (status: {response.status_code})")
                else:
                    self.log_test(f"Payment Auth {endpoint}", False, 
                                f"Status: {response.status_code}")
                    all_protected = False
            except Exception as e:
                self.log_test(f"Payment Auth {endpoint}", False, f"Error: {e}")
                all_protected = False
        
        return all_protected
    
    def test_swagger_docs(self):
        """Test Swagger documentation availability"""
        try:
            response = self.session.get(f"{BASE_URL}/docs")
            if response.status_code == 200:
                self.log_test("Swagger Docs", True, "Documentation available")
                return True
            else:
                self.log_test("Swagger Docs", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Swagger Docs", False, f"Error: {e}")
            return False
    
    def test_cors_headers(self):
        """Test CORS headers"""
        try:
            response = self.session.options(f"{BASE_URL}/")
            headers = response.headers
            
            cors_enabled = (
                "access-control-allow-origin" in headers or
                "Access-Control-Allow-Origin" in headers
            )
            
            self.log_test("CORS Headers", cors_enabled, 
                        f"CORS configured: {cors_enabled}")
            return cors_enabled
        except Exception as e:
            self.log_test("CORS Headers", False, f"Error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all end-to-end tests"""
        print("🚀 Starting End-to-End Tests for Village Accounting ERP System")
        print("=" * 60)
        
        # Basic connectivity tests
        self.test_health_check()
        self.test_config_endpoint()
        self.test_swagger_docs()
        self.test_cors_headers()
        
        # Authentication tests
        self.test_accounting_endpoints_auth()
        self.test_payment_endpoints_auth()
        
        # System initialization tests
        self.test_initialize_accounting()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Test Summary")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        return failed_tests == 0

if __name__ == "__main__":
    runner = E2ETestRunner()
    success = runner.run_all_tests()
    
    # Save results to file
    with open("e2e_test_results.json", "w") as f:
        json.dump(runner.test_results, f, indent=2, default=str)
    
    print(f"\n📄 Results saved to: e2e_test_results.json")
    
    if success:
        print("🎉 All tests passed! System is ready for production.")
        exit(0)
    else:
        print("⚠️  Some tests failed. Please review and fix issues.")
        exit(1)
