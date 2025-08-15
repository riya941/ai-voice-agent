import requests
import os
from dotenv import load_dotenv

load_dotenv()

MURF_API_KEY = os.getenv("MURF_API_KEY")

def text_to_speech(text: str) -> str:
    murf_url = "https://api.murf.ai/v1/speech/generate"
    headers = {
        "api-key": MURF_API_KEY,
        "Content-Type": "application/json"
    }
    body = {"text": text, "voiceId": "en-US-terrell"}

    response = requests.post(murf_url, headers=headers, json=body)
    response.raise_for_status()
    return response.json().get("audioFile")

def fallback_response(message: str):
    try:
        return {
            "transcript": "",
            "llm_response": message,
            "audio_url": text_to_speech(message)
        }
    except:
        return {"transcript": "", "llm_response": message, "audio_url": ""}
