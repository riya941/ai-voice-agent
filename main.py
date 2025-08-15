from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import File, UploadFile
from pydantic import BaseModel
from typing import Dict, List

from services.stt_service import transcribe_audio
from services.tts_service import text_to_speech, fallback_response
from services.llm_service import generate_response

app = FastAPI()
chat_sessions: Dict[str, List[dict]] = {}

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class ChatResponse(BaseModel):
    transcript: str
    llm_response: str
    audio_url: str


@app.get("/", response_class=HTMLResponse)
def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

   

@app.post("/agent/chat/{session_id}", response_model=ChatResponse)
async def chat_with_agent(session_id: str, file: UploadFile = File(...)):
    try:
        audio_bytes = await file.read()
        user_message = transcribe_audio(audio_bytes)

        if not user_message:
            raise HTTPException(status_code=400, detail="No speech detected.")

        if session_id not in chat_sessions:
            chat_sessions[session_id] = []

        chat_sessions[session_id].append({"role": "user", "content": user_message})

        conversation_text = (
            "You are a helpful conversational AI. If the user's question is about something "
            "already mentioned in this conversation, use that memory. "
            "If it is a general knowledge question, answer it based on your own knowledge.\n\n"
        )

        for msg in chat_sessions[session_id]:
            role_label = "User" if msg["role"] == "user" else "Assistant"
            conversation_text += f"{role_label}: {msg['content']}\n"

        assistant_reply = generate_response(conversation_text)
        chat_sessions[session_id].append({"role": "assistant", "content": assistant_reply})

        audio_url = text_to_speech(assistant_reply)

        return ChatResponse(
            transcript=user_message,
            llm_response=assistant_reply,
            audio_url=audio_url
        )

    except Exception as e:
        print(f"Error: {e}")
        return fallback_response("I'm having trouble connecting right now.")