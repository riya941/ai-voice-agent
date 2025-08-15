import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_response(conversation: str) -> str:
    model = genai.GenerativeModel("gemini-1.5-flash")
    llm_response = model.generate_content(conversation)
    return llm_response.text.strip()
