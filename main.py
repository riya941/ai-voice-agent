from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import File, UploadFile
from pydantic import BaseModel
from typing import Dict, List
from routes.transcriber import AssemblyAIStreamingTranscriber
from utils.logging import setup_logger
import os
import asyncio
from routes import agent_chat
from fastapi import  WebSocket
from config import set_user_keys, USER_KEYS
from fastapi.responses import FileResponse, JSONResponse
from services.stt_service import transcribe_audio
from services.tts_service import text_to_speech
from fastapi.responses import FileResponse
from services.llm_service import stream_generate_response

setup_logger()

app = FastAPI()
chat_sessions: Dict[str, List[dict]] = {}

OUTPUT_DIR = os.path.join("Agent", "Output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(agent_chat.router)


@app.post("/set-keys")
async def set_keys(request: Request):
    """
    Receive API keys from frontend UI and update USER_KEYS in config.py.
    Payload example:
    {
        "google_api_key": "...",
        "tavily_api_key": "...",
        "assembly_api_key": "...",
        "murf_api_key": "...",
        "openweather_api_key": "..."
    }
    """
    try:
        data = await request.json()
        set_user_keys(data)

        missing = [k for k, v in data.items() if not v]
        if missing:
            return JSONResponse({
                "status": "error",
                "message": f"Missing required keys: {', '.join(missing)}"
            })

        return JSONResponse({"status": "success", "message": "API keys updated."})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)})
    
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    print("🎤 Client connected")

    if session_id not in chat_sessions:
        chat_sessions[session_id] = []

    file_path = os.path.join(OUTPUT_DIR, "recorded_audio.webm")
    if os.path.exists(file_path):
        os.remove(file_path)

    loop = asyncio.get_event_loop()
    transcriber = AssemblyAIStreamingTranscriber(websocket=websocket,  loop=loop, chat_sessions=chat_sessions,
    session_id=session_id,sample_rate=44100)
    

    try:
        with open(file_path, "ab") as f:
            while True:
                data = await websocket.receive_bytes()
                f.write(data)
                transcriber.stream_audio(data)

    except Exception as e:
        print(f"⚠️ WebSocket connection closed: {e}")

    finally:
        transcriber.close()
        print(f"✅ Audio saved at {file_path}")

@app.get("/")
def get_homepage():
    return FileResponse("templates/index.html", media_type="text/html")

@app.get("/style.css")
def get_style():
    return FileResponse("static/styles.css", media_type="text/css")

@app.get("/script.js")
def get_script():
    return FileResponse("static/script.js", media_type="application/javascript")

app.include_router(agent_chat.router)
