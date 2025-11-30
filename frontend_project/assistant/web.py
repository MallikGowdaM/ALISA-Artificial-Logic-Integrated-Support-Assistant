import os
import time
import webbrowser
import pyautogui
import requests
import re
import urllib.request
from deep_translator import GoogleTranslator
from speech import speak, takecommand
from config import WEATHER_API_KEY, SERPAPI_KEY

# ----------------------------------------------------
# Known website shortcuts
# ----------------------------------------------------
SITE_MAP = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "facebook": "https://www.facebook.com",
    "instagram": "https://www.instagram.com",
    "twitter": "https://www.twitter.com",
    "github": "https://www.github.com",
    "wikipedia": "https://www.wikipedia.org",
    "chatgpt": "https://chat.openai.com"
}

current_tab = None


# ----------------------------------------------------
# Handle web-related commands
# ----------------------------------------------------
def handle_web_command(command, lang="en"):
    global current_tab
    command = command.lower()
    site_found = None

    for site in SITE_MAP:
        if site in command:
            site_found = site
            break

    # ---------- OPEN / SEARCH / PLAY ----------
    if "open" in command or "play" in command:
        if site_found:
            url = SITE_MAP[site_found]

            # ----- if search or play query exists -----
            if "search" in command or "play" in command:
                query = (
                    command.split("search", 1)[-1].strip()
                    if "search" in command
                    else command.split("play", 1)[-1].strip()
                )

                if query:
                    if "youtube" in site_found:
                        try:
                            search_query = query.replace(" ", "+")
                            html = urllib.request.urlopen(
                                f"https://www.youtube.com/results?search_query={search_query}"
                            )
                            video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
                            if video_ids:
                                first_video = f"https://www.youtube.com/watch?v={video_ids[0]}"
                                speak(f"Playing {query} on YouTube", lang)
                                webbrowser.open(first_video)
                            else:
                                speak(f"Couldn't find a video for {query}", lang)
                                webbrowser.open(f"https://www.youtube.com/results?search_query={search_query}")
                        except Exception as e:
                            print(f"YouTube autoplay error: {e}")
                            speak(f"Opening YouTube search results for {query}", lang)
                            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")

                    elif "google" in site_found:
                        speak(f"Searching {query} on Google", lang)
                        webbrowser.open(f"https://www.google.com/search?q={query}")

                    else:
                        speak(f"Searching {query} on {site_found}", lang)
                        webbrowser.open(f"{url}/search?q={query}")

                else:
                    # If user didn’t say what to search
                    speak(f"What should I search on {site_found}?", lang)
                    query = takecommand(lang)
                    if query and query.lower() != "none":
                        if "youtube" in site_found:
                            search_query = query.replace(" ", "+")
                            html = urllib.request.urlopen(
                                f"https://www.youtube.com/results?search_query={search_query}"
                            )
                            video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
                            if video_ids:
                                first_video = f"https://www.youtube.com/watch?v={video_ids[0]}"
                                speak(f"Playing {query} on YouTube", lang)
                                webbrowser.open(first_video)
                            else:
                                webbrowser.open(f"https://www.youtube.com/results?search_query={search_query}")
                        elif "google" in site_found:
                            webbrowser.open(f"https://www.google.com/search?q={query}")
                        else:
                            webbrowser.open(f"{url}/search?q={query}")
                    else:
                        speak(f"Opening {site_found}", lang)
                        webbrowser.open(url)

            else:
                # No search or play detected → ask user
                speak(f"What should I search on {site_found}?", lang)
                query = takecommand(lang)
                if query and query.lower() != "none":
                    if "youtube" in site_found:
                        try:
                            search_query = query.replace(" ", "+")
                            html = urllib.request.urlopen(
                                f"https://www.youtube.com/results?search_query={search_query}"
                            )
                            video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
                            if video_ids:
                                first_video = f"https://www.youtube.com/watch?v={video_ids[0]}"
                                speak(f"Playing {query} on YouTube", lang)
                                webbrowser.open(first_video)
                            else:
                                speak(f"Couldn't find a video for {query}", lang)
                                webbrowser.open(f"https://www.youtube.com/results?search_query={search_query}")
                        except Exception as e:
                            print(f"YouTube autoplay error: {e}")
                            speak(f"Opening YouTube search results for {query}", lang)
                            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
                    elif "google" in site_found:
                        speak(f"Searching {query} on Google", lang)
                        webbrowser.open(f"https://www.google.com/search?q={query}")
                    else:
                        speak(f"Searching {query} on {site_found}", lang)
                        webbrowser.open(f"{url}/search?q={query}")
                else:
                    speak(f"Opening {site_found}", lang)
                    webbrowser.open(url)

            current_tab = site_found

        else:
            # Site not found → ask the user
            speak("Which site should I open?", lang)
            site_name = takecommand(lang)
            if site_name and site_name != "none":
                if site_name in SITE_MAP:
                    webbrowser.open(SITE_MAP[site_name])
                else:
                    webbrowser.open(f"https://www.google.com/search?q={site_name}")

    # ---------- CLOSE ----------
    elif "close" in command:
        try:
            speak("Closing browser tab", lang)
            time.sleep(0.5)
            pyautogui.hotkey("ctrl", "w")  # shortcut to close tab
        except Exception as e:
            print(f"Close error: {e}")
            speak("Unable to close the site right now.", lang)


# ----------------------------------------------------
# Translation helper
# ----------------------------------------------------
def translate_text(text, lang):
    try:
        if lang in ("hi", "kn"):
            return GoogleTranslator(source="auto", target=lang).translate(text)
        return text
    except Exception as e:
        print(f"Translation error: {e}")
        return text


# ----------------------------------------------------
# Weather information
# ----------------------------------------------------
def get_weather(city_name, lang="en"):
    try:
        city_name_en = GoogleTranslator(source="auto", target="en").translate(city_name)
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name_en}&appid={WEATHER_API_KEY}&units=metric"
        data = requests.get(url).json()

        if data.get("cod") != 200:
            speak("City not found.", lang)
            return

        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]

        if lang == "hi":
            msg = f"{city_name} में तापमान {temp} डिग्री सेल्सियस है, मौसम {desc} है।"
        elif lang == "kn":
            msg = f"{city_name} ನಲ್ಲಿ ತಾಪಮಾನ {temp}°C ಮತ್ತು ಹವಾಮಾನ {desc}."
        else:
            msg = f"The temperature in {city_name} is {temp}°C with {desc}."
        speak(msg, lang)

    except Exception as e:
        print(f"Weather error: {e}")
        speak("Sorry, weather info not available.", lang)


# ----------------------------------------------------
# News headlines using SerpAPI
# ----------------------------------------------------
def get_news_headlines(lang="en"):
    try:
        params = {
            "engine": "google_news",
            "q": "today news",
            "hl": "en",
            "gl": "in",
            "api_key": SERPAPI_KEY
        }
        data = requests.get("https://serpapi.com/search", params=params, timeout=5).json()
        headlines = [item.get("title", "") for item in data.get("news_results", [])[:5]]

        if not headlines:
            speak("No news found.", lang)
            return

        speak("Here are today's top headlines.", lang)
        for i, title in enumerate(headlines, 1):
            speak(f"Headline {i}: {title}", lang)

    except Exception as e:
        print(f"News error: {e}")
        speak("Sorry, I couldn't fetch the latest news.", lang)
