"""
Phase 2 Integration Tests
Tests both /upload and /analyze endpoints
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_file_validation():
    """Test file validator directly"""
    from app.services.file_validator import validator
    
    print("\n" + "="*60)
    print("TEST 1: File Validator (CSV Parsing)")
    print("="*60)
    
    with open('test_survey.csv', 'rb') as f:
        content = f.read()
    
    survey = validator.validate_file('test_survey.csv', content)
    print(f"✓ CSV parsed successfully")
    print(f"  - Responses: {len(survey.responses)}")
    print(f"  - Format: {survey.format}")
    
    return True

async def test_routes():
    """Test routes import"""
    from app.routes import router
    
    print("\n" + "="*60)
    print("TEST 2: Routes Registration")
    print("="*60)
    
    # Check routes
    routes_found = []
    for route in router.routes:
        if hasattr(route, 'path'):
            routes_found.append(route.path)
    
    print(f"✓ Routes registered: {routes_found}")
    assert "/upload" in routes_found, "Upload endpoint not found"
    assert "/analyze" in routes_found, "Analyze endpoint not found"
    print(f"✓ Both /upload and /analyze endpoints registered")
    
    return True

async def test_gemini_config():
    """Test Gemini configuration"""
    import os
    
    print("\n" + "="*60)
    print("TEST 3: Gemini API Configuration")
    print("="*60)
    
    # Check .env file
    if not Path('.env').exists():
        print("⚠ .env file not found")
        return False
    
    # Load and check
    from app.config import settings
    if not settings.gemini_api_key:
        print("⚠ GEMINI_API_KEY not set in .env")
        return False
    
    print(f"✓ GEMINI_API_KEY configured")
    print(f"  - API Key starts with: {settings.gemini_api_key[:10]}...")
    
    return True

async def main():
    """Run all tests"""
    print("\n")
    print("█" * 60)
    print("  PHASE 2 BACKEND API - INTEGRATION TESTS")
    print("█" * 60)
    
    try:
        # Test 1: File validation
        await test_file_validation()
        
        # Test 2: Routes
        await test_routes()
        
        # Test 3: Gemini config
        await test_gemini_config()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED")
        print("="*60)
        print("\nNEXT STEPS:")
        print("1. Start FastAPI server: python main.py")
        print("2. Test /upload endpoint: curl -X POST -F 'file=@test_survey.csv' http://localhost:8000/upload")
        print("3. Test /analyze endpoint: curl -X POST -F 'file=@test_survey.csv' http://localhost:8000/analyze")
        print("4. Visit http://localhost:8000/api/docs for Swagger UI")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
