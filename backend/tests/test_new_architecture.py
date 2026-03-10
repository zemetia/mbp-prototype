
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.database import engine, SessionLocal
from models.domain import Client, Base
from api.routers.sessions import router as sessions_router
from api.routers.questions import router as questions_router

# Setup simple testing app
test_app = FastAPI()
test_app.include_router(sessions_router)
test_app.include_router(questions_router)
client = TestClient(test_app)

def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Create test client
    test_client = Client(id="test_client_id_123", nama="Test User", agama="None")
    db.add(test_client)
    db.commit()
    db.close()

def teardown_db():
    Base.metadata.drop_all(bind=engine)

def test_create_and_get_session():
    setup_db()
    
    try:
        # Test 1: Create Session
        resp = client.post("/sessions/", json={"client_id": "test_client_id_123"})
        assert resp.status_code == 201, f"Failed to create session: {resp.text}"
        data = resp.json()
        assert data["status"] == "created"
        
        session_id = data["session_id"]
        
        # Test 2: Get Session
        resp2 = client.get(f"/sessions/{session_id}")
        assert resp2.status_code == 200, f"Failed to get session: {resp2.text}"
        data2 = resp2.json()
        assert data2["session_id"] == session_id
        assert data2["current_phase"] == "safety"
        
        # Test 4: Get questions for Phase 0
        resp4 = client.get(f"/sessions/{session_id}/questions")
        assert resp4.status_code == 200, f"Failed to get questions: {resp4.text}"
        data4 = resp4.json()
        assert data4["phase"] == "safety"
        assert len(data4["questions"]) > 0

        # Read first question ID
        q_id = data4["questions"][0]["id"]
        
        # Test 5: Submit an answer
        ans_payload = {"question_id": q_id, "answer": "Ini jawaban testing"}
        resp5 = client.post(f"/sessions/{session_id}/answer", json=ans_payload)
        assert resp5.status_code == 200, f"Failed to answer: {resp5.text}"
        data5 = resp5.json()
        
        # We know safety phase only has 1 question typically, 
        # but check for phase completeness automatically
        if data5["phase_complete"]:
            # Test 6: Advance Phase
            resp6 = client.post(f"/sessions/{session_id}/next-phase", json={"confirm": True})
            assert resp6.status_code == 200, f"Failed to advance phase: {resp6.text}"
            data6 = resp6.json()
            assert data6["new_phase"] == "core"

        print("\n✅ All API Integration Tests Passed! The new layered architecture is working correctly!\n")
    finally:
        teardown_db()

if __name__ == "__main__":
    test_create_and_get_session()
