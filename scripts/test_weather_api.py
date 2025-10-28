"""
Test script to verify OpenWeatherMap API key is working.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("OPENWEATHER_API_KEY")

print("=" * 60)
print("OpenWeatherMap API Key Test")
print("=" * 60)
print(f"\nAPI Key: {api_key[:10]}...{api_key[-4:] if api_key else 'NOT FOUND'}")

if not api_key:
    print("\n❌ ERROR: OPENWEATHER_API_KEY not found in .env file")
    print("\nPlease add it to .env file:")
    print("OPENWEATHER_API_KEY=your_api_key_here")
    exit(1)

# Test API call
print("\n📡 Testing API connection...")
url = "http://api.openweathermap.org/data/2.5/weather"
params = {
    "q": "Delhi",
    "appid": api_key,
    "units": "metric"
}

try:
    response = requests.get(url, params=params, timeout=10)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ SUCCESS! API is working!")
        print("\n📊 Current Weather in Delhi:")
        print(f"   Temperature: {data['main']['temp']}°C")
        print(f"   Wind Speed: {data['wind']['speed']} m/s")
        print(f"   Weather: {data['weather'][0]['description']}")
        print(f"   Humidity: {data['main']['humidity']}%")
        
    elif response.status_code == 401:
        print("\n❌ ERROR: 401 Unauthorized")
        print("\nThis means:")
        print("1. API key is invalid, OR")
        print("2. API key was just created and needs activation (wait 10 min - 2 hours)")
        print("\nTo fix:")
        print("• Check your API key at: https://home.openweathermap.org/api_keys")
        print("• Make sure you verified your email")
        print("• Wait a few minutes if you just created the key")
        print(f"\nAPI Key being used: {api_key}")
        
    elif response.status_code == 429:
        print("\n⚠️  Rate limit exceeded")
        print("Free tier: 60 calls/minute, 1000 calls/day")
        
    else:
        print(f"\n❌ Unexpected error: {response.status_code}")
        print(response.text)
        
except requests.exceptions.RequestException as e:
    print(f"\n❌ Network error: {e}")

print("\n" + "=" * 60)
