# Threshold Update Summary

## Date
$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## Changes Made
Updated wind speed thresholds from conservative values to BWF (Badminton World Federation) standards.

### Old Thresholds (Too Conservative)
- **Median wind**: 1.5 m/s (5.4 km/h)
- **Gust wind**: 2.5 m/s (9.0 km/h)
- **Issue**: Below BWF optimal minimum of 6 km/h, rejecting safe playing conditions

### New Thresholds (BWF Compliant)
- **Median wind**: 3.33 m/s (12 km/h) ✅
- **Gust wind**: 5.0 m/s (18 km/h) ✅
- **Complies with**: BWF AirBadminton official recommendations

## Files Modified

1. **`src/config.py`**
   - Updated `DEFAULT_THRESHOLDS["play"]["median_max_m_s"]` from 1.5 to 3.33
   - Updated `DEFAULT_THRESHOLDS["play"]["q90_max_m_s"]` from 2.5 to 5.0
   - Added BWF reference comments

2. **`src/integrations/telegram_bot.py`**
   - Updated `safe_median_wind` from 1.5 to 3.33 in `play_now_command()`
   - Updated `safe_gust_wind` from 3.5 to 5.0
   - Updated help message with BWF-compliant thresholds
   - Added BWF standards reference in help text

3. **`src/decision/thresholds.json`**
   - Updated runtime thresholds to match new standards

4. **`docs/BWF_STANDARDS.md`** (NEW)
   - Created comprehensive documentation of BWF standards
   - Includes conversion tables
   - Explains decision logic for both NOW and FORECAST modes

## Impact

### Before (Conservative Approach)
```
Wind: 2.0 m/s (7.2 km/h)
Decision: ❌ DON'T PLAY (exceeded 1.5 m/s threshold)
Reality: Safe to play according to BWF (within 6-12 km/h optimal range)
```

### After (BWF-Compliant)
```
Wind: 2.0 m/s (7.2 km/h)
Decision: ✅ PLAY (within 3.33 m/s threshold)
Reality: Safe to play according to BWF (within 6-12 km/h optimal range)
```

## Testing Needed
- [ ] Test NOW mode with winds around 2-3 m/s (should now say PLAY)
- [ ] Test FORECAST mode with predictions around 2-3 m/s
- [ ] Verify help message displays correctly
- [ ] Ensure decisions align with BWF standards

## Deployment Steps
1. Commit changes to git
2. Push to GitHub (triggers Railway auto-deploy)
3. Monitor bot behavior in production
4. Validate with real-world conditions

## References
- BWF AirBadminton Guidelines: https://airbadminton.bwf.sport/
- Optimal wind: 6-12 km/h (1.67-3.33 m/s)
- Maximum safe: 12 km/h (3.33 m/s)
