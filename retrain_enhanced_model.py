"""
Retrain model with enhanced weather features (temp, humidity).

This script:
1. Loads sample training data
2. Builds enhanced features (including temp/humidity lags)
3. Trains a new LSTM model
4. Saves it to experiments/latest/
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.data.fetch import load_sample
from src.data.preprocess import build_features
from src.models.lstm_model import LSTMForecaster
from src.config import LATEST_MODEL_DIR
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Retrain model with enhanced features."""
    
    # Load sample data
    logger.info("📊 Loading sample data...")
    df = load_sample()
    logger.info(f"Loaded {len(df)} samples")
    
    # Build enhanced features
    logger.info("🔧 Building enhanced features (including temp/humidity)...")
    data_df = build_features(df)
    logger.info(f"Features created: {data_df.shape}")
    logger.info(f"Columns: {data_df.columns.tolist()}")
    
    # Initialize model
    logger.info("🧠 Initializing LSTM model...")
    model = LSTMForecaster()
    
    # Train model (will auto-split train/val)
    logger.info("🏋️ Training model with enhanced features...")
    model.fit(data_df, epochs=20)  # Quick training
    
    # Save model
    logger.info(f"💾 Saving enhanced model to {LATEST_MODEL_DIR}...")
    LATEST_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    
    model_path = LATEST_MODEL_DIR / "model.keras"
    scaler_path = LATEST_MODEL_DIR / "scaler.npz"
    
    model.save(str(model_path))
    logger.info(f"✅ Model saved to {model_path}")
    logger.info(f"✅ Scaler saved to {scaler_path}")
    
    # Test prediction
    logger.info("🧪 Testing prediction with enhanced features...")
    forecast = model.predict_latest(data_df)
    logger.info(f"Test forecast: {forecast}")
    
    print("\n✅ Model retrained successfully with enhanced features!")
    print(f"📂 Model location: {model_path}")
    print(f"🎯 Features used: {len(model.feature_cols)}")
    print(f"📋 Feature list: {model.feature_cols[:10]}...")

if __name__ == "__main__":
    main()
