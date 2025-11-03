"""
Test bot forecast command exactly as it runs on Railway.
This mimics the exact flow the Telegram bot uses.
"""

import logging
import os

# Setup logging like the bot does
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_bot_forecast():
    """Test the exact forecast flow the bot uses."""
    try:
        print("\n=== Testing Bot Forecast Flow ===\n")
        
        # Step 1: Import required modules (like bot does)
        print("1. Importing modules...")
        from src.cli.infer import load_model, make_forecast
        from src.data.fetch import load_sample
        from src.data.preprocess import build_features
        from src.decision.rules import decide_play
        print("   ✅ Imports successful\n")
        
        # Step 2: Load model
        print("2. Loading model...")
        model_path = "experiments/latest/model.keras"
        model = load_model(model_path)
        print(f"   ✅ Model loaded: {type(model)}\n")
        
        # Step 3: Load sample data
        print("3. Loading sample data...")
        df = load_sample()
        print(f"   ✅ Data loaded: {len(df)} rows\n")
        
        # Step 4: Build features
        print("4. Building features...")
        data_df = build_features(df)
        print(f"   ✅ Features built: {data_df.shape}\n")
        
        # Step 5: Make forecast
        print("5. Making forecast...")
        forecast_result = make_forecast(model, data_df)
        print(f"   ✅ Forecast: {forecast_result}\n")
        
        # Step 6: Make decision
        print("6. Making decision...")
        decision_result = decide_play(
            median_forecast=forecast_result["median"],
            q90_forecast=forecast_result["q90"]
        )
        print(f"   ✅ Decision: {decision_result['decision']}")
        print(f"   Reason: {decision_result['reason']}\n")
        
        # Step 7: Format response (like bot does)
        print("7. Formatting response...")
        decision = decision_result["decision"]
        forecast = decision_result["forecast"]
        
        lines = []
        if decision == "PLAY":
            lines.append("✅ *PLAY* - Conditions look good! 🏸")
        else:
            lines.append("❌ *DON'T PLAY* - Wind too strong 🌬️")
        
        lines.append("")
        lines.append("*Wind Forecast:*")
        for horizon, data in forecast.items():
            h = horizon.replace("horizon_", "")
            lines.append(f"• {h}: {data['median']:.1f} m/s (gust: {data['q90']:.1f} m/s)")
        
        response = "\n".join(lines)
        print(f"   ✅ Response formatted:\n{response}\n")
        
        print("✅ ALL STEPS COMPLETED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_bot_forecast()
    exit(0 if success else 1)
