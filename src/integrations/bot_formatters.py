"""
Message formatters for Telegram bot responses.

This module contains all message formatting functions for the bot,
keeping presentation logic separate from business logic.
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


def format_welcome_message(location: str, lat: float, lon: float) -> str:
    """
    Format welcome message for /start command.
    
    Args:
        location: Location name
        lat: Latitude
        lon: Longitude
        
    Returns:
        Formatted welcome message
    """
    return f"""
🏸 *Welcome to Badminton Wind Forecast Bot!* 🌬️

I help you decide if it's safe to play badminton based on wind conditions.

📍 *Current Location:* {location}
🌍 *Coordinates:* {lat}°N, {lon}°E

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


def format_help_message() -> str:
    """Format help message for /help command."""
    return """
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

*🌬️ Safety Thresholds (BWF Standards):*
• Maximum wind: < 3.33 m/s (12 km/h)
• Optimal range: 1.67-3.33 m/s (6-12 km/h)
• Maximum gusts: < 5.0 m/s (18 km/h)

*Based on Badminton World Federation (BWF) AirBadminton recommendations*

*🎯 Understanding Results:*
✅ PLAY - Conditions are safe
❌ DON'T PLAY - Wind too strong for badminton

Stay safe and enjoy playing! 🏸
    """


def format_current_weather_response(
    can_play: bool,
    current_weather: Dict,
    data_source: str,
    location: str,
    weather_data_time: Optional[datetime],
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


def format_forecast_response(
    decision_result: Dict,
    forecast_result: Dict,
    current_weather: Optional[Dict] = None,
    data_source: str = "sample",
    location: str = "Unknown",
    weather_data_time: Optional[datetime] = None
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
            logger.warning(f"Error formatting timestamp: {e}")
    
    lines.append("")
    
    # Add current weather conditions if available
    if current_weather:
        lines.append("*🌤️ Current Weather:*")
        
        if 'wind_m_s' in current_weather:
            wind = current_weather['wind_m_s']
            lines.append(f"💨 Wind: {wind:.1f} m/s ({wind*3.6:.1f} km/h)")
        
        if 'temp' in current_weather:
            temp = current_weather['temp']
            lines.append(f"🌡️ Temp: {temp:.1f}°C")
        
        if 'humidity' in current_weather:
            humidity = current_weather['humidity']
            lines.append(f"💧 Humidity: {humidity:.0f}%")
        
        lines.append("")

    lines.append("*🔮 Wind Forecast:*")

    # Add horizon forecasts
    for horizon in ["1h", "3h", "6h"]:
        median = median_forecast[f"horizon_{horizon}"]
        q90 = q90_forecast[f"horizon_{horizon}"]
        
        # Check if this horizon is safe
        safe = (median <= 3.33 and q90 <= 5.0)  # BWF thresholds
        emoji_status = "✅" if safe else "⚠️"
        
        lines.append(
            f"{emoji_status} *{horizon}*: {median:.1f} m/s "
            f"(gust: {q90:.1f} m/s)"
        )

    # Add reason if don't play
    if decision == "DON'T PLAY" and details.get("reason"):
        lines.append("")
        lines.append(f"*Reason:* {details['reason']}")

    lines.append("")
    lines.append("_Safe wind: < 3.33 m/s | Max gust: < 5.0 m/s_")

    return "\n".join(lines)


def format_location_change_message(location: str, lat: Optional[float], lon: Optional[float]) -> str:
    """
    Format location change confirmation message.
    
    Args:
        location: New location name
        lat: Latitude (None if not found)
        lon: Longitude (None if not found)
        
    Returns:
        Formatted message
    """
    if lat and lon:
        return f"""
📍 *Location Updated!*

*New Location:* {location}
*Coordinates:* {lat}°N, {lon}°E

Use /now or /forecast to check conditions at this location.
        """
    else:
        return f"""
⚠️ *Location Not Found*

Could not find coordinates for "{location}".

Currently using: Default location
Try a different city name or use /location <city> to change.
        """
