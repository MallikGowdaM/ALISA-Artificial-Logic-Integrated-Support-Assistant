import random
import datetime
from speech import speak

MORNING_QUOTES = [
    "Rise and shine! Today is full of opportunities. 🌞",
    "Good morning! Start your day with positivity and determination.",
    "Wake up with determination, go to bed with satisfaction. 💪"
]

AFTERNOON_QUOTES = [
    "Keep pushing, you’re doing amazing! 🌟",
    "Stay focused, you’re halfway through the day!",
    "Good afternoon! Take a short break, refresh, and get back stronger."
]

NIGHT_QUOTES = [
    "Relax, you’ve done enough for today. 🌙",
    "Good night! Tomorrow is a new chance to shine.",
    "End the day with gratitude and a smile. ✨"
]

GENERAL_QUOTES = [
    "Believe you can, and you’re halfway there. 🌟",
    "Your limitation—it’s only your imagination. 🚀",
    "Great things never come from comfort zones. 💪",
    "Stay positive, work hard, and make it happen."
]
def introduce(lang="en"):
    if lang == "en":
        speak("Hey! I’m Jarvis, your friendly AI assistant.", lang)
        speak("I can chat with you, understand your feelings, and keep you company.", lang)
        speak("Technically, I can also send WhatsApp messages, emails, play music on Spotify, control apps, manage reminders, and even plan your trips or study schedule.", lang)
        speak("So, I’m both your buddy and your smart assistant!", lang)
    elif lang == "hi":
        speak("नमस्ते! मैं जार्विस हूँ, आपका दोस्ताना एआई सहायक। 🤖", lang)
        speak("मैं आपसे बात कर सकता हूँ, आपकी भावनाओं को समझ सकता हूँ और आपका साथ दे सकता हूँ।", lang)
        speak("तकनीकी रूप से, मैं व्हाट्सएप संदेश भेज सकता हूँ, ईमेल भेज सकता हूँ, स्पॉटिफ़ाई पर गाने चला सकता हूँ, ऐप्स नियंत्रित कर सकता हूँ और रिमाइंडर भी संभाल सकता हूँ।", lang)
        speak("यानी मैं आपका दोस्त भी हूँ और स्मार्ट सहायक भी!", lang)
    elif lang == "kn":
        speak("ನಮಸ್ಕಾರ! ನಾನು ಜಾರ್ವಿಸ್, ನಿಮ್ಮ ಸ್ನೇಹಪರ ಎಐ ಸಹಾಯಕ. 🤖", lang)
        speak("ನಾನು ನಿಮ್ಮೊಂದಿಗೆ ಮಾತನಾಡಬಹುದು, ನಿಮ್ಮ ಭಾವನೆಗಳನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಬಹುದು ಮತ್ತು ನಿಮ್ಮ ಜೊತೆಗಿರುತ್ತೇನೆ.", lang)
        speak("ತಾಂತ್ರಿಕವಾಗಿ, ನಾನು ವಾಟ್ಸಾಪ್ ಸಂದೇಶಗಳನ್ನು ಕಳುಹಿಸಬಹುದು, ಇಮೇಲ್ ಕಳುಹಿಸಬಹುದು, ಸ್ಪಾಟಿಫೈನಲ್ಲಿ ಹಾಡುಗಳನ್ನು ಪ್ಲೇ ಮಾಡಬಹುದು, ಆಪ್‌ಗಳನ್ನು ನಿಯಂತ್ರಿಸಬಹುದು ಮತ್ತು ರಿಮೈಂಡರ್‌ಗಳನ್ನು ನಿರ್ವಹಿಸಬಹುದು.", lang)
        speak("ಹೀಗಾಗಿ ನಾನು ನಿಮ್ಮ ಸ್ನೇಹಿತನೂ ಆಗಿದ್ದೇನೆ ಮತ್ತು ಬುದ್ಧಿವಂತ ಸಹಾಯಕನೂ ಆಗಿದ್ದೇನೆ!", lang)

def daily_quote(lang="en"):
    hour = datetime.datetime.now().hour

    if 5 <= hour < 12:
        quote = random.choice(MORNING_QUOTES)
    elif 12 <= hour < 18:
        quote = random.choice(AFTERNOON_QUOTES)
    elif 18 <= hour < 23:
        quote = random.choice(NIGHT_QUOTES)
    else:
        quote = random.choice(GENERAL_QUOTES)

    if lang == "en":
        speak(f"Here’s your motivational boost: {quote}", lang)
    elif lang == "hi":
        speak(f"आज का प्रेरणादायक विचार: {quote}", lang)
    elif lang == "kn":
        speak(f"ಇಂದಿನ ಪ್ರೇರಣಾದಾಯಕ ವಾಕ್ಯ: {quote}", lang)
