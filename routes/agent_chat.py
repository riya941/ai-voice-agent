# routes/agent_chat.py
from fastapi import APIRouter, Form, UploadFile, File
from fastapi.responses import JSONResponse
import os

router = APIRouter()

OUTPUT_DIR = os.path.join("Agent", "Output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

@router.post("/agent/chat/{session_id}")
async def agent_chat(session_id: str, audio: UploadFile = File(...)):
    """
    Simple endpoint to handle uploaded audio and return dummy response
    """
    file_location = os.path.join(OUTPUT_DIR, f"{session_id}.webm")
    with open(file_location, "wb") as f:
        f.write(await audio.read())

    # Dummy response; you can integrate actual AI response logic here
    response = {
        "history": [
            {"role": "user", "content": "Audio uploaded"},
            {"role": "ai", "content": "Hello! This is your AI response."}
        ]
    }
    return JSONResponse(content=response)
