# services/tts_service.py
import json
import websocket
import threading
import queue
import os
from dotenv import load_dotenv
from config import get_api_key


#load_dotenv()
#MURF_API_KEY = os.getenv("MURF_API_KEY")

#MURF_API_KEY = get_api_key("murf_api_key")


def text_to_speech(text: str, session_id: str = "default"):
    """
    Connect to Murf WebSocket and yield base64 audio chunks in real-time.
    """

    MURF_API_KEY = get_api_key("murf_api_key")  # ✅ fetch at runtime
    if not MURF_API_KEY:
        raise ValueError("[KEY ERROR] Murf API key is missing. Please enter it in the UI.")
    ws_url = "wss://api.murf.ai/v1/speech/stream-input"


    headers = {
        "api-key": MURF_API_KEY,
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    chunk_queue = queue.Queue()

    def on_open(ws):
      print("🔗 Connected to Murf WebSocket")
      payload = {
        "voice_config": {
            "voiceId": "en-US-amara",
            "style": "Conversational",
            "rate": 0,
            "pitch": 0,
            "variation": 1,
        },
        "text": text,
        "context_id": session_id,
        "sample_rate": 44100,
        "channel_type": "mono",
        "format": "pcm16",
        "end": True
      }
      ws.send(json.dumps(payload))


    def on_message(ws, message):
        data = json.loads(message)
        print("DEBUG: Received Murf message:", data.keys())
        if "audio" in data:
            chunk_queue.put(data["audio"])  # put chunk into queue
        if data.get("final", False):
            chunk_queue.put(None)  # mark end
            ws.close()

    def on_error(ws, error):
        print("❌ Murf WS Error:", error)
        chunk_queue.put(None)

    def on_close(ws, code, msg):
        print("🔒 Murf WebSocket closed")
        chunk_queue.put(None)

    ws = websocket.WebSocketApp(
        ws_url,
        header=headers,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )

    # Run WS in separate thread to avoid blocking
    ws_thread = threading.Thread(target=ws.run_forever, daemon=True)
    ws_thread.start()

    # Yield chunks as they arrive
    while True:
        chunk = chunk_queue.get()
        if chunk is None:
            break
        yield chunk
