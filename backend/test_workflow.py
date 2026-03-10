#!/usr/bin/env python3
"""
MBP Full Workflow Test
Simulates a complete user journey through all 6 phases
"""
import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

async def test_workflow():
    async with httpx.AsyncClient(timeout=60.0) as client:
        
        print("=" * 60)
        print("🧠 MIRRORBREAK PROTOCOL - FULL WORKFLOW TEST")
        print("=" * 60)
        
        # 1. Health Check
        print("\n📡 1. Health Check")
        r = await client.get(f"{BASE_URL}/health")
        print(f"   Status: {r.json()}")
        
        # 2. Create Session
        print("\n🆕 2. Creating New Session")
        r = await client.post(f"{BASE_URL}/sessions")
        session = r.json()
        session_id = session["session_id"]
        print(f"   Session ID: {session_id[:8]}...")
        print(f"   Initial Phase: {session.get('phase', 'N/A')}")
        
        # Test conversation turns
        test_messages = [
            {
                "role": "user",
                "message": "Halo, saya ingin memulai assessment tentang diri saya.",
                "expected_phase": "safety_check"
            },
            {
                "role": "user", 
                "message": "Saya merasa baik-baik saja, tidak ada masalah kesehatan mental.",
                "expected_phase": "analyzer"
            },
            {
                "role": "user",
                "message": "Saya cenderung memikirkan banyak kemungkinan sebelum bertindak.",
                "expected_phase": "hypothesis_maker"
            },
            {
                "role": "user",
                "message": "Di kantor saya sering menunggu instruksi dulu tapi juga bisa inisiatif kalau perlu.",
                "expected_phase": "adaptation_mining"
            },
            {
                "role": "user",
                "message": "Saya suka eksplorasi ide baru tapi tetap perlu struktur yang jelas.",
                "expected_phase": "cross_validation"
            },
            {
                "role": "user",
                "message": "Ketika stress, saya biasanya menarik diri sejenak untuk merenung.",
                "expected_phase": "assessor"
            },
            {
                "role": "user",
                "message": "Saya merasa sudah cukup memahami pola perilaku saya.",
                "expected_phase": "synthesizer"
            }
        ]
        
        turn = 0
        for test in test_messages:
            turn += 1
            print(f"\n💬 Turn {turn}: {test['role'].upper()}")
            print(f"   Message: {test['message'][:50]}...")
            
            # Send message
            r = await client.post(
                f"{BASE_URL}/sessions/{session_id}/respond",
                json={
                    "message": test["message"],
                    "client_timestamp": datetime.now().isoformat()
                }
            )
            
            if r.status_code != 200:
                print(f"   ❌ Error: {r.status_code} - {r.text[:100]}")
                continue
                
            result = r.json()
            
            print(f"   📊 Phase: {result.get('phase', 'N/A')}")
            print(f"   🎯 Confidence: {result.get('confidence', 'N/A')}")
            print(f"   💭 AI Response: {result.get('message', 'N/A')[:80]}...")
            
            # Check timing
            if "processing_time_ms" in result:
                print(f"   ⏱️  Processing: {result['processing_time_ms']}ms")
            
            # If profile generated, show it
            if result.get("profile_generated"):
                print(f"\n   ✅ PROFILE GENERATED!")
                profile = result.get("profile", {})
                print(f"   Dimensions: {len(profile.get('dimensions', {}))}")
                
        # 4. Get Final Session Status
        print("\n" + "=" * 60)
        print("📊 FINAL SESSION STATUS")
        print("=" * 60)
        
        r = await client.get(f"{BASE_URL}/sessions/{session_id}")
        status = r.json()
        print(f"   Final Phase: {status.get('phase')}")
        print(f"   Status: {status.get('status')}")
        print(f"   Overall Confidence: {status.get('overall_confidence', 'N/A')}")
        
        # 5. Get Messages
        print("\n💬 Message History:")
        r = await client.get(f"{BASE_URL}/sessions/{session_id}/messages")
        msgs = r.json()
        for m in msgs.get("messages", [])[:5]:
            print(f"   [{m.get('phase', '?')}] {m.get('role', '?')}: {m.get('content', '')[:40]}...")
        
        # 6. Get Timings
        print("\n⏱️  Timing Analytics:")
        r = await client.get(f"{BASE_URL}/sessions/{session_id}/timings")
        timings = r.json()
        print(f"   Total timing records: {len(timings.get('timings', []))}")
        
        # 7. Get Profile if available
        print("\n📋 Final Profile:")
        r = await client.get(f"{BASE_URL}/sessions/{session_id}/profile")
        if r.status_code == 200:
            profile = r.json()
            if profile.get("profile"):
                dims = profile["profile"].get("dimensions", {})
                print(f"   12D Dimensions assessed: {len(dims)}")
                for dim, score in list(dims.items())[:5]:
                    print(f"     - {dim}: {score}")
            else:
                print("   Profile not yet generated")
        else:
            print("   Profile endpoint error")
        
        print("\n" + "=" * 60)
        print("✅ WORKFLOW TEST COMPLETE")
        print("=" * 60)

if __name__ == "__main__":
    # Check if server is running
    import sys
    try:
        import httpx
    except ImportError:
        print("Installing httpx...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "httpx"])
    
    print("Make sure server is running: uvicorn main:app --reload")
    print("Testing in 3 seconds...")
    import time
    time.sleep(3)
    
    asyncio.run(test_workflow())
