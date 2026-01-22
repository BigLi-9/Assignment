"""
Test /analyze endpoint
Run this while server is running in another terminal
"""
import requests
import json

print("\n" + "="*60)
print("TESTING /analyze ENDPOINT")
print("="*60)
print("⏳ Uploading test_survey.csv and calling Gemini...")
print("   (This will take 5-10 seconds)")

with open('test_survey.csv', 'rb') as f:
    files = {'file': ('test_survey.csv', f, 'text/csv')}
    response = requests.post('http://localhost:8000/analyze', files=files, timeout=30)

print(f"\nStatus: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    persona = data['persona']
    
    print("\n" + "="*60)
    print("✅ SUCCESS! PLAYER PERSONA GENERATED")
    print("="*60)
    print(f"\n🎮 Archetype: {persona['archetype_name']}")
    print(f"\n👤 Demographics:")
    print(f"   - Age Range: {persona['demographics']['age_range']}")
    print(f"   - Gaming Frequency: {persona['demographics']['gaming_frequency']}")
    print(f"   - Preferred Genres: {', '.join(persona['demographics']['preferred_genres'])}")
    print(f"   - Primary Platform: {persona['demographics']['primary_platform']}")
    
    print(f"\n💪 Motivations:")
    print(f"   - Primary Driver: {persona['motivations']['primary_driver']}")
    print(f"   - Engagement Factors: {', '.join(persona['motivations']['engagement_factors'])}")
    
    print(f"\n😤 Pain Points:")
    print(f"   - Frustrations: {', '.join(persona['pain_points']['frustrations'])}")
    print(f"   - What They Hate: {persona['pain_points']['what_they_hate']}")
    
    print(f"\n💰 Spending Habits:")
    print(f"   - Purchase Likelihood: {persona['spending_habits']['in_game_purchase_likelihood']}")
    print(f"   - Monetization Preference: {persona['spending_habits']['monetization_preference']}")
    print(f"   - Price Sensitivity: {persona['spending_habits']['price_sensitivity']}")
    
    print("\n" + "="*60)
    print("✅ Phase 2 Backend API: 100% COMPLETE!")
    print("="*60)
else:
    print(f"\n❌ Error Response:")
    print(response.text)
