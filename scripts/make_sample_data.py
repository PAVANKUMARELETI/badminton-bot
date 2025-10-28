"""
Generate synthetic hourly weather data for testing and development.

This script creates a deterministic sample dataset with realistic-looking
weather patterns using random walks and correlations.
"""

import numpy as np
import pandas as pd

from src.config import (
    DATA_DIR,
    RANDOM_SEED,
    SAMPLE_DATA_PATH,
    SAMPLE_DATA_SIZE,
    SYNTH_GUST_MULTIPLIER,
    SYNTH_HUMIDITY_MEAN,
    SYNTH_HUMIDITY_STD,
    SYNTH_PRESSURE_MEAN,
    SYNTH_PRESSURE_STD,
    SYNTH_TEMP_MEAN,
    SYNTH_TEMP_STD,
    SYNTH_WIND_MEAN,
    SYNTH_WIND_STD,
)


def generate_synthetic_weather_data(
    n_records: int = SAMPLE_DATA_SIZE, seed: int = RANDOM_SEED
) -> pd.DataFrame:
    """
    Generate synthetic hourly weather data using random walks.

    The data has realistic autocorrelation and cross-correlations between variables.

    Args:
        n_records: Number of hourly records to generate
        seed: Random seed for reproducibility

    Returns:
        pd.DataFrame: Synthetic weather data
    """
    rng = np.random.RandomState(seed)

    # Create hourly timestamps starting from a fixed date
    start_date = pd.Timestamp("2024-01-01 00:00:00")
    timestamps = pd.date_range(start=start_date, periods=n_records, freq="1H")

    # Initialize arrays
    wind = np.zeros(n_records)
    wind_gust = np.zeros(n_records)
    wind_dir = np.zeros(n_records)
    pressure = np.zeros(n_records)
    temp = np.zeros(n_records)
    humidity = np.zeros(n_records)
    precip = np.zeros(n_records)

    # Set initial values
    wind[0] = SYNTH_WIND_MEAN
    wind_dir[0] = rng.uniform(0, 360)
    pressure[0] = SYNTH_PRESSURE_MEAN
    temp[0] = SYNTH_TEMP_MEAN
    humidity[0] = SYNTH_HUMIDITY_MEAN

    # Generate data using random walks with mean reversion
    # This creates autocorrelation (realistic weather persistence)

    for i in range(1, n_records):
        # Wind speed: random walk with mean reversion
        wind_change = rng.normal(0, SYNTH_WIND_STD * 0.3)
        wind[i] = wind[i - 1] + wind_change + 0.1 * (SYNTH_WIND_MEAN - wind[i - 1])
        wind[i] = max(0, wind[i])  # Wind can't be negative

        # Wind gusts: correlated with wind speed but higher
        gust_factor = rng.uniform(1.2, 1.6)
        wind_gust[i] = wind[i] * gust_factor

        # Wind direction: random walk (circular)
        dir_change = rng.normal(0, 20)
        wind_dir[i] = (wind_dir[i - 1] + dir_change) % 360

        # Pressure: slow random walk (weather systems change slowly)
        pressure_change = rng.normal(0, SYNTH_PRESSURE_STD * 0.1)
        pressure[i] = pressure[i - 1] + pressure_change + 0.05 * (
            SYNTH_PRESSURE_MEAN - pressure[i - 1]
        )

        # Temperature: daily cycle + random walk
        # Add sinusoidal pattern for day/night
        hour_of_day = timestamps[i].hour
        daily_cycle = 5 * np.sin(2 * np.pi * (hour_of_day - 6) / 24)  # Peak at ~2pm
        temp_change = rng.normal(0, SYNTH_TEMP_STD * 0.2)
        temp[i] = temp[i - 1] + temp_change + 0.1 * (SYNTH_TEMP_MEAN - temp[i - 1]) + daily_cycle * 0.1

        # Humidity: inversely correlated with temperature
        humidity_change = rng.normal(0, SYNTH_HUMIDITY_STD * 0.3)
        humidity[i] = humidity[i - 1] + humidity_change - 0.5 * temp_change
        humidity[i] = np.clip(humidity[i], 0, 100)

        # Precipitation: rare events (mostly 0)
        if rng.random() < 0.05:  # 5% chance of rain
            precip[i] = rng.exponential(2.0)  # Exponential distribution for rain amount
        else:
            precip[i] = 0

    # Create DataFrame
    df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "wind_m_s": wind,
            "wind_gust_m_s": wind_gust,
            "wind_dir_deg": wind_dir,
            "pressure": pressure,
            "temp": temp,
            "humidity": humidity,
            "precip_mm": precip,
        }
    )

    return df


def main():
    """Generate and save synthetic weather data."""
    print(f"Generating {SAMPLE_DATA_SIZE} hours of synthetic weather data...")
    print(f"Random seed: {RANDOM_SEED}")

    # Create data directory if it doesn't exist
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Generate data
    df = generate_synthetic_weather_data()

    # Save to CSV
    df.to_csv(SAMPLE_DATA_PATH, index=False)
    print(f"✓ Saved to {SAMPLE_DATA_PATH}")

    # Print summary statistics
    print("\nData summary:")
    print(df.describe())

    print(f"\nDate range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"Total records: {len(df)}")


if __name__ == "__main__":
    main()
