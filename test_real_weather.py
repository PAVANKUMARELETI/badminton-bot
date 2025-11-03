"""
Test using real weather data from OpenWeatherMap API
"""
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_real_weather_forecast():
    """Test complete flow with real weather data."""
    try:
        print("\n=== Testing Real Weather API Flow ===\n")
        
        # Import modules
        from src.data.weather_api import OpenWeatherMapAPI
        from src.data.preprocess import build_features
        from src.cli.infer import load_model, make_forecast
        from src.decision.rules import decide_play
        
        # Get API key
        api_key = os.getenv("OPENWEATHER_API_KEY")
        print(f"1. API Key: {api_key[:10]}..." if api_key else "No API key!")
        
        # IIIT Lucknow coordinates
        lat = 26.7984
        lon = 81.0241
        
        # Fetch real weather data
        print(f"\n2. Fetching weather for IIIT Lucknow ({lat}, {lon})...")
        weather_api = OpenWeatherMapAPI(api_key)
        df = weather_api.get_hourly_forecast(lat=lat, lon=lon, hours=48)
        print(f"   ✅ Fetched {len(df)} hours of data")
        print(f"   Columns: {list(df.columns)}")
        print(f"\n   First row:")
        print(df.head(1))
        
        # Build features
        print("\n3. Building features...")
        data_df = build_features(df)
        print(f"   ✅ Features built: {data_df.shape}")
        
        # Load model
        print("\n4. Loading model...")
        model = load_model("experiments/latest/model.keras")
        print(f"   ✅ Model loaded")
        
        # Make forecast
        print("\n5. Making forecast...")
        forecast_result = make_forecast(model, data_df)
        print(f"   ✅ Forecast: {forecast_result}")
        
        # Make decision
        print("\n6. Making decision...")
        decision = decide_play(
            median_forecast=forecast_result["median"],
            q90_forecast=forecast_result["q90"]
        )
        print(f"   ✅ Decision: {decision['decision']}")
        print(f"   Reason: {decision['reason']}")
        
        print("\n✅ SUCCESS! Real weather data works!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_real_weather_forecast()
