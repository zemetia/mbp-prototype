#!/usr/bin/env python3
"""
MBP Backend v2.0 - Complete API Endpoint Testing Script
Tests all endpoints and documents results
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"
API_URL = "http://localhost:8000/api"

# Test results storage
test_results = []
errors_found = []

def log_test(name, status, details="", error=None):
    """Log test result"""
    result = {
        "name": name,
        "status": status,
        "details": details,
        "error": error,
        "timestamp": datetime.now().isoformat()
    }
    test_results.append(result)
    
    icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"\n{icon} {name}")
    if details:
        print(f"   Details: {details}")
    if error:
        print(f"   Error: {error}")
        errors_found.append({"test": name, "error": error})

def test_health_endpoints():
    """Test health check endpoints"""
    print("\n" + "="*60)
    print("1. HEALTH CHECK ENDPOINTS")
    print("="*60)
    
    # Test GET /health
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            log_test("GET /health", "PASS", f"Status: {data.get('status')}, Version: {data.get('version')}")
        else:
            log_test("GET /health", "FAIL", f"Status code: {response.status_code}")
    except Exception as e:
        log_test("GET /health", "FAIL", error=str(e))
    
    # Test GET /api/health
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            log_test("GET /api/health", "PASS", f"Status: {data.get('status')}, Agents: {data.get('agents_count')}")
        else:
            log_test("GET /api/health", "FAIL", f"Status code: {response.status_code}")
    except Exception as e:
        log_test("GET /api/health", "FAIL", error=str(e))

def test_personal_data_endpoints():
    """Test personal data endpoints"""
    print("\n" + "="*60)
    print("2. PERSONAL DATA ENDPOINTS")
    print("="*60)
    
    personal_data_id = None
    
    # Test POST /api/personal-data - Create
    try:
        payload = {
            "nama": "Budi Santoso",
            "tanggal_lahir": "15/05/1990",
            "tempat_lahir": "Jakarta",
            "agama": "Islam"
        }
        response = requests.post(f"{API_URL}/personal-data", json=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            personal_data_id = data.get("personal_data_id")
            log_test("POST /api/personal-data", "PASS", f"ID: {personal_data_id}")
        else:
            log_test("POST /api/personal-data", "FAIL", f"Status: {response.status_code}, Body: {response.text}")
    except Exception as e:
        log_test("POST /api/personal-data", "FAIL", error=str(e))
    
    # Test GET /api/personal-data/{id} - Retrieve
    if personal_data_id:
        try:
            response = requests.get(f"{API_URL}/personal-data/{personal_data_id}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                log_test("GET /api/personal-data/{id}", "PASS", f"Name: {data.get('nama')}")
            else:
                log_test("GET /api/personal-data/{id}", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            log_test("GET /api/personal-data/{id}", "FAIL", error=str(e))
        
        # Test GET with invalid ID
        try:
            response = requests.get(f"{API_URL}/personal-data/invalid-id", timeout=5)
            if response.status_code == 404:
                log_test("GET /api/personal-data/{invalid-id}", "PASS", "Correctly returns 404")
            else:
                log_test("GET /api/personal-data/{invalid-id}", "FAIL", f"Expected 404, got {response.status_code}")
        except Exception as e:
            log_test("GET /api/personal-data/{invalid-id}", "FAIL", error=str(e))
    
    return personal_data_id

def test_session_endpoints(personal_data_id):
    """Test session endpoints"""
    print("\n" + "="*60)
    print("3. SESSION ENDPOINTS")
    print("="*60)
    
    session_id = None
    
    # Test POST /api/sessions - Create session
    try:
        payload = {"user_id": "test_user_123", "metadata": {"source": "api_test"}}
        response = requests.post(f"{API_URL}/sessions", json=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            session_id = data.get("session_id")
            log_test("POST /api/sessions", "PASS", f"ID: {session_id[:8]}...")
        else:
            log_test("POST /api/sessions", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("POST /api/sessions", "FAIL", error=str(e))
    
    # Test POST /api/sessions/with-personal-data
    if personal_data_id:
        try:
            payload = {"personal_data_id": personal_data_id, "metadata": {"test": True}}
            response = requests.post(f"{API_URL}/sessions/with-personal-data", json=payload, timeout=5)
            if response.status_code == 200:
                data = response.json()
                linked_session_id = data.get("session_id")
                log_test("POST /api/sessions/with-personal-data", "PASS", f"ID: {linked_session_id[:8]}...")
            else:
                log_test("POST /api/sessions/with-personal-data", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            log_test("POST /api/sessions/with-personal-data", "FAIL", error=str(e))
        
        # Test with invalid personal_data_id
        try:
            payload = {"personal_data_id": "invalid-id"}
            response = requests.post(f"{API_URL}/sessions/with-personal-data", json=payload, timeout=5)
            if response.status_code == 404:
                log_test("POST /api/sessions/with-personal-data (invalid)", "PASS", "Correctly returns 404")
            else:
                log_test("POST /api/sessions/with-personal-data (invalid)", "FAIL", f"Expected 404, got {response.status_code}")
        except Exception as e:
            log_test("POST /api/sessions/with-personal-data (invalid)", "FAIL", error=str(e))
    
    # Test GET /api/sessions/{id}
    if session_id:
        try:
            response = requests.get(f"{API_URL}/sessions/{session_id}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                log_test("GET /api/sessions/{id}", "PASS", f"Phase: {data.get('phase')}")
            else:
                log_test("GET /api/sessions/{id}", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            log_test("GET /api/sessions/{id}", "FAIL", error=str(e))
        
        # Test GET with invalid ID
        try:
            response = requests.get(f"{API_URL}/sessions/invalid-id", timeout=5)
            if response.status_code == 404:
                log_test("GET /api/sessions/{invalid-id}", "PASS", "Correctly returns 404")
            else:
                log_test("GET /api/sessions/{invalid-id}", "FAIL", f"Expected 404, got {response.status_code}")
        except Exception as e:
            log_test("GET /api/sessions/{invalid-id}", "FAIL", error=str(e))
    
    # Test POST /api/sessions/{id}/respond
    if session_id:
        try:
            payload = {"message": "Saya sering merasa cemas dalam situasi sosial", "client_timestamp": datetime.now().isoformat()}
            response = requests.post(f"{API_URL}/sessions/{session_id}/respond", json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                log_test("POST /api/sessions/{id}/respond", "PASS", f"Phase: {data.get('phase')}, Iteration: {data.get('iteration_count')}")
            else:
                log_test("POST /api/sessions/{id}/respond", "FAIL", f"Status: {response.status_code}, Body: {response.text[:200]}")
        except Exception as e:
            log_test("POST /api/sessions/{id}/respond", "FAIL", error=str(e))
    
    # Test GET /api/sessions/{id}/profile (expect 400 since not complete)
    if session_id:
        try:
            response = requests.get(f"{API_URL}/sessions/{session_id}/profile", timeout=5)
            if response.status_code == 400:
                log_test("GET /api/sessions/{id}/profile (incomplete)", "PASS", "Correctly returns 400 for incomplete session")
            elif response.status_code == 200:
                log_test("GET /api/sessions/{id}/profile", "PASS", "Profile available")
            else:
                log_test("GET /api/sessions/{id}/profile", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            log_test("GET /api/sessions/{id}/profile", "FAIL", error=str(e))
    
    return session_id

def test_analyses_endpoints(personal_data_id, session_id):
    """Test analyses endpoints"""
    print("\n" + "="*60)
    print("4. ANALYSES ENDPOINTS")
    print("="*60)
    
    analysis_id = None
    
    # Test POST /api/analyses - Save analysis
    if personal_data_id and session_id:
        try:
            payload = {
                "personal_data_id": personal_data_id,
                "session_id": session_id,
                "final_profile": {
                    "core_structure": {
                        "core_fear": {"primary": {"type": "abandonment"}},
                        "core_drive": {"primary": {"type": "achievement"}}
                    }
                },
                "matrix_12d": {"AB": {"score": 75, "confidence": 80}},
                "executive_summary": "Test analysis summary",
                "core_insights": ["Insight 1", "Insight 2"],
                "tensions": [{"type": "approach_avoidance", "strength": 0.8}]
            }
            response = requests.post(f"{API_URL}/analyses", json=payload, timeout=5)
            if response.status_code == 200:
                data = response.json()
                analysis_id = data.get("analysis_id")
                log_test("POST /api/analyses", "PASS", f"ID: {analysis_id[:8]}...")
            else:
                log_test("POST /api/analyses", "FAIL", f"Status: {response.status_code}, Body: {response.text[:200]}")
        except Exception as e:
            log_test("POST /api/analyses", "FAIL", error=str(e))
        
        # Test with invalid personal_data_id
        try:
            payload = {
                "personal_data_id": "invalid-id",
                "session_id": session_id,
                "final_profile": {"test": "data"}
            }
            response = requests.post(f"{API_URL}/analyses", json=payload, timeout=5)
            if response.status_code == 404:
                log_test("POST /api/analyses (invalid personal_data)", "PASS", "Correctly returns 404")
            else:
                log_test("POST /api/analyses (invalid personal_data)", "FAIL", f"Expected 404, got {response.status_code}")
        except Exception as e:
            log_test("POST /api/analyses (invalid personal_data)", "FAIL", error=str(e))
        
        # Test with invalid session_id
        try:
            payload = {
                "personal_data_id": personal_data_id,
                "session_id": "invalid-id",
                "final_profile": {"test": "data"}
            }
            response = requests.post(f"{API_URL}/analyses", json=payload, timeout=5)
            if response.status_code == 404:
                log_test("POST /api/analyses (invalid session)", "PASS", "Correctly returns 404")
            else:
                log_test("POST /api/analyses (invalid session)", "FAIL", f"Expected 404, got {response.status_code}")
        except Exception as e:
            log_test("POST /api/analyses (invalid session)", "FAIL", error=str(e))
    
    # Test GET /api/analyses - List all
    try:
        response = requests.get(f"{API_URL}/analyses", timeout=5)
        if response.status_code == 200:
            data = response.json()
            log_test("GET /api/analyses", "PASS", f"Total analyses: {data.get('total')}")
        else:
            log_test("GET /api/analyses", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("GET /api/analyses", "FAIL", error=str(e))
    
    # Test GET /api/analyses?personal_data_id=... - Filtered list
    if personal_data_id:
        try:
            response = requests.get(f"{API_URL}/analyses?personal_data_id={personal_data_id}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                log_test("GET /api/analyses?personal_data_id=...", "PASS", f"Filtered count: {data.get('total')}")
            else:
                log_test("GET /api/analyses?personal_data_id=...", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            log_test("GET /api/analyses?personal_data_id=...", "FAIL", error=str(e))
    
    # Test GET /api/analyses/{id}
    if analysis_id:
        try:
            response = requests.get(f"{API_URL}/analyses/{analysis_id}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                log_test("GET /api/analyses/{id}", "PASS", f"Name: {data.get('nama')}")
            else:
                log_test("GET /api/analyses/{id}", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            log_test("GET /api/analyses/{id}", "FAIL", error=str(e))
        
        # Test with invalid ID
        try:
            response = requests.get(f"{API_URL}/analyses/invalid-id", timeout=5)
            if response.status_code == 404:
                log_test("GET /api/analyses/{invalid-id}", "PASS", "Correctly returns 404")
            else:
                log_test("GET /api/analyses/{invalid-id}", "FAIL", f"Expected 404, got {response.status_code}")
        except Exception as e:
            log_test("GET /api/analyses/{invalid-id}", "FAIL", error=str(e))
    
    return analysis_id

def test_validation():
    """Test input validation"""
    print("\n" + "="*60)
    print("5. INPUT VALIDATION TESTS")
    print("="*60)
    
    # Test empty message
    try:
        # First create a session
        response = requests.post(f"{API_URL}/sessions", json={}, timeout=5)
        session_id = response.json().get("session_id")
        
        # Test empty message
        response = requests.post(f"{API_URL}/sessions/{session_id}/respond", json={"message": ""}, timeout=5)
        if response.status_code == 422:
            log_test("Validation: Empty message", "PASS", "Correctly returns 422")
        else:
            log_test("Validation: Empty message", "FAIL", f"Expected 422, got {response.status_code}")
    except Exception as e:
        log_test("Validation: Empty message", "FAIL", error=str(e))
    
    # Test missing required fields in personal data
    try:
        response = requests.post(f"{API_URL}/personal-data", json={"nama": "Test"}, timeout=5)
        if response.status_code == 422:
            log_test("Validation: Missing fields", "PASS", "Correctly returns 422 for missing fields")
        else:
            log_test("Validation: Missing fields", "FAIL", f"Expected 422, got {response.status_code}")
    except Exception as e:
        log_test("Validation: Missing fields", "FAIL", error=str(e))

def generate_report():
    """Generate final report"""
    print("\n" + "="*60)
    print("TEST SUMMARY REPORT")
    print("="*60)
    
    total = len(test_results)
    passed = len([r for r in test_results if r["status"] == "PASS"])
    failed = len([r for r in test_results if r["status"] == "FAIL"])
    
    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success Rate: {passed/total*100:.1f}%" if total > 0 else "N/A")
    
    if errors_found:
        print("\n" + "-"*60)
        print("ERRORS FOUND:")
        print("-"*60)
        for err in errors_found:
            print(f"\n🔴 {err['test']}")
            print(f"   {err['error']}")
    
    # Save report to file
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "success_rate": f"{passed/total*100:.1f}%" if total > 0 else "N/A"
        },
        "results": test_results,
        "errors": errors_found
    }
    
    with open("/mnt/d/Yoel/Projects/mbp-prototype/backend-v2/test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Full report saved to: test_report.json")
    
    return failed == 0

def main():
    print("🧪 MBP Backend v2.0 - API Endpoint Testing")
    print(f"🎯 Base URL: {BASE_URL}")
    print(f"🎯 API URL: {API_URL}")
    
    # Check server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"\n✅ Server is running - Status: {response.json().get('status')}")
    except Exception as e:
        print(f"\n❌ Server is not running: {e}")
        print("Please start the server first with: ./run.sh")
        sys.exit(1)
    
    # Run all tests
    test_health_endpoints()
    personal_data_id = test_personal_data_endpoints()
    session_id = test_session_endpoints(personal_data_id)
    test_analyses_endpoints(personal_data_id, session_id)
    test_validation()
    
    # Generate report
    success = generate_report()
    
    print("\n" + "="*60)
    if success:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️ SOME TESTS FAILED - See report above")
    print("="*60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
