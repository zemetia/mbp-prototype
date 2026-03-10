#!/usr/bin/env python3
"""Debug the questions API response"""
import sys
sys.path.insert(0, '/mnt/d/Yoel/Projects/mbp-prototype/backend-v2')

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

# Create personal data
r = client.post('/api/personal-data', json={
    'nama': 'Test User',
    'tanggal_lahir': '01/01/1990',
    'tempat_lahir': 'Jakarta',
    'agama': 'Islam'
})
pd_id = r.json()['personal_data_id']
print(f'✅ Personal data: {pd_id[:8]}...')

# Create session with personal data
r = client.post('/api/sessions/with-personal-data', json={
    'personal_data_id': pd_id
})
data = r.json()
session_id = data['session_id']
print(f'✅ Session: {session_id[:8]}...')
print(f'✅ Current phase from create: {data.get("current_phase")}')
print(f'✅ First question from create: {data.get("first_question", {}).get("id") if data.get("first_question") else "None"}')

# Get questions
r = client.get(f'/api/sessions/{session_id}/questions')
data = r.json()
print(f'\n📥 GET /questions response:')
print(f'   phase: {data.get("phase")}')
print(f'   phase_number: {data.get("phase_number")}')
print(f'   has question key: {"question" in data}')
print(f'   question value: {data.get("question")}')
print(f'   has questions key: {"questions" in data}')
print(f'   questions count: {len(data.get("questions", []))}')
print(f'   phase_complete: {data.get("phase_complete")}')
print(f'   analysis_complete: {data.get("analysis_complete")}')

if data.get('question'):
    print(f'\n✅ Current question: {data["question"]["id"]}')
    print(f'   Text: {data["question"]["text"][:50]}...')
else:
    print(f'\n❌ ERROR: No question field in response!')
    print(f'   Full response: {data}')
