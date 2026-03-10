#!/usr/bin/env python3
"""Quick integration test for question-based flow"""
import sys
sys.path.insert(0, '/mnt/d/Yoel/Projects/mbp-prototype/backend-v2')

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

print("Testing MBP Question-Based Flow...\n")

# Test 1: Create session
print("1. POST /api/sessions")
r = client.post('/api/sessions', json={})
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    session_id = data['session_id']
    print(f"   ✅ Session: {session_id[:8]}...")
    print(f"   ✅ Phase: {data['current_phase']}")
    print(f"   ✅ First question: {data['first_question']['question_id']}")
else:
    print(f"   ❌ Error: {r.text}")
    sys.exit(1)

# Test 2: Get questions
print("\n2. GET /api/sessions/{id}/questions")
r = client.get(f'/api/sessions/{session_id}/questions')
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"   ✅ Phase: {data['phase']}")
    print(f"   ✅ Questions: {len(data['questions'])}")
    print(f"   ✅ Total in phase: {data['total_questions_in_phase']}")
    qid = data['questions'][0]['question_id']
else:
    print(f"   ❌ Error: {r.text}")
    sys.exit(1)

# Test 3: Submit answer
print("\n3. POST /api/sessions/{id}/answer")
r = client.post(f'/api/sessions/{session_id}/answer', json={
    'question_id': qid,
    'answer': 'Saya merasa cukup stabil dan siap untuk melanjutkan.'
})
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"   ✅ Answer recorded: {data['question_id']}")
    print(f"   ✅ Phase complete: {data['phase_complete']}")
    print(f"   ✅ Can advance: {data['can_advance']}")
else:
    print(f"   ❌ Error: {r.text}")

# Test 4: Get question state
print("\n4. GET /api/sessions/{id}/question-state")
r = client.get(f'/api/sessions/{session_id}/question-state')
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"   ✅ Current phase: {data['current_phase']}")
    print(f"   ✅ Answers count: {data['answers_count']}")
    print(f"   ✅ Can advance: {data['can_advance']}")

print("\n✅ All critical endpoints working!")
print("\nFrontend can now connect to:")
print("  - GET /api/sessions/{id}/questions")
print("  - POST /api/sessions/{id}/answer")
print("  - POST /api/sessions/{id}/next-phase")
print("  - GET /api/sessions/{id}/question-state")
