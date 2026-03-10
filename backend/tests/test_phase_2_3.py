#!/usr/bin/env python3
"""Test Phase 2 and 3 to find ASGI error"""
import sys
sys.path.insert(0, '/mnt/d/Yoel/Projects/mbp-prototype/backend-v2')

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

print("=== Testing Phase 2 & 3 ===\n")

# Create and complete Phase 0 & 1
print("1. Setup: Create session and complete Phase 0 & 1...")
r = client.post('/api/sessions', json={})
session_id = r.json()['session_id']

# Answer Phase 0 (7 questions)
for i in range(7):
    client.post(f'/api/sessions/{session_id}/answer', json={
        'question_id': f'q0.{i+1}',
        'answer': f'Jawaban {i+1}'
    })

# Advance to Phase 1
client.post(f'/api/sessions/{session_id}/next-phase', json={'confirm': True})

# Answer Phase 1 (11 questions)
for i in range(11):
    client.post(f'/api/sessions/{session_id}/answer', json={
        'question_id': f'q1.{i+1}',
        'answer': f'Jawaban {i+1}'
    })

# Advance to Phase 2
print("\n2. Advancing to Phase 2 (Probing)...")
r = client.post(f'/api/sessions/{session_id}/next-phase', json={'confirm': True})
print(f"   Status: {r.status_code}")
if r.status_code != 200:
    print(f"   ERROR: {r.text}")
    sys.exit(1)
print(f"   Phase: {r.json().get('new_phase')}")

# Get Phase 2 questions
print("\n3. Getting Phase 2 questions...")
r = client.get(f'/api/sessions/{session_id}/questions')
print(f"   Status: {r.status_code}")
if r.status_code != 200:
    print(f"   ERROR: {r.text}")
    sys.exit(1)

data = r.json()
print(f"   Phase: {data.get('phase')}")
print(f"   Total questions: {len(data.get('questions', []))}")
if data.get('question'):
    print(f"   Current question: {data['question']['text'][:60]}...")

# Answer all Phase 2 questions
print("\n4. Answering Phase 2 questions...")
questions = data.get('questions', [])
for q in questions:
    qid = q.get('id') or q.get('question_id')
    r = client.post(f'/api/sessions/{session_id}/answer', json={
        'question_id': qid,
        'answer': 'Jawaban untuk pertanyaan adaptive'
    })
    if r.status_code != 200:
        print(f"   ERROR answering {qid}: {r.status_code}")
        print(f"   {r.text}")
        sys.exit(1)
    print(f"   ✓ {qid}")

# Advance to Phase 3
print("\n5. Advancing to Phase 3 (Mining)...")
r = client.post(f'/api/sessions/{session_id}/next-phase', json={'confirm': True})
print(f"   Status: {r.status_code}")
if r.status_code != 200:
    print(f"   ERROR: {r.text}")
    sys.exit(1)
print(f"   Phase: {r.json().get('new_phase')}")

# Get Phase 3 questions
print("\n6. Getting Phase 3 questions...")
r = client.get(f'/api/sessions/{session_id}/questions')
print(f"   Status: {r.status_code}")
if r.status_code != 200:
    print(f"   ERROR: {r.text}")
    sys.exit(1)

data = r.json()
print(f"   Phase: {data.get('phase')}")
print(f"   Total questions: {len(data.get('questions', []))}")

print("\n✅ SUCCESS: Phase 2 & 3 working!")
