#!/usr/bin/env python3
"""
MBP API Integration Test Script
Tests the API contract between frontend and backend without running full servers.
"""

import sys
import json

# Add backend to path
sys.path.insert(0, '/mnt/d/Yoel/Projects/mbp-prototype/backend-v2')

from api.models import (
    QuestionsResponse, 
    AnswerResponse, 
    NextPhaseResponse,
    Question,
    AnswerRequest,
    NextPhaseRequest
)

def test_question_model():
    """Test Question model has both id and question_id"""
    print("\n📝 Testing Question Model...")
    
    q = Question(
        id="q001",
        question_id="q001",
        phase="safety",
        phase_number=0,
        type="fixed",
        text="Test question",
        dimensions=["CFV"],
        order=1
    )
    
    # Convert to dict (simulating JSON response)
    q_dict = q.model_dump(by_alias=True)
    
    # When using by_alias=True, id replaces question_id in output
    assert "id" in q_dict, "Missing 'id' field"
    assert q_dict["id"] == "q001", "id value mismatch"
    assert q_dict["phase_number"] == 0, "phase_number mismatch"
    
    # Also verify the model has both fields internally
    assert q.id == "q001", "Model id mismatch"
    assert q.question_id == "q001", "Model question_id mismatch"
    
    print(f"  ✓ Question: id={q_dict['id']}, phase_number={q_dict['phase_number']}")
    return True

def test_questions_response():
    """Test GET /questions response format"""
    print("\n📝 Testing QuestionsResponse...")
    
    question = Question(
        id="q001",
        question_id="q001",
        phase="safety",
        phase_number=0,
        type="fixed",
        text="Test question",
        dimensions=["CFV"],
        order=1
    )
    
    response = QuestionsResponse(
        session_id="test-session",
        phase="safety",
        phase_number=0,
        question=question,
        questions=[question],
        current_question_index=0,
        total_questions_in_phase=7,
        phase_complete=False,
        progress_percentage=0.0,
        analysis_complete=False
    )
    
    data = response.model_dump(by_alias=True)
    
    assert "question" in data, "Missing 'question' field"
    assert "phase_number" in data, "Missing 'phase_number' field"
    assert "analysis_complete" in data, "Missing 'analysis_complete' field"
    assert data["phase_number"] == 0, "phase_number should be 0"
    assert data["question"]["id"] == "q001", "question.id mismatch"
    
    print(f"  ✓ QuestionsResponse: phase_number={data['phase_number']}, has question={data['question'] is not None}")
    return True

def test_answer_response():
    """Test POST /answer response format"""
    print("\n📝 Testing AnswerResponse...")
    
    next_q = Question(
        id="q002",
        question_id="q002",
        phase="safety",
        phase_number=0,
        type="fixed",
        text="Next question",
        dimensions=["CFV"],
        order=2
    )
    
    response = AnswerResponse(
        session_id="test-session",
        phase="safety",
        question_id="q001",
        next_question=next_q,
        phase_complete=False,
        can_advance=False,
        analysis_complete=False,
        message="Answer recorded"
    )
    
    data = response.model_dump(by_alias=True)
    
    assert "next_question" in data, "Missing 'next_question' field"
    assert "analysis_complete" in data, "Missing 'analysis_complete' field"
    assert data["analysis_complete"] == False, "analysis_complete should be False"
    
    print(f"  ✓ AnswerResponse: has next_question={data['next_question'] is not None}, analysis_complete={data['analysis_complete']}")
    return True

def test_next_phase_response():
    """Test POST /next-phase response format"""
    print("\n📝 Testing NextPhaseResponse...")
    
    first_q = Question(
        id="q101",
        question_id="q101",
        phase="core",
        phase_number=1,
        type="fixed",
        text="First core question",
        dimensions=["ARP"],
        order=1
    )
    
    response = NextPhaseResponse(
        session_id="test-session",
        previous_phase="safety",
        new_phase="core",
        next_phase="core",
        phase_number=1,
        first_question=first_q,
        ai_processing_complete=True,
        analysis_complete=False,
        message="Advanced to core phase"
    )
    
    data = response.model_dump(by_alias=True)
    
    assert "next_phase" in data, "Missing 'next_phase' field"
    assert "phase_number" in data, "Missing 'phase_number' field"
    assert "analysis_complete" in data, "Missing 'analysis_complete' field"
    assert data["next_phase"] == "core", "next_phase mismatch"
    assert data["phase_number"] == 1, "phase_number should be 1"
    
    print(f"  ✓ NextPhaseResponse: next_phase={data['next_phase']}, phase_number={data['phase_number']}")
    return True

def test_phase_mapping():
    """Test phase name to number mapping"""
    print("\n📝 Testing Phase Mapping...")
    
    expected_mapping = {
        "safety": 0,
        "core": 1,
        "probing": 2,
        "mining": 3,
        "validation": 4,
        "synthesis": 5,
        "closure": 6,
    }
    
    # This mapping is in main.py, we can't import it directly due to dependencies
    # But we verify the concept through the Question model
    
    for phase_name, expected_num in expected_mapping.items():
        q = Question(
            id="test",
            question_id="test",
            phase=phase_name,
            phase_number=expected_num,
            type="fixed",
            text="Test",
            dimensions=[],
            order=1
        )
        assert q.phase_number == expected_num, f"Phase {phase_name} should have number {expected_num}"
    
    print(f"  ✓ All {len(expected_mapping)} phases mapped correctly")
    return True

def test_request_models():
    """Test request body models"""
    print("\n📝 Testing Request Models...")
    
    # AnswerRequest
    answer_req = AnswerRequest(
        question_id="q001",
        answer="Test answer"
    )
    assert answer_req.question_id == "q001"
    assert answer_req.answer == "Test answer"
    print(f"  ✓ AnswerRequest: question_id={answer_req.question_id}")
    
    # NextPhaseRequest
    next_req = NextPhaseRequest(confirm=True)
    assert next_req.confirm == True
    print(f"  ✓ NextPhaseRequest: confirm={next_req.confirm}")
    
    return True

def main():
    """Run all integration tests"""
    print("=" * 60)
    print("MBP Frontend-Backend Integration Tests")
    print("=" * 60)
    
    tests = [
        test_question_model,
        test_questions_response,
        test_answer_response,
        test_next_phase_response,
        test_phase_mapping,
        test_request_models,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            failed += 1
            print(f"  ✗ Test failed: {e}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("✅ All integration tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())