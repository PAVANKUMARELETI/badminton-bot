"""Quick check of current weather at IIIT Lucknow"""
import requests

response = requests.get(
    'https://api.openweathermap.org/data/2.5/weather',
    params={
        'lat': 26.7984,
        'lon': 81.0241,
        'appid': 'c9bff12eb91b0e17f64594137bbd16fd',
        'units': 'metric'
    }
)

data = response.json()

print("=== Current Weather at IIIT Lucknow ===")
print(f"Wind Speed: {data['wind']['speed']} m/s ({data['wind']['speed']*3.6:.1f} km/h)")
wind_gust = data['wind'].get('gust', data['wind']['speed'] * 1.3)
print(f"Wind Gust: {wind_gust} m/s ({wind_gust*3.6:.1f} km/h)")
print(f"Temperature: {data['main']['temp']}°C")
print(f"Conditions: {data['weather'][0]['description']}")
print(f"Humidity: {data['main']['humidity']}%")
print(f"Pressure: {data['main']['pressure']} hPa")
