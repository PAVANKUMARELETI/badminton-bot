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

I help you decide if it's safe to play badminton based on wind conditions at IIIT Lucknow campus.

📍 *Location:* {self.current_location}
🌍 *Coordinates:* {self.current_lat}°N, {self.current_lon}°E

*🎯 Quick Start:*
Just type: "Can I play?" or "Should I play badminton?"

*📋 Commands:*
/forecast - Get detailed wind forecast
/location - Change location
/help - Show help message

👇 *Or use the buttons below:*
        """
        
        # Create inline keyboard with buttons
        keyboard = [
            [
                InlineKeyboardButton("🏸 Can I Play?", callback_data="forecast"),
                InlineKeyboardButton("📊 Forecast", callback_data="forecast")
            ],
            [
                InlineKeyboardButton("📍 Location", callback_data="location"),
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

*💬 Option 1: Just Type*
Send me any message like:
• "Can I play?"
• "Weather check"
• "Is it windy?"
• "Should I play badminton?"

*⌨️ Option 2: Use Commands*
/forecast - Get detailed wind forecast
/location <city> - Change location (e.g., /location Delhi)
/help - Show this message
/start - Main menu

*🔘 Option 3: Click Buttons*
Tap any button below for quick actions!

*📊 Understanding the Forecast:*
✅ *PLAY* - Wind is within safe limits
❌ *DON'T PLAY* - Wind too strong for badminton

*⏱️ Forecast Horizons:*
• 1h - Next hour forecast
• 3h - Next 3 hours forecast
• 6h - Next 6 hours forecast

*🌬️ Safety Thresholds:*
• Safe median wind: < 1.5 m/s
• Safe max gust (Q90): < 3.5 m/s

Stay safe and enjoy playing! 🏸
        """
        
        # Add quick action buttons
        keyboard = [
            [InlineKeyboardButton("🏸 Get Forecast", callback_data="forecast")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            help_message, 
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

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
            
            try:
                from src.data.weather_api import OpenWeatherMapAPI
                
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
                            logger.info(f"Current weather: {current_weather}")
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
                location=self.current_location
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
        if callback_data == "forecast":
            logger.info("Handling forecast button click")
            # Trigger forecast command for button click
            await self.forecast_command(update, context)
            
        elif callback_data == "start":
            # Show main menu
            welcome_message = f"""
🏸 *Welcome to Badminton Wind Forecast Bot!* 🌬️

I help you decide if it's safe to play badminton based on wind conditions at IIIT Lucknow campus.

📍 *Location:* {self.current_location}
🌍 *Coordinates:* {self.current_lat}°N, {self.current_lon}°E

Use the buttons below to get started! 👇
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("🏸 Can I Play?", callback_data="forecast"),
                    InlineKeyboardButton("📊 Forecast", callback_data="forecast")
                ],
                [
                    InlineKeyboardButton("📍 Location", callback_data="location"),
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

*Quick Check:*
Just tap the "Can I Play?" button or send any message like:
• "Can I play?"
• "Weather check"
• "Is it windy?"

*Understanding the Forecast:*
✅ PLAY - Wind is within safe limits
❌ DON'T PLAY - Wind too strong for badminton

*Horizons:*
• 1h - Next hour forecast
• 3h - Next 3 hours forecast
• 6h - Next 6 hours forecast

*Thresholds:*
• Safe wind: < 1.5 m/s (median)
• Max gust: < 3.5 m/s (90th percentile)

Stay safe and enjoy playing! 🏸
            """
            
            keyboard = [
                [InlineKeyboardButton("🏸 Get Forecast", callback_data="forecast")],
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
        location: str = "Unknown"
    ) -> str:
        """
        Format forecast result for Telegram with detailed weather info.

        Args:
            decision_result: Decision output from decide_play()
            forecast_result: Forecast output from make_forecast()
            current_weather: Current weather data from API (optional)
            data_source: "live" or "sample"
            location: Location name

        Returns:
            Formatted message string
        """
        from datetime import datetime
        
        decision = decision_result["decision"]
        details = decision_result["details"]
        median_forecast = forecast_result["median"]
        q90_forecast = forecast_result["q90"]

        # Emoji for decision
        emoji = "✅" if decision == "PLAY" else "❌"
        
        # Data source indicator
        source_emoji = "🌐" if data_source == "live" else "📊"
        source_text = "Live Weather Data" if data_source == "live" else "Sample Data"

        # Build message
        lines = [
            f"{emoji} *{decision}* {emoji}",
            "",
            f"📍 *Location:* {location}",
            f"{source_emoji} *Data Source:* {source_text}",
            f"🕒 *Updated:* {datetime.now().strftime('%I:%M %p')}",
            "",
        ]
        
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
