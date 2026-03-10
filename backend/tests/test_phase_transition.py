#!/usr/bin/env python3
"""Test the next-phase endpoint to reproduce the error"""
import sys
sys.path.insert(0, '/mnt/d/Yoel/Projects/mbp-prototype/backend-v2')

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

print("=== Testing Next-Phase Transition ===\n")

# 1. Create session
print("1. Creating session...")
r = client.post('/api/sessions', json={})
data = r.json()
session_id = data['session_id']
print(f"   Session: {session_id}")

# 2. Answer all Phase 0 questions
print("\n2. Answering Phase 0 questions...")
phase_0_questions = [
    ("q0.1", "Ya, saya merasa stabil."),
    ("q0.2", "Saya punya keluarga yang bisa dihubungi."),
    ("q0.3", "Ya, saya setuju untuk melanjutkan."),
    ("q0.4", "Lingkungan saya penuh ekspektasi tinggi."),
    ("q0.5", "Keluarga saya jarang menunjukkan emosi."),
    ("q0.6", "Saya belajar untuk selalu waspada."),
    ("q0.7", "Budaya kami menghargai kerja keras.")
]

for qid, answer in phase_0_questions:
    r = client.post(f'/api/sessions/{session_id}/answer', json={
        'question_id': qid,
        'answer': answer
    })
    if r.status_code != 200:
        print(f"   ERROR answering {qid}: {r.status_code}")
        print(f"   {r.text}")
    else:
        print(f"   ✓ {qid}")

# 3. Try to advance to Phase 1
print("\n3. Advancing to Phase 1 (Core)...")
r = client.post(f'/api/sessions/{session_id}/next-phase', json={'confirm': True})
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"   New Phase: {data.get('new_phase')}")
else:
    print(f"   Error: {r.text}")
    sys.exit(1)

# 4. Answer all Phase 1 questions (11 questions)
print("\n4. Answering Phase 1 questions...")
r = client.get(f'/api/sessions/{session_id}/questions')
q_data = r.json()
questions = q_data.get('questions', [])
print(f"   Total Phase 1 questions: {len(questions)}")

for q in questions[:11]:  # Answer first 11
    qid = q['id'] if 'id' in q else q['question_id']
    r = client.post(f'/api/sessions/{session_id}/answer', json={
        'question_id': qid,
        'answer': f'Jawaban untuk pertanyaan tentang {q["dimensions"][0] if q["dimensions"] else "umum"}'
    })
    if r.status_code != 200:
        print(f"   ERROR answering {qid}: {r.status_code}")
        print(f"   {r.text}")
    else:
        print(f"   ✓ {qid}")

# 5. Try to advance to Phase 2 (Probing/Adaptive)
print("\n5. Advancing to Phase 2 (Probing/Adaptive)...")
r = client.post(f'/api/sessions/{session_id}/next-phase', json={'confirm': True})
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"   New Phase: {data.get('new_phase')}")
    print(f"   Phase Number: {data.get('phase_number')}")
    if data.get('first_question'):
        print(f"   First Question: {data['first_question']['text'][:60]}...")
    print("\n✅ SUCCESS: Phase 2 transition works!")
else:
    print(f"   ❌ ERROR: {r.status_code}")
    print(f"   {r.text}")
