"""
Test enhanced feature engineering with real weather API data.
"""
import os
from dotenv import load_dotenv
load_dotenv()

from src.data.weather_api import OpenWeatherMapAPI
from src.data.preprocess import build_features, get_feature_columns

# Get API key
api_key = os.getenv("OPENWEATHER_API_KEY")
print(f"API Key: {api_key[:10]}...")

# IIIT Lucknow coordinates
lat, lon = 26.7984, 81.0241

# Fetch real weather data
print(f"\n🌐 Fetching weather data for IIIT Lucknow ({lat}, {lon})...")
weather_api = OpenWeatherMapAPI(api_key)

# Get current weather
current = weather_api.get_current_weather(lat=lat, lon=lon)
print(f"\n📊 Current weather:")
print(current)
print(f"\nColumns: {current.columns.tolist()}")

# Get forecast
forecast = weather_api.get_hourly_forecast(lat=lat, lon=lon, hours=48)
print(f"\n🔮 Forecast data: {len(forecast)} hours")
print(f"Columns: {forecast.columns.tolist()}")
print(f"\nFirst few rows:")
print(forecast.head())

# Build features
print(f"\n🔧 Building enhanced features...")
features_df = build_features(forecast)
print(f"\n✅ Features built: {features_df.shape}")

# Get feature columns
feature_cols = get_feature_columns(features_df, exclude_target=True)
print(f"\n📋 Selected features ({len(feature_cols)} total):")
for i, col in enumerate(feature_cols, 1):
    print(f"  {i:2d}. {col}")

# Show sample of features
print(f"\n📊 Sample of feature values:")
print(features_df[feature_cols[:5]].head(3))

print("\n✅ Enhanced feature engineering test PASSED!")
