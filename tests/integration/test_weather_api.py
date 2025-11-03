"""Quick test script for weather API."""

from src.data.weather_api import get_weather_for_location

# Test API connection
print("=== Testing OpenWeatherMap API ===\n")

try:
    # Get weather for Delhi
    df = get_weather_for_location('Delhi', hours=3)
    
    # Display current conditions
    current = df.iloc[0]
    
    print("✅ API Connection Successful!")
    print("\n=== CURRENT WEATHER IN DELHI ===")
    print(f"Wind Speed:  {current['wind_m_s']:.1f} m/s")
    print(f"Wind Gust:   {current['wind_gust_m_s']:.1f} m/s")
    print(f"Temperature: {current['temp']:.1f}°C")
    print(f"Humidity:    {current['humidity']:.0f}%")
    print(f"Conditions:  {current['weather']}")
    print(f"Location:    ({current['lat']:.2f}, {current['lon']:.2f})")
    
    # Check if safe to play
    is_safe = current['wind_m_s'] < 1.5
    print(f"\n🏸 Safe to play: {'YES ✅' if is_safe else 'NO ❌ (too windy)'}")
    
    # Show forecast
    print("\n=== NEXT 3 HOURS FORECAST ===")
    for i, (timestamp, row) in enumerate(df.iterrows()):
        safe_emoji = "✅" if row['wind_m_s'] < 1.5 else "❌"
        print(f"{timestamp.strftime('%H:%M')}: {row['wind_m_s']:.1f} m/s, {row['temp']:.0f}°C - {safe_emoji}")
    
    print("\n✅ Real weather data integration working!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check if API key is activated (can take up to 2 hours)")
    print("2. Verify API key in .env file")
    print("3. Check internet connection")
