"""
MBP Migration Helper
Easy upgrade path from original to optimized implementation
"""
import os
import sys


def check_dependencies():
    """Check if all required dependencies are available"""
    try:
        import langgraph
        import langchain_openai
        print("✓ Dependencies OK")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Run: pip install langgraph langchain-openai")
        return False


def check_files():
    """Check if all required files exist"""
    required = [
        "state.py",
        "llm.py", 
        "prompts.py",
        "utils.py",
        "graph.py",  # Original
        "nodes.py",  # Original
    ]
    
    missing = []
    for f in required:
        if not os.path.exists(f):
            missing.append(f)
    
    if missing:
        print(f"✗ Missing files: {missing}")
        return False
    
    print("✓ All required files present")
    return True


def verify_optimized_files():
    """Check if optimized files were created"""
    optimized = [
        "graph_optimized.py",
        "nodes_optimized.py",
        "config.py",
        "benchmark.py",
        "OPTIMIZATION_GUIDE.md",
    ]
    
    missing = []
    for f in optimized:
        if not os.path.exists(f):
            missing.append(f)
    
    if missing:
        print(f"✗ Missing optimized files: {missing}")
        return False
    
    print("✓ All optimized files present")
    return True


def test_imports():
    """Test if optimized modules can be imported"""
    try:
        from graph_optimized import run_optimized_mbp_graph, create_optimized_mbp_graph
        from nodes_optimized import cached_llm_invoke, LLMCache
        from config import MBPPerformanceConfig, set_fast_mode
        print("✓ Optimized imports successful")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False


def generate_migration_patch():
    """Generate a patch file for easy migration"""
    patch_content = '''"""
Migration patch for MBP
Add this to your main application file
"""

# Configuration
USE_OPTIMIZED_MBP = True  # Set to False to use original

# Import based on flag
if USE_OPTIMIZED_MBP:
    from graph_optimized import run_optimized_mbp_graph as run_mbp_graph
    from config import set_balanced_mode
    
    # Initialize optimized mode
    set_balanced_mode()
    print("MBP: Using optimized graph")
else:
    from graph import run_mbp_graph
    print("MBP: Using original graph")

# Your existing code continues unchanged...
# result = await run_mbp_graph(...)
'''
    
    with open("migration_patch.py", "w") as f:
        f.write(patch_content)
    
    print("✓ Generated migration_patch.py")


def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*60)
    print("MIGRATION COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. Review OPTIMIZATION_GUIDE.md for detailed documentation")
    print("2. Add migration_patch.py to your main application")
    print("3. Run benchmark.py to verify performance gains")
    print("4. Set USE_OPTIMIZED_MBP = True to enable optimizations")
    print("\nQuick test:")
    print("  python -c \"from graph_optimized import run_optimized_mbp_graph; print('OK')\"")
    print("\nRollback:")
    print("  Set USE_OPTIMIZED_MBP = False in your application")
    print("="*60)


def main():
    """Run migration checks"""
    print("="*60)
    print("MBP OPTIMIZATION MIGRATION")
    print("="*60)
    print()
    
    # Get current directory
    current_dir = os.path.basename(os.getcwd())
    print(f"Current directory: {current_dir}")
    print()
    
    # Run checks
    checks = [
        ("Dependencies", check_dependencies),
        ("Required files", check_files),
        ("Optimized files", verify_optimized_files),
        ("Import test", test_imports),
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\nChecking {name}...")
        if not check_func():
            all_passed = False
    
    print()
    
    if all_passed:
        generate_migration_patch()
        print_next_steps()
        return 0
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
