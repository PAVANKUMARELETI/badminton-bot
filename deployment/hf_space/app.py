"""
Gradio app for Badminton Wind Predictor.

This app provides a simple UI for:
- Viewing wind forecasts for 1h/3h/6h horizons
- Seeing Play/Don't Play recommendations
- Uploading custom weather data or using sample data

Deploy to Hugging Face Spaces or run locally.
"""

import json
import sys
from pathlib import Path

import gradio as gr
import pandas as pd

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.preprocess import build_features
from src.decision.rules import decide_play
from src.models.lstm_model import LSTMForecaster

# Load model at startup
MODEL_PATH = Path(__file__).parent.parent.parent / "experiments" / "latest" / "model.h5"

# Global model instance
model = None


def load_model_if_needed():
    """Load model if not already loaded."""
    global model

    if model is None:
        if MODEL_PATH.exists():
            model = LSTMForecaster()
            model.load(str(MODEL_PATH))
            return True, "Model loaded successfully"
        else:
            return False, f"Model not found at {MODEL_PATH}. Please train a model first."

    return True, "Model already loaded"


def process_data(csv_file):
    """
    Process uploaded CSV or use sample data.

    Args:
        csv_file: Uploaded file or None

    Returns:
        Processed DataFrame
    """
    if csv_file is not None:
        # Use uploaded file
        df = pd.read_csv(csv_file.name, parse_dates=["timestamp"])
        df = df.set_index("timestamp")
    else:
        # Use sample data
        from src.data.fetch import load_sample

        df = load_sample()

    # Preprocess
    df_processed = build_features(df)

    return df_processed


def make_forecast(csv_file):
    """
    Make forecast and decision.

    Args:
        csv_file: Uploaded CSV file or None (use sample)

    Returns:
        Tuple of (forecast_text, decision_text, details_json)
    """
    # Load model
    success, message = load_model_if_needed()

    if not success:
        return message, "", ""

    try:
        # Process data
        df = process_data(csv_file)

        # Make forecast
        median_forecast = model.predict_latest(df)

        # Compute q90 (simplified)
        q90_forecast = {key: value * 1.2 for key, value in median_forecast.items()}

        # Make decision
        decision = decide_play(median_forecast, q90_forecast)

        # Format outputs
        forecast_lines = ["**Wind Forecast:**\n"]

        for horizon_key in sorted(median_forecast.keys()):
            horizon = horizon_key.replace("horizon_", "")
            median = median_forecast[horizon_key]
            q90 = q90_forecast[horizon_key]

            forecast_lines.append(f"- **{horizon}**: {median:.2f} m/s (median), {q90:.2f} m/s (q90)")

        forecast_text = "\n".join(forecast_lines)

        # Decision text
        decision_icon = "✅" if decision["decision"] == "PLAY" else "⛔"
        decision_text = f"## {decision_icon} {decision['decision']}\n\n{decision['reason']}"

        # Details JSON
        details_json = json.dumps(decision["details"], indent=2)

        return forecast_text, decision_text, details_json

    except Exception as e:
        return f"Error: {str(e)}", "", ""


def get_data_info(csv_file):
    """
    Get information about the data.

    Args:
        csv_file: Uploaded CSV or None

    Returns:
        Data info text
    """
    try:
        if csv_file is not None:
            df = pd.read_csv(csv_file.name, parse_dates=["timestamp"])
            source = "Uploaded file"
        else:
            from src.data.fetch import load_sample

            df = load_sample()
            source = "Sample data"

        info_lines = [
            f"**Data Source:** {source}",
            f"**Records:** {len(df)}",
            f"**Date Range:** {df['timestamp'].min()} to {df['timestamp'].max()}",
            f"\n**Latest values:**",
            f"- Wind speed: {df['wind_m_s'].iloc[-1]:.2f} m/s",
            f"- Wind gust: {df['wind_gust_m_s'].iloc[-1]:.2f} m/s",
            f"- Pressure: {df['pressure'].iloc[-1]:.1f} hPa",
            f"- Temperature: {df['temp'].iloc[-1]:.1f} °C",
        ]

        return "\n".join(info_lines)

    except Exception as e:
        return f"Error loading data: {str(e)}"


# Create Gradio interface
with gr.Blocks(title="Badminton Wind Predictor") as app:
    gr.Markdown(
        """
    # 🏸 Badminton Wind Predictor
    
    Upload your weather data or use the sample dataset to get wind forecasts
    and a recommendation on whether it's safe to play badminton outdoors.
    
    **Forecast horizons:** 1 hour, 3 hours, 6 hours
    """
    )

    with gr.Row():
        with gr.Column():
            gr.Markdown("### Input Data")

            csv_input = gr.File(
                label="Upload Weather Data CSV (optional)",
                file_types=[".csv"],
            )

            gr.Markdown(
                """
            **CSV format:**
            - `timestamp`: datetime
            - `wind_m_s`: wind speed (m/s)
            - `wind_gust_m_s`: wind gusts (m/s)
            - `wind_dir_deg`: direction (degrees)
            - `pressure`: pressure (hPa)
            - `temp`: temperature (°C)
            - `humidity`: humidity (%)
            - `precip_mm`: precipitation (mm)
            
            Leave empty to use sample data.
            """
            )

            data_info = gr.Markdown(label="Data Information")

            csv_input.change(
                fn=get_data_info,
                inputs=[csv_input],
                outputs=[data_info],
            )

            forecast_btn = gr.Button("🔮 Make Forecast", variant="primary")

        with gr.Column():
            gr.Markdown("### Forecast Results")

            forecast_output = gr.Markdown(label="Wind Forecast")

            decision_output = gr.Markdown(label="Decision")

            with gr.Accordion("Detailed Breakdown", open=False):
                details_output = gr.Code(label="Per-Horizon Details", language="json")

    forecast_btn.click(
        fn=make_forecast,
        inputs=[csv_input],
        outputs=[forecast_output, decision_output, details_output],
    )

    gr.Markdown(
        """
    ---
    
    ### How it works
    
    1. **Data Processing**: Weather data is preprocessed with feature engineering (lags, cyclical time, etc.)
    2. **Forecasting**: LSTM model predicts wind speed for 1h/3h/6h ahead
    3. **Uncertainty**: 90th percentile estimates provide upper bounds
    4. **Decision**: Rules check if conditions meet safety thresholds
    
    ### Safety Thresholds (default)
    
    - Median wind speed: ≤ 1.5 m/s
    - 90th percentile: ≤ 2.5 m/s
    
    **Note:** This is a demonstration project. For real applications, use official weather forecasts
    and consult local conditions.
    """
    )

if __name__ == "__main__":
    # Pre-load model if available
    load_model_if_needed()

    # Launch app
    app.launch()
