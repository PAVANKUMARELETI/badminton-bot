# BWF Wind Speed Standards for Badminton

## Overview
This document outlines the official wind speed recommendations from the Badminton World Federation (BWF) for their AirBadminton game and how they're applied in this bot.

## BWF Official Standards

### Maximum Wind Speed
- **12 km/h (3.33 m/s)** - Maximum recommended wind speed for safe play

### Optimal Playing Conditions
- **6-12 km/h (1.67-3.33 m/s)** - Ideal wind speed range for optimal play
- Below 6 km/h: Very calm, minimal wind interference
- Above 12 km/h: Wind may affect shuttlecock trajectory too much

## Implementation in This Bot

### Current Thresholds
Based on BWF standards, we use the following thresholds:

```python
{
    "median_max_m_s": 3.33,  # 12 km/h - BWF maximum
    "q90_max_m_s": 5.0,       # ~18 km/h - Allow some margin for gusts
    "prob_over_3m_s_max": 0.1
}
```

### Decision Logic

#### NOW Mode (Current Weather)
- **PLAY**: Wind ≤ 3.33 m/s (12 km/h) AND Gusts ≤ 5.0 m/s (18 km/h)
- **DON'T PLAY**: Wind > 3.33 m/s OR Gusts > 5.0 m/s

#### FORECAST Mode (Future Predictions)
- **PLAY**: Median forecast ≤ 3.33 m/s AND Q90 (gusts) ≤ 5.0 m/s
- **DON'T PLAY**: Median forecast > 3.33 m/s OR Q90 > 5.0 m/s

## Comparison with Previous Thresholds

### Old (Conservative)
- Median: 1.5 m/s (5.4 km/h) ❌ Too strict
- Gusts: 3.5 m/s (12.6 km/h)

### New (BWF Compliant)
- Median: 3.33 m/s (12 km/h) ✅ Matches BWF standards
- Gusts: 5.0 m/s (18 km/h) ✅ Reasonable margin for safety

## Conversions Reference

| m/s  | km/h | mph  | Description          |
|------|------|------|---------------------|
| 1.67 | 6.0  | 3.7  | BWF Minimum Optimal |
| 3.33 | 12.0 | 7.5  | BWF Maximum         |
| 5.0  | 18.0 | 11.2 | Bot Gust Threshold  |

## Formula
- **m/s to km/h**: multiply by 3.6
- **km/h to m/s**: divide by 3.6

## References
- BWF AirBadminton Official Guidelines
- [AirBadminton Website](https://airbadminton.bwf.sport/)

## Notes
- These thresholds are specifically for **outdoor** badminton (AirBadminton)
- Indoor badminton should have minimal wind (< 0.5 m/s)
- Local conditions may vary - use your judgment
- The bot adds a small safety margin for gusts (5.0 m/s vs 3.33 m/s)
