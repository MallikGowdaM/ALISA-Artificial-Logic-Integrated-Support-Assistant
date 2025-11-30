import datetime
import time
import threading
import re
import json
import os
from speech import speak

REMINDER_FILE = "reminders.json"
reminders = []  # list of dicts {time: datetime, task: str}

# -------------------------
# Load & Save Persistence
# -------------------------
def load_reminders():
    global reminders
    if os.path.exists(REMINDER_FILE):
        with open(REMINDER_FILE, "r") as f:
            try:
                data = json.load(f)
                reminders = [
                    {"time": datetime.datetime.fromisoformat(r["time"]), "task": r["task"]}
                    for r in data
                ]
            except Exception:
                reminders = []

def save_reminders():
    with open(REMINDER_FILE, "w") as f:
        json.dump(
            [{"time": r["time"].isoformat(), "task": r["task"]} for r in reminders],
            f,
            indent=4
        )

# -------------------------
# Time Parser
# -------------------------
def parse_time(text):
    text = text.lower().strip()
    # Normalize AM/PM variants
    text = text.replace(".", "")       # remove dots in "a.m." / "p.m."
    text = text.replace("a m", "am").replace("p m", "pm")
    text = text.replace("am.", "am").replace("pm.", "pm")
    text = text.replace("A M", "am").replace("P M", "pm")
    text = text.replace("AM", "am").replace("PM", "pm")

    now = datetime.datetime.now()
    base_date = now
    explicit_date = False

    # --------------------------
    # Relative time: "in 10 minutes / 2 hours / 3 days"
    # --------------------------
    match = re.search(r"in (\d+) (minute|minutes|hour|hours|day|days)", text)
    if match:
        amount = int(match.group(1))
        unit = match.group(2)
        if "hour" in unit:
            return now + datetime.timedelta(hours=amount)
        elif "minute" in unit:
            return now + datetime.timedelta(minutes=amount)
        elif "day" in unit:
            return now + datetime.timedelta(days=amount)

    # --------------------------
    # Date-based: "tomorrow", "day after tomorrow"
    # --------------------------
    if "day after tomorrow" in text:
        base_date = now + datetime.timedelta(days=2)
    elif "tomorrow" in text:
        base_date = now + datetime.timedelta(days=1)

    # --------------------------
    # Specific date formats
    # --------------------------
    # "26 September" or "26th September"
    date_match = re.search(
        r"(\d{1,2})(st|nd|rd|th)?\s*(january|february|march|april|may|june|"
        r"july|august|september|october|november|december)", text
    )
    # "September 26"
    month_match = re.search(
        r"(january|february|march|april|may|june|july|august|september|"
        r"october|november|december)\s+(\d{1,2})(st|nd|rd|th)?", text
    )

    if date_match:
        day = int(date_match.group(1))
        month = date_match.group(3)
    elif month_match:
        month = month_match.group(1)
        day = int(month_match.group(2))
    else:
        month, day = None, None

    if month and day:
        try:
            month_num = time.strptime(month, "%B").tm_mon
            year = now.year
            if datetime.date(year, month_num, day) < now.date():
                year += 1
            base_date = datetime.datetime(year, month_num, day)
        except Exception:
            pass

    # --------------------------
    # Absolute time: "6 pm", "18:30", "6:30"
    # --------------------------
    match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        meridian = match.group(3)

        # Sanity checks
        if hour > 23:
            hour = 23
        if minute > 59:
            minute = 59

        if meridian == "pm" and hour != 12:
            hour += 12
        elif meridian == "am" and hour == 12:
            hour = 0
        elif meridian is None:
            # No AM/PM → guess
            guess_time = base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if guess_time < now and hour < 12:
                hour += 12  # assume PM if time already passed

        reminder_time = base_date.replace(hour=hour % 24, minute=minute, second=0, microsecond=0)
        if reminder_time < now:
            reminder_time += datetime.timedelta(days=1)
        return reminder_time

    return None


# -------------------------
# Core Reminder Functions
# -------------------------
def set_reminder(task, time_str, lang="en"):
    reminder_time = parse_time(time_str)
    if not reminder_time:
        if lang == "hi":
            speak("माफ़ कीजिए, मैं समय समझ नहीं पाया।", lang)
        elif lang == "kn":
            speak("ಕ್ಷಮಿಸಿ, ನಾನು ಸಮಯವನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ.", lang)
        else:
            speak("Sorry, I could not understand the reminder time.", lang)
        return

    reminders.append({"time": reminder_time, "task": task})
    save_reminders()

    msg_time = reminder_time.strftime('%I:%M %p')
    if lang == "hi":
        speak(f"{msg_time} पर {task} के लिए रिमाइंडर सेट कर दिया गया है।", lang)
    elif lang == "kn":
        speak(f"{msg_time} ಕ್ಕೆ {task} ರಿಮೈಂಡರ್ ಹೊಂದಿಸಲಾಗಿದೆ.", lang)
    else:
        speak(f"Reminder set for {task} at {msg_time}", lang)


def list_reminders(lang="en"):
    if not reminders:
        if lang == "hi":
            speak("आपके पास कोई रिमाइंडर नहीं है।", lang)
        elif lang == "kn":
            speak("ನಿಮಗೆ ಯಾವುದೇ ರಿಮೈಂಡರ್ ಇಲ್ಲ.", lang)
        else:
            speak("You have no reminders.", lang)
        return

    if lang == "hi":
        speak("ये रहे आपके रिमाइंडर:", lang)
    elif lang == "kn":
        speak("ಇವು ನಿಮ್ಮ ರಿಮೈಂಡರ್ಗಳು:", lang)
    else:
        speak("Here are your reminders:", lang)

    for r in reminders:
        time_str = r["time"].strftime("%I:%M %p")
        task = r["task"]
        if lang == "hi":
            speak(f"{time_str} पर {task}", lang)
        elif lang == "kn":
            speak(f"{time_str} ಕ್ಕೆ {task}", lang)
        else:
            speak(f"{task} at {time_str}", lang)


def delete_reminder(task, lang="en"):
    global reminders
    found = False
    for r in reminders[:]:
        if task.lower() in r["task"].lower():
            reminders.remove(r)
            found = True
    save_reminders()

    if found:
        if lang == "hi":
            speak(f"{task} का रिमाइंडर हटा दिया गया है।", lang)
        elif lang == "kn":
            speak(f"{task} ರಿಮೈಂಡರ್ ಅಳಿಸಲಾಗಿದೆ.", lang)
        else:
            speak(f"Reminder for {task} has been deleted.", lang)
    else:
        if lang == "hi":
            speak(f"{task} का कोई रिमाइंडर नहीं मिला।", lang)
        elif lang == "kn":
            speak(f"{task} ರಿಮೈಂಡರ್ ಕಂಡುಬಂದಿಲ್ಲ.", lang)
        else:
            speak(f"I couldn’t find any reminder for {task}.", lang)


def clear_all_reminders(lang="en"):
    global reminders
    reminders.clear()
    save_reminders()

    if lang == "hi":
        speak("सभी रिमाइंडर हटा दिए गए हैं।", lang)
    elif lang == "kn":
        speak("ಎಲ್ಲಾ ರಿಮೈಂಡರ್ಗಳು ಅಳಿಸಲಾಗಿದೆ.", lang)
    else:
        speak("All reminders have been cleared.", lang)

# -------------------------
# Direct + Interactive Handler
# -------------------------
def handle_reminder(cmd, takecommand, lang="en"):
    """
    Handle both direct and interactive reminders.
    Supports English, Hindi, and Kannada.
    """
    text = cmd.lower()
    task, time_str = None, None

    # Hindi direct style
    if "बजे" in text:
        parts = text.split("बजे", 1)
        time_str = parts[0].split()[-1] + " pm"
        task = parts[1].replace("कि", "").replace("का", "").strip()

    # Kannada direct style
    elif "ಗಂಟೆ" in text:
        parts = text.split("ಗಂಟೆ", 1)
        time_str = parts[0].split()[-1]
        task = parts[1].replace("ಎಂದು", "").strip()

    # English direct style
    elif any(x in text for x in [" at ", " for ", " in "]):
        if "that" in text:
            before, after = text.split("that", 1)
            if "at" in before:
                time_str = before.split("at", 1)[1].strip()
            elif "for" in before:
                time_str = before.split("for", 1)[1].strip()
            elif "in" in before:
                time_str = before.split("in", 1)[1].strip()
            task = after.strip()
        else:
            tokens = text.split()
            if "at" in tokens:
                idx = tokens.index("at")
                time_str = " ".join(tokens[idx+1:idx+3])
                task = " ".join(tokens[idx+3:])
            elif "in" in tokens:
                idx = tokens.index("in")
                time_str = " ".join(tokens[idx:idx+3])
                task = " ".join(tokens[idx+3:])

    if task and time_str:
        set_reminder(task, time_str, lang)
        return

    # Interactive mode
    if lang == "hi":
        speak("आपको किस चीज़ के लिए याद दिलाना है?", lang)
    elif lang == "kn":
        speak("ನಾನು ನಿಮಗೆ ಯಾವ ವಿಷಯವನ್ನು ನೆನಪಿಸಲು ಬೇಕು?", lang)
    else:
        speak("What should I remind you about?", lang)

    task = takecommand(lang)

    if lang == "hi":
        speak("कब याद दिलाना है?", lang)
    elif lang == "kn":
        speak("ಯಾವ ಸಮಯದಲ್ಲಿ ನೆನಪಿಸಲು ಬೇಕು?", lang)
    else:
        speak("When should I remind you?", lang)

    time_str = takecommand(lang)

    if task != "None" and time_str != "None":
        set_reminder(task, time_str, lang)

# -------------------------
# Background Checker
# -------------------------
def reminder_checker():
    while True:
        now = datetime.datetime.now()
        for r in reminders[:]:
            if now >= r["time"]:
                speak(f"Reminder: {r['task']}", lang="en")
                reminders.remove(r)
                save_reminders()
        time.sleep(30)

# -------------------------
# Initialize
# -------------------------
load_reminders()
threading.Thread(target=reminder_checker, daemon=True).start()
