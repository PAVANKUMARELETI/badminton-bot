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

from src.cli.infer import load_model, make_forecast
from src.data.fetch import load_sample
from src.data.preprocess import build_features
from src.decision.rules import decide_play

logger = logging.getLogger(__name__)


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

    def _load_model(self):
        """Load the forecasting model."""
        if self.model is None:
            logger.info(f"Loading model from {self.model_path}")
            self.model = load_model(self.model_path)
            logger.info("Model loaded successfully")

    async def start_command(self, update, context):
        """Handle /start command."""
        welcome_message = """
🏸 *Welcome to Badminton Wind Forecast Bot!* 🌬️

I help you decide if it's safe to play badminton based on wind conditions.

*Commands:*
/forecast - Get current wind forecast
/help - Show this help message
/settings - Customize your preferences

Just ask me "Can I play?" anytime! 🎯
        """
        await update.message.reply_text(
            welcome_message, parse_mode="Markdown"
        )

    async def help_command(self, update, context):
        """Handle /help command."""
        help_message = """
🏸 *How to Use This Bot* 🏸

*Quick Check:*
Just send me any message like:
• "Can I play?"
• "Weather check"
• "Is it windy?"

*Commands:*
/forecast - Detailed wind forecast
/start - Welcome message
/help - This help message

*Understanding the Forecast:*
✅ PLAY - Wind is within safe limits
❌ DON'T PLAY - Wind too strong for badminton

*Horizons:*
• 1h - Next hour forecast
• 3h - Next 3 hours forecast
• 6h - Next 6 hours forecast

Safe wind: < 1.5 m/s (median)
Max gust: < 3.5 m/s (90th percentile)

Stay safe and enjoy playing! 🏸
        """
        await update.message.reply_text(help_message, parse_mode="Markdown")

    async def forecast_command(self, update, context):
        """Handle /forecast command."""
        try:
            # Load model if not already loaded
            self._load_model()

            # Send "thinking" message
            thinking_msg = await update.message.reply_text(
                "🤔 Analyzing wind conditions..."
            )

            # Get forecast
            # TODO: In production, replace with actual weather API
            df = load_sample()
            data_df = build_features(df)
            forecast_result = make_forecast(self.model, data_df)

            # Make decision
            decision_result = decide_play(forecast_result)

            # Format response
            response = self._format_forecast_response(decision_result)

            # Delete thinking message and send result
            await thinking_msg.delete()
            await update.message.reply_text(response, parse_mode="Markdown")

        except Exception as e:
            logger.error(f"Error in forecast_command: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ Sorry, I encountered an error. Please try again later."
            )

    async def handle_message(self, update, context):
        """Handle general text messages."""
        # Treat any message as a forecast request
        await self.forecast_command(update, context)

    def _format_forecast_response(self, decision_result: dict) -> str:
        """
        Format forecast result for Telegram.

        Args:
            decision_result: Decision output from decide_play()

        Returns:
            Formatted message string
        """
        decision = decision_result["decision"]
        forecast = decision_result["forecast"]
        details = decision_result["details"]

        # Emoji for decision
        emoji = "✅" if decision == "PLAY" else "❌"

        # Build message
        lines = [
            f"{emoji} *{decision}* {emoji}",
            "",
            f"📅 *Forecast Time:* {decision_result['timestamp']}",
            "",
            "*Wind Speed Predictions:*",
        ]

        # Add horizon forecasts
        for horizon in ["1h", "3h", "6h"]:
            median = forecast["median"][f"horizon_{horizon}"]
            q90 = forecast["q90"][f"horizon_{horizon}"]
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

        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("forecast", self.forecast_command))
        self.application.add_handler(CommandHandler("settings", self.settings_command))

        # Handle all text messages as forecast requests
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

        logger.info("Bot is ready! Press Ctrl+C to stop.")

        # Run the bot
        self.application.run_polling(allowed_updates=["message"])


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
