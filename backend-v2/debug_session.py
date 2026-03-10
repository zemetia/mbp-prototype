#!/usr/bin/env python3
"""Debug session storage issue"""
import sys
sys.path.insert(0, '/mnt/d/Yoel/Projects/mbp-prototype/backend-v2')

from fastapi.testclient import TestClient
from api.main import app, sessions

client = TestClient(app)

print("=== Debug Session Storage ===\n")

# Create session
r = client.post('/api/sessions', json={})
data = r.json()
session_id = data['session_id']

print(f"1. Session created: {session_id}")
print(f"   Sessions dict keys: {list(sessions.keys())}")
print(f"   Session in dict: {session_id in sessions}")

# Check session content
if session_id in sessions:
    print(f"   Session data: {sessions[session_id]}")
else:
    print("   ERROR: Session not found in memory!")

# Try to get questions
print(f"\n2. Getting questions for {session_id}...")
r = client.get(f'/api/sessions/{session_id}/questions')
print(f"   Response status: {r.status_code}")
print(f"   Response: {r.text}")

print(f"\n3. Sessions dict after GET:")
print(f"   Keys: {list(sessions.keys())}")
print(f"   Count: {len(sessions)}")
