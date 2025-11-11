"""
Telegram bot integration for badminton wind forecasting - REFACTORED.

This is the refactored version with modular architecture:
- bot_formatters.py: Message formatting
- bot_weather.py: Weather data handling
- bot_keyboards.py: Inline keyboard layouts
- bot_location.py: Location management

Setup:
1. Create bot via @BotFather on Telegram
2. Get your bot token
3. Set TELEGRAM_BOT_TOKEN environment variable
4. Run: python -m src.integrations.telegram_bot_refactored

Features:
- /start - Welcome and main menu
- /now - Check current conditions
- /forecast - Future predictions
- /help - Usage instructions
- /location - Change location
"""

import logging
import os
from pathlib import Path
from typing import Optional

# Sentry error tracking
try:
    import sentry_sdk
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Import our modular components
from src.integrations.bot_formatters import (
    format_welcome_message,
    format_help_message,
    format_current_weather_response,
    format_forecast_response,
    format_location_change_message
)
from src.integrations.bot_weather import (
    fetch_current_weather,
    fetch_forecast_data,
    prepare_forecast_dataframe,
    make_play_decision,
    get_bwf_thresholds
)
from src.integrations.bot_keyboards import (
    get_main_menu_keyboard,
    get_now_action_keyboard,
    get_forecast_action_keyboard,
    get_help_keyboard
)
from src.integrations.bot_location import (
    parse_location,
    get_default_location
)

# Model and decision imports
from src.cli.infer import load_model as load_lstm_model, make_forecast
from src.data.preprocess import build_features
from src.decision.rules import decide_play

logger = logging.getLogger(__name__)


def initialize_sentry():
    """Initialize Sentry error tracking if DSN is configured."""
    if not SENTRY_AVAILABLE:
        logger.warning("Sentry SDK not installed. Run: pip install sentry-sdk")
        return False
    
    sentry_dsn = os.getenv("SENTRY_DSN")
    if not sentry_dsn:
        logger.info("SENTRY_DSN not set. Error tracking disabled.")
        return False
    
    try:
        sentry_sdk.init(
            dsn=sentry_dsn,
            traces_sample_rate=1.0,
            environment=os.getenv("ENVIRONMENT", "production"),
            release=f"badminton-bot@{os.getenv('VERSION', 'unknown')}",
        )
        logger.info("✅ Sentry error tracking initialized")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")
        return False


class BadmintonBot:
    """Refactored Telegram bot for wind forecasting."""

    def __init__(self, token: Optional[str] = None, model_path: Optional[str] = None):
        """
        Initialize bot.
        
        Args:
            token: Telegram bot token
            model_path: Path to LSTM model
        """
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN required")

        self.model_path = model_path or "experiments/latest/model.keras"
        self.model = None
        self.application = None
        
        # Location tracking
        lat, lon, name = get_default_location()
        self.current_lat = lat
        self.current_lon = lon
        self.current_location = name
        
        logger.info(f"Bot initialized for {self.current_location}")

    def _load_model(self):
        """Lazy load LSTM model."""
        if self.model is None:
            try:
                logger.info(f"Loading model from {self.model_path}")
                self.model = load_lstm_model(self.model_path)
                logger.info("Model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                self.model = None

    # ==================== COMMAND HANDLERS ====================

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        message = format_welcome_message(
            self.current_location,
            self.current_lat,
            self.current_lon
        )
        keyboard = get_main_menu_keyboard()
        
        await update.message.reply_text(
            message,
            parse_mode="Markdown",
            reply_markup=keyboard
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        message = format_help_message()
        keyboard = get_help_keyboard()
        
        await update.message.reply_text(
            message,
            parse_mode="Markdown",
            reply_markup=keyboard
        )

    async def now_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /now command - check current weather."""
        # Determine if from button or message
        if update.callback_query:
            query = update.callback_query
            thinking_msg = await query.edit_message_text("🌤️ Checking current weather...")
        else:
            thinking_msg = await update.message.reply_text("🌤️ Checking current weather...")

        # Fetch current weather
        current_weather, data_source, weather_data_time = fetch_current_weather(
            self.current_lat,
            self.current_lon,
            self.current_location
        )

        # Make decision
        if current_weather and data_source == "live":
            can_play = make_play_decision(current_weather)
            safe_median, safe_gust = get_bwf_thresholds()
            
            response = format_current_weather_response(
                can_play=can_play,
                current_weather=current_weather,
                data_source=data_source,
                location=self.current_location,
                weather_data_time=weather_data_time,
                safe_median_wind=safe_median,
                safe_gust_wind=safe_gust
            )
        else:
            response = "❌ Unable to fetch current weather data. Please try again later."

        keyboard = get_now_action_keyboard()
        
        # Send or edit response
        if update.callback_query:
            await update.callback_query.edit_message_text(
                response,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        else:
            await thinking_msg.edit_text(
                response,
                parse_mode="Markdown",
                reply_markup=keyboard
            )

    async def forecast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /forecast command - future predictions."""
        # Load model
        self._load_model()

        # Determine if from button or message
        if update.callback_query:
            query = update.callback_query
            thinking_msg = await query.edit_message_text("🤔 Analyzing wind conditions...")
        else:
            thinking_msg = await update.message.reply_text("🤔 Analyzing wind conditions...")

        try:
            # Fetch forecast data
            weather_data, data_source = fetch_forecast_data(
                self.current_lat,
                self.current_lon,
                self.current_location
            )
            
            # Get current weather for display
            current_weather, _, weather_data_time = fetch_current_weather(
                self.current_lat,
                self.current_lon,
                self.current_location
            )

            # Prepare data
            df = prepare_forecast_dataframe(weather_data)
            
            # Build features
            logger.info("Building features")
            data_df = build_features(df)
            
            # Make forecast
            logger.info("Making forecast")
            forecast_result = make_forecast(self.model, data_df)
            
            # Make decision
            logger.info("Making decision")
            decision_result = decide_play(
                median_forecast=forecast_result["median"],
                q90_forecast=forecast_result["q90"]
            )

            # Format response
            response = format_forecast_response(
                decision_result=decision_result,
                forecast_result=forecast_result,
                current_weather=current_weather,
                data_source=data_source,
                location=self.current_location,
                weather_data_time=weather_data_time
            )

            keyboard = get_forecast_action_keyboard()
            
            # Send or edit response
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    response,
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
            else:
                await thinking_msg.edit_text(
                    response,
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )

        except Exception as e:
            logger.error(f"Error in forecast: {e}", exc_info=True)
            error_msg = "❌ Sorry, encountered an error. Please try again."
            
            if update.callback_query:
                await update.callback_query.edit_message_text(error_msg)
            else:
                await thinking_msg.edit_text(error_msg)

    async def location_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /location command."""
        if not context.args:
            await update.message.reply_text(
                "📍 Usage: `/location <city name>`\n\n"
                "Example: `/location Delhi`",
                parse_mode="Markdown"
            )
            return

        new_location_text = " ".join(context.args)
        lat, lon, name = parse_location(new_location_text)
        
        if lat and lon:
            self.current_lat = lat
            self.current_lon = lon
            self.current_location = name
            logger.info(f"Location changed to: {name}")

        message = format_location_change_message(name, lat, lon)
        keyboard = get_main_menu_keyboard()
        
        await update.message.reply_text(
            message,
            parse_mode="Markdown",
            reply_markup=keyboard
        )

    # ==================== BUTTON CALLBACKS ====================

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard button presses."""
        query = update.callback_query
        await query.answer()  # Acknowledge button press
        
        callback_data = query.data
        logger.info(f"Button pressed: {callback_data}")

        if callback_data == "play_now":
            await self.now_command(update, context)
            
        elif callback_data == "forecast":
            await self.forecast_command(update, context)
            
        elif callback_data == "start":
            message = format_welcome_message(
                self.current_location,
                self.current_lat,
                self.current_lon
            )
            keyboard = get_main_menu_keyboard()
            await query.edit_message_text(
                message,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            
        elif callback_data == "help":
            message = format_help_message()
            keyboard = get_help_keyboard()
            await query.edit_message_text(
                message,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            
        elif callback_data == "location":
            await query.edit_message_text(
                "📍 To change location, use:\n`/location <city name>`\n\n"
                "Example: `/location Delhi`",
                parse_mode="Markdown"
            )

    # ==================== BOT LIFECYCLE ====================

    def run(self):
        """Start the bot."""
        try:
            from telegram.ext import Application
        except ImportError:
            raise ImportError("python-telegram-bot required: pip install python-telegram-bot")

        logger.info("Starting Badminton Bot...")

        # Create application
        self.application = Application.builder().token(self.token).build()

        # Add command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("now", self.now_command))
        self.application.add_handler(CommandHandler("forecast", self.forecast_command))
        self.application.add_handler(CommandHandler("location", self.location_command))

        # Add button callback handler
        self.application.add_handler(CallbackQueryHandler(self.button_callback))

        # Add text message handler (treat as forecast request)
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.forecast_command)
        )

        logger.info("Bot ready! Press Ctrl+C to stop.")
        
        # Run bot
        self.application.run_polling(allowed_updates=["message", "callback_query"])


def main():
    """Entry point for bot."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Initialize Sentry error tracking
    initialize_sentry()

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN environment variable not set!")
        print("\nSetup:")
        print("1. Create bot via @BotFather on Telegram")
        print("2. Get your bot token")
        print("3. Set environment variable:")
        print("   PowerShell: $env:TELEGRAM_BOT_TOKEN='your-token-here'")
        return

    bot = BadmintonBot(token=token)
    bot.run()


if __name__ == "__main__":
    main()
