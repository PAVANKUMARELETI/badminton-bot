"""
WhatsApp bot integration for badminton wind forecasting.

This uses Twilio's WhatsApp API for messaging.

Setup:
1. Sign up for Twilio (https://www.twilio.com)
2. Set up WhatsApp sandbox or get approved sender
3. Get your Account SID, Auth Token, and WhatsApp number
4. Set environment variables:
   - TWILIO_ACCOUNT_SID
   - TWILIO_AUTH_TOKEN
   - TWILIO_WHATSAPP_NUMBER
5. Run: python -m src.integrations.whatsapp_bot

Users can then send:
- "forecast" - Get latest wind forecast
- "help" - Get help message
- Any text - Get forecast (default behavior)
"""

import logging
import os
from datetime import datetime
from typing import Optional

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

from src.cli.infer import load_model, make_forecast
from src.data.fetch import load_sample
from src.data.preprocess import build_features
from src.decision.rules import decide_play

logger = logging.getLogger(__name__)


class WhatsAppBot:
    """WhatsApp bot for wind forecasting using Twilio."""

    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        whatsapp_number: Optional[str] = None,
        model_path: Optional[str] = None,
    ):
        """
        Initialize WhatsApp bot.

        Args:
            account_sid: Twilio Account SID
            auth_token: Twilio Auth Token
            whatsapp_number: Twilio WhatsApp number (format: whatsapp:+14155238886)
            model_path: Path to trained model (default: latest)
        """
        self.account_sid = account_sid or os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = auth_token or os.getenv("TWILIO_AUTH_TOKEN")
        self.whatsapp_number = whatsapp_number or os.getenv("TWILIO_WHATSAPP_NUMBER")

        if not all([self.account_sid, self.auth_token]):
            raise ValueError(
                "Twilio credentials required. "
                "Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN env vars."
            )

        self.model_path = model_path or "experiments/latest/model.keras"
        self.model = None
        self.app = Flask(__name__)

        # Set up routes
        self._setup_routes()

    def _load_model(self):
        """Load the forecasting model."""
        if self.model is None:
            logger.info(f"Loading model from {self.model_path}")
            self.model = load_model(self.model_path)
            logger.info("Model loaded successfully")

    def _setup_routes(self):
        """Set up Flask routes for webhook."""

        @self.app.route("/webhook", methods=["POST"])
        def webhook():
            """Handle incoming WhatsApp messages."""
            return self.handle_message(request)

        @self.app.route("/health", methods=["GET"])
        def health():
            """Health check endpoint."""
            return {"status": "healthy", "service": "badminton-wind-bot"}, 200

    def handle_message(self, request):
        """
        Handle incoming WhatsApp message.

        Args:
            request: Flask request object

        Returns:
            TwiML response
        """
        # Get message details
        incoming_msg = request.values.get("Body", "").strip().lower()
        sender = request.values.get("From", "")

        logger.info(f"Received message from {sender}: {incoming_msg}")

        # Create response
        resp = MessagingResponse()
        msg = resp.message()

        try:
            # Route message to appropriate handler
            if incoming_msg in ["help", "start"]:
                response_text = self._get_help_message()
            elif incoming_msg in ["settings", "config"]:
                response_text = self._get_settings_message()
            else:
                # Default: treat any message as forecast request
                response_text = self._get_forecast()

            msg.body(response_text)

        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            msg.body("❌ Sorry, I encountered an error. Please try again later.")

        return str(resp)

    def _get_help_message(self) -> str:
        """Get help message."""
        return """
🏸 *Badminton Wind Forecast Bot* 🌬️

I help you decide if it's safe to play badminton based on wind conditions.

*How to use:*
Just send me any message like "Can I play?" and I'll check the wind!

*Commands:*
• forecast - Get wind forecast
• help - Show this message
• settings - View current settings

*Understanding Results:*
✅ PLAY - Wind is safe
❌ DON'T PLAY - Too windy

Safe limits:
• Wind: < 1.5 m/s
• Gusts: < 3.5 m/s

Stay safe! 🏸
        """.strip()

    def _get_settings_message(self) -> str:
        """Get settings message."""
        return """
⚙️ *Current Settings*

*Safety Thresholds:*
• Max median wind: 1.5 m/s
• Max wind gust: 3.5 m/s

*Forecast Horizons:*
• 1 hour ahead
• 3 hours ahead
• 6 hours ahead

Contact your admin to customize thresholds.
        """.strip()

    def _get_forecast(self) -> str:
        """
        Get wind forecast and decision.

        Returns:
            Formatted forecast message
        """
        # Load model if needed
        self._load_model()

        # Get forecast
        # TODO: Replace with real weather API
        df = load_sample()
        data_df = build_features(df)
        forecast_result = make_forecast(self.model, data_df)

        # Make decision
        decision_result = decide_play(forecast_result)

        # Format response
        return self._format_forecast_response(decision_result)

    def _format_forecast_response(self, decision_result: dict) -> str:
        """
        Format forecast result for WhatsApp.

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
            f"📅 {decision_result['timestamp']}",
            "",
            "*Wind Forecast:*",
        ]

        # Add horizon forecasts
        for horizon in ["1h", "3h", "6h"]:
            median = forecast["median"][f"horizon_{horizon}"]
            q90 = forecast["q90"][f"horizon_{horizon}"]
            passes = details[horizon]["passes"]

            status = "✅" if passes else "⚠️"
            lines.append(f"{status} *{horizon}:* {median:.1f} m/s (gust {q90:.1f})")

        # Add reason if don't play
        if decision == "DON'T PLAY":
            lines.append("")
            lines.append(f"⚠️ {decision_result['reason']}")

        lines.append("")
        lines.append("_Safe: <1.5 m/s | Max gust: <3.5 m/s_")

        return "\n".join(lines)

    def run(self, host: str = "0.0.0.0", port: int = 5000):
        """
        Start the WhatsApp bot server.

        Args:
            host: Host to bind to
            port: Port to listen on
        """
        logger.info(f"Starting WhatsApp bot on {host}:{port}...")
        logger.info("Webhook URL: http://your-server:5000/webhook")
        logger.info("Configure this URL in Twilio Console")
        self.app.run(host=host, port=port, debug=False)


def main():
    """Main entry point for WhatsApp bot."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Check environment variables
    if not all(
        [
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN"),
        ]
    ):
        print("❌ Twilio credentials not set!")
        print("\nHow to set up WhatsApp bot:")
        print("1. Sign up at https://www.twilio.com")
        print("2. Set up WhatsApp sandbox or approved sender")
        print("3. Set environment variables:")
        print("   PowerShell:")
        print("     $env:TWILIO_ACCOUNT_SID='your-sid'")
        print("     $env:TWILIO_AUTH_TOKEN='your-token'")
        print("     $env:TWILIO_WHATSAPP_NUMBER='whatsapp:+14155238886'")
        print("\n4. Run: python -m src.integrations.whatsapp_bot")
        print("5. Expose port 5000 with ngrok or deploy to cloud")
        print("6. Configure webhook URL in Twilio Console")
        return

    # Create and run bot
    bot = WhatsAppBot()
    bot.run()


if __name__ == "__main__":
    main()
