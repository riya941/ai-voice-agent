# services/llm_service.py
from google import genai
from google.genai import types
from pydantic import BaseModel, ConfigDict
from agent_skills import execute_skill_function
import os
from dotenv import load_dotenv
import re
from tavily import TavilyClient
from config import get_api_key



#load_dotenv()
#TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
#tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

# Initialize Gemini client
#client = genai.Client()

# Use user-provided key if available, else fallback to .env
#tavily_client = TavilyClient(api_key=get_api_key("tavily_api_key"))
#client = genai.Client(api_key=get_api_key("google_api_key"))  # Your Google/Gemini key


# Persona definition
PERSONA = """You are Detective Vega, a mysterious investigator with sharp instincts. 
You always introduce yourself as Detective Vega.
You answer in short, clever, and intriguing sentences, 
as if uncovering hidden clues. Keep replies concise (3-4 sentences), 
but maintain the investigative, enigmatic tone."""

# ------------------------------
# Flexible Tool for Gemini
# ------------------------------
class FlexibleTool(types.Tool):
    model_config = ConfigDict(extra="allow")

# Callable for weather skill
def weather_callable(location: str):
    """Call the get_weather skill."""
    return execute_skill_function("get_weather", {"location": location})

# Instantiate weather tool
weather_tool = FlexibleTool(
    name="get_weather",
    description="Gets current weather for a given location.",
    parameters={"location": "string"},
    function=weather_callable
)

def extract_search_query(text: str) -> str:
    """
    Extract a web-search query from the current user message.
    """
    low = text.lower().strip()

    # explicit patterns
    m = re.search(r'\b(?:search|lookup|find|google)\s+(?:for\s+)?(.+)', low)
    if m:
        return m.group(1).strip()

    # common intents without the verbs
    # e.g. "latest news about ai", "tesla stock price", "news on openai"
    m2 = re.search(r'\b(?:latest|news|update|price|stock|trending|info|information)\b(.+)?', low)
    if m2:
        return text.strip()

    # safe default: use the message itself
    return text.strip()

# ------------------------------
# Helper: extract location from user input
# ------------------------------
def extract_location(text: str) -> str:
    """
    Extract location from user text. Defaults to London if not found.
    """
    text_lower = text.lower()
    
    # Match patterns like: "weather in London", "weather at Tokyo"
    m = re.search(r'weather\s+(?:in|at)\s+([a-zA-Z\s\-]+)', text_lower)
    if m:
        return m.group(1).strip().title()

    # Match patterns like: "temperature in London", "forecast for Paris"
    m2 = re.search(r'(?:temperature|forecast)\s+(?:in|for|at)\s+([a-zA-Z\s\-]+)', text_lower)
    if m2:
        return m2.group(1).strip().title()

    # Match "how was the weather today in London", "how is the weather in Paris"
    m3 = re.search(r'weather.*\b(?:in|at)\s+([a-zA-Z\s\-]+)', text_lower)
    if m3:
        return m3.group(1).strip().title()

    # Default fallback
    return "London"



# ------------------------------
# Main streaming response generator
# ------------------------------
def stream_generate_response(*, user_text: str, conversation_text: str):
    """
    Decide per-turn using ONLY the current user_text.
    Use full conversation_text only when talking to the LLM (persona).
    """
    user_low = user_text.lower().strip()

    # 1) Weather?
    weather_triggers = (r'\bweather\b', r'\btemperature\b', r'\bforecast\b')
    needs_weather = any(re.search(p, user_low) for p in weather_triggers)
    if needs_weather:
      location = extract_location(user_text)  # Now always returns a city
      try:
          skill_result = execute_skill_function("get_weather", {"location": location})
          if skill_result.get("success"):
            reply = (
                f"Detective Vega. The weather in {skill_result['location']} is "
                f"{skill_result['condition']} at {skill_result['temperature']}°C. "
                "A curious atmosphere indeed."
            )
            yield reply
          else:
            yield f"⚠️ Could not fetch weather: {skill_result.get('error','Unknown error')}"
      except Exception as e:
        yield f"⚠️ Weather skill error: {e}"
      return


    # 2) Web search?
    search_triggers = (r'\bsearch\b', r'\blookup\b', r'\bfind\b', r'\bgoogle\b',
                       r'\blatest\b', r'\bnews\b', r'\bupdate\b', r'\bprice\b', r'\bstock\b')
    needs_search = any(re.search(p, user_low) for p in search_triggers)
    if needs_search :
        try:
            tavily_key = get_api_key("tavily_api_key")
            tavily_client = TavilyClient(api_key=tavily_key)
            query = extract_search_query(user_text)
            results = tavily_client.search(query, max_results=5, include_answer=True)
            if results.get("answer"):
                yield f"Detective Vega. {results['answer']}"
                return
            if results.get("results"):
                top = results["results"][0]
                title = top.get("title", "Result")
                url = top.get("url", "")
                snippet = top.get("content", "")[:160]
                yield f"Detective Vega. Here's what I found: {title} - {url}. {snippet} … The trail of truth begins here."
                return
            yield "Detective Vega. No clean leads from the web this time."
        except Exception as e:
            yield f"⚠️ Web search error: {e}"
        return

    # 3) Otherwise: normal LLM with persona (use full conversation context)
    try:
        google_key = get_api_key("google_api_key")
        client = genai.Client(api_key=google_key)
        prompt = f"{PERSONA}\nThis is the ongoing conversation:\n{conversation_text}\n\nReply to the last user message above."
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        if resp.text:
            yield resp.text
        else:
            yield "Detective Vega. The silence is suspicious. Try asking again."
    except Exception as e:
        yield f"⚠️ LLM error: {e}"

