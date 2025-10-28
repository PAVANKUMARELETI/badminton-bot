"""
Data collection service for automated weather data gathering.

This script:
1. Fetches weather data from API at regular intervals
2. Stores observations in SQLite database
3. Maintains historical record for model training
4. Handles errors and retries

Usage:
    # Run once manually
    python -m src.data.data_collector --location "Delhi" --collect-once
    
    # Run continuously (every hour)
    python -m src.data.data_collector --location "Delhi" --interval 3600
    
    # As background service
    python -m src.data.data_collector --location "bits_pilani" --daemon
"""

import argparse
import logging
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

from src.config import DATA_DIR
from src.data.weather_api import get_weather_for_location

logger = logging.getLogger(__name__)


class WeatherDataCollector:
    """Automated weather data collection service."""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize collector.
        
        Args:
            db_path: Path to SQLite database (default: data/weather.db)
        """
        self.db_path = db_path or str(DATA_DIR / "weather.db")
        self._create_database()

    def _create_database(self):
        """Create database tables if they don't exist."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Observations table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS observations (
                timestamp DATETIME PRIMARY KEY,
                location TEXT,
                lat REAL,
                lon REAL,
                wind_m_s REAL,
                wind_gust_m_s REAL,
                wind_direction INTEGER,
                temp REAL,
                pressure REAL,
                humidity REAL,
                weather TEXT,
                source TEXT,
                collected_at DATETIME
            )
        """
        )

        # Forecasts table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS forecasts (
                forecast_timestamp DATETIME,
                target_timestamp DATETIME,
                location TEXT,
                horizon_hours INTEGER,
                wind_m_s REAL,
                wind_gust_m_s REAL,
                source TEXT,
                PRIMARY KEY (forecast_timestamp, target_timestamp, source)
            )
        """
        )

        conn.commit()
        conn.close()

        logger.info(f"Database initialized at {self.db_path}")

    def collect_current_weather(self, location: str, api_provider: str = "openweather"):
        """
        Collect current weather observation.
        
        Args:
            location: Location name or campus code
            api_provider: API to use
        """
        try:
            # Fetch weather data
            df = get_weather_for_location(location, hours=0, api_provider=api_provider)

            if df.empty:
                logger.warning(f"No data received for {location}")
                return

            # Get current observation (first row)
            current = df.iloc[0]

            # Store in database
            conn = sqlite3.connect(self.db_path)

            record = {
                "timestamp": current.name,
                "location": location,
                "lat": current.get("lat", None),
                "lon": current.get("lon", None),
                "wind_m_s": current["wind_m_s"],
                "wind_gust_m_s": current["wind_gust_m_s"],
                "wind_direction": current.get("wind_direction", 0),
                "temp": current.get("temp", None),
                "pressure": current.get("pressure", None),
                "humidity": current.get("humidity", None),
                "weather": current.get("weather", ""),
                "source": current.get("source", api_provider),
                "collected_at": datetime.now(),
            }

            # Insert or replace
            pd.DataFrame([record]).to_sql(
                "observations", conn, if_exists="append", index=False
            )

            conn.close()

            logger.info(
                f"Collected weather for {location}: {current['wind_m_s']:.1f} m/s"
            )

        except Exception as e:
            logger.error(f"Error collecting weather for {location}: {e}", exc_info=True)

    def collect_forecast(
        self, location: str, hours: int = 6, api_provider: str = "openweather"
    ):
        """
        Collect weather forecast.
        
        Args:
            location: Location name or campus code
            hours: Forecast hours
            api_provider: API to use
        """
        try:
            # Fetch forecast
            df = get_weather_for_location(location, hours=hours, api_provider=api_provider)

            if df.empty:
                logger.warning(f"No forecast data for {location}")
                return

            forecast_time = datetime.now()
            conn = sqlite3.connect(self.db_path)

            records = []
            for timestamp, row in df.iterrows():
                # Calculate horizon in hours
                horizon = int((timestamp - pd.Timestamp(forecast_time)).total_seconds() / 3600)

                if horizon < 0:
                    continue  # Skip past data

                record = {
                    "forecast_timestamp": forecast_time,
                    "target_timestamp": timestamp,
                    "location": location,
                    "horizon_hours": horizon,
                    "wind_m_s": row["wind_m_s"],
                    "wind_gust_m_s": row["wind_gust_m_s"],
                    "source": row.get("source", api_provider),
                }
                records.append(record)

            if records:
                pd.DataFrame(records).to_sql(
                    "forecasts", conn, if_exists="append", index=False
                )

            conn.close()

            logger.info(f"Collected {len(records)} forecast points for {location}")

        except Exception as e:
            logger.error(f"Error collecting forecast for {location}: {e}", exc_info=True)

    def get_historical_data(
        self, location: str, days: int = 30
    ) -> pd.DataFrame:
        """
        Retrieve historical observations from database.
        
        Args:
            location: Location name
            days: Number of days to retrieve
        
        Returns:
            DataFrame with historical observations
        """
        conn = sqlite3.connect(self.db_path)

        query = """
            SELECT * FROM observations
            WHERE location = ?
            AND timestamp >= datetime('now', ? || ' days')
            ORDER BY timestamp ASC
        """

        df = pd.read_sql_query(query, conn, params=(location, -days))
        conn.close()

        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df.set_index("timestamp", inplace=True)

        logger.info(f"Retrieved {len(df)} historical records for {location}")
        return df

    def run_continuous(
        self, location: str, interval: int = 3600, api_provider: str = "openweather"
    ):
        """
        Run continuous data collection.
        
        Args:
            location: Location to monitor
            interval: Collection interval in seconds (default: 1 hour)
            api_provider: API provider to use
        """
        logger.info(
            f"Starting continuous collection for {location} every {interval}s"
        )

        while True:
            try:
                # Collect current observation
                self.collect_current_weather(location, api_provider)

                # Collect forecast every hour
                if interval >= 3600:
                    self.collect_forecast(location, hours=6, api_provider=api_provider)

                # Wait for next collection
                logger.info(f"Next collection in {interval} seconds")
                time.sleep(interval)

            except KeyboardInterrupt:
                logger.info("Stopping data collection")
                break
            except Exception as e:
                logger.error(f"Error in collection loop: {e}", exc_info=True)
                # Wait a bit before retrying
                time.sleep(60)


def main():
    """CLI entry point for data collector."""
    parser = argparse.ArgumentParser(description="Weather data collection service")

    parser.add_argument(
        "--location",
        type=str,
        required=True,
        help="Location to collect data for (e.g., 'Delhi', 'bits_pilani')",
    )

    parser.add_argument(
        "--api",
        type=str,
        default="openweather",
        choices=["openweather", "weatherapi"],
        help="Weather API provider",
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        help="Collection interval in seconds (default: 3600 = 1 hour)",
    )

    parser.add_argument(
        "--collect-once",
        action="store_true",
        help="Collect data once and exit (don't run continuously)",
    )

    parser.add_argument(
        "--db-path",
        type=str,
        help="Path to SQLite database (default: data/weather.db)",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create collector
    collector = WeatherDataCollector(db_path=args.db_path)

    if args.collect_once:
        # Single collection
        logger.info(f"Collecting weather for {args.location}...")
        collector.collect_current_weather(args.location, args.api)
        collector.collect_forecast(args.location, hours=6, api_provider=args.api)
        logger.info("Collection complete!")
    else:
        # Continuous collection
        collector.run_continuous(args.location, args.interval, args.api)


if __name__ == "__main__":
    main()
