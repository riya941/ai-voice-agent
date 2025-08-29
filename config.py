# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Default keys from .env
DEFAULT_KEYS = {
    "google_api_key": os.getenv("GOOGLE_API_KEY"),
    "tavily_api_key": os.getenv("TAVILY_API_KEY"),
    "assembly_api_key": os.getenv("ASSEMBLYAI_API_KEY"),
    "murf_api_key": os.getenv("MURF_API_KEY"),
    "openweather_api_key": os.getenv("OPENWEATHER_API_KEY"), 
}

# User overrides (from frontend UI)
USER_KEYS = {
    "google_api_key": None,
    "tavily_api_key": None,
    "assembly_api_key": None,
    "murf_api_key": None,
    "openweather_api_key": None,
}

def set_user_keys(new_keys: dict):
    """Update user-provided keys from frontend."""
    for k, v in new_keys.items():
        if k in USER_KEYS and v:
            USER_KEYS[k] = v.strip()
            print(f"[KEY USED] {k}: frontend provided ✅", flush=True)
        elif k in USER_KEYS:
            print(f"[KEY MISSING] {k}: frontend key required ❌", flush=True)


def get_api_key(service: str):
    """Return API key with priority: user > env > None."""
    #return USER_KEYS.get(service) or DEFAULT_KEYS.get(service)
    user_key = USER_KEYS.get(service)

    if user_key:
        return user_key
    else:
        # 🚫 No fallback — force user to enter their own key
        raise ValueError(f"[KEY ERROR] {service}: No API key provided. Please enter in UI.")