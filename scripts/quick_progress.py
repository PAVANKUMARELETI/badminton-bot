"""
Quick progress check for Phase 1 data collection.

Shows:
- How many days of data collected
- Total data points
- Progress toward 30-day goal
"""

from pathlib import Path
import csv
from datetime import datetime

log_dir = Path("data/logged_weather")

if not log_dir.exists():
    print("❌ No data yet. Bot will create files when it starts logging.")
else:
    files = sorted(log_dir.glob("weather_*.csv"))
    if not files:
        print("❌ No weather files yet.")
    else:
        total_points = 0
        for f in files:
            with open(f, 'r') as file:
                total_points += sum(1 for _ in csv.DictReader(file))
        
        days = len(files)
        progress = (days / 30) * 100
        
        print("=" * 50)
        print("📊 PHASE 1: DATA COLLECTION PROGRESS")
        print("=" * 50)
        print(f"📅 Days collected: {days}/30 ({progress:.1f}%)")
        print(f"📈 Total data points: {total_points}")
        print(f"⏳ Days remaining: {max(0, 30 - days)}")
        
        bar = "█" * int(progress / 2) + "░" * (50 - int(progress / 2))
        print(f"\n[{bar}]")
        
        if days >= 30:
            print("\n✅ READY TO RETRAIN MODEL!")
        else:
            print(f"\n💡 Keep bot running to collect data!")
        print("=" * 50)
