# Vega: AI Voice Agent



Vega is an AI-powered voice agent built with **FastAPI** and **Python**.  
It uses **Google Gemini API** for natural language responses, **Tavily API** for web search, and **OpenWeather API** for real-time weather updates.  
---

## 🚀 Features
- 🎙️ **Conversational Persona:** Detective Vega – a mysterious investigator with short, clever responses.  
- 🔎 **Web Search:** Real-time Tavily integration with links to top results.  
- ☁️ **Weather Info:** Current and forecast data from OpenWeather API.  
- 🔊 **Voice Interaction:** Record audio directly from the web UI.  
- 🔐 **Session-based API Keys:** Users can enter their own API keys for Gemini, Tavily, and OpenWeather.  
- ⚡ **Streaming Responses:** Real-time LLM answers streamed back to frontend. 

---

## 🛠️ Tech Stack

- **Backend:** FastAPI (Python)  
- **Frontend:** HTML, JavaScript  
- **LLM:** Google Gemini API  
- **Search:** Tavily API  
- **Weather:** OpenWeather API  
- **Deployment:** Render 

---

## 📂 Project Folder Structure

```
## 📂 Project Folder Structure

Aiagent/
├── main.py                # FastAPI entry point
├── config.py              # Configuration (API keys, settings)
├── requirements.txt       # Python dependencies
├── README.md              # Documentation
│
├── routes/                # API routes
│   ├── agent_chat.py      # Handles chat with LLM
│   └── transcriber.py     # Handles transcription
│
├── services/              # Core service modules
│   ├── llm_service.py     # Gemini LLM persona (Detective Vega)
│   ├── search_service.py  # Tavily web search integration
│   ├── weather_service.py # Weather API integration
│   └── tts_service.py     # Text-to-Speech streaming
│
├── static/                # Frontend files
│   ├── audio-processor.js # Audio processing for browser
│   ├── script.js          # Handles recording + WebSocket
│   └── style.css          # Optional styling
│
├── templates/             # (Optional) Jinja2 templates
│   └── index.html         # Web UI for user interaction
│
├── uploads/               # Stores uploaded files (if any)
│
├── utils/                 # Helper utilities
│
├── Agent/Output/          # Stores recorded audio locally
│   └── recorded_audio.webm
│
└── .env                   # Environment variables (ignored by Git)
     # (Optional) For persistent chat history storage
```
# 1️⃣ Clone the repository
git clone https://github.com/riya941/Aiagent.git
cd Aiagent

# 2️⃣ Create and activate virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# 3️⃣ Install dependencies
pip install -r requirements.txt

# 4️⃣ 🔑 API Keys Setup:

By default, this project **requires you to enter API keys per session** inside the code or when prompted.  
This is useful for testing, but not secure for production.  

### Option 1: Enter keys per session 
- Open `config.py` and paste your keys directly:
  -GEMINI_API_KEY = "your-gemini-key"
  -MURF_API_KEY = "your-murf-key"
  -WEATHER_API_KEY = "your-weather-key"
  -TAVILY_API_KEY = "your-tavily-key"

### Option 2: Use environment variables 
Create a .env file in the project root:

-GEMINI_API_KEY=your-gemini-key
-MURF_API_KEY=your-murf-key
-WEATHER_API_KEY=your-weather-key
-TAVILY_API_KEY=your-tavily-key


These will be automatically loaded by config.py if present.

# 5️⃣ Run the FastAPI server
uvicorn main:app --reload

# 6️⃣ Open the application in browser
http://127.0.0.1:8000

## 🎤 Usage Examples

### 🌐 Web Search
- "Latest Tesla stock price"
- "Search news about AI startups"

### ☁️ Weather
- "Weather in New York"
- "Forecast for Tokyo tomorrow"

### 🧠 General Knowledge
- "Who is the president of India?"
- "What is the national animal of India?"

---

## 🌍 Deployment (Render)

1. Push your project to GitHub.
2. Connect repo to Render.
4. Render automatically builds & deploys.

**ℹ️ Note:**
- If redeployment fails, old version keeps running ✅
- URL remains the same ✅
