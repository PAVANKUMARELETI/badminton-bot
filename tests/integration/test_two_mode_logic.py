"""Test the updated bot logic with two modes: NOW vs FORECAST"""
import os
from dotenv import load_dotenv
load_dotenv()

from src.data.weather_api import OpenWeatherMapAPI

# IIIT Lucknow
lat, lon = 26.7984, 81.0241
api_key = os.getenv("OPENWEATHER_API_KEY")

print("=" * 60)
print("TESTING TWO-MODE BOT LOGIC")
print("=" * 60)

weather_api = OpenWeatherMapAPI(api_key)

# Mode 1: Can I play NOW? (Current conditions)
print("\n🏸 MODE 1: Can I Play NOW?")
print("-" * 60)

current_df = weather_api.get_current_weather(lat=lat, lon=lon)
current = current_df.iloc[0].to_dict()

wind_speed = current.get('wind_m_s', 0)
wind_gust = current.get('wind_gust_m_s', 0)

safe_median_wind = 1.5
safe_gust_wind = 3.5

can_play_now = (wind_speed <= safe_median_wind and wind_gust <= safe_gust_wind)

print(f"Current Wind: {wind_speed:.1f} m/s ({wind_speed*3.6:.1f} km/h)")
print(f"Current Gust: {wind_gust:.1f} m/s ({wind_gust*3.6:.1f} km/h)")
print(f"Temperature: {current.get('temp', 0):.1f}°C")
print(f"Humidity: {current.get('humidity', 0):.0f}%")
print(f"\nThresholds: Wind < {safe_median_wind} m/s, Gust < {safe_gust_wind} m/s")

decision_text = "✅ PLAY NOW" if can_play_now else "❌ DON'T PLAY NOW"
print(f"\n{decision_text}")

if not can_play_now:
    reasons = []
    if wind_speed > safe_median_wind:
        reasons.append(f"Wind {wind_speed:.1f} m/s > {safe_median_wind} m/s")
    if wind_gust > safe_gust_wind:
        reasons.append(f"Gust {wind_gust:.1f} m/s > {safe_gust_wind} m/s")
    print(f"Reason: {', '.join(reasons)}")

# Mode 2: Future Forecast (Predictions)
print("\n\n📊 MODE 2: Future Forecast (for planning)")
print("-" * 60)

forecast_df = weather_api.get_hourly_forecast(lat=lat, lon=lon, hours=48)
print(f"Fetched {len(forecast_df)} hours of forecast data")

from src.data.preprocess import build_features
from src.models.lstm_model import LSTMForecaster

features_df = build_features(forecast_df)
print(f"Built features: {features_df.shape}")

model = LSTMForecaster()
model.load("experiments/latest/model.keras")

median_forecast = model.predict_latest(features_df)
q90_forecast = {k: v * 1.2 for k, v in median_forecast.items()}

print("\nPredicted Wind Speed:")
for horizon in ["1h", "3h", "6h"]:
    median = median_forecast[f"horizon_{horizon}"]
    q90 = q90_forecast[f"horizon_{horizon}"]
    safe = (median <= safe_median_wind and q90 <= safe_gust_wind)
    emoji = "✅" if safe else "⚠️"
    print(f"  {emoji} {horizon}: {median:.1f} m/s (gust: {q90:.1f} m/s)")

print("\n" + "=" * 60)
print("KEY DIFFERENCE:")
print("=" * 60)
print("🏸 NOW mode: Based on CURRENT wind (real-time measurement)")
print("📊 FORECAST mode: Based on FUTURE predictions (AI model)")
print("\nThis allows users to:")
print("  • Play immediately if current conditions are good")
print("  • Plan ahead if they want to play in 1-6 hours")
print("=" * 60)
