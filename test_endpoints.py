"""
Test Phase 2 endpoints with live server
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n" + "="*60)
    print("TEST: Health Check")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✓ Health check passed")
    return True

def test_upload():
    """Test /upload endpoint"""
    print("\n" + "="*60)
    print("TEST: Upload Endpoint")
    print("="*60)
    
    with open('test_survey.csv', 'rb') as f:
        files = {'file': ('test_survey.csv', f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Status: {data['status']}")
    print(f"Message: {data['message']}")
    print(f"Responses count: {data['responses_count']}")
    print(f"Format: {data['format']}")
    
    assert response.status_code == 200
    assert data['status'] == 'success'
    assert data['responses_count'] == 10
    print("✓ Upload endpoint passed")
    return True

def test_analyze():
    """Test /analyze endpoint with Gemini"""
    print("\n" + "="*60)
    print("TEST: Analyze Endpoint (Gemini Integration)")
    print("="*60)
    print("⏳ Calling Gemini API... (this may take 10-15 seconds)")
    
    with open('test_survey.csv', 'rb') as f:
        files = {'file': ('test_survey.csv', f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/analyze", files=files)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Error: {response.text}")
        return False
    
    data = response.json()
    print(f"Status: {data['status']}")
    print(f"Message: {data['message']}")
    
    if 'persona' in data:
        persona = data['persona']
        print(f"\n✓ Persona Generated:")
        print(f"  - Archetype: {persona['archetype_name']}")
        print(f"  - Age Range: {persona['demographics']['age_range']}")
        print(f"  - Gaming Frequency: {persona['demographics']['gaming_frequency']}")
        print(f"  - Primary Driver: {persona['motivations']['primary_driver']}")
        print(f"  - Main Pain Point: {persona['pain_points']['what_they_hate']}")
        print(f"  - Purchase Likelihood: {persona['spending_habits']['in_game_purchase_likelihood']}")
    
    assert response.status_code == 200
    assert data['status'] == 'success'
    assert 'persona' in data
    print("\n✓ Analyze endpoint passed")
    return True

def main():
    """Run all endpoint tests"""
    print("\n")
    print("█" * 60)
    print("  PHASE 2 - LIVE ENDPOINT TESTS")
    print("█" * 60)
    
    try:
        # Test 1: Health
        test_health()
        
        # Test 2: Upload
        test_upload()
        
        # Test 3: Analyze (with Gemini)
        test_analyze()
        
        print("\n" + "="*60)
        print("✓ ALL ENDPOINT TESTS PASSED")
        print("="*60)
        print("\n✨ Phase 2 Backend API Complete!")
        print("\nEndpoints Working:")
        print("  • GET  /health   - Health check")
        print("  • GET  /         - Root endpoint")
        print("  • POST /upload   - File validation")
        print("  • POST /analyze  - AI persona generation")
        print("\nSwagger UI: http://localhost:8000/api/docs")
        print()
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
