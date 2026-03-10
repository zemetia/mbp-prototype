#!/usr/bin/env python3
"""
MBP v2.0 - Test Script
Tests the modular agent system
"""
import asyncio
import sys
import os

# Read .env manually
with open('/mnt/d/Yoel/projects/mbp-prototype/backend/.env', 'r') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

# Add backend-v2 to path
sys.path.insert(0, '/mnt/d/Yoel/projects/mbp-prototype/backend-v2')

from graph.graph import run_mbp_v2


async def test_mbp_v2():
    """Test MBP v2.0 with a single turn"""
    print("="*70)
    print("🧠 MBP v2.0 - MODULAR AGENT SYSTEM TEST")
    print("="*70)
    
    session_id = "test-v2-001"
    message = "Halo, saya ingin memulai assessment. Saya cenderung perfeksionis dan suka menganalisis segala sesuatu sebelum bertindak."
    messages = [{"role": "user", "content": message}]
    
    print(f"\n💬 User: {message[:60]}...")
    print("\n⏳ Processing... (this may take 2-3 minutes)\n")
    
    try:
        result = await asyncio.wait_for(
            run_mbp_v2(session_id, message, messages),
            timeout=300  # 5 minute timeout
        )
        
        print(f"\n📊 RESULT:")
        print(f"   Phase: {result.get('current_phase')}")
        print(f"   Safety Cleared: {result.get('safety_cleared')}")
        print(f"   Iterations: {result.get('iteration_count')}")
        
        # Show extracted signals summary
        signals = result.get('extracted_signals', {})
        print(f"\n🔍 Extracted Signals:")
        for sig_type, data in signals.items():
            patterns = data.get('patterns', [])
            print(f"   - {sig_type}: {len(patterns)} patterns")
        
        # Show hypotheses
        hyps = result.get('hypotheses', {})
        print(f"\n💡 Hypotheses:")
        for field, field_hyps in hyps.items():
            print(f"   - {field}: {len(field_hyps)} generated")
        
        # Show next question or final profile
        if result.get('next_question'):
            print(f"\n❓ Next Question:")
            print(f"   {result['next_question'][:100]}...")
        
        if result.get('final_profile'):
            print(f"\n✅ FINAL PROFILE GENERATED!")
            profile = result['final_profile']
            core = profile.get('core_structure', {})
            print(f"   Core Fear: {core.get('core_fear', {}).get('primary', {}).get('type', 'unknown')}")
            print(f"   Core Drive: {core.get('core_drive', {}).get('primary', {}).get('type', 'unknown')}")
        
        print(f"\n{'='*70}")
        print("✅ TEST COMPLETE")
        print(f"{'='*70}")
        
    except asyncio.TimeoutError:
        print("\n❌ Timeout after 5 minutes")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Testing MBP v2.0 Modular Agent System")
    print(f"API Key: {os.getenv('MOONSHOT_API_KEY', 'NOT SET')[:20]}...")
    
    asyncio.run(test_mbp_v2())
