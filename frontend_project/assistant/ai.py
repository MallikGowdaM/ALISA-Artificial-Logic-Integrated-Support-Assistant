# ai.py
import ollama
import re

import requests
from deep_translator import GoogleTranslator
from langdetect import detect

# ==============================
# Config: Task → Model Mapping
# ==============================
MODEL_MAP = {
    "friendly": "phi3:mini",       # Fast and natural small talk
    "qa": "mistral",               # Strong reasoning and Q&A
    "summarize": "phi3:mini",      # Quick summaries
    "planning": "mistral",         # For reasoning and planning
    "email": "llama3:instruct",    # Great for writing friendly emails
    "default": "phi3:mini"         # Fallback: lightweight and fast
}


# ==============================
# Helpers
# ==============================
def clean_text_for_speech(text):
    if isinstance(text, tuple):
        text = text[0]  # just take the string
    return re.sub(r"[*_#`]", "", str(text))

def detect_language(text: str) -> str:
    """Detect language code ('en', 'hi', 'kn')."""
    try:
        lang = detect(text)
        if lang.startswith("hi"):
            return "hi"
        elif lang.startswith("kn"):
            return "kn"
        else:
            return "en"
    except Exception:
        return "en"

def translate_text(text: str, target_lang: str) -> str:
    """Translate text using deep-translator (Google)."""
    try:
        lang_map = {"hi": "hi", "kn": "kn"}
        if target_lang in lang_map:
            return GoogleTranslator(source="auto", target=lang_map[target_lang]).translate(text)
        return text
    except Exception:
        return text

# ==============================
# Task Classifier
# ==============================
def classify_task(user_text: str) -> str:
    """Decide which model/task to use based on user query."""
    tl = user_text.lower()

    # Summarization
    if any(k in tl for k in ["summarize", "summary", "explain briefly"]):
        return "summarize"

    # Planning (trips, timetables, schedules)
    if any(k in tl for k in ["plan", "schedule", "timetable", "trip", "itinerary", "travel"]):
        return "planning"

    # Email generation
    if any(k in tl for k in ["email", "mail", "letter", "write to"]):
        return "email"

    # Friendly small talk
    if any(k in tl for k in ["joke", "funny", "chat", "friend", "talk", "story"]):
        return "friendly"

    # Default → Q&A
    return "qa"

# ==============================
# Real-time Search via SerpApi
# ==============================
from serpapi import GoogleSearch

SERPAPI_KEY = "dad3b8ebf15903b18c0e7fec72b5b0820cdbf6fb4ed2d462d78721ffd49bb039"  # 🔒 Replace with your actual key

def get_serp_answer(query: str) -> str:
    """
    Use SerpApi (Google Search) to fetch real-time answers.
    Falls back to snippets, knowledge graph, or organic results.
    """
    try:
        params = {
            "engine": "google",
            "q": query,
            "api_key": SERPAPI_KEY,
            "location": "India",
            "hl": "en"
        }
        search = GoogleSearch(params)
        results = search.get_dict()

        # Try to extract from Knowledge Graph
        if "knowledge_graph" in results:
            kg = results["knowledge_graph"]
            if "title" in kg and "type" in kg:
                return f"{kg['title']} ({kg['type']})"
            elif "description" in kg:
                return kg["description"]

        # Try answer box (featured snippet)
        if "answer_box" in results:
            ab = results["answer_box"]
            if "answer" in ab:
                return ab["answer"]
            elif "snippet" in ab:
                return ab["snippet"]

        # Try organic results
        if "organic_results" in results and len(results["organic_results"]) > 0:
            top_result = results["organic_results"][0]
            snippet = top_result.get("snippet") or top_result.get("title")
            link = top_result.get("link")
            if snippet:
                return f"{snippet} (Source: {link})"

        return "Sorry, I couldn’t find a reliable live answer right now."

    except Exception as e:
        print(f"⚠️ SerpApi fetch failed: {e}")
        return "Unable to fetch live information at the moment."


# ==============================
# Ollama Models (Optimized)
# ==============================
def ask_ollama(prompt: str, model: str = "phi3:mini") -> str:
    """Send a query to a local Ollama model (fast streaming)."""
    try:
        instruction = (
            "You are a concise AI assistant. "
            "Answer the user's question briefly in 1–3 sentences. "
            "Avoid unnecessary details or long explanations. "
            f"User question: {prompt}"
        )

        stream = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": instruction}],
            stream=True
        )

        full_response = ""
        for chunk in stream:
            if "message" in chunk and "content" in chunk["message"]:
                piece = chunk["message"]["content"]
                print(piece, end="", flush=True)  # live stream to console
                full_response += piece

        print()  # newline at end
        return full_response.strip()

    except Exception as e:
        if "not found" in str(e).lower():
            print("\n⚠️ Model missing — using fallback: phi3:mini")
            return ask_ollama(prompt, model="phi3:mini")
        return f"Ollama error: {e}"


def ask_ai(user_text: str) -> tuple[str, str]:
    """Auto-route query to the correct Ollama model."""
    text_lower = user_text.lower()
    lang = detect_language(user_text)
    task = classify_task(user_text)

    question_triggers = ["who", "what", "when", "where", "which", "whose", "whom", "how", "current", "latest", "today"]

    if any(word in text_lower.split() or word in text_lower for word in question_triggers):
        print("🌐 Using SerpApi for real-time Q&A...")
        answer = get_serp_answer(user_text)
        return answer, lang

    # Smart routing for speed and reasoning
    if any(k in user_text.lower() for k in ["sing", "friend", "difference", "hey"]):
        model = "phi3:mini"   # smarter, slower
    elif len(user_text.split()) < 6:
        model = "phi3:mini"             # short commands → super fast
    else:
        model = MODEL_MAP.get(task, "phi3:mini")  # default fast model
    print(f"\n🧠 Using model: {model} (task: {task})")
    answer = ask_ollama(user_text, model=model)
    lang = detect_language(user_text)
    return answer, lang
