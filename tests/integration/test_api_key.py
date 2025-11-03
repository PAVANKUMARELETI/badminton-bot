"""Direct API key test - minimal dependencies."""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENWEATHER_API_KEY")

print("=== OpenWeatherMap API Key Test ===\n")
print(f"API Key: {api_key[:10]}...{api_key[-4:]}")
print(f"Key length: {len(api_key)} characters")

# Test with a simple API call
url = "http://api.openweathermap.org/data/2.5/weather"
params = {
    "q": "Delhi",
    "appid": api_key,
    "units": "metric"
}

print(f"\nTesting URL: {url}")
print("Making request...")

response = requests.get(url, params=params)

print(f"\nStatus Code: {response.status_code}")

if response.status_code == 200:
    print("✅ SUCCESS! API key is working!")
    data = response.json()
    print(f"\nWeather in Delhi:")
    print(f"  Temperature: {data['main']['temp']}°C")
    print(f"  Wind Speed: {data['wind']['speed']} m/s")
    print(f"  Description: {data['weather'][0]['description']}")
elif response.status_code == 401:
    print("❌ UNAUTHORIZED - API key is invalid or not yet activated")
    print("\nPossible reasons:")
    print("1. API key is new and needs time to activate (up to 2 hours)")
    print("2. API key was copied incorrectly")
    print("3. API key was revoked or deleted")
    print("\nWhat to do:")
    print("• Wait 10-15 minutes and try again")
    print("• Check your OpenWeatherMap account dashboard")
    print("• Verify the API key is for 'Current Weather Data' (free tier)")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
