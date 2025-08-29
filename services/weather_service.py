# services/weather_service.py
import requests
import os
from dotenv import load_dotenv
load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather(city: str) -> str:
    """
    Fetch current weather for a given city using OpenWeatherMap API.
    Always returns a simple string (not dict).
    """
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"}
        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code != 200 or "main" not in data:
            return "unavailable right now"

        desc = data["weather"][0]["description"].capitalize()
        temp = data["main"]["temp"]
        return f"{temp}°C, {desc}"

    except Exception as e:
        return "unavailable due to error"
