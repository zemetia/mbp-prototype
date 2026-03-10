#!/usr/bin/env python3
"""Quick backend test script"""
import sys
sys.path.insert(0, '/mnt/d/Yoel/Projects/mbp-prototype/backend-v2')

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

print("Testing MBP Backend v2.0...\n")

# Test 1: Health endpoints
print("1. Testing Health Endpoints...")
r = client.get('/health')
print(f"   GET /health: {r.status_code} {r.json() if r.status_code == 200 else r.text}")

r = client.get('/api/health')
print(f"   GET /api/health: {r.status_code} {r.json() if r.status_code == 200 else r.text}")

# Test 2: Create Personal Data
print("\n2. Testing Personal Data...")
r = client.post('/api/personal-data', json={
    'nama': 'Budi Santoso',
    'tanggal_lahir': '15/03/1995',
    'tempat_lahir': 'Jakarta',
    'agama': 'Islam'
})
print(f"   POST /api/personal-data: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    personal_data_id = data.get('personal_data_id')
    print(f"   personal_data_id: {personal_data_id}")
    
    # Test 3: Get Personal Data
    r = client.get(f'/api/personal-data/{personal_data_id}')
    print(f"   GET /api/personal-data/{personal_data_id}: {r.status_code}")
    
    # Test 4: Create Session with Personal Data
    print("\n3. Testing Sessions...")
    r = client.post('/api/sessions/with-personal-data', json={
        'personal_data_id': personal_data_id
    })
    print(f"   POST /api/sessions/with-personal-data: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        session_id = data.get('session_id')
        print(f"   session_id: {session_id}")
        
        # Test 5: Get Session
        r = client.get(f'/api/sessions/{session_id}')
        print(f"   GET /api/sessions/{session_id}: {r.status_code}")
        
        # Test 6: Send Message
        print("\n4. Testing Message Response...")
        r = client.post(f'/api/sessions/{session_id}/respond', json={
            'message': 'Halo, saya ingin memahami diri saya lebih baik'
        })
        print(f"   POST /api/sessions/{session_id}/respond: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"   phase: {data.get('phase')}")
            print(f"   next_question: {data.get('next_question', 'N/A')[:50]}..." if data.get('next_question') else "   (no next_question)")
        
        # Test 7: List Analyses
        print("\n5. Testing Analyses...")
        r = client.get('/api/analyses')
        print(f"   GET /api/analyses: {r.status_code} {r.json()}")

print("\n✅ All tests completed!")
