"""
Telegram bot integration for badminton wind forecasting.

Setup:
1. Create bot via @BotFather on Telegram
2. Get your bot token
3. Set TELEGRAM_BOT_TOKEN environment variable
4. Run: python -m src.integrations.telegram_bot

Users can then:
- /start - Get welcome message
- /forecast - Get latest wind forecast and play decision
- /help - Get help message
- Send location - Get forecast for that location (future feature)
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use system env vars only

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.cli.infer import load_model, make_forecast
from src.data.fetch import load_sample
from src.data.preprocess import build_features
from src.decision.rules import decide_play

logger = logging.getLogger(__name__)

# Default location configuration for IIIT Lucknow
DEFAULT_LOCATION = "IIIT Lucknow"
DEFAULT_LAT = 26.7984  # IIIT Lucknow latitude
DEFAULT_LON = 81.0241  # IIIT Lucknow longitude


class TelegramBot:
    """Telegram bot for wind forecasting."""

    def __init__(self, token: Optional[str] = None, model_path: Optional[str] = None):
        """
        Initialize Telegram bot.

        Args:
            token: Telegram bot token (or set TELEGRAM_BOT_TOKEN env var)
            model_path: Path to trained model (default: latest)
        """
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError(
                "Telegram bot token required. "
                "Set TELEGRAM_BOT_TOKEN env var or pass token parameter."
            )

        self.model_path = model_path or "experiments/latest/model.keras"
        self.model = None
        self.application = None
        
        # Location tracking
        self.current_location = DEFAULT_LOCATION
        self.current_lat = DEFAULT_LAT
        self.current_lon = DEFAULT_LON
        logger.info(f"Bot initialized for {self.current_location} ({self.current_lat}°N, {self.current_lon}°E)")

    def _load_model(self):
        """Load the forecasting model."""
        if self.model is None:
            logger.info(f"Loading model from {self.model_path}")
            self.model = load_model(self.model_path)
            logger.info("Model loaded successfully")

    async def start_command(self, update, context):
        """Handle /start command."""
        welcome_message = f"""
🏸 *Welcome to Badminton Wind Forecast Bot!* 🌬️

I help you decide if it's safe to play badminton based on wind conditions.

📍 *Current Location:* {self.current_location}
🌍 *Coordinates:* {self.current_lat}°N, {self.current_lon}°E

*🎯 What do you want to know?*

🏸 *Can I play NOW?* - Check current weather conditions
📊 *Future Forecast* - See predictions for next 6 hours

*📋 Commands:*
/now - Check if you can play right now
/forecast - Get future wind predictions
/location - Change location
/help - Show help message

👇 *Or use the buttons below:*
        """
        
        # Create inline keyboard with buttons
        keyboard = [
            [
                InlineKeyboardButton("🏸 Can I Play NOW?", callback_data="play_now"),
                InlineKeyboardButton("📊 Future Forecast", callback_data="forecast")
            ],
            [
                InlineKeyboardButton("📍 Change Location", callback_data="location"),
                InlineKeyboardButton("❓ Help", callback_data="help")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_message, 
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

    async def help_command(self, update, context):
        """Handle /help command."""
        help_message = """
🏸 *How to Use This Bot* 🏸

*🎯 Two Ways to Check:*

*1️⃣ Can I Play NOW?*
Checks CURRENT weather conditions
✅ Perfect if you want to play immediately
📊 Decision based on current wind speed
💨 Shows real-time wind data

*2️⃣ Future Forecast*
Shows predictions for next 1, 3, and 6 hours
📈 Perfect for planning ahead
🔮 Uses AI model to predict wind patterns
🌤️ Includes weather context (temp, humidity)

*📋 Commands:*
/now - Quick check of current conditions
/forecast - Future wind predictions
/location <city> - Change location (e.g., /location Delhi)
/help - Show this help message
/start - Main menu

* Safety Thresholds (BWF Standards):*
 Maximum wind: < 3.33 m/s (12 km/h)
 Optimal range: 1.67-3.33 m/s (6-12 km/h)
 Maximum gusts: < 5.0 m/s (18 km/h)

*Based on Badminton World Federation (BWF) AirBadminton recommendations*
*� Understanding Results:*
✅ PLAY - Conditions are safe
❌ DON'T PLAY - Wind too strong for badminton

Stay safe and enjoy playing! 🏸
        """
        
        # Add quick action buttons
        keyboard = [
            [InlineKeyboardButton("🏸 Can I Play NOW?", callback_data="play_now")],
            [InlineKeyboardButton("📊 Future Forecast", callback_data="forecast")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            help_message, 
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

    async def play_now_command(self, update, context):
        """Handle /now command - check current weather conditions only."""
        try:
            logger.info("Play NOW command received")

            # Determine if this is from a button click or direct message
            if update.callback_query:
                query = update.callback_query
                message = query.message
                thinking_msg = await query.edit_message_text("🌤️ Checking current weather...")
            else:
                message = update.message
                thinking_msg = await message.reply_text("🌤️ Checking current weather...")

            # Get current weather data
            current_weather = None
            data_source = "sample"
            weather_data_time = None
            
            try:
                from src.data.weather_api import OpenWeatherMapAPI
                from datetime import datetime, timezone
                
                api_key = os.getenv("OPENWEATHER_API_KEY")
                if api_key and self.current_lat and self.current_lon:
                    logger.info(f"Fetching current weather for {self.current_location}")
                    weather_api = OpenWeatherMapAPI(api_key)
                    
                    current_weather_df = weather_api.get_current_weather(
                        lat=self.current_lat,
                        lon=self.current_lon
                    )
                    
                    if current_weather_df is not None and not current_weather_df.empty:
                        current_weather = current_weather_df.iloc[0].to_dict()
                        weather_data_time = current_weather_df.index[0]
                        data_source = "live"
                        logger.info(f"Current weather: Wind {current_weather.get('wind_m_s', 0):.1f} m/s")
                    else:
                        logger.warning("Could not fetch current weather")
                else:
                    logger.warning("No API key or coordinates set")
                    
            except Exception as api_error:
                logger.error(f"Weather API error: {api_error}", exc_info=True)

            # Make decision based on current conditions
            if current_weather and data_source == "live":
                wind_speed = current_weather.get('wind_m_s', 0)
                wind_gust = current_weather.get('wind_gust_m_s', 0)
                
                # BWF (Badminton World Federation) AirBadminton standards:
                # Optimal: 6-12 km/h (1.67-3.33 m/s), Maximum: 12 km/h (3.33 m/s)
                safe_median_wind = 3.33  # 12 km/h - BWF maximum
                safe_gust_wind = 5.0     # ~18 km/h - Allow some margin for gusts
                
                can_play = (wind_speed <= safe_median_wind and wind_gust <= safe_gust_wind)
                
                response = self._format_current_weather_response(
                    can_play=can_play,
                    current_weather=current_weather,
                    data_source=data_source,
                    location=self.current_location,
                    weather_data_time=weather_data_time,
                    safe_median_wind=safe_median_wind,
                    safe_gust_wind=safe_gust_wind
                )
            else:
                response = "❌ Unable to fetch current weather data. Please try again later."

            # Add action buttons
            keyboard = [
                [
                    InlineKeyboardButton("🔄 Refresh", callback_data="play_now"),
                    InlineKeyboardButton("📊 See Forecast", callback_data="forecast")
                ],
                [InlineKeyboardButton("🔙 Main Menu", callback_data="start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send or edit response
            if update.callback_query:
                await query.edit_message_text(response, parse_mode="Markdown", reply_markup=reply_markup)
            else:
                await thinking_msg.edit_text(response, parse_mode="Markdown", reply_markup=reply_markup)

        except Exception as e:
            logger.error(f"Error in play_now_command: {e}", exc_info=True)
            error_msg = "Sorry, I encountered an error. Please try again later."
            if update.callback_query:
                await update.callback_query.edit_message_text(error_msg)
            else:
                await update.message.reply_text(error_msg)

    async def forecast_command(self, update, context):
        """Handle /forecast command."""
        try:
            logger.info("Forecast command received")
            
            # Load model if not already loaded
            self._load_model()
            logger.info("Model loaded successfully")

            # Determine if this is from a button click or direct message
            if update.callback_query:
                # It's a button click
                query = update.callback_query
                message = query.message
                # Send "thinking" message by editing the existing one
                thinking_msg = await query.edit_message_text("🤔 Analyzing wind conditions...")
            else:
                # It's a direct message/command
                message = update.message
                # Send new "thinking" message
                thinking_msg = await message.reply_text("🤔 Analyzing wind conditions...")

            # Get forecast - try real weather data first, fall back to sample
            current_weather = None  # Store current weather details
            data_source = "sample"  # Track if using real or sample data
            weather_data_time = None  # Store when weather data was fetched
            
            try:
                from src.data.weather_api import OpenWeatherMapAPI
                from datetime import datetime, timezone
                
                api_key = os.getenv("OPENWEATHER_API_KEY")
                if api_key and self.current_lat and self.current_lon:
                    logger.info(f"Fetching real weather data for {self.current_location} ({self.current_lat}, {self.current_lon})")
                    weather_api = OpenWeatherMapAPI(api_key)
                    
                    # Fetch current weather for detailed display
                    try:
                        current_weather_df = weather_api.get_current_weather(
                            lat=self.current_lat,
                            lon=self.current_lon
                        )
                        if current_weather_df is not None and not current_weather_df.empty:
                            # Extract current weather details
                            current_weather = current_weather_df.iloc[0].to_dict()
                            # Store the timestamp from the weather data (when it was observed)
                            weather_data_time = current_weather_df.index[0]
                            logger.info(f"Current weather: {current_weather}")
                            logger.info(f"Weather data timestamp: {weather_data_time}")
                    except Exception as cw_error:
                        logger.warning(f"Could not fetch current weather: {cw_error}")
                    
                    # Use coordinates for accurate location-based data
                    weather_data = weather_api.get_hourly_forecast(
                        lat=self.current_lat,
                        lon=self.current_lon,
                        hours=48
                    )
                    
                    if weather_data is not None and not weather_data.empty:
                        logger.info(f"✅ Using REAL weather data from OpenWeatherMap: {len(weather_data)} hours")
                        data_source = "live"
                        # Some API columns are non-numeric (e.g. 'weather' text). Prepare dataframe
                        df = weather_data.copy()

                        # Normalize column names the preprocess expects
                        if "wind_direction" in df.columns and "wind_dir_deg" not in df.columns:
                            df = df.rename(columns={"wind_direction": "wind_dir_deg"})

                        # Drop any non-numeric columns (e.g. 'weather', 'source') to avoid aggregation errors
                        import numpy as _np
                        df = df.select_dtypes(include=[_np.number])

                        # Ensure target column exists
                        if "wind_m_s" not in df.columns:
                            logger.warning("Real weather data missing 'wind_m_s' column - falling back to sample")
                            df = load_sample()
                            data_source = "sample"
                    else:
                        logger.warning("Could not fetch real weather data, using sample")
                        df = load_sample()
                else:
                    logger.warning("No API key or coordinates set, using sample data")
                    df = load_sample()
            except Exception as api_error:
                logger.error(f"Weather API error: {api_error}", exc_info=True)
                logger.info("Falling back to sample data")
                df = load_sample()
            
            logger.info(f"Data loaded: {len(df)} rows")
            
            logger.info("Building features")
            data_df = build_features(df)
            logger.info(f"Features built: {data_df.shape}")
            
            logger.info("Making forecast")
            forecast_result = make_forecast(self.model, data_df)
            logger.info(f"Forecast complete: {forecast_result}")

            # Make decision
            logger.info("Making decision")
            decision_result = decide_play(
                median_forecast=forecast_result["median"],
                q90_forecast=forecast_result["q90"]
            )
            logger.info(f"Decision made: {decision_result['decision']}")

            # Format response
            response = self._format_forecast_response(
                decision_result=decision_result,
                forecast_result=forecast_result,
                current_weather=current_weather,
                data_source=data_source,
                location=self.current_location,
                weather_data_time=weather_data_time
            )

            # Add action buttons
            keyboard = [
                [
                    InlineKeyboardButton("🔄 Refresh", callback_data="forecast"),
                    InlineKeyboardButton("📍 Change Location", callback_data="location")
                ],
                [InlineKeyboardButton("🔙 Main Menu", callback_data="start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send or edit the message depending on source
            if update.callback_query:
                # Edit existing message from button click
                await thinking_msg.edit_text(
                    response,
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )
            else:
                # Delete thinking message and send new one for direct command
                await thinking_msg.delete()
                await message.reply_text(
                    response, 
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )
            
            logger.info("Forecast response sent successfully")

        except Exception as e:
            logger.error(f"Error in forecast_command: {e}", exc_info=True)
            
            keyboard = [[InlineKeyboardButton("🔄 Try Again", callback_data="forecast")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            error_message = "❌ Sorry, I encountered an error. Please try again later."
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    error_message,
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(
                    error_message,
                    reply_markup=reply_markup
                )

    async def handle_message(self, update, context):
        """Handle general text messages."""
        # Treat any message as a forecast request
        await self.forecast_command(update, context)

    async def button_callback(self, update, context):
        """Handle button clicks from inline keyboards."""
        query = update.callback_query
        
        # IMPORTANT: Always answer callback queries to remove loading state
        await query.answer()
        
        callback_data = query.data
        logger.info(f"Button clicked: {callback_data}")
        
        # Handle different button actions
        if callback_data == "play_now":
            logger.info("Handling play NOW button click")
            # Trigger play_now command for button click
            await self.play_now_command(update, context)
            
        elif callback_data == "forecast":
            logger.info("Handling forecast button click")
            # Trigger forecast command for button click
            await self.forecast_command(update, context)
            
        elif callback_data == "start":
            # Show main menu
            welcome_message = f"""
🏸 *Welcome to Badminton Wind Forecast Bot!* 🌬️

I help you decide if it's safe to play badminton based on wind conditions.

📍 *Current Location:* {self.current_location}
🌍 *Coordinates:* {self.current_lat}°N, {self.current_lon}°E

*🎯 What do you want to know?*

🏸 *Can I play NOW?* - Check current weather
📊 *Future Forecast* - See predictions for next 6 hours

Use the buttons below to get started! 👇
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("🏸 Can I Play NOW?", callback_data="play_now"),
                    InlineKeyboardButton("📊 Future Forecast", callback_data="forecast")
                ],
                [
                    InlineKeyboardButton("📍 Change Location", callback_data="location"),
                    InlineKeyboardButton("❓ Help", callback_data="help")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                welcome_message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            
        elif callback_data == "help":
            # Show help message
            help_message = """
🏸 *How to Use This Bot* 🏸

*🎯 Two Ways to Check:*

*1️⃣ Can I Play NOW?*
Checks CURRENT weather conditions
✅ Perfect if you want to play immediately
📊 Decision based on current wind speed

*2️⃣ Future Forecast*
Shows predictions for next 1, 3, and 6 hours
📈 Perfect for planning ahead
🔮 Uses AI model to predict wind patterns

*📋 Commands:*
/now - Quick check of current conditions
/forecast - Future wind predictions
/location - Change your location
/help - Show this help message

*🌬️ Safety Thresholds:*
• Safe wind speed: < 1.5 m/s (5.4 km/h)
• Safe wind gusts: < 3.5 m/s (12.6 km/h)

*💡 Understanding Results:*
✅ PLAY - Conditions are safe
❌ DON'T PLAY - Wind too strong for badminton

Stay safe and enjoy playing! 🏸
            """
            
            keyboard = [
                [InlineKeyboardButton("🏸 Can I Play NOW?", callback_data="play_now")],
                [InlineKeyboardButton("📊 Future Forecast", callback_data="forecast")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                help_message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            
        elif callback_data == "location":
            # Show location selection
            keyboard = [
                [
                    InlineKeyboardButton("🏫 IIIT Lucknow", callback_data="loc_iiit"),
                    InlineKeyboardButton("🏛️ Delhi", callback_data="loc_delhi")
                ],
                [
                    InlineKeyboardButton("🌆 Mumbai", callback_data="loc_mumbai"),
                    InlineKeyboardButton("🌃 Bangalore", callback_data="loc_bangalore")
                ],
                [
                    InlineKeyboardButton("🌇 Hyderabad", callback_data="loc_hyderabad"),
                    InlineKeyboardButton("🌉 Chennai", callback_data="loc_chennai")
                ],
                [InlineKeyboardButton("🔙 Main Menu", callback_data="start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"📍 *Current location:* {self.current_location}\n"
                f"🌍 *Coordinates:* {self.current_lat}°N, {self.current_lon}°E\n\n"
                "Choose a city from the options below:",
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            
        elif callback_data.startswith("loc_"):
            # Handle city selection
            city_map = {
                "loc_iiit": "IIIT Lucknow",
                "loc_delhi": "Delhi",
                "loc_mumbai": "Mumbai",
                "loc_bangalore": "Bangalore",
                "loc_hyderabad": "Hyderabad",
                "loc_chennai": "Chennai"
            }
            
            city = city_map.get(callback_data)
            if city:
                self._update_location(city)
                
                keyboard = [
                    [InlineKeyboardButton("🏸 Get Forecast", callback_data="forecast")],
                    [InlineKeyboardButton("🔙 Main Menu", callback_data="start")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                if self.current_lat and self.current_lon:
                    message = (
                        f"✅ Location set to: *{self.current_location}*\n"
                        f"🌍 *Coordinates:* {self.current_lat}°N, {self.current_lon}°E"
                    )
                else:
                    message = f"✅ Location updated to: *{self.current_location}*"
                
                await query.edit_message_text(
                    message,
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )

    def _format_forecast_response(
        self, 
        decision_result: dict, 
        forecast_result: dict,
        current_weather: dict = None,
        data_source: str = "sample",
        location: str = "Unknown",
        weather_data_time = None
    ) -> str:
        """
        Format forecast result for Telegram with detailed weather info.

        Args:
            decision_result: Decision output from decide_play()
            forecast_result: Forecast output from make_forecast()
            current_weather: Current weather data from API (optional)
            data_source: "live" or "sample"
            location: Location name
            weather_data_time: Timestamp when weather data was observed

        Returns:
            Formatted message string
        """
        from datetime import datetime, timezone, timedelta
        
        decision = decision_result["decision"]
        details = decision_result["details"]
        median_forecast = forecast_result["median"]
        q90_forecast = forecast_result["q90"]

        # Emoji for decision
        emoji = "✅" if decision == "PLAY" else "❌"
        
        # Data source indicator
        source_emoji = "🌐" if data_source == "live" else "📊"
        source_text = "Live Weather Data" if data_source == "live" else "Sample Data"

        # Get current time in IST (UTC+5:30)
        ist = timezone(timedelta(hours=5, minutes=30))
        current_time_ist = datetime.now(timezone.utc).astimezone(ist)
        
        # Build message
        lines = [
            f"{emoji} *{decision}* {emoji}",
            "",
            f"📍 *Location:* {location}",
            f"{source_emoji} *Data Source:* {source_text}",
            f"🕒 *Checked:* {current_time_ist.strftime('%I:%M %p IST')}",
        ]
        
        # If we have weather data timestamp, show when it was observed
        if weather_data_time is not None:
            try:
                # Convert weather data time to IST
                if hasattr(weather_data_time, 'tz_localize'):
                    weather_time_ist = weather_data_time.tz_localize('UTC').tz_convert(ist)
                elif hasattr(weather_data_time, 'astimezone'):
                    weather_time_ist = weather_data_time.astimezone(ist)
                else:
                    # If it's a naive datetime, assume UTC
                    weather_time_ist = weather_data_time.replace(tzinfo=timezone.utc).astimezone(ist)
                
                # Calculate how many minutes ago the data was observed
                time_diff = current_time_ist - weather_time_ist
                minutes_ago = int(time_diff.total_seconds() / 60)
                
                if minutes_ago < 1:
                    freshness = "just now"
                elif minutes_ago < 60:
                    freshness = f"{minutes_ago} min ago"
                else:
                    hours_ago = minutes_ago // 60
                    freshness = f"{hours_ago}h {minutes_ago % 60}m ago"
                
                lines.append(f"📊 *Data Age:* {freshness}")
            except Exception as e:
                logger.warning(f"Error formatting weather data time: {e}")
        
        lines.append("")
        
        # Add current weather conditions if available
        if current_weather:
            lines.append("*🌤️ Current Conditions:*")
            
            # Wind
            wind_speed = current_weather.get('wind_m_s', 0)
            wind_gust = current_weather.get('wind_gust_m_s', 0)
            lines.append(f"💨 Wind: {wind_speed:.1f} m/s ({wind_speed*3.6:.1f} km/h)")
            lines.append(f"💨 Gusts: {wind_gust:.1f} m/s ({wind_gust*3.6:.1f} km/h)")
            
            # Wind direction
            if 'wind_dir_deg' in current_weather:
                wind_dir = current_weather['wind_dir_deg']
                # Convert degrees to compass direction
                directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
                idx = int((wind_dir + 22.5) / 45) % 8
                lines.append(f"🧭 Direction: {directions[idx]} ({wind_dir:.0f}°)")
            
            # Temperature
            if 'temp' in current_weather:
                temp = current_weather['temp']
                lines.append(f"🌡️ Temperature: {temp:.1f}°C")
            
            # Humidity
            if 'humidity' in current_weather:
                humidity = current_weather['humidity']
                lines.append(f"💧 Humidity: {humidity:.0f}%")
            
            # Pressure
            if 'pressure' in current_weather:
                pressure = current_weather['pressure']
                lines.append(f"🔽 Pressure: {pressure:.0f} hPa")
            
            lines.append("")

        lines.append("*🔮 Wind Forecast:*")

        # Add horizon forecasts
        for horizon in ["1h", "3h", "6h"]:
            median = median_forecast[f"horizon_{horizon}"]
            q90 = q90_forecast[f"horizon_{horizon}"]
            passes = details[horizon]["passes"]

            status_emoji = "✅" if passes else "⚠️"
            lines.append(
                f"{status_emoji} *{horizon}:* {median:.1f} m/s (gust: {q90:.1f} m/s)"
            )

        # Add reason if don't play
        if decision == "DON'T PLAY":
            lines.append("")
            lines.append(f"*Reason:* {decision_result['reason']}")

        lines.append("")
        lines.append("_Safe wind: < 1.5 m/s | Max gust: < 3.5 m/s_")

        return "\n".join(lines)

    def _format_current_weather_response(
        self,
        can_play: bool,
        current_weather: dict,
        data_source: str,
        location: str,
        weather_data_time,
        safe_median_wind: float,
        safe_gust_wind: float
    ) -> str:
        """
        Format current weather conditions for immediate play decision.

        Args:
            can_play: Whether it's safe to play now
            current_weather: Current weather data from API
            data_source: "live" or "sample"
            location: Location name
            weather_data_time: Timestamp when weather data was observed
            safe_median_wind: Safe wind speed threshold
            safe_gust_wind: Safe gust threshold

        Returns:
            Formatted message string
        """
        from datetime import datetime, timezone, timedelta

        # Emoji for decision
        emoji = "✅" if can_play else "❌"
        decision_text = "PLAY NOW" if can_play else "DON'T PLAY NOW"
        
        # Data source indicator
        source_emoji = "🌐" if data_source == "live" else "📊"
        source_text = "Live Weather Data" if data_source == "live" else "Sample Data"

        # Get current time in IST (UTC+5:30)
        ist = timezone(timedelta(hours=5, minutes=30))
        current_time_ist = datetime.now(timezone.utc).astimezone(ist)
        
        # Build message
        lines = [
            f"{emoji} *{decision_text}* {emoji}",
            "",
            f"📍 *Location:* {location}",
            f"{source_emoji} *Data Source:* {source_text}",
            f"🕒 *Current Time:* {current_time_ist.strftime('%I:%M %p IST')}",
        ]
        
        # Add data freshness
        if weather_data_time is not None:
            try:
                if hasattr(weather_data_time, 'tz_localize'):
                    weather_time_ist = weather_data_time.tz_localize('UTC').tz_convert(ist)
                elif hasattr(weather_data_time, 'astimezone'):
                    weather_time_ist = weather_data_time.astimezone(ist)
                else:
                    weather_time_ist = weather_data_time.replace(tzinfo=timezone.utc).astimezone(ist)
                
                time_diff = current_time_ist - weather_time_ist
                minutes_ago = int(time_diff.total_seconds() / 60)
                
                if minutes_ago < 1:
                    freshness = "just now"
                elif minutes_ago < 60:
                    freshness = f"{minutes_ago} min ago"
                else:
                    hours_ago = minutes_ago // 60
                    freshness = f"{hours_ago}h {minutes_ago % 60}m ago"
                
                lines.append(f"📊 *Data Age:* {freshness}")
            except Exception as e:
                logger.warning(f"Error formatting weather data time: {e}")
        
        lines.append("")
        lines.append("*🌤️ Current Weather Conditions:*")
        
        # Wind (most important for decision)
        wind_speed = current_weather.get('wind_m_s', 0)
        wind_gust = current_weather.get('wind_gust_m_s', 0)
        
        wind_emoji = "✅" if wind_speed <= safe_median_wind else "⚠️"
        gust_emoji = "✅" if wind_gust <= safe_gust_wind else "⚠️"
        
        lines.append(f"{wind_emoji} *Wind Speed:* {wind_speed:.1f} m/s ({wind_speed*3.6:.1f} km/h)")
        lines.append(f"{gust_emoji} *Wind Gusts:* {wind_gust:.1f} m/s ({wind_gust*3.6:.1f} km/h)")
        
        # Wind direction
        if 'wind_dir_deg' in current_weather:
            wind_dir = current_weather['wind_dir_deg']
            directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
            idx = int((wind_dir + 22.5) / 45) % 8
            lines.append(f"🧭 *Direction:* {directions[idx]} ({wind_dir:.0f}°)")
        
        lines.append("")
        
        # Additional weather info
        if 'temp' in current_weather:
            temp = current_weather['temp']
            lines.append(f"🌡️ Temperature: {temp:.1f}°C")
        
        if 'humidity' in current_weather:
            humidity = current_weather['humidity']
            lines.append(f"💧 Humidity: {humidity:.0f}%")
        
        if 'pressure' in current_weather:
            pressure = current_weather['pressure']
            lines.append(f"🔽 Pressure: {pressure:.0f} hPa")
        
        lines.append("")
        
        # Decision explanation
        if can_play:
            lines.append("✅ *Good news!* Current wind conditions are safe for outdoor badminton.")
        else:
            reasons = []
            if wind_speed > safe_median_wind:
                reasons.append(f"Wind speed {wind_speed:.1f} m/s > {safe_median_wind} m/s")
            if wind_gust > safe_gust_wind:
                reasons.append(f"Wind gusts {wind_gust:.1f} m/s > {safe_gust_wind} m/s")
            
            lines.append("⚠️ *Current conditions are not ideal:*")
            for reason in reasons:
                lines.append(f"  • {reason}")
        
        lines.append("")
        lines.append("_💡 Tip: Want to plan ahead? Check the Future Forecast!_")
        lines.append(f"_Safe thresholds: Wind < {safe_median_wind} m/s | Gusts < {safe_gust_wind} m/s_")

        return "\n".join(lines)

    async def settings_command(self, update, context):
        """Handle /settings command."""
        settings_message = """
⚙️ *Settings*

*Current Thresholds:*
• Max median wind: 1.5 m/s
• Max wind gust (Q90): 3.5 m/s

To customize thresholds, contact your administrator.

*Data Source:*
Currently using sample data. In production, this will use real weather station data.
        """
        await update.message.reply_text(settings_message, parse_mode="Markdown")

    async def location_command(self, update, context):
        """Handle /location command to change location."""
        if not context.args:
            # Show current location with popular city buttons
            keyboard = [
                [
                    InlineKeyboardButton("🏫 IIIT Lucknow", callback_data="loc_iiit"),
                    InlineKeyboardButton("🏛️ Delhi", callback_data="loc_delhi")
                ],
                [
                    InlineKeyboardButton("🌆 Mumbai", callback_data="loc_mumbai"),
                    InlineKeyboardButton("🌃 Bangalore", callback_data="loc_bangalore")
                ],
                [
                    InlineKeyboardButton("🌇 Hyderabad", callback_data="loc_hyderabad"),
                    InlineKeyboardButton("🌉 Chennai", callback_data="loc_chennai")
                ],
                [InlineKeyboardButton("🔙 Main Menu", callback_data="start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"📍 *Current location:* {self.current_location}\n"
                f"🌍 *Coordinates:* {self.current_lat}°N, {self.current_lon}°E\n\n"
                "*🔘 Click a city button below*\n"
                "*OR*\n"
                "*⌨️ Type:* `/location <city name>`\n\n"
                "Example: `/location Kolkata`",
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            return
        
        new_location = " ".join(context.args)
        self._update_location(new_location)
        
        keyboard = [
            [InlineKeyboardButton("🏸 Get Forecast", callback_data="forecast")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if self.current_lat and self.current_lon:
            message = (
                f"✅ Location set to: *{self.current_location}*\n"
                f"🌍 *Coordinates:* {self.current_lat}°N, {self.current_lon}°E"
            )
        else:
            message = f"✅ Location updated to: *{self.current_location}*"
        
        await update.message.reply_text(
            message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        logger.info(f"Location changed to: {self.current_location}")

    def _update_location(self, location: str):
        """Update bot location (helper method)."""
        location_lower = location.lower()
        
        # Check if user wants to return to IIIT Lucknow
        if "iiit" in location_lower and "lucknow" in location_lower:
            self.current_location = DEFAULT_LOCATION
            self.current_lat = DEFAULT_LAT
            self.current_lon = DEFAULT_LON
        else:
            self.current_location = location
            # Reset coordinates so API will geocode the city name
            self.current_lat = None
            self.current_lon = None

    def run(self):
        """Start the Telegram bot."""
        try:
            from telegram.ext import (
                Application,
                CommandHandler,
                MessageHandler,
                filters,
            )
        except ImportError:
            raise ImportError(
                "python-telegram-bot not installed. "
                "Install with: pip install python-telegram-bot"
            )

        logger.info("Starting Telegram bot...")

        # Create application
        self.application = Application.builder().token(self.token).build()

        # Add command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("now", self.play_now_command))
        self.application.add_handler(CommandHandler("forecast", self.forecast_command))
        self.application.add_handler(CommandHandler("location", self.location_command))
        self.application.add_handler(CommandHandler("settings", self.settings_command))

        # Add callback query handler for button clicks
        from telegram.ext import CallbackQueryHandler
        self.application.add_handler(CallbackQueryHandler(self.button_callback))

        # Handle all text messages as forecast requests
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

        logger.info("Bot is ready! Press Ctrl+C to stop.")

        # Run the bot - IMPORTANT: Must include callback_query for buttons to work!
        self.application.run_polling(allowed_updates=["message", "callback_query"])


def main():
    """Main entry point for Telegram bot."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Get token from environment or command line
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN environment variable not set!")
        print("\nHow to set up:")
        print("1. Create a bot via @BotFather on Telegram")
        print("2. Get your bot token")
        print("3. Set environment variable:")
        print("   PowerShell: $env:TELEGRAM_BOT_TOKEN='your-token-here'")
        print("   Linux/Mac: export TELEGRAM_BOT_TOKEN='your-token-here'")
        return

    # Create and run bot
    bot = TelegramBot(token=token)
    bot.run()


if __name__ == "__main__":
    main()

