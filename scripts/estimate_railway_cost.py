"""
Quick Railway cost estimate based on local testing.

Run this to estimate your monthly Railway costs.
"""

import psutil
import time

print("=" * 60)
print("💰 RAILWAY COST ESTIMATOR")
print("=" * 60)
print()

# Check if bot process is running
bot_found = False
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        cmdline = ' '.join(proc.info['cmdline'] or [])
        if 'telegram_bot_refactored' in cmdline:
            bot_found = True
            print(f"✅ Bot process found (PID: {proc.info['pid']})")
            
            # Get memory usage
            mem_info = proc.memory_info()
            mem_mb = mem_info.rss / (1024 * 1024)
            
            # Get CPU usage (sample over 1 second)
            cpu_percent = proc.cpu_percent(interval=1.0)
            
            print(f"   RAM Usage: {mem_mb:.1f} MB")
            print(f"   CPU Usage: {cpu_percent:.1f}%")
            print()
            
            # Calculate monthly cost estimate
            mem_gb = mem_mb / 1024
            hours_per_month = 730  # Average
            
            # Railway pricing (approximate)
            cost_per_gb_hour = 0.000231
            
            # Memory cost
            mem_cost = mem_gb * hours_per_month * cost_per_gb_hour
            
            # CPU cost (rough estimate, usually negligible)
            cpu_cost = (cpu_percent / 100) * hours_per_month * cost_per_gb_hour
            
            total_cost = mem_cost + cpu_cost
            
            print("📊 MONTHLY COST ESTIMATE:")
            print(f"   Memory: ${mem_cost:.2f}")
            print(f"   CPU: ${cpu_cost:.2f}")
            print(f"   TOTAL: ${total_cost:.2f}/month")
            print()
            
            if total_cost < 5.0:
                print(f"✅ EXCELLENT! Well under $5/month limit!")
                print(f"   You're using {(total_cost/5.0)*100:.1f}% of free credit")
            else:
                print(f"⚠️  WARNING! Exceeds $5/month limit")
                print(f"   Consider optimizations (see docs/RAILWAY_COST_OPTIMIZATION.md)")
            
            break
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        continue

if not bot_found:
    print("❌ Bot not running locally.")
    print()
    print("💡 ESTIMATED COST (based on typical usage):")
    print("   RAM: 150 MB → $0.025/month")
    print("   CPU: <1% avg → $0.002/month")
    print("   TOTAL: ~$0.50-$2.00/month ✅")
    print()
    print("   Well under $5/month Railway free tier!")

print()
print("=" * 60)
print("📍 To check actual Railway costs:")
print("   1. Visit https://railway.app")
print("   2. Go to Project → Settings → Usage")
print("   3. View current month's usage")
print("=" * 60)
