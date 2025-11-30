import datetime
import os,re
import shlex
import time
import re

from keywords import EMERGENCY_CONTACTS
from speech import speak

def run_adb(command):
    return os.system(f"adb {command}")
def adb_read(command: str) -> str:
    try:
        return os.popen(f"adb {command}").read()
    except Exception:
        return ""

def get_screen_size():
    out = adb_read("shell wm size")
    # e.g., "Physical size: 1080x2340"
    m = re.search(r'Physical size:\s*(\d+)\s*x\s*(\d+)', out)
    if m:
        return int(m.group(1)), int(m.group(2))
    return 1080, 2340  # fallback

def tap_relative(rx: float, ry: float):
    w, h = get_screen_size()
    x = int(rx * w)
    y = int(ry * h)
    run_adb(f"shell input tap {x} {y}")

# These come from your captured event (raw / 4095)
REL_SEND_X = 3753 / 4095  # ≈ 0.91648
REL_SEND_Y = 3858 / 4095  # ≈ 0.94212

# 📞 Pick up call
def pick_call(lang="en"):
    try:
        run_adb("shell input keyevent KEYCODE_CALL")
        if lang == "en":
            speak("Call picked up.", lang)
        elif lang == "hi":
            speak("कॉल उठा लिया गया है।", lang)
        elif lang == "kn":
            speak("ಕಾಲ್ ಸ್ವೀಕರಿಸಲಾಗಿದೆ.", lang)
    except Exception as e:
        speak(f"Error picking call: {e}", lang)

# ❌ Reject call
def reject_call(lang="en"):
    try:
        run_adb("shell input keyevent KEYCODE_ENDCALL")
        if lang == "en":
            speak("Call rejected.", lang)
        elif lang == "hi":
            speak("कॉल काट दिया गया है।", lang)
        elif lang == "kn":
            speak("ಕಾಲ್ ತಿರಸ್ಕರಿಸಲಾಗಿದೆ.", lang)
    except Exception as e:
        speak(f"Error rejecting call: {e}", lang)

# 🚨 Emergency SMS
def send_emergency_sms(target, message, lang="en"):
    try:
        number = EMERGENCY_CONTACTS.get(target.lower(), target)
        number = number.replace(" ", "").replace("-", "").strip()
        safe_message = shlex.quote(message)

        # Open SMS compose with prefilled text
        run_adb(
            f'shell am start -a android.intent.action.SENDTO -d sms:{number} '
            f'--es sms_body {safe_message} --ez exit_on_sent true'
        )

        # wait for UI to render then tap SEND
        time.sleep(1.8)
        tap_relative(REL_SEND_X, REL_SEND_Y)

        if lang == "en":
            speak(f"Emergency message sent to {target}.", lang)
        elif lang == "hi":
            speak(f"आपातकालीन संदेश {target} पर भेजा गया है।", lang)
        elif lang == "kn":
            speak(f"ತುರ್ತು ಸಂದೇಶವನ್ನು {target} ಗೆ ಕಳುಹಿಸಲಾಗಿದೆ.", lang)

    except Exception as e:
        speak(f"Error sending emergency message: {e}", lang)

def make_emergency_call(target, lang="en"):
    try:
        # Get number from contacts dict or use directly
        number = EMERGENCY_CONTACTS.get(target.lower(), target)
        number = number.replace(" ", "").replace("-", "").strip()

        # Open dialer with number
        run_adb(f"shell am start -a android.intent.action.DIAL -d tel:{number}")
        time.sleep(1.5)  # wait for dialer to load

        # Tap CALL button (calculated coordinates)
        run_adb("shell input tap 542 1990")

        if lang == "en":
            speak(f"Calling {target} now.", lang)
        elif lang == "hi":
            speak(f"{target} को कॉल किया जा रहा है।", lang)
        elif lang == "kn":
            speak(f"{target} ಗೆ ಕರೆ ಮಾಡಲಾಗುತ್ತಿದೆ.", lang)

    except Exception as e:
        speak(f"Error making call: {e}", lang)

# 🛠️ Wrapper for emergency SMS (direct/interactive)
def handle_emergency_message(cmd, takecommand, lang="en"):
    target = None
    for name in EMERGENCY_CONTACTS.keys():
        if name in cmd.lower():
            target = name
            break

    if target:
        msg = cmd.replace("emergency message", "").replace(target, "").strip()
        if msg:
            send_emergency_sms(target, msg, lang)
        else:
            speak("What message should I send?", lang)
            msg = takecommand(lang)
            send_emergency_sms(target, msg, lang)
    else:
        speak("Whom should I send the message to?", lang)
        target = takecommand(lang)
        speak("What message should I send?", lang)
        msg = takecommand(lang)
        send_emergency_sms(target, msg, lang)

# 🛠️ Wrapper for emergency call (direct/interactive)
def handle_emergency_call(cmd, takecommand, lang="en"):
    target = None
    for name in EMERGENCY_CONTACTS.keys():
        if name in cmd.lower():
            target = name
            break

    if target:
        make_emergency_call(target, lang)
    else:
        speak("Whom should I call?", lang)
        target = takecommand(lang)
        make_emergency_call(target, lang)



def parse_time_12hr(time_str: str):
    """
    Convert natural language time like '4am', '5 30 pm', '12:45AM', '6:30 p.m.'
    into (hour, minute) in 24-hour format.
    """
    time_str = time_str.strip().lower().replace(":", " ")

    # Normalize am/pm (remove dots/spaces)
    time_str = time_str.replace("a.m.", "am").replace("p.m.", "pm")
    time_str = time_str.replace("a m", "am").replace("p m", "pm")

    # Regex to extract (hour, minute, am/pm)
    match = re.match(r"(\d{1,2})(?:\s+(\d{1,2}))?\s*(am|pm)?", time_str)
    if not match:
        return None, None

    hour = int(match.group(1))
    minute = int(match.group(2)) if match.group(2) else 0
    meridian = match.group(3)

    if meridian == "pm" and hour != 12:
        hour += 12
    elif meridian == "am" and hour == 12:
        hour = 0

    return hour, minute

# ⏰ Set alarm
def set_alarm(time_str, lang="en"):
    try:
        hour, minute = parse_time_12hr(time_str)
        if hour is None:
            speak("Sorry, I could not understand the time.", lang)
            return

        run_adb(
            f"shell am start -a android.intent.action.SET_ALARM "
            f"--ei android.intent.extra.alarm.HOUR {hour} "
            f"--ei android.intent.extra.alarm.MINUTES {minute} "
            f"--ez android.intent.extra.alarm.SKIP_UI true"
        )

        if lang == "en":
            speak(f"Alarm set for {time_str}.", lang)
        elif lang == "hi":
            speak(f"अलार्म {time_str} के लिए सेट कर दिया गया है।", lang)
        elif lang == "kn":
            speak(f"ಅಲಾರ್ಮ್ {time_str} ಕ್ಕೆ ಹೊಂದಿಸಲಾಗಿದೆ.", lang)

    except Exception as e:
        speak(f"Error setting alarm: {e}", lang)


