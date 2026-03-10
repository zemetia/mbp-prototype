#!/usr/bin/env python3
"""
Direct Graph Test - No HTTP Server Needed
Tests the MBP LangGraph flow directly
"""
import asyncio
import sys
import os

sys.path.insert(0, '/mnt/d/Yoel/projects/mbp-prototype/backend')

# Load .env before importing modules that use env vars
from dotenv import load_dotenv
load_dotenv()

from graph import run_mbp_graph
from state import Phase
from utils import get_current_timestamp

async def test_direct_graph():
    print("=" * 60)
    print("🧠 MIRRORBREAK PROTOCOL - DIRECT GRAPH TEST")
    print("=" * 60)
    
    # Test messages simulating user conversation
    test_messages = [
        "Halo, saya ingin memulai assessment tentang diri saya.",
        "Saya merasa baik-baik saja, tidak ada masalah kesehatan mental.",
        "Saya cenderung memikirkan banyak kemungkinan sebelum bertindak.",
        "Di kantor saya sering menunggu instruksi dulu.",
        "Saya suka eksplorasi ide baru tapi tetap perlu struktur.",
    ]
    
    session_id = "test-session-001"
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{'='*60}")
        print(f"💬 TURN {i}: User")
        print(f"   Message: {message[:50]}...")
        print(f"{'='*60}")
        
        # Build messages list up to this point
        messages = [{"role": "user", "content": m} for m in test_messages[:i]]
        
        result = await run_mbp_graph(
            session_id=session_id,
            user_response=message,
            messages=messages
        )
        
        print(f"\n📊 RESULT:")
        print(f"   Phase: {result.get('phase')}")
        print(f"   Safety Cleared: {result.get('safety_cleared')}")
        print(f"   Confidence: {result.get('overall_confidence', 0):.2f}")
        
        if result.get('error'):
            print(f"   ❌ Error: {result['error']}")
        
        if result.get('next_question'):
            print(f"\n🤖 AI Response:")
            print(f"   {result['next_question'][:150]}...")
        
        if result.get('final_profile'):
            print(f"\n✅ FINAL PROFILE GENERATED!")
            profile = result['final_profile']
            print(f"   Dimensions: {len(profile.get('dimensions', {}))}")
            break
        
        # Safety check abort
        if result.get('phase') == 'aborted':
            print(f"\n⚠️  SESSION ABORTED (Safety Check)")
            break
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    print("Testing MBP Graph directly (no HTTP server)...")
    print("Make sure MOONSHOT_API_KEY is set in .env")
    print()
    
    asyncio.run(test_direct_graph())
