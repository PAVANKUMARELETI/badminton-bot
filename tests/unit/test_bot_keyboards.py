"""Unit tests for bot_keyboards module."""
import pytest
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.integrations.bot_keyboards import (
    get_main_menu_keyboard,
    get_now_action_keyboard,
    get_forecast_action_keyboard,
    get_help_keyboard,
)


class TestBotKeyboards:
    """Test inline keyboard generation functions."""

    def test_get_main_menu_keyboard(self):
        """Test main menu keyboard structure."""
        keyboard = get_main_menu_keyboard()
        
        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 2  # Two rows
        
        # First row: Play Now, Forecast
        first_row = keyboard.inline_keyboard[0]
        assert len(first_row) == 2
        assert first_row[0].text == "🏸 Can I Play NOW?"
        assert first_row[0].callback_data == "play_now"
        assert first_row[1].text == "📊 Future Forecast"
        assert first_row[1].callback_data == "forecast"
        
        # Second row: Change Location, Help
        second_row = keyboard.inline_keyboard[1]
        assert len(second_row) == 2
        assert second_row[0].text == "📍 Change Location"
        assert second_row[0].callback_data == "location"
        assert second_row[1].text == "❓ Help"
        assert second_row[1].callback_data == "help"

    def test_get_now_action_keyboard(self):
        """Test NOW action keyboard structure."""
        keyboard = get_now_action_keyboard()
        
        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 2  # Two rows
        
        # First row: Refresh, See Forecast
        first_row = keyboard.inline_keyboard[0]
        assert len(first_row) == 2
        assert first_row[0].text == "🔄 Refresh"
        assert first_row[0].callback_data == "play_now"
        assert first_row[1].text == "📊 See Forecast"
        assert first_row[1].callback_data == "forecast"
        
        # Second row: Main Menu
        second_row = keyboard.inline_keyboard[1]
        assert len(second_row) == 1
        assert second_row[0].text == "🔙 Main Menu"
        assert second_row[0].callback_data == "start"

    def test_get_forecast_action_keyboard(self):
        """Test FORECAST action keyboard structure."""
        keyboard = get_forecast_action_keyboard()
        
        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 2  # Two rows
        
        # First row: Refresh, Change Location
        first_row = keyboard.inline_keyboard[0]
        assert len(first_row) == 2
        assert first_row[0].text == "🔄 Refresh"
        assert first_row[0].callback_data == "forecast"
        assert first_row[1].text == "📍 Change Location"
        assert first_row[1].callback_data == "location"
        
        # Second row: Main Menu
        second_row = keyboard.inline_keyboard[1]
        assert len(second_row) == 1
        assert second_row[0].text == "🔙 Main Menu"
        assert second_row[0].callback_data == "start"

    def test_get_help_keyboard(self):
        """Test help keyboard structure."""
        keyboard = get_help_keyboard()
        
        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 3  # Three rows
        
        # First row: Play NOW
        assert len(keyboard.inline_keyboard[0]) == 1
        assert keyboard.inline_keyboard[0][0].text == "🏸 Can I Play NOW?"
        assert keyboard.inline_keyboard[0][0].callback_data == "play_now"
        
        # Second row: Forecast
        assert len(keyboard.inline_keyboard[1]) == 1
        assert keyboard.inline_keyboard[1][0].text == "📊 Future Forecast"
        assert keyboard.inline_keyboard[1][0].callback_data == "forecast"
        
        # Third row: Back to Menu
        assert len(keyboard.inline_keyboard[2]) == 1
        assert keyboard.inline_keyboard[2][0].text == "🔙 Back to Menu"
        assert keyboard.inline_keyboard[2][0].callback_data == "start"

    def test_all_keyboards_return_markup(self):
        """Test that all keyboard functions return InlineKeyboardMarkup."""
        keyboards = [
            get_main_menu_keyboard(),
            get_now_action_keyboard(),
            get_forecast_action_keyboard(),
            get_help_keyboard(),
        ]
        
        for keyboard in keyboards:
            assert isinstance(keyboard, InlineKeyboardMarkup)
            assert len(keyboard.inline_keyboard) > 0

    def test_callback_data_consistency(self):
        """Test that callback data is consistent across keyboards."""
        # Collect all callback data
        all_callbacks = set()
        
        for keyboard_func in [get_main_menu_keyboard, get_now_action_keyboard, 
                               get_forecast_action_keyboard, get_help_keyboard]:
            keyboard = keyboard_func()
            for row in keyboard.inline_keyboard:
                for button in row:
                    all_callbacks.add(button.callback_data)
        
        # Expected callbacks
        expected = {"play_now", "forecast", "location", "help", "start"}
        assert all_callbacks == expected
