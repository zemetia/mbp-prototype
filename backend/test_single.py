#!/usr/bin/env python3
"""
Direct Graph Test - Single Turn (Fast)
Tests one turn through MBP LangGraph flow
"""
import asyncio
import sys
import os

sys.path.insert(0, '/mnt/d/Yoel/projects/mbp-prototype/backend')

# Read .env manually
with open('/mnt/d/Yoel/projects/mbp-prototype/backend/.env', 'r') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

from graph import run_mbp_graph
from utils import get_current_timestamp

async def test_single_turn():
    print("=" * 60)
    print("🧠 MBP - SINGLE TURN TEST")
    print("=" * 60)
    
    session_id = "test-session-001"
    message = "Halo, saya ingin memulai assessment tentang diri saya."
    
    print(f"\n💬 User: {message[:50]}...")
    print("\n⏳ Processing (this may take 30-60s)...")
    
    try:
        result = await asyncio.wait_for(
            run_mbp_graph(
                session_id=session_id,
                user_response=message,
                messages=[{"role": "user", "content": message}]
            ),
            timeout=90  # 90 second timeout
        )
        
        print(f"\n📊 RESULT:")
        print(f"   Phase: {result.get('phase')}")
        print(f"   Safety Cleared: {result.get('safety_cleared')}")
        print(f"   Confidence: {result.get('overall_confidence', 0):.2f}")
        
        if result.get('error'):
            print(f"   ❌ Error: {result['error']}")
        
        if result.get('next_question'):
            print(f"\n🤖 AI Response:")
            print(f"   {result['next_question'][:200]}...")
        
        if result.get('final_profile'):
            print(f"\n✅ PROFILE GENERATED!")
        
        print("\n" + "=" * 60)
        print("✅ TEST COMPLETE")
        print("=" * 60)
        
    except asyncio.TimeoutError:
        print("\n❌ Timeout: Request took too long")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Testing MBP Graph with Moonshot API...")
    print(f"API Key: {os.getenv('MOONSHOT_API_KEY', 'NOT SET')[:20]}...")
    print()
    
    asyncio.run(test_single_turn())
