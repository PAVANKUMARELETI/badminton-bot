"""
Integration modules for messaging platforms (WhatsApp, Telegram, etc.)
"""

from .telegram_bot import TelegramBot

# Import WhatsApp bot only if Flask is installed
try:
    from .whatsapp_bot import WhatsAppBot
    __all__ = ["TelegramBot", "WhatsAppBot"]
except ImportError:
    # Flask not installed, skip WhatsApp bot
    __all__ = ["TelegramBot"]
