import os
import subprocess
import webbrowser
import pywhatkit
from speech import speak, takecommand


APP_MAP = {
    # System apps
     "word": ("winword", "WINWORD.EXE"),
    "ms word": ("winword", "WINWORD.EXE"),
    "microsoft word": ("winword", "WINWORD.EXE"),
    "excel": ("excel", "EXCEL.EXE"),
    "ms excel": ("excel", "EXCEL.EXE"),
    "microsoft excel": ("excel", "EXCEL.EXE"),
    "powerpoint": ("powerpnt", "POWERPNT.EXE"),
    "ms powerpoint": ("powerpnt", "POWERPNT.EXE"),
    "microsoft powerpoint": ("powerpnt", "POWERPNT.EXE"),
    "onenote": ("onenote", "ONENOTE.EXE"),
    "ms onenote": ("onenote", "ONENOTE.EXE"),
    "microsoft onenote": ("onenote", "ONENOTE.EXE"),
    "notepad": ("notepad", "notepad.exe"),
    "calculator": ("calc", "Calculator.exe"),
    "paint": ("mspaint", "mspaint.exe"),
    "explorer": ("explorer", "explorer.exe"),
    "terminal": ("cmd", "cmd.exe"),
    "calendar": ("outlookcal:", "OUTLOOK.EXE"),
    "settings": ("ms-settings:", "SystemSettings.exe"),
}

# ---------------------------------
# OPEN
# ---------------------------------
def open_app(app_name: str, lang="en", query=None):
    app_name = app_name.lower().strip()

    # SYSTEM APP
    if app_name in APP_MAP and APP_MAP[app_name] != "web":
        exe = APP_MAP[app_name]
        subprocess.Popen(["start", exe[0]], shell=True)
        speak(f"Opening {app_name}", lang)

    # WEB APP
    elif app_name == "google":
        if not query:
            speak("What should I search on Google?", lang)
            query = takecommand(lang)
        if query and query != "None":
            webbrowser.open(f"https://www.google.com/search?q={query}")
            speak(f"Searching {query} on Google", lang)

    elif app_name == "youtube":
        if not query:
            speak("What should I play on YouTube?", lang)
            query = takecommand(lang)
        if query and query != "None":
            pywhatkit.playonyt(query)
            speak(f"Playing {query} on YouTube", lang)

    elif app_name == "instagram":
        webbrowser.open("https://www.instagram.com")
        speak("Opening Instagram", lang)

    elif app_name == "facebook":
        webbrowser.open("https://www.facebook.com")
        speak("Opening Facebook", lang)

    else:
        speak(f"Sorry, I don’t know how to open {app_name}.", lang)


# ---------------------------------
# CLOSE
# ---------------------------------
def close_app(app_name: str, lang="en"):
    app_name = app_name.lower().strip()

    # SYSTEM APP
    if app_name in APP_MAP and APP_MAP[app_name] != "web":
        exe = APP_MAP[app_name]
        os.system(f"taskkill /f /im {exe[1]}")
        speak(f"{app_name} closed successfully.", lang)

    # WEB APP → close browser processes
    elif app_name in ["google", "youtube", "instagram", "facebook", "browser"]:
        browsers = ["brave.exe", "chrome.exe", "msedge.exe", "firefox.exe"]
        closed_any = False
        for browser in browsers:
            result = os.system(f"taskkill /f /im {browser} >nul 2>&1")
            if result == 0:
                closed_any = True
        if closed_any:
            speak("Browser closed successfully.", lang)
        else:
            speak("No browser was running or I couldn’t close it.", lang)

    else:
        speak(f"I don’t know how to close {app_name}.", lang)
