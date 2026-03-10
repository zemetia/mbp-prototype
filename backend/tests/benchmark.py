"""
MBP v2.0 Performance Benchmark
Compare with v1 and track metrics
"""
import asyncio
import time
import sys

sys.path.insert(0, '/mnt/d/Yoel/projects/mbp-prototype/backend-v2')

from graph.graph import run_mbp_v2


async def benchmark_single_turn():
    """Benchmark single turn performance"""
    print("="*60)
    print("🚀 MBP v2.0 Performance Benchmark")
    print("="*60)
    
    session_id = "benchmark-001"
    message = "Halo, saya cenderung perfeksionis dan suka menganalisis segala sesuatu sebelum bertindak."
    messages = [{"role": "user", "content": message}]
    
    start = time.time()
    
    result = await run_mbp_v2(session_id, message, messages)
    
    elapsed = time.time() - start
    
    # Get timing breakdown
    node_times = result.get("node_execution_times", {})
    
    print(f"\n📊 Results:")
    print(f"   Total time: {elapsed:.2f}s")
    print(f"   Phase: {result.get('current_phase')}")
    print(f"   Iterations: {result.get('iteration_count')}")
    
    print(f"\n⏱️  Node Timing:")
    for node, t in sorted(node_times.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {node}: {t:.2f}s")
    
    # Signals summary
    signals = result.get("extracted_signals", {})
    total_patterns = sum(len(s.get("patterns", [])) for s in signals.values())
    print(f"\n🔍 Patterns extracted: {total_patterns}")
    
    # Hypotheses
    hyps = result.get("hypotheses", {})
    total_hyps = sum(len(h) for h in hyps.values())
    print(f"💡 Hypotheses generated: {total_hyps}")
    
    print(f"\n✅ Benchmark complete!")
    
    return {
        "total_time": elapsed,
        "node_times": node_times,
        "patterns": total_patterns,
        "hypotheses": total_hyps
    }


if __name__ == "__main__":
    print("Starting MBP v2.0 Benchmark...")
    asyncio.run(benchmark_single_turn())