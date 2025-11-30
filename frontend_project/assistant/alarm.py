import datetime
import time
import threading
import re
from speech import speak, takecommand

alarms = []  # store all active alarms


# ----------------------------------------------------------
# Helper: Wait until target time, then announce
# ----------------------------------------------------------
def _alarm_thread(alarm_time, message):
    now = datetime.datetime.now()
    target = datetime.datetime.combine(now.date(), alarm_time)

    if target <= now:
        target += datetime.timedelta(days=1)

    diff = (target - now).total_seconds()
    time.sleep(diff)

    speak(f"⏰ Alarm time! {message if message else 'Wake up!'}")


# ----------------------------------------------------------
# Helper: Robust parser for spoken 12-hour / 24-hour time
# ----------------------------------------------------------
def _parse_alarm_time(time_input: str):
    """
    Convert spoken time like '12 30 pm' or '7 15 a.m.' or '12:30 pm'
    into a datetime.time object (handles 12-hour and 24-hour formats).
    """

    time_input = time_input.lower().strip()
    time_input = (
        time_input.replace("a.m.", "am")
        .replace("p.m.", "pm")
        .replace(".", " ")
        .replace(":", " ")
    )

    # Remove filler words like "set alarm for", "at"
    for filler in ["set", "alarm", "for", "at", "to"]:
        time_input = time_input.replace(filler, "")

    # Extract numbers
    numbers = re.findall(r"\d+", time_input)
    hour = minute = 0

    # Convert words like 'twelve thirty pm' into digits
    words_to_digits = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
        "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
        "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
        "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40,
        "fifty": 50,
    }
    tokens = time_input.split()

    # If speech gives words (like "twelve thirty pm"), handle it
    for word in tokens:
        if word in words_to_digits and str(words_to_digits[word]) not in numbers:
            numbers.append(str(words_to_digits[word]))

    is_pm = "pm" in time_input
    is_am = "am" in time_input

    # Determine hour/minute
    if len(numbers) == 0:
        raise ValueError("No valid digits found in time input.")
    elif len(numbers) == 1:
        hour = int(numbers[0])
        minute = 0
    else:
        hour, minute = int(numbers[0]), int(numbers[1])

    # Handle 12-hour conversion
    if is_pm and hour != 12:
        hour += 12
    elif is_am and hour == 12:
        hour = 0

    if hour > 23 or minute > 59:
        raise ValueError("Invalid time specified.")

    return datetime.time(hour, minute)


# ----------------------------------------------------------
# Main alarm functions
# ----------------------------------------------------------
def set_alarm():
    speak("Please tell me the alarm time. For example, say '7 30 a m' or '12 45 p m'.")
    time_input = takecommand()

    if not time_input or time_input == "None":
        speak("Sorry, I didn't catch that. Please say the alarm time again.")
        time_input = takecommand()

    try:
        alarm_time = _parse_alarm_time(time_input)
        formatted_time = alarm_time.strftime("%I:%M %p")
        speak(f"Alarm set for {formatted_time}. What should I remind you about?")
        message = takecommand()
        if not message or message == "None":
            message = "Wake up!"

        # Run alarm in background
        t = threading.Thread(target=_alarm_thread, args=(alarm_time, message), daemon=True)
        t.start()
        alarms.append((alarm_time, message))

        speak(f"Your alarm for {formatted_time} has been set successfully.")
    except Exception as e:
        print(f"Alarm parsing error: {e}")
        speak("Sorry, I could not understand the time. Please try again.")


def list_alarms():
    if not alarms:
        speak("No alarms are currently set.")
    else:
        for t, msg in alarms:
            speak(f"Alarm for {t.strftime('%I:%M %p')} to remind {msg}.")


def clear_alarms():
    global alarms
    alarms.clear()
    speak("All alarms have been cleared.")
