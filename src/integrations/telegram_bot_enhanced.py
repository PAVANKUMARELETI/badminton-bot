"""
Enhanced Telegram bot with fun features for college groups.

This extends the basic bot with:
- Fun randomized responses
- User tracking and stats
- Daily scheduled forecasts
- Group polls
- Leaderboard system
- Achievement badges
- Court booking suggestions

Setup same as basic bot, just use this instead:
python -m src.integrations.telegram_bot_enhanced
"""

import asyncio
import logging
import os
import random
from datetime import datetime, time
from pathlib import Path
from typing import Optional

from telegram import Update, Poll
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    PollAnswerHandler,
    filters,
)

from src.integrations.telegram_bot import TelegramBot

logger = logging.getLogger(__name__)


class TelegramBotEnhanced(TelegramBot):
    """Enhanced Telegram bot with fun features for college groups."""

    def __init__(self, token: Optional[str] = None, model_path: Optional[str] = None):
        super().__init__(token, model_path)
        
        # Fun responses
        self.play_responses = [
            "🏸 Let's SMASH! Wind is perfect! 💪",
            "🌟 Game ON! Court conditions are IDEAL! 🎯",
            "⚡ Shuttlecock won't know what hit it! Perfect weather! 🔥",
            "🎊 YESSS! Time to show off those drop shots! 🏆",
            "🌈 Beautiful day for badminton! Let's GOOO! 🚀",
            "💯 Perfect conditions! Your serve is calling! 🎾",
            "🔥 Wind gods are with us! Rally time! 🏸",
            "✨ Today's your day to shine on court! ⭐",
        ]
        
        self.dont_play_responses = [
            "🌪️ Too windy mate! How about Netflix instead? 🍿",
            "💨 Wind says NO. Gym day? 🏋️",
            "⛈️ Save your energy for tomorrow! 💪",
            "🌬️ Shuttlecock would fly to next campus! Better wait 😅",
            "❄️ Wind chill mode ON. Indoor games? 🎮",
            "🍃 Even the trees are bending! Rest day 🛋️",
            "💤 Weather says: Take a break! You earned it 😌",
            "🌊 This wind could power a wind farm! Tomorrow's better 🔋",
        ]

        # User stats (in production, use a database)
        self.user_stats = {}  # {user_id: {games: int, forecasts: int, streak: int}}

    async def start_command(self, update, context):
        """Enhanced welcome message."""
        user_name = update.effective_user.first_name
        welcome_message = f"""
🏸 *Hey {user_name}! Welcome to Badminton HQ!* 🌬️

I'm your personal wind forecaster and badminton buddy! 🤖

*Quick Commands:*
/forecast - Check if we can play 🎯
/stats - Your playing stats 📊
/leaderboard - Top players this week 🏆
/subscribe - Daily 7 AM forecasts ⏰
/poll - Should we play? (group vote) 🗳️
/joke - Badminton dad joke 😄
/motivation - Inspirational quote 💪
/help - Full help menu 📚

*Pro Tip:* Just ask naturally!
"Can I play?" 
"Is it windy?"
"Weather check!"

Let's get you on the court! 🚀
        """
        await update.message.reply_text(welcome_message, parse_mode="Markdown")
        
        # Initialize user stats
        user_id = update.effective_user.id
        if user_id not in self.user_stats:
            self.user_stats[user_id] = {
                "forecasts": 0,
                "games": 0,
                "streak": 0,
                "last_play": None,
            }

    async def forecast_command(self, update, context):
        """Enhanced forecast with fun responses."""
        try:
            user_id = update.effective_user.id
            
            # Track usage
            if user_id in self.user_stats:
                self.user_stats[user_id]["forecasts"] += 1

            # Load model and get forecast
            self._load_model()
            
            thinking_emojis = ["🤔", "🧐", "🔍", "🌡️", "🎯"]
            thinking_msg = await update.message.reply_text(
                f"{random.choice(thinking_emojis)} Checking wind conditions..."
            )

            # Get forecast (using parent class method)
            from src.data.fetch import load_sample
            from src.data.preprocess import build_features
            from src.cli.infer import make_forecast
            from src.decision.rules import decide_play

            df = load_sample()
            data_df = build_features(df)
            forecast_result = make_forecast(self.model, data_df)
            decision_result = decide_play(forecast_result)

            # Choose fun response
            decision = decision_result["decision"]
            if decision == "PLAY":
                fun_message = random.choice(self.play_responses)
            else:
                fun_message = random.choice(self.dont_play_responses)

            # Format complete response
            response = (
                f"{fun_message}\n\n"
                + self._format_forecast_response(decision_result)
                + f"\n\n_Forecast #{self.user_stats[user_id]['forecasts']}_"
            )

            await thinking_msg.delete()
            await update.message.reply_text(response, parse_mode="Markdown")

        except Exception as e:
            logger.error(f"Error in forecast_command: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ Oops! Something went wrong. Try `/forecast` again?"
            )

    async def stats_command(self, update, context):
        """Show user stats."""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        
        if user_id not in self.user_stats:
            self.user_stats[user_id] = {
                "forecasts": 0,
                "games": 0,
                "streak": 0,
                "last_play": None,
            }
        
        stats = self.user_stats[user_id]
        
        # Calculate badges
        badges = []
        if stats["forecasts"] >= 50:
            badges.append("🔮 Forecast Pro")
        if stats["games"] >= 20:
            badges.append("🏆 Regular Player")
        if stats["streak"] >= 7:
            badges.append("🔥 Week Warrior")
        if stats["forecasts"] >= 100:
            badges.append("⭐ Weather Master")
        
        badges_text = " ".join(badges) if badges else "🎯 Keep playing to unlock badges!"
        
        stats_message = f"""
📊 *{user_name}'s Badminton Stats*

*Forecasts Checked:* {stats['forecasts']} 🔍
*Games Played:* {stats['games']} 🏸
*Current Streak:* {stats['streak']} days 🔥

*Badges:*
{badges_text}

_Keep playing to unlock more achievements!_ 🏆
        """
        
        await update.message.reply_text(stats_message, parse_mode="Markdown")

    async def leaderboard_command(self, update, context):
        """Show weekly leaderboard."""
        # Sort users by games played
        sorted_users = sorted(
            self.user_stats.items(),
            key=lambda x: x[1]["games"],
            reverse=True
        )[:10]
        
        if not sorted_users:
            await update.message.reply_text(
                "🏆 No games recorded yet! Be the first to play! 🎯"
            )
            return
        
        medals = ["🥇", "🥈", "🥉"]
        leaderboard = ["🏆 *This Week's Top Players* 🏆\n"]
        
        for idx, (user_id, stats) in enumerate(sorted_users):
            medal = medals[idx] if idx < 3 else f"{idx + 1}."
            # In production, fetch actual usernames
            username = f"Player{user_id % 1000}"
            games = stats["games"]
            leaderboard.append(f"{medal} {username} - {games} games")
        
        leaderboard_text = "\n".join(leaderboard)
        await update.message.reply_text(leaderboard_text, parse_mode="Markdown")

    async def poll_command(self, update, context):
        """Create a poll asking if group should play."""
        # Get forecast first
        self._load_model()
        
        from src.data.fetch import load_sample
        from src.data.preprocess import build_features
        from src.cli.infer import make_forecast
        from src.decision.rules import decide_play

        df = load_sample()
        data_df = build_features(df)
        forecast_result = make_forecast(self.model, data_df)
        decision_result = decide_play(forecast_result)
        
        median_wind = decision_result["forecast"]["median"]["horizon_1h"]
        decision = decision_result["decision"]
        
        # Create poll
        question = f"🏸 Wind is {median_wind:.1f} m/s. Should we play?"
        options = [
            "✅ Yes, let's play!",
            "⚠️ Maybe, I'm flexible",
            "❌ No, too risky",
        ]
        
        message = await update.message.reply_poll(
            question=question,
            options=options,
            is_anonymous=False,
        )
        
        # Add context
        context_msg = f"_Bot recommends: {decision}_"
        await update.message.reply_text(context_msg, parse_mode="Markdown")

    async def joke_command(self, update, context):
        """Send a random badminton joke."""
        jokes = [
            "Why don't badminton players ever get lost? Because they always follow the *shuttle*! 🚐",
            "What's a badminton player's favorite type of music? *Net*herlands folk music! 🎵",
            "Why did the shuttlecock go to therapy? It had too many *ups and downs*! 😅",
            "What do you call a badminton player who loves math? A *racket* scientist! 🔢",
            "Why don't shuttlecocks ever win arguments? They always get *batted* down! 🏸",
            "What's a badminton player's favorite drink? *Smash* berry smoothie! 🍓",
            "Why was the badminton court always busy? Because everyone wanted to get a *net* gain! 💰",
        ]
        
        joke = random.choice(jokes)
        await update.message.reply_text(joke, parse_mode="Markdown")

    async def motivation_command(self, update, context):
        """Send inspirational badminton quote."""
        quotes = [
            "🏸 *Champions are made in the gym, legends on the court!*",
            "⚡ *Your only limit is the net. Jump higher!*",
            "🔥 *Every smash brings you closer to greatness!*",
            "💪 *The shuttle may be light, but your spirit is mighty!*",
            "🌟 *Practice like you've never won. Play like you've never lost!*",
            "🎯 *Precision, power, perseverance. That's badminton!*",
            "✨ *The court is your canvas. Paint it with perfect shots!*",
            "🚀 *Dream big, play bigger, smash hardest!*",
        ]
        
        quote = random.choice(quotes)
        await update.message.reply_text(quote, parse_mode="Markdown")

    async def subscribe_command(self, update, context):
        """Subscribe to daily 7 AM forecasts."""
        user_id = update.effective_user.id
        
        # In production, store subscriptions in database
        subscribe_msg = """
✅ *Subscribed to Daily Forecasts!*

You'll receive:
🌅 Morning forecast at 7:00 AM
🌆 Evening update at 5:00 PM

Use /unsubscribe to stop notifications.

_Note: This is a demo. In production, you'd receive actual scheduled messages!_
        """
        
        await update.message.reply_text(subscribe_msg, parse_mode="Markdown")

    # Schedule daily forecast (example - requires proper scheduling in production)
    async def send_daily_forecast(self, chat_id: int):
        """Send scheduled daily forecast."""
        try:
            self._load_model()
            
            from src.data.fetch import load_sample
            from src.data.preprocess import build_features
            from src.cli.infer import make_forecast
            from src.decision.rules import decide_play

            df = load_sample()
            data_df = build_features(df)
            forecast_result = make_forecast(self.model, data_df)
            decision_result = decide_play(forecast_result)
            
            decision = decision_result["decision"]
            emoji = "☀️" if decision == "PLAY" else "⛅"
            
            message = f"""
{emoji} *Good Morning, Badminton Squad!*

*Today's Forecast:* {decision}

{self._format_forecast_response(decision_result)}

Have a great day! 🏸
            """
            
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Error sending daily forecast: {e}")

    def run(self):
        """Start the enhanced bot."""
        try:
            from telegram.ext import Application, CommandHandler, MessageHandler, filters
        except ImportError:
            raise ImportError(
                "python-telegram-bot not installed. "
                "Install with: pip install python-telegram-bot"
            )

        logger.info("Starting Enhanced Telegram bot...")

        # Create application
        self.application = Application.builder().token(self.token).build()

        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("forecast", self.forecast_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("leaderboard", self.leaderboard_command))
        self.application.add_handler(CommandHandler("poll", self.poll_command))
        self.application.add_handler(CommandHandler("joke", self.joke_command))
        self.application.add_handler(CommandHandler("motivation", self.motivation_command))
        self.application.add_handler(CommandHandler("subscribe", self.subscribe_command))
        self.application.add_handler(CommandHandler("settings", self.settings_command))

        # Handle all text messages
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

        logger.info("✨ Enhanced Bot is ready! Features unlocked:")
        logger.info("  🎯 Fun randomized responses")
        logger.info("  📊 User stats & leaderboards")
        logger.info("  🗳️ Group polls")
        logger.info("  😄 Jokes & motivation")
        logger.info("  🏆 Achievement badges")
        logger.info("")
        logger.info("Press Ctrl+C to stop.")

        # Run the bot
        self.application.run_polling(allowed_updates=["message", "poll"])


def main():
    """Main entry point for enhanced Telegram bot."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

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

    # Create and run enhanced bot
    bot = TelegramBotEnhanced(token=token)
    bot.run()


if __name__ == "__main__":
    main()
