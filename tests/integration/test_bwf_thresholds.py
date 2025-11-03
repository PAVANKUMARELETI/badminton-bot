"""Test BWF-compliant thresholds with various wind scenarios"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.decision.rules import decide_play

print("=" * 70)
print("TESTING BWF-COMPLIANT THRESHOLDS")
print("=" * 70)
print("\nBWF Standards:")
print("  • Optimal wind: 6-12 km/h (1.67-3.33 m/s)")
print("  • Maximum safe: 12 km/h (3.33 m/s)")
print("\nBot Thresholds:")
print("  • Median max: 3.33 m/s (12 km/h)")
print("  • Q90 max: 5.0 m/s (18 km/h)")
print("=" * 70)

# Test scenarios
scenarios = [
    # (median_m/s, q90_m/s, expected_decision, description)
    (0.5, 0.8, "PLAY", "Very calm - 0.5 m/s (1.8 km/h) - Below optimal"),
    (1.0, 1.5, "PLAY", "Calm - 1.0 m/s (3.6 km/h) - Below optimal"),
    (1.67, 2.0, "PLAY", "Lower optimal - 1.67 m/s (6.0 km/h) - BWF minimum optimal"),
    (2.0, 2.5, "PLAY", "Good - 2.0 m/s (7.2 km/h) - Within optimal range"),
    (2.5, 3.0, "PLAY", "Good - 2.5 m/s (9.0 km/h) - Within optimal range"),
    (3.0, 3.5, "PLAY", "Upper optimal - 3.0 m/s (10.8 km/h) - Within optimal range"),
    (3.33, 4.5, "PLAY", "Max safe - 3.33 m/s (12 km/h) - BWF maximum"),
    (3.5, 5.0, "DON'T PLAY", "Too windy - 3.5 m/s (12.6 km/h) - Above BWF max"),
    (4.0, 5.5, "DON'T PLAY", "Too windy - 4.0 m/s (14.4 km/h) - Above BWF max"),
    (5.0, 6.0, "DON'T PLAY", "Very windy - 5.0 m/s (18 km/h) - Well above BWF max"),
    (2.0, 5.5, "DON'T PLAY", "Calm but gusty - Median OK but Q90 too high"),
]

print("\n🧪 RUNNING TEST SCENARIOS:")
print("-" * 70)

passed = 0
failed = 0

for median, q90, expected, description in scenarios:
    result = decide_play(
        median_forecast={"horizon_1h": median, "horizon_3h": median, "horizon_6h": median},
        q90_forecast={"horizon_1h": q90, "horizon_3h": q90, "horizon_6h": q90}
    )
    
    actual = result["decision"]
    success = (actual == expected)
    
    if success:
        emoji = "✅"
        passed += 1
    else:
        emoji = "❌"
        failed += 1
    
    # Format output
    median_kmh = median * 3.6
    q90_kmh = q90 * 3.6
    
    print(f"\n{emoji} {description}")
    print(f"   Wind: {median:.2f} m/s ({median_kmh:.1f} km/h) | Gust: {q90:.2f} m/s ({q90_kmh:.1f} km/h)")
    print(f"   Expected: {expected} | Actual: {actual}", end="")
    
    if not success:
        print(f" ❌ FAILED!")
        if result.get("details", {}).get("reason"):
            print(f"   Reason: {result['details']['reason']}")
    else:
        print(f" ✅")

print("\n" + "=" * 70)
print(f"TEST RESULTS: {passed} passed, {failed} failed")
print("=" * 70)

if failed == 0:
    print("\n🎉 ALL TESTS PASSED! BWF thresholds working correctly.")
    print("\n✅ Ready to push to GitHub!")
else:
    print(f"\n⚠️  {failed} test(s) failed. Please review before pushing.")

print("\n" + "=" * 70)
print("KEY IMPROVEMENTS FROM OLD THRESHOLDS:")
print("=" * 70)
print("\nScenario: Wind at 2.0 m/s (7.2 km/h)")
print("  OLD (1.5 m/s threshold): ❌ DON'T PLAY (too conservative)")
print("  NEW (3.33 m/s threshold): ✅ PLAY (BWF compliant)")
print("\nScenario: Wind at 3.0 m/s (10.8 km/h)")
print("  OLD (1.5 m/s threshold): ❌ DON'T PLAY (false negative)")
print("  NEW (3.33 m/s threshold): ✅ PLAY (correct - within BWF optimal)")
print("=" * 70)
