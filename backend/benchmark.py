"""
MBP Performance Benchmark
Compare original vs optimized implementations
"""
import asyncio
import time
from typing import List, Dict, Any
from dataclasses import dataclass

# Import both implementations
from graph import run_mbp_graph
from graph_optimized import run_optimized_mbp_graph, get_performance_stats


@dataclass
class BenchmarkResult:
    """Single benchmark run result"""
    name: str
    duration: float
    success: bool
    error: str = None


class MBPBenchmark:
    """Benchmark suite for MBP performance testing"""
    
    TEST_RESPONSES = [
        "Hari ini saya merasa cukup baik, walaupun ada beberapa hal yang mengganjal di pikiran.",
        "Saya ngerasa kalau di kantor itu saya harus selalu tampil kuat, padahal sebenarnya capek.",
        "Dulu waktu kecil saya sering disalahin sama orang tua, jadi sekarang saya selalu takut bikin kesalahan.",
        "Saya punya impian besar tapi seringkali rasa takut gagal bikin saya nggak mulai-mulai.",
    ]
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
    
    async def benchmark_single(
        self, 
        name: str, 
        runner_func, 
        session_id: str,
        response: str,
        messages: List[Dict]
    ) -> BenchmarkResult:
        """Run single benchmark"""
        print(f"  Running {name}...", end=" ")
        start = time.time()
        
        try:
            result = await runner_func(
                session_id=session_id,
                user_response=response,
                messages=messages,
                previous_state=None
            )
            duration = time.time() - start
            print(f"✓ {duration:.1f}s")
            return BenchmarkResult(name, duration, True)
            
        except Exception as e:
            duration = time.time() - start
            print(f"✗ {duration:.1f}s - {e}")
            return BenchmarkResult(name, duration, False, str(e))
    
    async def run_comparison(self, iterations: int = 3):
        """Compare original vs optimized over multiple iterations"""
        print("=" * 60)
        print("MBP PERFORMANCE BENCHMARK")
        print("=" * 60)
        print(f"Iterations per test: {iterations}")
        print()
        
        original_times = []
        optimized_times = []
        
        for i, response in enumerate(self.TEST_RESPONSES[:2]):  # Use first 2 for speed
            print(f"\nTest Response {i+1}: {response[:50]}...")
            
            messages = [{"role": "user", "content": response}]
            
            for iteration in range(iterations):
                # Benchmark original
                result = await self.benchmark_single(
                    f"  Original #{iteration+1}",
                    run_mbp_graph,
                    f"bench_orig_{i}_{iteration}",
                    response,
                    messages
                )
                if result.success:
                    original_times.append(result.duration)
                self.results.append(result)
                
                # Small delay between runs
                await asyncio.sleep(1)
                
                # Benchmark optimized
                result = await self.benchmark_single(
                    f"  Optimized #{iteration+1}",
                    run_optimized_mbp_graph,
                    f"bench_opt_{i}_{iteration}",
                    response,
                    messages
                )
                if result.success:
                    optimized_times.append(result.duration)
                self.results.append(result)
                
                await asyncio.sleep(1)
        
        # Print summary
        print("\n" + "=" * 60)
        print("RESULTS SUMMARY")
        print("=" * 60)
        
        if original_times and optimized_times:
            avg_original = sum(original_times) / len(original_times)
            avg_optimized = sum(optimized_times) / len(optimized_times)
            improvement = ((avg_original - avg_optimized) / avg_original) * 100
            
            print(f"\nOriginal Average:  {avg_original:.1f}s")
            print(f"Optimized Average: {avg_optimized:.1f}s")
            print(f"Improvement:       {improvement:.1f}% faster")
            
            if improvement > 0:
                print(f"\n✓ Optimization successful!")
            else:
                print(f"\n⚠ No improvement (may need tuning)")
        
        # Print stats
        stats = get_performance_stats()
        print(f"\nPerformance Stats:")
        print(f"  Total runs: {stats.get('total_runs', 0)}")
        print(f"  Average time: {stats.get('average_run_time', 0):.1f}s")


async def main():
    """Run benchmark"""
    benchmark = MBPBenchmark()
    await benchmark.run_comparison(iterations=2)


if __name__ == "__main__":
    asyncio.run(main())
