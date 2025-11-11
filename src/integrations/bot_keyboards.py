"""
Button callback handlers for Telegram bot.

This module contains all inline keyboard button callback handlers,
keeping UI interaction logic separate from command handlers.
"""
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Get main menu inline keyboard."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🏸 Can I Play NOW?", callback_data="play_now"),
            InlineKeyboardButton("📊 Future Forecast", callback_data="forecast")
        ],
        [
            InlineKeyboardButton("📍 Change Location", callback_data="location"),
            InlineKeyboardButton("❓ Help", callback_data="help")
        ]
    ])


def get_now_action_keyboard() -> InlineKeyboardMarkup:
    """Get action keyboard for NOW command response."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="play_now"),
            InlineKeyboardButton("📊 See Forecast", callback_data="forecast")
        ],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="start")]
    ])


def get_forecast_action_keyboard() -> InlineKeyboardMarkup:
    """Get action keyboard for FORECAST command response."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="forecast"),
            InlineKeyboardButton("📍 Change Location", callback_data="location")
        ],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="start")]
    ])


def get_help_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for help message."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏸 Can I Play NOW?", callback_data="play_now")],
        [InlineKeyboardButton("📊 Future Forecast", callback_data="forecast")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="start")]
    ])


def get_location_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for location selection."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="start")]
    ])
