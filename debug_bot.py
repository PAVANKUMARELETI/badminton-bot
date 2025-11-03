"""
Debug script to test if the bot can load the model and make predictions locally.
Run this to identify the issue before deploying.
"""

import os
import sys

print("=" * 60)
print("Badminton Bot Debug Test")
print("=" * 60)

# Test 1: Check environment
print("\n1. Environment Check:")
print(f"   Python: {sys.version}")
print(f"   Working Directory: {os.getcwd()}")
print(f"   TELEGRAM_BOT_TOKEN: {'Set' if os.getenv('TELEGRAM_BOT_TOKEN') else 'NOT SET'}")

# Test 2: Import dependencies
print("\n2. Import Check:")
try:
    import tensorflow as tf
    print(f"   ✅ TensorFlow {tf.__version__}")
except Exception as e:
    print(f"   ❌ TensorFlow: {e}")

try:
    import pandas as pd
    print(f"   ✅ Pandas {pd.__version__}")
except Exception as e:
    print(f"   ❌ Pandas: {e}")

try:
    from telegram import Bot
    print(f"   ✅ python-telegram-bot")
except Exception as e:
    print(f"   ❌ python-telegram-bot: {e}")

# Test 3: Check model file
print("\n3. Model File Check:")
model_path = "experiments/latest/model.keras"
scaler_path = "experiments/latest/scaler.npz"

if os.path.exists(model_path):
    size_mb = os.path.getsize(model_path) / (1024 * 1024)
    print(f"   ✅ Model found: {model_path} ({size_mb:.2f} MB)")
else:
    print(f"   ❌ Model NOT found: {model_path}")

if os.path.exists(scaler_path):
    print(f"   ✅ Scaler found: {scaler_path}")
else:
    print(f"   ❌ Scaler NOT found: {scaler_path}")

# Test 4: Load model
print("\n4. Model Loading Test:")
try:
    from src.utils.io import load_model
    model = load_model(model_path)
    print(f"   ✅ Model loaded successfully")
    print(f"   Model type: {type(model)}")
except Exception as e:
    print(f"   ❌ Model loading failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Make a test prediction
print("\n5. Prediction Test:")
try:
    from src.cli.infer import run_inference
    
    # Create test data
    from src.data.fetch import load_sample
    df = load_sample()
    
    result = run_inference(model_path, data_source="sample")
    print(f"   ✅ Inference successful!")
    print(f"   Sample forecast: {result}")
except Exception as e:
    print(f"   ❌ Prediction failed: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Test bot initialization
print("\n6. Bot Initialization Test:")
try:
    from src.integrations.telegram_bot import TelegramBot
    
    # Check if token exists
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("   ⚠️  TELEGRAM_BOT_TOKEN not set - skipping bot init")
    else:
        bot = TelegramBot(model_path=model_path)
        print(f"   ✅ Bot initialized successfully")
except Exception as e:
    print(f"   ❌ Bot initialization failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Debug test complete!")
print("=" * 60)
