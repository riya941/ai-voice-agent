import assemblyai as aai
import os
from dotenv import load_dotenv
from config import get_api_key
#load_dotenv()

#aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")
#aai.settings.api_key = get_api_key("assembly_api_key")
#_transcriber = aai.Transcriber()

def transcribe_audio(audio_bytes: bytes) -> str:
    aai.settings.api_key = get_api_key("assembly_api_key")
    _transcriber = aai.Transcriber()
    transcript = _transcriber.transcribe(audio_bytes)
    return transcript.text.strip()