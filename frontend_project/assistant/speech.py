import os
import playsound
import threading
import pyttsx3
import speech_recognition as sr
from gtts import gTTS
import datetime
import tempfile
import traceback
import sys
sys.stdout.reconfigure(encoding="utf-8")

# ==============================
# Init TTS Engine
# ==============================
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # default: first voice
speak_lock = threading.Lock()
assistant_speaking = False
listening_enabled = True
listening_active = True  # flag for continuous listening loop

# ==============================
# Voice Config
# ==============================
def set_voice(index=0):
    """Change the TTS voice by index (check available voices with list_voices)."""
    global voices
    voices = engine.getProperty('voices')
    if 0 <= index < len(voices):
        engine.setProperty('voice', voices[index].id)
    else:
        print(f"[Warning] Voice index {index} not available.")

def list_voices():
    """List all available voices."""
    for i, v in enumerate(voices):
        print(f"{i}: {v.name} ({v.languages})")


# ==============================
# Speak
# ==============================
def speak(audio, lang="en"):
    """Speak text in the given language (en, hi, kn) and log it"""
    global assistant_speaking, listening_enabled
    try:
        listening_enabled = False
        if lang in ["hi", "kn"]:   # Hindi/Kannada → gTTS
            tts = gTTS(text=audio, lang=lang)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                filename = f.name
            tts.save(filename)
            playsound.playsound(filename)
            os.remove(filename)
        else:   # English → pyttsx3
            with speak_lock:
                assistant_speaking = True
                print("Assistant:", audio)
                engine.say(audio)
                engine.runAndWait()
                assistant_speaking = False
    except Exception as e:
        print(f"TTS error: {e}")
        traceback.print_exc()
    finally:
        listening_enabled = True


# ==============================
# Stop Speaking
# ==============================
def stop_speaking():
    global assistant_speaking
    with speak_lock:
        if assistant_speaking:
            engine.stop()
            assistant_speaking = False
            print("[Speech stopped due to user interruption]")


# ==============================
# Take Command
# ==============================
LANG_MAP = {
    "en": "en-IN",
    "hi": "hi-IN",
    "kn": "kn-IN"
}

def takecommand(lang="en", ignore_flag=False, timeout=5, phrase_time_limit=None):
    """Listen from mic and return recognized text"""
    global listening_enabled
    if not listening_enabled and not ignore_flag:
        return "None"

    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening....")

        try:
            recog_lang = LANG_MAP.get(lang, "en-IN")
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            print("Processing...")

            text = r.recognize_google(audio, language=recog_lang)
            print(f"User said: {text}".encode("utf-8", "ignore").decode())  # ✅ safe print
            return text.lower()

        except sr.WaitTimeoutError:
            msg = "[Timeout: No input]"
            print(msg)
            return "None"

        except sr.UnknownValueError:
            msg = "[Unrecognized speech]"
            print(msg)
            return "None"

        except sr.RequestError:
            msg = "[Speech recognition network error]"
            print(msg)
            return "None"


# ==============================
# Wish
# ==============================
def wish(lang="en"):
    hour = int(datetime.datetime.now().hour)
    if lang == "en":
        if 0 <= hour < 12:
            speak("Good morning sir!", "en")
        elif 12 <= hour < 18:
            speak("Good afternoon sir!", "en")
        else:
            speak("Good evening sir!", "en")
        speak("How can I help you today?", "en")


# ==============================
# Exit Message
# ==============================
def exit_message(lang="en"):
    if lang == "en":
        speak("Thank you Sir, if you need any help just say a wake word. I will be there to help you.", "en")


# ==============================
# Continuous Listening
# ==============================
def continuous_listening(callback):
    """Always listen in background and pass recognized commands to callback"""
    def _listen_loop():
        global listening_active
        while listening_active:
            query = takecommand()
            if query != "None":
                stop_speaking()
                callback(query)

    t = threading.Thread(target=_listen_loop, daemon=True)
    t.start()
    return t

def stop_continuous_listening():
    """Stop the continuous listening loop."""
    global listening_active
    listening_active = False
    print("[Continuous listening stopped]")
