# feelings.py
import random
import time
from speech import speak, takecommand
from ai import  clean_text_for_speech,ask_ai
from social import send_whatsapp_message
from keywords import CONTACTS, EMERGENCY_CONTACTS

# --- Mood memory ---
LAST_MOOD = None
LAST_REASON = None
LAST_MOOD_TIME = 0
COMFORT_ACTIVE = False
FAILED_COMFORT_COUNT = 0
MAX_FAILED_COMFORT = 3  # after 3 failed tries, inform Kiran

# Fixed friends
SAD_FRIEND = "Kiran"
HAPPY_FRIEND = "Varun"

JOKES = [
    "Why don’t skeletons ever fight each other? Because they don’t have the guts!",
    "Why did the math book look sad? Because it had too many problems!",
    "Parallel lines have so much in common… it’s a shame they’ll never meet!"
]

QUOTES = [
    "Tough times never last, but tough people do. 💪",
    "Every day may not be good, but there’s something good in every day. 🌟",
    "Small steps each day lead to big changes. 🌱"
]

CHECKIN_DELAY = 120  # seconds (2 minutes)


# -------------------------
# Build shareable message
# -------------------------
def build_share_message(reason: str, mood: str, tone="empathetic") -> str:
    """Return a direct message using user’s exact words"""
    if tone == "celebratory":
        return f"I'm feeling really happy today because {reason}."
    else:
        return f"I'm not feeling well. I'm feeling {mood} because {reason}."


# -------------------------
# Auto share with fixed contacts
# -------------------------
def auto_share_with(contact_name: str, mood: str, reason: str, tone="empathetic", lang="en"):
    message = build_share_message(reason, mood, tone=tone)
    cmd = f"send whatsapp to {contact_name} saying {message}"
    send_whatsapp_message(cmd, lang)


# -------------------------
# Comfort followup multi-turn
# -------------------------
def comfort_followup(user_text: str, lang="en"):
    global COMFORT_ACTIVE, LAST_MOOD, LAST_REASON, FAILED_COMFORT_COUNT

    tl = user_text.lower().strip()

    # Positive resolution
    if any(k in tl for k in ["yes", "better", "fine now", "okay now"]):
        speak("I’m really glad you’re feeling better 💙.", lang)
        COMFORT_ACTIVE = False
        FAILED_COMFORT_COUNT = 0
        return True

    # Negative response
    if any(k in tl for k in ["no", "not really", "still", "worse", "not yet"]):
        FAILED_COMFORT_COUNT += 1

        if FAILED_COMFORT_COUNT >= MAX_FAILED_COMFORT and LAST_REASON:
            # 🚨 Auto share with Kiran
            speak(f"I noticed you’re still not feeling better. I’m informing {SAD_FRIEND} so they can check in on you 💙.", lang)
            auto_share_with(SAD_FRIEND, LAST_MOOD or "unwell", LAST_REASON, tone="empathetic", lang=lang)
            COMFORT_ACTIVE = False
            FAILED_COMFORT_COUNT = 0
            return True

        # Still sad but not max tries yet → comfort again
        ai_reply = ask_ai(f"The user said '{user_text}' while still feeling {LAST_MOOD}. Reply with gentle encouragement.")
        speak(ai_reply, lang)
        choice = random.choice(["joke", "quote", "listen"])
        if choice == "joke":
            speak(f"Maybe this will help: {random.choice(JOKES)}", lang)
        elif choice == "quote":
            speak(f"Here’s a thought: {random.choice(QUOTES)}", lang)
        else:
            speak("I’m here with you. Do you want to tell me more about it?", lang)
        return True

    return False


# -------------------------
# Main friendly response
# -------------------------
def friendly_response(user_text: str, lang="en"):
    global LAST_MOOD, LAST_REASON, LAST_MOOD_TIME, COMFORT_ACTIVE, FAILED_COMFORT_COUNT

    text_lower = user_text.lower()
    now = time.time()

    # If in comfort mode → handle followups
    if COMFORT_ACTIVE:
        handled = comfort_followup(user_text, lang)
        if handled:
            return

    # Scheduled check-in
    if (LAST_MOOD in ["sad", "stressed", "angry"] and now - LAST_MOOD_TIME > CHECKIN_DELAY):
        speak(f"Hey, I was thinking about you. Are you feeling any better?", lang)
        LAST_MOOD_TIME = now
        COMFORT_ACTIVE = True
        return

    # --- Detect moods ---
    if any(word in text_lower for word in ["happy", "excited", "great", "awesome"]):
        LAST_MOOD = "happy"
        LAST_REASON = None
        LAST_MOOD_TIME = now
        FAILED_COMFORT_COUNT = 0

        # Friendly reply
        ai_reply = ask_ai(f"The user said they feel happy: '{user_text}'. Reply like a cheerful close friend.")
        speak(ai_reply, lang)

        # Ask why
        speak("That’s wonderful! What makes you this much happier?", lang)
        reason_reply = takecommand(lang)

        if reason_reply != "None":
            LAST_REASON = reason_reply
            speak(f"Wow! That’s amazing — {reason_reply}! 🎉", lang)

            # 🎉 Auto share happiness with Varun
            auto_share_with(HAPPY_FRIEND, "happy", LAST_REASON, tone="celebratory", lang=lang)
            speak(f"I’ve shared your happiness with {HAPPY_FRIEND} so they can celebrate with you too!", lang)

        COMFORT_ACTIVE = False
        return

    elif any(k in text_lower for k in ["sad", "lonely", "unhappy", "depressed"]):
        LAST_MOOD = "sad"
        LAST_REASON = None
        LAST_MOOD_TIME = now
        FAILED_COMFORT_COUNT = 0
        ai_reply = ask_ai(f"The user said they feel sad: '{user_text}'. Reply with empathy and care.")
        speak(ai_reply, lang)

        # Ask why
        speak("I’m here for you. Can you tell me what’s making you feel this way?", lang)
        reason_reply = takecommand(lang)
        if reason_reply != "None":
            LAST_REASON = reason_reply

        COMFORT_ACTIVE = True

    elif any(k in text_lower for k in ["angry", "frustrated", "irritated"]):
        LAST_MOOD = "angry"
        LAST_REASON = None
        LAST_MOOD_TIME = now
        FAILED_COMFORT_COUNT = 0
        ai_reply = ask_ai(f"The user said they feel angry: '{user_text}'. Reply calmly and help them relax.")
        speak(ai_reply, lang)
        speak("Can you tell me what made you feel this way?", lang)
        reason_reply = takecommand(lang)
        if reason_reply != "None":
            LAST_REASON = reason_reply
        speak("Take a deep breath in… and out. Feeling a little better?", lang)
        COMFORT_ACTIVE = True

    elif any(k in text_lower for k in ["stressed", "tired", "anxious", "worried"]):
        LAST_MOOD = "stressed"
        LAST_REASON = None
        LAST_MOOD_TIME = now
        FAILED_COMFORT_COUNT = 0
        ai_reply = ask_ai(f"The user said they feel stressed: '{user_text}'. Reply with empathy and calming advice.")
        speak(ai_reply, lang)
        speak("Would you like to share what’s making you feel stressed?", lang)
        reason_reply = takecommand(lang)
        if reason_reply != "None":
            LAST_REASON = reason_reply
        speak("Maybe take a short pause, stretch, and sip some water 🌿.", lang)
        COMFORT_ACTIVE = True


    else:
        # Neutral / general queries → ask AI directly
        ai_reply = ask_ai(f"The user asked: '{user_text}'. Reply helpfully, in a friendly and conversational way. "
                             f"If it's a factual question, give a clear short answer. "
                             f"If it's an opinion question, answer creatively. "
                             f"Never use asterisks, just speak naturally.")
        from ai import clean_text_for_speech
        speak(clean_text_for_speech(ai_reply), lang)
        COMFORT_ACTIVE = False
        FAILED_COMFORT_COUNT = 0
        return True
