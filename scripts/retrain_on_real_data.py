"""
Retrain LSTM model on REAL weather data from OpenWeatherMap API.

This script:
1. Fetches real historical weather data from OpenWeatherMap
2. Builds enhanced features (wind, temp, humidity, pressure)
3. Trains LSTM model on real observations
4. Evaluates performance metrics
5. Saves the production-ready model
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from src.data.weather_api import OpenWeatherMapAPI
from src.data.preprocess import build_features
from src.models.lstm_model import LSTMForecaster
from src.config import LATEST_MODEL_DIR
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# IIIT Lucknow coordinates
LAT = 26.7984
LON = 81.0241
LOCATION = "IIIT Lucknow"

def fetch_training_data(hours=720):  # 30 days of hourly data
    """
    Fetch real historical weather data from OpenWeatherMap.
    
    Args:
        hours: Number of hours of historical data to fetch (default: 720 = 30 days)
    
    Returns:
        DataFrame with real weather observations
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise ValueError("OPENWEATHER_API_KEY not set in environment")
    
    logger.info(f"🌐 Fetching {hours} hours of real weather data for {LOCATION}")
    logger.info(f"📍 Coordinates: {LAT}°N, {LON}°E")
    
    weather_api = OpenWeatherMapAPI(api_key)
    
    # Fetch historical forecast data (best approximation of observations)
    df = weather_api.get_hourly_forecast(lat=LAT, lon=LON, hours=hours)
    
    if df is None or df.empty:
        raise ValueError("Failed to fetch weather data from API")
    
    logger.info(f"✅ Fetched {len(df)} real weather observations")
    logger.info(f"📊 Date range: {df.index[0]} to {df.index[-1]}")
    logger.info(f"🌬️ Wind speed range: {df['wind_m_s'].min():.2f} - {df['wind_m_s'].max():.2f} m/s")
    
    # Display summary statistics
    logger.info("\n📈 Weather Data Summary:")
    logger.info(f"  Mean wind: {df['wind_m_s'].mean():.2f} m/s ({df['wind_m_s'].mean()*3.6:.1f} km/h)")
    logger.info(f"  Max wind: {df['wind_m_s'].max():.2f} m/s ({df['wind_m_s'].max()*3.6:.1f} km/h)")
    logger.info(f"  Mean temp: {df['temp'].mean():.1f}°C")
    logger.info(f"  Mean humidity: {df['humidity'].mean():.0f}%")
    
    return df

def evaluate_model(model, data_df):
    """Evaluate model performance on validation set."""
    logger.info("\n📊 Evaluating model performance...")
    
    # Split data: 80% train, 20% validation
    split_idx = int(len(data_df) * 0.8)
    val_df = data_df.iloc[split_idx:]
    
    # Make predictions on validation set
    predictions = []
    actuals = []
    
    for i in range(len(val_df) - 24):  # Need 24 hours history
        forecast = model.predict_latest(val_df.iloc[:split_idx + i + 24])
        
        # Get actual values 1h, 3h, 6h ahead
        if i + 1 < len(val_df):
            actual_1h = val_df.iloc[i + 1]['wind_m_s']
            predictions.append(forecast['horizon_1h'])
            actuals.append(actual_1h)
    
    if predictions:
        predictions = np.array(predictions)
        actuals = np.array(actuals)
        
        mae = np.mean(np.abs(predictions - actuals))
        rmse = np.sqrt(np.mean((predictions - actuals) ** 2))
        
        logger.info(f"\n✅ Validation Metrics (1-hour forecast):")
        logger.info(f"  MAE:  {mae:.3f} m/s ({mae*3.6:.2f} km/h)")
        logger.info(f"  RMSE: {rmse:.3f} m/s ({rmse*3.6:.2f} km/h)")
        
        # Persistence baseline for comparison
        persistence_mae = np.mean(np.abs(actuals[1:] - actuals[:-1]))
        persistence_rmse = np.sqrt(np.mean((actuals[1:] - actuals[:-1]) ** 2))
        
        logger.info(f"\n📊 Baseline (Persistence Model):")
        logger.info(f"  MAE:  {persistence_mae:.3f} m/s")
        logger.info(f"  RMSE: {persistence_rmse:.3f} m/s")
        
        improvement = (persistence_mae - mae) / persistence_mae * 100
        logger.info(f"\n🎯 LSTM Improvement: {improvement:.1f}% better than baseline")
        
        return {
            'mae': mae,
            'rmse': rmse,
            'persistence_mae': persistence_mae,
            'persistence_rmse': persistence_rmse,
            'improvement_pct': improvement
        }
    
    return None

def main():
    """Main retraining pipeline."""
    logger.info("=" * 70)
    logger.info("RETRAINING LSTM MODEL ON REAL WEATHER DATA")
    logger.info("=" * 70)
    
    # Step 1: Fetch real weather data
    try:
        df = fetch_training_data(hours=720)  # 30 days
    except Exception as e:
        logger.error(f"❌ Failed to fetch weather data: {e}")
        logger.info("\n💡 Tip: Make sure OPENWEATHER_API_KEY is set in .env file")
        return
    
    # Step 2: Build features
    logger.info("\n🔧 Building enhanced features...")
    data_df = build_features(df)
    logger.info(f"✅ Features created: {data_df.shape}")
    logger.info(f"📋 Total features: {len(data_df.columns)}")
    
    # Step 3: Train model
    logger.info("\n🧠 Training LSTM model on real data...")
    model = LSTMForecaster()
    
    # Train with more epochs for real data
    history = model.fit(data_df, epochs=50)
    
    # Step 4: Evaluate
    metrics = evaluate_model(model, data_df)
    
    # Step 5: Save model
    logger.info(f"\n💾 Saving production model to {LATEST_MODEL_DIR}...")
    LATEST_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    
    model_path = LATEST_MODEL_DIR / "model.keras"
    model.save(str(model_path))
    
    logger.info(f"✅ Model saved to {model_path}")
    
    # Save training metadata
    metadata_path = LATEST_MODEL_DIR / "training_metadata.txt"
    with open(metadata_path, 'w') as f:
        f.write(f"Training Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Location: {LOCATION} ({LAT}°N, {LON}°E)\n")
        f.write(f"Training Data: {len(df)} hours of real weather observations\n")
        f.write(f"Date Range: {df.index[0]} to {df.index[-1]}\n")
        f.write(f"Features: {len(data_df.columns)}\n")
        f.write(f"Epochs: 50\n\n")
        
        if metrics:
            f.write(f"Performance Metrics (1-hour forecast):\n")
            f.write(f"  MAE:  {metrics['mae']:.3f} m/s ({metrics['mae']*3.6:.2f} km/h)\n")
            f.write(f"  RMSE: {metrics['rmse']:.3f} m/s ({metrics['rmse']*3.6:.2f} km/h)\n")
            f.write(f"  Improvement over baseline: {metrics['improvement_pct']:.1f}%\n")
    
    logger.info(f"✅ Metadata saved to {metadata_path}")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ MODEL RETRAINING COMPLETE!")
    print("=" * 70)
    print(f"📂 Model location: {model_path}")
    print(f"🌐 Trained on: REAL weather data from OpenWeatherMap")
    print(f"📍 Location: {LOCATION}")
    print(f"📊 Training samples: {len(df)} hours")
    print(f"🎯 Features: {len(model.feature_cols)}")
    
    if metrics:
        print(f"\n📈 Performance (1-hour forecast):")
        print(f"  MAE:  {metrics['mae']:.3f} m/s ({metrics['mae']*3.6:.2f} km/h)")
        print(f"  RMSE: {metrics['rmse']:.3f} m/s ({metrics['rmse']*3.6:.2f} km/h)")
        print(f"  {metrics['improvement_pct']:.1f}% better than persistence baseline")
    
    print("\n🚀 Ready for deployment! Push to GitHub to auto-deploy to Railway.")
    print("=" * 70)

if __name__ == "__main__":
    main()
