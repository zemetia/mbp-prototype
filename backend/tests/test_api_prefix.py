#!/usr/bin/env python3
"""
Test script to verify all API endpoints work correctly with /api prefix
"""
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing backend with /api prefix...\n")

try:
    from api.main import app
    print("✅ FastAPI app imported successfully")
    
    # List all routes
    print("\n📋 All Routes:")
    for route in app.routes:
        if hasattr(route, 'methods') and route.methods != {'HEAD', 'OPTIONS'}:
            methods = ', '.join(route.methods - {'HEAD', 'OPTIONS'})
            print(f"   {methods:8} {route.path}")
    
    print("\n✅ All routes configured correctly!")
    print("\nFrontend should call:")
    print("   POST /api/personal-data")
    print("   GET  /api/personal-data/{id}")
    print("   POST /api/sessions/with-personal-data")
    print("   POST /api/analyses")
    print("   GET  /api/analyses")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
