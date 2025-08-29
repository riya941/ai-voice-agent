# routes/transcriber.py
import os
from services.tts_service import text_to_speech 
from services.llm_service import stream_generate_response 
from config import get_api_key
import asyncio
import assemblyai as aai
from assemblyai.streaming.v3 import (
    StreamingClient, StreamingClientOptions,
    StreamingParameters, StreamingSessionParameters,
    StreamingEvents, BeginEvent, TurnEvent,
    TerminationEvent, StreamingError
)
from fastapi import WebSocket
# Set your AssemblyAI API key


#aai.settings.api_key = get_api_key("assembly_api_key")

class AssemblyAIStreamingTranscriber:
    def __init__(self, websocket: WebSocket, loop, chat_sessions: dict, session_id: str = "default",sample_rate=44100,):
        # Initialize streaming client
        assembly_key = get_api_key("assembly_api_key")
        if not assembly_key:
            raise ValueError("[KEY ERROR] AssemblyAI key is missing. Please enter it in the UI.")

        aai.settings.api_key = assembly_key  # set here, after validation

        self.websocket = websocket
        self.loop = loop  
        self.session_id = session_id
        self.chat_sessions = chat_sessions
        self.client = StreamingClient(
            StreamingClientOptions(
                api_key=aai.settings.api_key,
                api_host="streaming.assemblyai.com"
            )
        )

        
        self.client.on(StreamingEvents.Begin, self.on_begin)
        self.client.on(StreamingEvents.Turn, self.on_turn)
        self.client.on(StreamingEvents.Termination, self.on_termination)
        self.client.on(StreamingEvents.Error, self.on_error)

        # Connect to the streaming session
        self.client.connect(
            StreamingParameters(
                sample_rate=sample_rate,
                format_turns=False  # set True if you want automatic turn formatting
            )
        )

    def on_begin(self, client, event: BeginEvent):
        print(f"🎤 Session started: {event.id}")

    def on_turn(self, client, event: TurnEvent):
        print(f"{event.transcript} (end_of_turn={event.end_of_turn})")

        if event.end_of_turn:
            self.chat_sessions[self.session_id].append({"role": "user", "content": event.transcript})
            try:
                # Send transcript to client via WebSocket
                asyncio.run_coroutine_threadsafe(
                    self.websocket.send_json({
                        "type": "turn_detected",
                        "transcript": event.transcript
                    }),
                    self.loop
                )

                conversation_text = ""
                for msg in self.chat_sessions[self.session_id]:
                 #if msg["role"] == "user":
                  conversation_text += msg['content'] + "\n" 


                reply_accum = ""
                for chunk in stream_generate_response(
                      user_text=event.transcript,             # ← classify from CURRENT turn only
                      conversation_text=conversation_text     # ← still give full context to LLM
                  ):
                  if chunk:
                     reply_accum += chunk
                     print("🧠 LLM chunk:", chunk, flush=True)

                self.chat_sessions[self.session_id].append({"role": "assistant", "content": reply_accum})
                asyncio.run_coroutine_threadsafe(
                     self.websocket.send_json({
                      "type": "llm_transcript",
                      "transcript": reply_accum
                    }),
                    self.loop
                )

                print("🎤 Sending reply to Murf TTS...")
                for audio_chunk in text_to_speech(reply_accum, session_id=self.session_id):
                    print("🔹 Sending chunk to client...", audio_chunk[:50]) 
                    asyncio.run_coroutine_threadsafe(
                        self.websocket.send_json({
                            "type": "audio_chunk",
                            "data": audio_chunk  # base64 string
                        }),
                        self.loop
                    )

                asyncio.run_coroutine_threadsafe(
                    self.websocket.send_json({
                        "type": "audio_end"
                    }),
                    self.loop
                )

                asyncio.run_coroutine_threadsafe(
                   self.websocket.send_json({
                     "type": "llm_final",
                
                   }),
                   self.loop
                )
  
            except Exception as e:
                print("⚠️ Failed to send transcript:", e)

            if not event.turn_is_formatted:
                client.set_params(StreamingSessionParameters(format_turns=True))

    def on_termination(self, client, event: TerminationEvent):
        print(f"🛑 Session terminated after {event.audio_duration_seconds} s")

    def on_error(self, client, error: StreamingError):
        print("❌ Error:", error)

    def stream_audio(self, audio_chunk: bytes):
        self.client.stream(audio_chunk)

    def close(self):
        self.client.disconnect(terminate=True)
