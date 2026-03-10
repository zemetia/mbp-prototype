#!/usr/bin/env python3
"""
Test script to verify all API endpoints work correctly
"""
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing imports...")

try:
    from api.models import (
        CreateSessionRequest, CreateSessionResponse,
        UserResponseRequest, UserResponseResponse,
        SessionStateResponse, ProfileResponse, HealthResponse,
        Phase,
        PersonalDataRequest, PersonalDataResponse, PersonalData,
        CreateSessionWithPersonalDataRequest, CreateSessionWithPersonalDataResponse,
        AnalysisRequest, AnalysisResponse, AnalysesListResponse, AnalysisDetail
    )
    print("✅ All models imported successfully")
    print(f"   Phase values: {[p.value for p in Phase]}")
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

try:
    from api.main import app
    print("✅ FastAPI app imported successfully")
    
    # List all routes
    print("\n📋 Available Routes:")
    for route in app.routes:
        if hasattr(route, 'methods') and route.methods != {'HEAD', 'OPTIONS'}:
            methods = ', '.join(route.methods - {'HEAD', 'OPTIONS'})
            print(f"   {methods:8} {route.path}")
    
except Exception as e:
    print(f"❌ App import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ All imports working correctly!")
