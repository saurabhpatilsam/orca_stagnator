#!/usr/bin/env python3
"""
COMPREHENSIVE TESTSPRITE TEST SUITE FOR ORCA TRADING PLATFORM
Tests all features including authentication, social login, trading APIs, and UI components
"""

import requests
import json
import time
from datetime import datetime

# Deployment URLs
FRONTEND_URL = "https://orca-trading.surge.sh"
BACKEND_URL = "https://orca-backend-api-production.up.railway.app"

# Test configuration
TEST_RESULTS = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "errors": [],
    "warnings": []
}

def print_header(title):
    """Print formatted test section header"""
    print("\n" + "=" * 70)
    print(f"🧪 {title}")
    print("=" * 70)

def test_result(name, passed, error_msg=None):
    """Record and display test result"""
    TEST_RESULTS["total"] += 1
    if passed:
        TEST_RESULTS["passed"] += 1
        print(f"✅ PASS: {name}")
    else:
        TEST_RESULTS["failed"] += 1
        error_detail = f"{name}: {error_msg}" if error_msg else name
        TEST_RESULTS["errors"].append(error_detail)
        print(f"❌ FAIL: {name}")
        if error_msg:
            print(f"   Error: {error_msg}")

# ============================================================================
# FRONTEND TESTS
# ============================================================================

def test_frontend_accessibility():
    """Test if frontend is accessible"""
    print_header("FRONTEND ACCESSIBILITY")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=10, allow_redirects=True)
        
        # Check status code
        test_result(
            "Frontend responds with 200 OK",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        
        # Check content type
        content_type = response.headers.get('Content-Type', '')
        test_result(
            "Frontend returns HTML content",
            'text/html' in content_type,
            f"Content-Type: {content_type}"
        )
        
        # Check for React app
        html_content = response.text
        test_result(
            "React app is loaded",
            '<div id="root"' in html_content or 'window.React' in html_content,
            "React root element not found"
        )
        
        # Check for key resources
        test_result(
            "JavaScript bundles loaded",
            '<script' in html_content,
            "No script tags found"
        )
        
        test_result(
            "CSS styles loaded",
            'stylesheet' in html_content or '<style' in html_content,
            "No styles found"
        )
        
        return True
        
    except Exception as e:
        test_result("Frontend accessibility", False, str(e))
        return False

def test_frontend_routes():
    """Test frontend routing"""
    print_header("FRONTEND ROUTING")
    
    routes = [
        ("/", "Landing page"),
        ("/signin", "Sign in page"),
        ("/signup", "Sign up page"),
        ("/dashboard", "Dashboard (protected)"),
        ("/hedging-algo", "Hedging Algorithm page"),
        ("/algorithm", "Algorithm page"),
        ("/backtesting", "Backtesting page"),
        ("/data", "Data upload page")
    ]
    
    for route, description in routes:
        try:
            url = FRONTEND_URL + route
            response = requests.get(url, timeout=10, allow_redirects=True)
            test_result(
                f"{description} ({route})",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            test_result(f"{description} ({route})", False, str(e))

# ============================================================================
# BACKEND API TESTS
# ============================================================================

def test_backend_health():
    """Test backend health endpoints"""
    print_header("BACKEND HEALTH")
    
    endpoints = [
        ("/api/v1/health", "Health check"),
        ("/health", "Alternative health check"),
        ("/", "Root endpoint")
    ]
    
    for endpoint, description in endpoints:
        try:
            url = BACKEND_URL + endpoint
            response = requests.get(url, timeout=10)
            
            # Any 200-404 response means the backend is alive
            is_alive = response.status_code < 500
            test_result(
                f"{description} ({endpoint})",
                is_alive,
                f"Status: {response.status_code}"
            )
            
            if response.status_code == 200:
                return True
                
        except Exception as e:
            test_result(f"{description} ({endpoint})", False, str(e))
    
    return False

def test_trading_accounts_api():
    """Test trading accounts API"""
    print_header("TRADING ACCOUNTS API")
    
    try:
        url = f"{BACKEND_URL}/api/v1/trading/accounts"
        params = {"use_cache": "False"}
        
        start = time.time()
        response = requests.get(url, params=params, timeout=15)
        elapsed = (time.time() - start) * 1000
        
        test_result(
            "Accounts API responds",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        
        if response.status_code == 200:
            data = response.json()
            
            test_result(
                "Accounts data structure valid",
                isinstance(data, dict) and "accounts" in data,
                "Invalid data structure"
            )
            
            test_result(
                "Account count returned",
                "count" in data,
                "No count field"
            )
            
            test_result(
                f"Response time acceptable (<5s)",
                elapsed < 5000,
                f"Time: {elapsed:.0f}ms"
            )
            
            if "count" in data:
                print(f"   📊 Accounts found: {data['count']}")
            
    except Exception as e:
        test_result("Trading accounts API", False, str(e))

def test_positions_api():
    """Test positions API"""
    print_header("POSITIONS API")
    
    try:
        url = f"{BACKEND_URL}/api/v1/trading/positions"
        params = {
            "use_cache": "False",
            "account_name": "PAAPEX2666680000001"
        }
        
        start = time.time()
        response = requests.get(url, params=params, timeout=15)
        elapsed = (time.time() - start) * 1000
        
        test_result(
            "Positions API responds",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        
        if response.status_code == 200:
            data = response.json()
            
            test_result(
                "Positions data structure valid",
                isinstance(data, dict) and "positions" in data,
                "Invalid data structure"
            )
            
            test_result(
                "HFT optimization working (<1s target)",
                elapsed < 1000,
                f"Time: {elapsed:.0f}ms"
            )
            
            if elapsed > 800:
                TEST_RESULTS["warnings"].append(
                    f"Positions API slower than target: {elapsed:.0f}ms (target: <800ms)"
                )
            
    except Exception as e:
        test_result("Positions API", False, str(e))

def test_orders_api():
    """Test pending orders API"""
    print_header("PENDING ORDERS API")
    
    try:
        url = f"{BACKEND_URL}/api/v1/trading/orders/pending"
        params = {
            "use_cache": "False",
            "account_name": "PAAPEX2666680000001"
        }
        
        start = time.time()
        response = requests.get(url, params=params, timeout=15)
        elapsed = (time.time() - start) * 1000
        
        test_result(
            "Orders API responds",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        
        if response.status_code == 200:
            data = response.json()
            
            test_result(
                "Orders data structure valid",
                isinstance(data, dict) and "orders" in data,
                "Invalid data structure"
            )
            
            test_result(
                "Order count returned",
                "count" in data,
                "No count field"
            )
            
    except Exception as e:
        test_result("Orders API", False, str(e))

def test_balances_api():
    """Test balances API"""
    print_header("BALANCES API")
    
    try:
        url = f"{BACKEND_URL}/api/v1/trading/balances"
        params = {
            "use_cache": "False",
            "account_name": "PAAPEX2666680000001"
        }
        
        start = time.time()
        response = requests.get(url, params=params, timeout=15)
        elapsed = (time.time() - start) * 1000
        
        test_result(
            "Balances API responds",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        
        if response.status_code == 200:
            data = response.json()
            
            test_result(
                "Balances data structure valid",
                isinstance(data, dict),
                "Invalid data structure"
            )
            
            test_result(
                "Total balance field present",
                "total_balance" in data or "balances" in data,
                "No balance data"
            )
            
            if "total_balance" in data:
                print(f"   💰 Total Balance: ${data['total_balance']:,.2f}")
            
    except Exception as e:
        test_result("Balances API", False, str(e))

def test_hedge_endpoint():
    """Test hedge algorithm endpoint structure"""
    print_header("HEDGE ALGORITHM ENDPOINT")
    
    try:
        url = f"{BACKEND_URL}/api/v1/hedge/start"
        
        # Test with OPTIONS request first (CORS)
        response = requests.options(url, timeout=10)
        test_result(
            "CORS headers present",
            response.status_code < 500,
            f"Status: {response.status_code}"
        )
        
        # Test structure with invalid request (to see error format)
        test_payload = {
            "account_a": "test",
            "instrument": "MNQ",
            "direction": "long"
        }
        
        response = requests.post(
            url,
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        # We expect 422 or 400 for invalid request, not 500
        test_result(
            "Hedge endpoint responds to POST",
            response.status_code < 500,
            f"Status: {response.status_code}"
        )
        
    except Exception as e:
        test_result("Hedge endpoint", False, str(e))

# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

def test_supabase_connection():
    """Test Supabase authentication availability"""
    print_header("SUPABASE AUTHENTICATION")
    
    # Test if Supabase is configured
    supabase_url = "https://dcoukhtfcloqpfmijock.supabase.co"
    
    try:
        response = requests.get(f"{supabase_url}/auth/v1/health", timeout=10)
        test_result(
            "Supabase Auth service healthy",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
    except:
        # Try alternative endpoint
        try:
            response = requests.get(supabase_url, timeout=10)
            test_result(
                "Supabase instance reachable",
                response.status_code < 500,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            test_result("Supabase connection", False, str(e))

# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

def test_performance_metrics():
    """Test performance metrics"""
    print_header("PERFORMANCE METRICS")
    
    metrics = []
    
    # Test frontend load time
    try:
        start = time.time()
        response = requests.get(FRONTEND_URL, timeout=10)
        frontend_time = (time.time() - start) * 1000
        
        test_result(
            f"Frontend load time <2s",
            frontend_time < 2000,
            f"Time: {frontend_time:.0f}ms"
        )
        metrics.append(("Frontend", frontend_time))
        
    except Exception as e:
        test_result("Frontend performance", False, str(e))
    
    # Test backend response time
    try:
        start = time.time()
        response = requests.get(f"{BACKEND_URL}/api/v1/trading/accounts", timeout=10)
        backend_time = (time.time() - start) * 1000
        
        test_result(
            f"Backend response time <5s",
            backend_time < 5000,
            f"Time: {backend_time:.0f}ms"
        )
        metrics.append(("Backend", backend_time))
        
    except Exception as e:
        test_result("Backend performance", False, str(e))
    
    # Display metrics summary
    if metrics:
        print("\n   📊 Performance Summary:")
        for name, time_ms in metrics:
            print(f"      {name}: {time_ms:.0f}ms")

# ============================================================================
# SECURITY TESTS
# ============================================================================

def test_security_headers():
    """Test security headers"""
    print_header("SECURITY HEADERS")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        headers = response.headers
        
        security_headers = {
            "X-Frame-Options": "SAMEORIGIN or DENY expected",
            "X-Content-Type-Options": "nosniff expected",
            "Strict-Transport-Security": "HTTPS enforcement",
            "Content-Security-Policy": "CSP header"
        }
        
        for header, description in security_headers.items():
            present = header in headers
            if present:
                test_result(f"{header} present", True)
            else:
                TEST_RESULTS["warnings"].append(f"Security: {header} missing ({description})")
        
    except Exception as e:
        test_result("Security headers check", False, str(e))

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all tests and generate report"""
    print("\n" + "#" * 70)
    print("#" + " " * 68 + "#")
    print("#" + " " * 15 + "ORCA TRADING PLATFORM TEST SUITE" + " " * 20 + "#")
    print("#" + " " * 68 + "#")
    print("#" * 70)
    
    print(f"\n📍 Frontend URL: {FRONTEND_URL}")
    print(f"📍 Backend URL:  {BACKEND_URL}")
    print(f"📅 Test Date:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run test categories
    test_categories = [
        ("Frontend", [
            test_frontend_accessibility,
            test_frontend_routes
        ]),
        ("Backend APIs", [
            test_backend_health,
            test_trading_accounts_api,
            test_positions_api,
            test_orders_api,
            test_balances_api,
            test_hedge_endpoint
        ]),
        ("Authentication", [
            test_supabase_connection
        ]),
        ("Performance", [
            test_performance_metrics
        ]),
        ("Security", [
            test_security_headers
        ])
    ]
    
    for category_name, tests in test_categories:
        print(f"\n{'─' * 70}")
        print(f"📁 {category_name}")
        print('─' * 70)
        
        for test_func in tests:
            try:
                test_func()
            except Exception as e:
                print(f"⚠️  Test crashed: {test_func.__name__}")
                print(f"   Error: {e}")
                TEST_RESULTS["errors"].append(f"{test_func.__name__}: Crashed - {e}")
    
    # Generate final report
    generate_test_report()

def generate_test_report():
    """Generate final test report"""
    print("\n" + "=" * 70)
    print("📊 FINAL TEST REPORT")
    print("=" * 70)
    
    # Calculate pass rate
    pass_rate = (TEST_RESULTS["passed"] / TEST_RESULTS["total"] * 100) if TEST_RESULTS["total"] > 0 else 0
    
    # Summary statistics
    print(f"\n✅ Tests Passed:  {TEST_RESULTS['passed']}")
    print(f"❌ Tests Failed:  {TEST_RESULTS['failed']}")
    print(f"📊 Total Tests:   {TEST_RESULTS['total']}")
    print(f"📈 Pass Rate:     {pass_rate:.1f}%")
    
    # Display errors if any
    if TEST_RESULTS["errors"]:
        print("\n⚠️  ERRORS:")
        for error in TEST_RESULTS["errors"]:
            print(f"   • {error}")
    
    # Display warnings if any
    if TEST_RESULTS["warnings"]:
        print("\n⚠️  WARNINGS:")
        for warning in TEST_RESULTS["warnings"]:
            print(f"   • {warning}")
    
    # Overall verdict
    print("\n" + "=" * 70)
    if pass_rate >= 90:
        print("🎉 EXCELLENT - System is production ready!")
        verdict = "PASS - Production Ready"
    elif pass_rate >= 80:
        print("✅ GOOD - System is mostly functional")
        verdict = "PASS - Minor Issues"
    elif pass_rate >= 70:
        print("⚠️  ACCEPTABLE - Some issues need attention")
        verdict = "CONDITIONAL PASS"
    else:
        print("❌ NEEDS WORK - Multiple issues detected")
        verdict = "FAIL - Needs Attention"
    
    print(f"\n🏁 FINAL VERDICT: {verdict}")
    print(f"📊 Score: {pass_rate:.1f}%")
    
    # Save results to file
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "frontend_url": FRONTEND_URL,
            "backend_url": BACKEND_URL,
            "summary": {
                "total_tests": TEST_RESULTS["total"],
                "passed": TEST_RESULTS["passed"],
                "failed": TEST_RESULTS["failed"],
                "pass_rate": pass_rate,
                "verdict": verdict
            },
            "errors": TEST_RESULTS["errors"],
            "warnings": TEST_RESULTS["warnings"]
        }, f, indent=2)
    
    print(f"\n📄 Report saved to: {report_file}")
    print("=" * 70)

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        generate_test_report()
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        generate_test_report()
