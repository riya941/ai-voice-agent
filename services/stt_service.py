import assemblyai as aai
import os
from dotenv import load_dotenv

load_dotenv()

aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")
_transcriber = aai.Transcriber()

def transcribe_audio(audio_bytes: bytes) -> str:
    transcript = _transcriber.transcribe(audio_bytes)
    return transcript.text.strip()
