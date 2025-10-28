# Design Document: Badminton Wind Predictor

## Overview

The Badminton Wind Predictor is an end-to-end machine learning system that forecasts short-term wind conditions and provides actionable play/don't play recommendations for outdoor badminton.

## Problem Statement

Outdoor badminton is highly sensitive to wind conditions. Even moderate wind (> 1.5 m/s) can significantly impact shuttlecock trajectory and game quality. Players need advance notice of upcoming wind conditions to decide whether to:

- Play now
- Wait for better conditions
- Move indoors

## Design Goals

1. **Actionable forecasts**: Convert numerical predictions into clear decisions
2. **Uncertainty quantification**: Provide not just point estimates but also worst-case scenarios (90th percentile)
3. **Short-term focus**: Optimize for 1-6 hour horizons where statistical models can be competitive
4. **Zero cost**: Runnable on free infrastructure (Colab, HF Spaces)
5. **Reproducible**: Deterministic results for testing and CI

## Data Assumptions

### Input Data

Expected hourly weather observations with:

- **wind_m_s**: Mean wind speed (m/s) - primary target
- **wind_gust_m_s**: Wind gusts (m/s) - useful predictor
- **wind_dir_deg**: Wind direction (degrees) - converted to u/v components
- **pressure**: Atmospheric pressure (hPa) - tendency is predictive
- **temp**: Temperature (°C) - seasonal context
- **humidity**: Relative humidity (%) - weather system indicator
- **precip_mm**: Precipitation (mm) - optional

### Temporal Characteristics

- **Resolution**: Hourly observations
- **Horizons**: 1h, 3h, 6h ahead
- **History**: Use past 24 hours (sequence length) for LSTM
- **Gaps**: Fill gaps up to 3 hours via linear interpolation
- **Stationarity**: Assume local stationarity (wind statistics don't change drastically within the dataset period)

### Synthetic Data

For development and testing, we generate synthetic data with:

- Realistic autocorrelation (random walk with mean reversion)
- Diurnal temperature cycle
- Correlated variables (e.g., gusts proportional to wind speed)
- Deterministic RNG (seed=42) for reproducibility

## Feature Engineering

### Lag Features

Wind exhibits strong autocorrelation. Past values are highly predictive:

- Lags: 1h, 2h, 3h, 6h, 12h, 24h
- Applied to: `wind_m_s` (primary) and `wind_gust_m_s`

### Cyclical Time Encoding

Time has cyclical properties (24h/day, 7 days/week). Use sine/cosine encoding to avoid discontinuity:

- Hour of day: `sin(2π * hour / 24)`, `cos(2π * hour / 24)`
- Day of week: `sin(2π * dow / 7)`, `cos(2π * dow / 7)`
- Day of year: for seasonal patterns

### Pressure Tendency

Rate of pressure change is a classic weather predictor:

- `pressure_tendency = (pressure(t) - pressure(t-3h)) / 3h`

### Wind Direction Components

Convert meteorological direction (degrees) to Cartesian components to avoid 0°/360° discontinuity:

- `wind_u = -wind_speed * sin(direction)` (east-west)
- `wind_v = -wind_speed * cos(direction)` (north-south)

## Model Architecture

### Baseline: Persistence

**Assumption**: Conditions at time `t+h` will be the same as time `t`.

- **Pros**: Simple, no training, strong baseline for short horizons
- **Cons**: Doesn't capture trends or weather system evolution

### LSTM Forecaster

**Architecture**:

```
Input: (batch, 24, n_features)
  ↓
LSTM Layer 1: 32 units, dropout=0.2
  ↓
LSTM Layer 2: 16 units, dropout=0.2
  ↓
Dense outputs: 3 neurons (one per horizon)
```

**Rationale**:

- LSTM captures temporal dependencies and trends
- Multi-output head for simultaneous horizon prediction
- Small architecture (32/16 units) for fast training on CPU/free GPUs
- Dropout for regularization

**Training**:

- Optimizer: Adam (lr=0.001)
- Loss: MSE (mean squared error)
- Early stopping: patience=5 epochs
- Sequence length: 24 hours

**Expected Performance** (on synthetic data):

- Persistence: MAE ~0.3 m/s
- LSTM (50 epochs): MAE ~0.25 m/s

Real-world performance depends heavily on:

- Data quality (sensor accuracy, missing data)
- Weather regime (stable vs. dynamic conditions)
- Station characteristics (terrain, exposure)

## Uncertainty Quantification

### Approach: Simplified Q90 Estimation

Due to computational constraints (single model, fast training), we use a simplified approach:

**Current implementation**: `q90 = median * 1.2`

This is a conservative scaling factor, documented as a limitation.

### Future Enhancements

For production systems:

1. **Ensemble**: Train N models (different seeds/data splits) and compute empirical quantiles
2. **Residual bootstrap**: Use historical residual distribution
3. **Quantile regression**: Train separate models for q10, q50, q90

## Decision Logic

### Safety Thresholds

Based on empirical badminton experience (configurable in `thresholds.json`):

- **Median wind**: ≤ 1.5 m/s (comfortable play)
- **Q90 wind**: ≤ 2.5 m/s (worst-case acceptable)
- **Probability of >3 m/s**: ≤ 10% (optional, if available)

### Decision Rules

**PLAY** if and only if:

1. Median forecast ≤ threshold for ALL horizons, AND
2. Q90 forecast ≤ threshold for ALL horizons

**DON'T PLAY** otherwise, with detailed reason (which horizon/threshold violated)

### Rationale

- Conservative: prioritize avoiding false positives (predicting safe when unsafe)
- Multi-horizon: must be safe for the entire forecast window
- Transparent: provide reasons for decisions

## Evaluation Strategy

### Metrics

- **Point forecasts**: MAE, RMSE, MAPE
- **Probabilistic**: Quantile loss, coverage (% of actuals within prediction interval)
- **Skill score**: Improvement over persistence baseline

### Backtesting

Rolling-window cross-validation:

- Window size: 168 hours (1 week test)
- Step size: 24 hours (1 day)
- Preserves temporal order (no data leakage)

### Acceptance Criteria

- LSTM should beat persistence on 3h/6h horizons (1h is hard to beat)
- 80% coverage for prediction intervals (well-calibrated uncertainty)

## Deployment

### Local Development

1. Generate data: `make data`
2. Train models: `make train`
3. Run inference: `make infer`
4. Launch UI: `make ui`

### Hugging Face Spaces

Gradio app with:

- File upload for custom data
- Fallback to sample data
- Real-time forecast display
- Play/Don't Play decision with explanations

### CI/CD

GitHub Actions:

- Run tests on every push
- Smoke test training (1 epoch, fast)
- Ensure reproducibility

## Known Limitations

1. **Simplified uncertainty**: Uses scaling factor instead of true ensemble
2. **Synthetic data**: Demo uses generated data, not real observations
3. **Small model**: Optimized for speed over accuracy
4. **No NWP integration**: Doesn't use numerical weather prediction inputs
5. **Single station**: Doesn't account for spatial variability

## Future Work

### Short-term

- [ ] Integrate real METAR/observation data
- [ ] Add ensemble uncertainty quantification
- [ ] Improve UI with historical accuracy display
- [ ] Add notification system (email/SMS)

### Long-term

- [ ] Multi-station forecasting
- [ ] Incorporate NWP model data (GFS, HRRR)
- [ ] Attention-based models (Transformer)
- [ ] Active learning (user feedback on decisions)
- [ ] Mobile app

## References

- Weather forecasting basics: persistence as baseline
- Time series forecasting: lag features and autocorrelation
- LSTM for sequences: Hochreiter & Schmidhuber (1997)
- Quantile regression: Koenker & Bassett (1978)
- Wind impact on badminton: empirical player experience

---

**Document Version**: 1.0  
**Last Updated**: 2025-10-28  
**Author**: Badminton Wind Predictor Team
