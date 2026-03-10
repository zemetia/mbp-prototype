#!/usr/bin/env python3
"""
MBP v2.0 - Question-Based Flow Test Script
Tests the quiz-style question flow through all phases.
"""
import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000/api"


def print_separator(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))


def test_health():
    """Test health endpoint"""
    print_separator("TEST 1: Health Check")
    try:
        resp = requests.get(f"{BASE_URL}/health")
        print(f"Status: {resp.status_code}")
        print_json(resp.json())
        return resp.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_create_session():
    """Test creating a new session"""
    print_separator("TEST 2: Create Session")
    try:
        resp = requests.post(
            f"{BASE_URL}/sessions",
            json={"metadata": {"test": True}}
        )
        print(f"Status: {resp.status_code}")
        data = resp.json()
        print_json(data)
        
        if resp.status_code == 200 and "session_id" in data:
            print(f"\n✅ Session created: {data['session_id']}")
            print(f"✅ Current phase: {data['current_phase']}")
            if data.get('first_question'):
                print(f"✅ First question ID: {data['first_question']['question_id']}")
            return data["session_id"]
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_get_questions(session_id):
    """Test getting questions for current phase"""
    print_separator(f"TEST 3: Get Questions (Session: {session_id[:8]}...)")
    try:
        resp = requests.get(f"{BASE_URL}/sessions/{session_id}/questions")
        print(f"Status: {resp.status_code}")
        data = resp.json()
        print_json(data)
        
        if resp.status_code == 200:
            print(f"\n✅ Phase: {data['phase']}")
            print(f"✅ Total questions: {data['total_questions_in_phase']}")
            print(f"✅ Progress: {data['progress_percentage']}%")
            return data["questions"]
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_submit_answer(session_id, question_id, answer_text):
    """Test submitting an answer"""
    print_separator(f"TEST 4: Submit Answer (Q: {question_id})")
    try:
        resp = requests.post(
            f"{BASE_URL}/sessions/{session_id}/answer",
            json={"question_id": question_id, "answer": answer_text}
        )
        print(f"Status: {resp.status_code}")
        data = resp.json()
        print_json(data)
        
        if resp.status_code == 200:
            print(f"\n✅ Answer submitted for: {data['question_id']}")
            print(f"✅ Phase complete: {data['phase_complete']}")
            print(f"✅ Can advance: {data['can_advance']}")
            if data.get('next_question'):
                print(f"✅ Next question: {data['next_question']['question_id']}")
            return data
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_get_question_state(session_id):
    """Test getting detailed question state"""
    print_separator(f"TEST 5: Get Question State (Session: {session_id[:8]}...)")
    try:
        resp = requests.get(f"{BASE_URL}/sessions/{session_id}/question-state")
        print(f"Status: {resp.status_code}")
        data = resp.json()
        print_json(data)
        
        if resp.status_code == 200:
            print(f"\n✅ Current phase: {data['current_phase']}")
            print(f"✅ Total answers: {data['answers_count']}")
            print(f"✅ Can advance: {data['can_advance']}")
        return data
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_advance_phase(session_id):
    """Test advancing to next phase"""
    print_separator(f"TEST 6: Advance Phase (Session: {session_id[:8]}...)")
    try:
        resp = requests.post(
            f"{BASE_URL}/sessions/{session_id}/next-phase",
            json={"confirm": True}
        )
        print(f"Status: {resp.status_code}")
        data = resp.json()
        print_json(data)
        
        if resp.status_code == 200:
            print(f"\n✅ Advanced from {data['previous_phase']} to {data['new_phase']}")
            if data.get('first_question'):
                print(f"✅ First question in new phase: {data['first_question']['question_id']}")
        return data
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_complete_phase(session_id, questions):
    """Answer all questions in current phase"""
    print_separator(f"TEST: Complete All Questions in Phase")
    
    sample_answers = [
        "Saya merasa cukup stabil saat ini, tidak ada krisis yang sedang dihadapi.",
        "Saya punya keluarga dan beberapa teman dekat yang bisa saya hubungi.",
        "Ya, saya setuju untuk melanjutkan sesi ini.",
        "Di keluarga saya, yang penting adalah selalu menghormati orang tua dan tidak mengecewakan mereka.",
        "Orang tua saya jarang menunjukkan emosi secara terbuka. Mereka lebih banyak diam.",
        "Saya sadar dunia tidak aman ketika melihat konflik di rumah. Saya belajar untuk selalu waspada.",
        "Keluarga kami menganut budaya Jawa yang mengutamakan kesopanan dan penghormatan.",
    ]
    
    for i, question in enumerate(questions):
        qid = question["question_id"]
        answer = sample_answers[i % len(sample_answers)]
        print(f"\n--- Answering {qid} ---")
        result = test_submit_answer(session_id, qid, answer)
        if not result:
            return False
        time.sleep(0.5)
    
    return True


def run_full_flow_test():
    """Run the complete question-based flow test"""
    print_separator("MBP v2.0 - QUESTION-BASED FLOW TEST")
    print("Testing quiz-style flow through MBP phases...")
    
    # Test health
    if not test_health():
        print("\n❌ Health check failed. Is the server running?")
        print("   Start server with: ./run.sh")
        return False
    
    # Create session
    session_id = test_create_session()
    if not session_id:
        print("\n❌ Failed to create session")
        return False
    
    # Test Phase 0 (Safety) - Answer all 7 questions
    print("\n" + "="*60)
    print("  PHASE 0: SAFETY & CONTEXT SCREENING")
    print("="*60)
    
    questions = test_get_questions(session_id)
    if not questions:
        print("\n❌ Failed to get questions")
        return False
    
    print(f"\n📋 Phase 0 has {len(questions)} fixed questions")
    
    # Answer all questions in Phase 0
    if not test_complete_phase(session_id, questions):
        print("\n❌ Failed to complete Phase 0")
        return False
    
    # Check state
    state = test_get_question_state(session_id)
    if not state:
        return False
    
    # Try to advance to Phase 1
    if state.get("can_advance"):
        result = test_advance_phase(session_id)
        if result and result.get("new_phase") == "core":
            print("\n✅ Successfully advanced to Phase 1 (Core)")
            
            # Get Phase 1 questions
            questions = test_get_questions(session_id)
            if questions:
                print(f"\n📋 Phase 1 has {len(questions)} questions")
                print(f"   (11 fixed + flexible questions generated by AI)")
    else:
        print("\n⚠️ Cannot advance yet - need AI processing")
    
    print_separator("TEST SUMMARY")
    print(f"✅ Session ID: {session_id}")
    print(f"✅ Question-based flow is working!")
    print(f"\nNext steps:")
    print(f"  - Continue answering questions in Phase 1")
    print(f"  - Use GET /api/sessions/{session_id}/questions")
    print(f"  - Use POST /api/sessions/{session_id}/answer")
    print(f"  - Use POST /api/sessions/{session_id}/next-phase")
    
    return True


def test_personal_data_endpoints():
    """Test that personal data endpoints still work"""
    print_separator("TEST: Personal Data Endpoints (Backward Compatibility)")
    
    # Create personal data
    resp = requests.post(
        f"{BASE_URL}/personal-data",
        json={
            "nama": "Test User",
            "tanggal_lahir": "01/01/1990",
            "tempat_lahir": "Jakarta",
            "agama": "Islam"
        }
    )
    
    if resp.status_code != 200:
        print(f"❌ Failed to create personal data: {resp.status_code}")
        return False
    
    data = resp.json()
    pd_id = data["personal_data_id"]
    print(f"✅ Created personal data: {pd_id}")
    
    # Get personal data
    resp = requests.get(f"{BASE_URL}/personal-data/{pd_id}")
    if resp.status_code != 200:
        print(f"❌ Failed to get personal data")
        return False
    
    print(f"✅ Retrieved personal data: {resp.json()['nama']}")
    
    # Create session with personal data
    resp = requests.post(
        f"{BASE_URL}/sessions/with-personal-data",
        json={"personal_data_id": pd_id}
    )
    
    if resp.status_code != 200:
        print(f"❌ Failed to create session with personal data")
        return False
    
    print(f"✅ Created session with personal data: {resp.json()['session_id']}")
    return True


if __name__ == "__main__":
    print("MBP v2.0 Question-Based Flow Test")
    print("Make sure the server is running: ./run.sh")
    print("")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--full":
        # Run full test including all phases
        run_full_flow_test()
    elif len(sys.argv) > 1 and sys.argv[1] == "--personal-data":
        # Test personal data endpoints
        test_personal_data_endpoints()
    else:
        # Run basic flow test
        success = run_full_flow_test()
        sys.exit(0 if success else 1)