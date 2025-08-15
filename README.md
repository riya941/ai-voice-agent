# 🎙️ AI Voice Agent

An intelligent voice-powered conversational AI built with **FastAPI**, **Google Gemini API**, **AssemblyAI**, and **Murf TTS**.  
It remembers previous conversations while also answering general knowledge questions.

---

## 🚀 Features
- 🎤 **Voice input** using browser recording
- 🧠 **Conversation memory** with session-based history
- 🌍 **General knowledge** via Gemini API
- 🗣 **Text-to-Speech responses** using Murf.ai
- 🎨 **Beautiful UI** with animations & chat display

---

## 🛠️ Tech Stack
- **Backend:** FastAPI, Python
- **Frontend:** HTML, CSS, JavaScript
- **APIs:** Google Gemini, AssemblyAI (STT), Murf.ai (TTS)
- **Others:** UUID for session IDs

---

## 📂 Project Folder Structure

```
Aiagent/
│
├── main.py               # FastAPI backend server
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (API keys)
├── README.md             # Project documentation
│
├── templates/
│   └── index.html        # Frontend HTML
│
├── static/
│   ├── styles.css        # CSS styling
│   ├── script.js         # Frontend JavaScript
│
└── chat_sessions/        # (Optional) For persistent chat history storage
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

# 4️⃣ Create a .env file in the project root and add:
# AssemblyAI, Gemini & Murf API keys
ASSEMBLYAI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
MURF_API_KEY=your_key_here

# 5️⃣ Run the FastAPI server
uvicorn main:app --reload

# 6️⃣ Open the application in browser
http://127.0.0.1:8000

