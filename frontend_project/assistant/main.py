import datetime
import socketio
from ai import ask_ai, clean_text_for_speech
from file import open_file_interactive, create_folder, create_file
from feelings import friendly_response
from shopping import handle_shopping_query
from introduction import introduce, daily_quote
from planning import plan_trip_interactive, study_timetable_interactive
from reminder import list_reminders, delete_reminder, clear_all_reminders, handle_reminder
from social import send_whatsapp_message, send_email, play_song_on_spotify
from speech import wish, speak as base_speak, takecommand as base_takecommand
from apps import open_app, close_app
from system import shutdown_pc, restart_pc, sleep, lock, system_status, open_camera, switch_window, minimize_window, \
    switch_tab, get_ip_address, control_volume, system_control
from keywords import KEYWORDS
from web import get_weather, get_news_headlines, handle_web_command
from phone_control import pick_call, reject_call, handle_emergency_message, handle_emergency_call
from alarm import set_alarm,list_alarms,clear_alarms
import queue
task_queue = queue.Queue()
WAKE_WORDS = ["jarvis", "assistant", "hey jarvis"]
sio = socketio.Client()
sio.connect("http://localhost:4000")

def emit_status(status, **kwargs):
    """Send assistant status or command info to frontend"""
    try:
        payload = {"status": status}
        payload.update(kwargs)
        sio.emit("assistant_status", payload)
    except Exception as e:
        print(f"Socket emit failed: {e}", flush=True)


# ✅ NEW speak wrapper
def speak(text, lang="en"):
    """Wrapper around base_speak that also updates frontend"""
    try:
        emit_status("assistant_reply", reply_text=text)
        emit_status("assistant_command", command_text=text)
        base_speak(text, lang=lang)
    finally:
        emit_status("idle")

def takecommand(lang="en"):
    """Wrapper around base_takecommand with frontend emit"""
    emit_status("listening")
    text = base_takecommand(lang)
    emit_status("idle")

    if text and text != "None":
        emit_status("user_command", command_text=text)
    return text

# -----------------------------
# Language selection
# -----------------------------
def ask_language():
    speak("Which language should I assist you in?", lang="en")
    while True:
        lang_choice = takecommand("en")
        if "english" in lang_choice:
            speak("Okay, I will assist you in English.", lang="en")
            emit_status("idle")
            return "en"
        elif "hindi" in lang_choice or "हिंदी" in lang_choice:
            speak("ठीक है, अब मैं हिंदी में बात करूंगा।", lang="hi")
            emit_status("idle")
            return "hi"
        elif "kannada" in lang_choice or "ಕನ್ನಡ" in lang_choice:
            speak("ಸರಿ, ನಾನು ಈಗ ಕನ್ನಡದಲ್ಲಿ ಮಾತನಾಡುತ್ತೇನೆ.", lang="kn")
            emit_status("idle")
            return "kn"
        else:
            speak("Sorry, please say English, Hindi or Kannada.", lang="en")
            emit_status("idle")

# -----------------------------
# Processing
# -----------------------------

def process_command(cmd,active_lang):
    global task_queue
    if not active_lang:
        active_lang = "en"
    print(f"Handling ({active_lang}): {cmd}")
    emit_status("assistant_command", command_text=cmd)
    # -----------------------------
    # CHANGE LANGUAGE
    # -----------------------------
    if any(kw in cmd for kw in KEYWORDS["change_lang"][active_lang]):
        active_lang = ask_language() or "en"
        return active_lang

    # -----------------------------
    # Introduction
    # -----------------------------
    elif "your name" in cmd or "introduce yourself" in cmd or "about yourself" in cmd:
        introduce(active_lang)
        emit_status("idle")

    # ---------------------------
    # NEWS HEADLINES
    # ---------------------------
    elif "news" in cmd or "headlines" in cmd:
        emit_status("assistant_command", command_text="⚡ Fetching latest news headlines")
        get_news_headlines(active_lang)

    # -----------------------------
    # WINDOW & TAB CONTROLS
    # -----------------------------
    elif "switch window" in cmd:
        emit_status("assistant_command", command_text="⚡ Switching window")
        switch_window(active_lang)
    elif "minimize window" in cmd or "minimise window" in cmd:#max
        emit_status("assistant_command", command_text="⚡ Minimizing window")
        minimize_window(active_lang)
    elif "next tab" in cmd or "switch tab" in cmd:
        emit_status("assistant_command", command_text="⚡ Switching browser tab")
        switch_tab(True, active_lang)
    elif "previous tab" in cmd:
        emit_status("assistant_command", command_text="⚡ Switching browser tab")
        switch_tab(True, active_lang)
    elif "ip address" in cmd or "my ip" in cmd:
        emit_status("assistant_command", command_text="⚡ Searching IP Addrerss")
        get_ip_address(active_lang)

    # -----------------------------
    # WEATHER
    # -----------------------------
    elif "weather" in cmd or "मौसम" in cmd or "ಹವಾಮಾನ" in cmd:
        city = None
        if active_lang == "hi":
            city = cmd.replace("मौसम", "").replace("का", "").replace("बताओ", "").strip()
        elif active_lang == "kn":
            city = cmd.replace("ಹವಾಮಾನ", "").replace("ವರದಿ", "").replace("ಏನು", "").strip()
        else:
            words = cmd.split()
            for i, w in enumerate(words):
                if w in ["in", "at"] and i + 1 < len(words):
                    city = " ".join(words[i + 1:])
                    break
        if not city:
            speak("Which city?", lang=active_lang)
            emit_status("idle")
            city = takecommand(active_lang)
        emit_status("assistant_command", command_text=f"⚡ Fetching weather for {city}")
        get_weather(city, active_lang)


    # -----------------------------
    # STOP
    # -----------------------------
    elif any(kw in cmd for kw in KEYWORDS["stop"][active_lang]):
        emit_status("assistant_command", command_text="⚡ Stopping assistant")
        speak("Goodbye. Just say the wake word when you need me.", lang=active_lang)
        emit_status("idle")
        print("EXIT_DETECTED", flush=True)
        exit(0)

    # -----------------------------
    # FILE HANDLING
    # -----------------------------
    elif cmd.startswith("open file") or "open a file" in cmd:
        emit_status("assistant_command", command_text=f"⚡ Opening file {cmd}")
        open_file_interactive(cmd, active_lang)
    elif cmd.startswith("create file"):
        emit_status("assistant_command", command_text=f"⚡ Creating file {cmd}")
        create_file(cmd)
    elif cmd.startswith("create folder"):
        emit_status("assistant_command", command_text=f"⚡ Creating folder {cmd}")
        create_folder(cmd)

    # -----------------------------
    # CAMERA
    # -----------------------------
    elif "open camera" in cmd or "start camera" in cmd:
        emit_status("assistant_command", command_text="⚡ Opening camera")
        open_camera(active_lang)

    elif "close camera" in cmd or "stop camera" in cmd:
        speak("Closing camera window.", active_lang)
        emit_status("idle")

    # -----------------------------
    # POWER COMMANDS
    # -----------------------------
    elif any(kw in cmd for kw in KEYWORDS["shutdown"][active_lang]):
        emit_status("assistant_command", command_text="⚡ Shutting down PC")
        shutdown_pc(active_lang)
    elif any(kw in cmd for kw in KEYWORDS["restart"][active_lang]):
        emit_status("assistant_command", command_text="⚡ Restarting PC")
        restart_pc(active_lang)
    elif any(kw in cmd for kw in KEYWORDS["sleep"][active_lang]):
        emit_status("assistant_command", command_text="⚡ Putting PC to sleep")
        sleep(active_lang)
    elif any(kw in cmd for kw in KEYWORDS["lock"][active_lang]):
        emit_status("assistant_command", command_text="⚡ Locking PC")
        lock(active_lang)

    elif any(kw in cmd for kw in KEYWORDS["status"][active_lang]):
        emit_status("assistant_command", command_text="⚡ Checking system status")
        system_status(active_lang)


    # -----------------------------
    # PLANNING
    # -----------------------------
    elif "study" in cmd:
        emit_status("assistant_command", command_text="⚡ Preparing study timetable")
        study_timetable_interactive(active_lang, speak, takecommand)

    elif "plan my trip" in cmd:
        emit_status("assistant_command", command_text="⚡ Planning your trip")
        plan_trip_interactive(active_lang, speak, takecommand)

    # -----------------------------
    # TIME
    # -----------------------------
    elif any(kw in cmd for kw in KEYWORDS["time"][active_lang]):
        strTime = datetime.datetime.now().strftime("%H:%M:%S")
        emit_status("assistant_command", command_text="⚡ Telling current time")
        speak(f"The time is {strTime}", lang=active_lang)
        emit_status("idle")

    # -----------------------------
    # AI ANSWERS
    # -----------------------------
    elif any(cmd.startswith(q) for q in KEYWORDS["question"]["en"] +
                                        KEYWORDS["question"]["hi"] +
                                        KEYWORDS["question"]["kn"]):
        emit_status("assistant_command", command_text="⚡ Asking AI for answer")
        answer, detected_lang = ask_ai(cmd)
        speak(answer, lang=detected_lang)
        emit_status("idle")

    # -----------------------------
    # COMMUNICATION
    # -----------------------------
    elif "send whatsapp" in cmd:
        emit_status("assistant_command", command_text="⚡ Sending WhatsApp message")
        send_whatsapp_message(cmd, active_lang)

    elif "send email" in cmd or "ईमेल भेजो" in cmd or "ಇಮೇಲ್ ಕಳುಹಿಸಿ" in cmd:
        emit_status("assistant_command", command_text="⚡ Sending email")
        send_email(active_lang)

    # -----------------------------
    # SPOTIFY
    # -----------------------------
    elif any(kw in cmd for kw in KEYWORDS["spotify_play"][active_lang]):
        query = cmd
        for kw in KEYWORDS["spotify_play"][active_lang]:
            query = query.replace(kw, "").strip()
        if not query or query.lower() in ["song", "music", "spotify"]:
            speak("Which song should I play?", lang=active_lang)
            song_name = takecommand(active_lang)
            if song_name != "None":
                emit_status("assistant_command", command_text=f"⚡ Playing {query} on Spotify")
                play_song_on_spotify(query, active_lang)

        else:
            play_song_on_spotify(query, active_lang)

    elif any(kw in cmd for kw in KEYWORDS["spotify_close"][active_lang]):
        from social import close_spotify
        emit_status("assistant_command", command_text="⚡ Closing Spotify")
        close_spotify(active_lang)

    # -----------------------------
    # SHOPPING / FOOD / MOVIES
    # -----------------------------
    elif any(word in cmd for word in [
        "buy", "shop", "order", "cloth", "food", "pizza", "dominos",
        "ticket", "movie", "suggest", "recommend", "dress"
    ]):
        emit_status("assistant_command", command_text="⚡ Handling shopping/food/movie query")
        reply = handle_shopping_query(cmd, takecommand, speak, active_lang)
        if reply:
            speak(reply, lang=active_lang)

    # -----------------------------
    # CALLS
    # -----------------------------
    elif "pick call" in cmd or "answer call" in cmd:
        emit_status("assistant_command", command_text="⚡ Picking up call")
        pick_call(active_lang)

    elif "reject call" in cmd or "cut call" in cmd:
        emit_status("assistant_command", command_text="⚡ Rejecting call")
        reject_call(active_lang)

    elif "emergency message" in cmd:
        emit_status("assistant_command", command_text="⚡ Handling emergency message")
        handle_emergency_message(cmd, takecommand, active_lang)

    elif "emergency call" in cmd:
        emit_status("assistant_command", command_text="⚡ Handling emergency call")
        handle_emergency_call(cmd, takecommand, active_lang)

    # -----------------------------
    # REMINDERS
    # -----------------------------
    elif "set a reminder" in cmd or "remind me" in cmd:
        emit_status("assistant_command", command_text="⚡ Setting a reminder")
        handle_reminder(cmd, takecommand, active_lang)

    elif "my reminders" in cmd:
        emit_status("assistant_command", command_text="⚡ Listing all reminders")
        list_reminders(active_lang)

    elif "delete reminder" in cmd:
        speak("Which reminder should I delete?", active_lang)
        emit_status("idle")
        task = takecommand(active_lang)
        if task != "None":
            emit_status("assistant_command", command_text="⚡ Deleting a reminder")
            delete_reminder(task, active_lang)

    elif "clear reminders" in cmd:
        emit_status("assistant_command", command_text="⚡ Clearing all reminders")
        clear_all_reminders(active_lang)
#------------------------------------------------------
# Resume Builder
#------------------------------------------------------
    elif "resume" in cmd or "build my resume" in cmd or "prepare resume" in cmd:
        emit_status("assistant_command", command_text="🧾 Building resume...")
        from resume_builder import build_resume
        build_resume(active_lang)

#---------------------------------------------------------------------
# Setting Alarm
#----------------------------------------------------------------------
    elif "set alarm" in cmd:
        set_alarm()
    elif "list alarm" in cmd:
        list_alarms()
    elif "clear alarms" in cmd or "delete all alarms" in cmd:
        clear_alarms()


    # -----------------------------
    # VOLUME CONTROL (catch first)
    # -----------------------------
    elif any(word in cmd for word in
             ["volume", "mute", "unmute", "sound", "increase volume", "decrease volume", "louder", "quieter", "raise",
              "lower"]):
        emit_status("assistant_command", command_text=f"🔊 Adjusting volume: {cmd}")
        control_volume(cmd, active_lang)
    # -----------------------------
    # SYSTEM CONTROLS
    # -----------------------------
    elif any(word in cmd for word in
             ["wifi", "bluetooth", "brightness", "keyboard light", "battery saver", "power saver"]):
        emit_status("assistant_command", command_text=f"⚙️ System control: {cmd}")
        system_control(cmd, active_lang)

    # -----------------------------
    # NORMAL OPEN / CLOSE (system & web)
    # -----------------------------
    elif "open" in cmd or "close" in cmd:
        emit_status("assistant_command", command_text=f"⚡ Handling command: {cmd}")

        known_sites = ["google", "youtube", "facebook", "instagram", "twitter", "wikipedia", "chatgpt", "github"]

        # ------------- CLOSE commands -------------
        if "close" in cmd:
            app = cmd.replace("close", "").strip().lower()

            # If command mentions a known website
            if any(site in app for site in known_sites):
                handle_web_command(cmd, active_lang)
            else:
                # Try to match system apps
                if not app:
                    speak("Which app should I close?", active_lang)
                    app = takecommand(active_lang).lower()
                if app and app != "none":
                    close_app(app, active_lang)
                else:
                    speak("Okay, not closing anything.", active_lang)

        # ------------- OPEN commands -------------
        elif "open" in cmd:
            app = cmd.replace("open", "").strip().lower()

            # If command mentions a known website
            if any(site in app for site in known_sites):
                handle_web_command(cmd, active_lang)
            else:
                # Try to match system apps
                if not app:
                    speak("Which app should I open?", active_lang)
                    app = takecommand(active_lang).lower()
                if app and app != "none":
                    open_app(app, active_lang)
                else:
                    speak("Okay, not opening anything.", active_lang)

    # -----------------------------
    # FALLBACK (Friendly AI + Feelings)
    # -----------------------------
    else:
        # First let feelings.py handle moods
        handled_before = False
        try:
            handled_before = friendly_response(cmd, active_lang)
        except Exception as e:
            print(f"Feelings fallback error: {e}")

        if not handled_before:
            # Use AI model for general queries (dog names, food, etc.)
            ai_reply, detected_lang = ask_ai(
                f"The user asked: '{cmd}'. Reply like a creative and friendly companion."
            )
            speak(clean_text_for_speech(ai_reply), detected_lang)

# -----------------------------
# Main
# -----------------------------
def main():
    speak("Hello! I am your assistant. Say the wake word to start.", lang="en")
    #emit_status("idle")
    active_lang = "en"

    while True:
        emit_status("listening")  # ✅ start listening
        query = takecommand("en")  # Wake words always in English
        emit_status("idle")
        if any(w in query for w in WAKE_WORDS):
            emit_status("reset")
            print("WAKEWORD_DETECTED", flush=True)  # ✅ Node catches this
            active_lang = ask_language()
            wish(active_lang)
            daily_quote(active_lang)
            #emit_status("idle")

            while True:
                cmd = takecommand(active_lang)
                emit_status("idle")
                if cmd == "None":
                    continue

                active_lang = process_command(cmd, active_lang)

if __name__ == "__main__":
        main()