# agent_skills.py
import os
import requests
from dotenv import load_dotenv
from config import get_api_key

#load_dotenv()
#OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# ------------------------------
# Skill function: get current weather
# ------------------------------
def get_weather(location: str) -> dict:
    """
    Fetches current weather for a given location using OpenWeatherMap API.
    Returns a dictionary with temperature, condition, and a preformatted 'answer'.
    """
    try:
        OPENWEATHER_API_KEY = get_api_key("openweather_api_key")

        if not OPENWEATHER_API_KEY:
            return {"success": False, "error": "No OpenWeather API key provided."}
        url = (
            f"http://api.openweathermap.org/data/2.5/weather"
            f"?q={location}&appid={OPENWEATHER_API_KEY}&units=metric"
        )
        response = requests.get(url)
        data = response.json()

        if data.get("cod") != 200:
            return {"success": False, "error": data.get("message", "City not found")}

        weather = {
            "success": True,
            "location": data["name"],
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "condition": data["weather"][0]["description"],
            "answer": (
                f"The weather in {data['name']} is {data['weather'][0]['description']} "
                f"at {data['main']['temp']}°C (feels like {data['main']['feels_like']}°C). "
                f"Humidity is {data['main']['humidity']}% with wind speed {data['wind']['speed']} m/s."
            )
        }
        return weather
    except Exception as e:
        return {"success": False, "error": str(e)}

# ------------------------------
# Map skill function names to Python functions
# ------------------------------
SKILL_FUNCTIONS = {
    "get_weather": get_weather
}

# ------------------------------
# Execute a skill function by name
# ------------------------------
def execute_skill_function(function_name: str, function_args: dict) -> dict:
    """
    Executes a skill function given its name and arguments.
    Returns a dictionary with success/error info.
    """
    if function_name not in SKILL_FUNCTIONS:
        return {"success": False, "error": f"Unknown skill function: {function_name}"}
    try:
        result = SKILL_FUNCTIONS[function_name](**function_args)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}
