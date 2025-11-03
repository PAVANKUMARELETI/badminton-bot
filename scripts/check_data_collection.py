"""
Check weather data collection status and retrain model when ready.

This script:
1. Checks accumulated weather observations
2. Reports collection progress
3. Retrains model if sufficient data is available (30+ days)

Usage:
    python scripts/check_data_collection.py
    python scripts/check_data_collection.py --retrain  # Force retrain if ready
"""
import sys
from pathlib import Path
import argparse
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data.weather_logger import get_dataset_info, load_historical_data
from src.data.preprocess import build_features
from src.models.lstm_model import LSTMForecaster
from src.config import LATEST_MODEL_DIR
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def display_progress(info: dict):
    """Display data collection progress."""
    print("\n" + "=" * 70)
    print("📊 WEATHER DATA COLLECTION STATUS")
    print("=" * 70)
    
    if not info['exists'] or info['count'] == 0:
        print("\n❌ No data collected yet")
        print("\n💡 Tip: Use the Telegram bot to start collecting data.")
        print("   Each time you check weather, observations are saved automatically.")
        return
    
    print(f"\n✅ Data collection active!")
    print(f"\n📈 Current Progress:")
    print(f"   • Total observations: {info['count']}")
    print(f"   • Start date: {info['start_date']}")
    print(f"   • End date: {info['end_date']}")
    print(f"   • Days of data: {info['days']:.1f} days")
    
    # Progress bar
    target_days = 30
    progress = min(info['days'] / target_days * 100, 100)
    bar_length = 40
    filled = int(bar_length * progress / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    
    print(f"\n🎯 Progress to training readiness (30 days):")
    print(f"   [{bar}] {progress:.1f}%")
    
    if info['ready_for_training']:
        print(f"\n🎉 READY FOR TRAINING!")
        print(f"   ✅ Sufficient data collected ({info['days']:.1f} days)")
        print(f"   ✅ Sufficient observations ({info['count']})")
        print(f"\n🚀 Run: python scripts/check_data_collection.py --retrain")
    else:
        days_remaining = max(0, target_days - info['days'])
        print(f"\n⏳ Not ready yet:")
        if info['days'] < 30:
            print(f"   • Need {days_remaining:.1f} more days of data")
        if info['count'] < 500:
            print(f"   • Need {500 - info['count']} more observations")
        print(f"\n💡 Keep using the bot! Data is being collected automatically.")
    
    print("=" * 70)


def retrain_model(force: bool = False):
    """Retrain model on collected data if ready."""
    info = get_dataset_info()
    
    if not info['ready_for_training'] and not force:
        logger.warning("Not enough data for training yet")
        logger.info(f"Current: {info['days']:.1f} days, {info['count']} observations")
        logger.info("Need: 30 days and 500+ observations")
        return False
    
    logger.info("=" * 70)
    logger.info("🚀 RETRAINING MODEL ON COLLECTED DATA")
    logger.info("=" * 70)
    
    # Load collected data
    logger.info("📊 Loading historical observations...")
    df = load_historical_data()
    logger.info(f"Loaded {len(df)} observations")
    logger.info(f"Date range: {df.index.min()} to {df.index.max()}")
    
    # Build features
    logger.info("\n🔧 Building features...")
    data_df = build_features(df)
    logger.info(f"Features created: {data_df.shape}")
    
    # Train model
    logger.info("\n🧠 Training LSTM model...")
    model = LSTMForecaster()
    model.fit(data_df, epochs=50)
    
    # Save model
    logger.info(f"\n💾 Saving model to {LATEST_MODEL_DIR}...")
    LATEST_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    
    model_path = LATEST_MODEL_DIR / "model.keras"
    model.save(str(model_path))
    
    # Save metadata
    metadata_path = LATEST_MODEL_DIR / "training_metadata.txt"
    with open(metadata_path, 'w') as f:
        f.write(f"Training Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Data Source: Collected real observations\n")
        f.write(f"Training Data: {len(df)} observations\n")
        f.write(f"Date Range: {df.index.min()} to {df.index.max()}\n")
        f.write(f"Days of Data: {info['days']:.1f}\n")
        f.write(f"Features: {len(data_df.columns)}\n")
        f.write(f"Epochs: 50\n")
    
    logger.info(f"✅ Metadata saved to {metadata_path}")
    
    print("\n" + "=" * 70)
    print("✅ MODEL RETRAINING COMPLETE!")
    print("=" * 70)
    print(f"📂 Model: {model_path}")
    print(f"📊 Trained on: {len(df)} real observations")
    print(f"📅 Data span: {info['days']:.1f} days")
    print(f"🎯 Features: {len(model.feature_cols)}")
    print("\n🚀 Deploy: git add . && git commit -m 'Update to real-data model' && git push")
    print("=" * 70)
    
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check data collection status and retrain model"
    )
    parser.add_argument(
        '--retrain',
        action='store_true',
        help='Retrain model if data is ready'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force retrain even if not enough data'
    )
    
    args = parser.parse_args()
    
    # Get collection info
    info = get_dataset_info()
    
    # Display progress
    display_progress(info)
    
    # Retrain if requested
    if args.retrain:
        print("\n")
        success = retrain_model(force=args.force)
        if not success:
            sys.exit(1)


if __name__ == "__main__":
    main()
