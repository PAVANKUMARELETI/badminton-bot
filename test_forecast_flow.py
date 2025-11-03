"""Test the forecast flow locally"""
import sys
import logging

logging.basicConfig(level=logging.INFO)

try:
    print("1. Loading modules...")
    from src.data.fetch import load_sample
    from src.data.preprocess import build_features
    from src.cli.infer import load_model, make_forecast
    from src.decision.rules import decide_play
    print("   ✅ Modules loaded")

    print("\n2. Loading model...")
    model = load_model("experiments/latest/model.keras")
    print(f"   ✅ Model loaded: {type(model)}")

    print("\n3. Loading sample data...")
    df = load_sample()
    print(f"   ✅ Data loaded: {len(df)} rows")

    print("\n4. Building features...")
    data_df = build_features(df)
    print(f"   ✅ Features built: {data_df.shape}")

    print("\n5. Making forecast...")
    forecast_result = make_forecast(model, data_df)
    print(f"   ✅ Forecast made:")
    print(f"      Median: {forecast_result['median']}")
    print(f"      Q90: {forecast_result['q90']}")

    print("\n6. Making decision...")
    decision_result = decide_play(
        median_forecast=forecast_result["median"],
        q90_forecast=forecast_result["q90"]
    )
    print(f"   ✅ Decision: {decision_result['decision']}")
    print(f"      Reason: {decision_result.get('reason', 'N/A')}")

    print("\n✅ ALL TESTS PASSED!")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
