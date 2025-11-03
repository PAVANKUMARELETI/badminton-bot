"""
Weather data logger for accumulating real observations over time.

This module automatically saves weather data fetched from the API
to build a historical dataset for future model retraining.

Data is stored in CSV format with automatic deduplication.
"""
import os
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)

# Data storage location
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "collected"
WEATHER_LOG_FILE = DATA_DIR / "weather_observations.csv"


class WeatherDataLogger:
    """Logs weather observations for building historical dataset."""
    
    def __init__(self, log_file: Path = WEATHER_LOG_FILE):
        """
        Initialize weather data logger.
        
        Args:
            log_file: Path to CSV file for storing observations
        """
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create file with headers if it doesn't exist
        if not self.log_file.exists():
            self._create_log_file()
            logger.info(f"Created new weather log file: {self.log_file}")
    
    def _create_log_file(self):
        """Create empty log file with headers."""
        headers = [
            'timestamp',
            'wind_m_s',
            'wind_gust_m_s',
            'wind_dir_deg',
            'temp',
            'humidity',
            'pressure',
            'lat',
            'lon',
            'data_source'  # 'current' or 'forecast'
        ]
        df = pd.DataFrame(columns=headers)
        df.to_csv(self.log_file, index=False)
    
    def log_observation(self, weather_df: pd.DataFrame, source: str = "current"):
        """
        Log weather observation to historical dataset.
        
        Args:
            weather_df: DataFrame with weather data (from weather_api)
            source: Data source ('current' or 'forecast')
        """
        try:
            if weather_df is None or weather_df.empty:
                logger.warning("Attempted to log empty weather data")
                return
            
            # Add source column
            weather_df = weather_df.copy()
            weather_df['data_source'] = source
            
            # Load existing data
            if self.log_file.exists():
                existing = pd.read_csv(self.log_file, parse_dates=['timestamp'])
                
                # Combine and remove duplicates (based on timestamp)
                combined = pd.concat([existing, weather_df], ignore_index=True)
                combined = combined.drop_duplicates(subset=['timestamp'], keep='last')
                combined = combined.sort_values('timestamp')
            else:
                combined = weather_df
            
            # Save back to file
            combined.to_csv(self.log_file, index=False)
            
            logger.info(f"Logged {len(weather_df)} observations to {self.log_file}")
            logger.info(f"Total observations in dataset: {len(combined)}")
            
        except Exception as e:
            logger.error(f"Failed to log weather data: {e}")
    
    def get_dataset_info(self) -> dict:
        """
        Get information about the accumulated dataset.
        
        Returns:
            Dictionary with dataset statistics
        """
        if not self.log_file.exists():
            return {
                'exists': False,
                'count': 0,
                'start_date': None,
                'end_date': None,
                'days': 0
            }
        
        df = pd.read_csv(self.log_file, parse_dates=['timestamp'])
        
        if df.empty:
            return {
                'exists': True,
                'count': 0,
                'start_date': None,
                'end_date': None,
                'days': 0
            }
        
        start_date = df['timestamp'].min()
        end_date = df['timestamp'].max()
        days = (end_date - start_date).total_seconds() / 86400
        
        return {
            'exists': True,
            'count': len(df),
            'start_date': start_date,
            'end_date': end_date,
            'days': days,
            'ready_for_training': days >= 30 and len(df) >= 500
        }
    
    def load_historical_data(self) -> pd.DataFrame:
        """
        Load accumulated historical data for model training.
        
        Returns:
            DataFrame with historical observations
        """
        if not self.log_file.exists():
            raise FileNotFoundError(f"No historical data found at {self.log_file}")
        
        df = pd.read_csv(self.log_file, parse_dates=['timestamp'])
        df = df.set_index('timestamp')
        
        logger.info(f"Loaded {len(df)} historical observations")
        logger.info(f"Date range: {df.index.min()} to {df.index.max()}")
        
        return df


# Global logger instance
_logger = WeatherDataLogger()


def log_weather_data(weather_df: pd.DataFrame, source: str = "current"):
    """
    Convenience function to log weather data.
    
    Args:
        weather_df: DataFrame with weather data
        source: Data source ('current' or 'forecast')
    """
    _logger.log_observation(weather_df, source)


def get_dataset_info() -> dict:
    """Get information about accumulated dataset."""
    return _logger.get_dataset_info()


def load_historical_data() -> pd.DataFrame:
    """Load accumulated historical data."""
    return _logger.load_historical_data()
