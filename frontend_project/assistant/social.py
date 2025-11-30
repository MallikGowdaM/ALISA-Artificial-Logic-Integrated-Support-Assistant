from datetime import datetime
import os
import time
import traceback
from email.utils import formataddr, formatdate
import pyautogui
import re
from ai import ask_ai, classify_task, ask_ollama
from speech import speak, takecommand
import smtplib
import win32gui
import win32con
from email.mime.text import MIMEText
from keywords import CONTACTS
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def open_whatsapp_foreground():
    os.system("start whatsapp:")
    time.sleep(6)

    def enumHandler(hwnd, lParam):
        if win32gui.IsWindowVisible(hwnd):
            if "WhatsApp" in win32gui.GetWindowText(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # restore if minimized
                win32gui.SetForegroundWindow(hwnd)              # bring to front

    win32gui.EnumWindows(enumHandler, None)

def send_whatsapp_message(cmd="", lang="en"):
    """
    Send WhatsApp message via Desktop.
    - Case 1: "send whatsapp message to Kiran and say hi" → direct send
    - Case 2: "send whatsapp message to Kiran" → ask for message
    - Case 3: "send whatsapp message" → ask for both
    - Case 4: "send whatsapp message hi" → ask for contact
    """
    try:
        contact_name = None
        message = None

        # --- Case 1: contact + message ---
        match_full = re.search(r"send whatsapp (?:message )?to (.+?) (?:saying|and say|say) (.+)", cmd, re.IGNORECASE)

        # --- Case 2: only contact (no message) ---
        match_contact_only = re.search(r"send whatsapp (?:message )?to (.+)$", cmd, re.IGNORECASE)

        # --- Case 4: only message (no contact) ---
        match_message_only = re.search(r"send whatsapp (?:message )?(?:say|saying)?\s*(.+)$", cmd, re.IGNORECASE)

        if match_full:  # contact + message
            contact_name = match_full.group(1).strip()
            message = match_full.group(2).strip()
        elif match_contact_only:  # only contact
            contact_name = match_contact_only.group(1).strip()
            message = None
        elif match_message_only and not ("to " in cmd):  # only message
            contact_name = None
            message = match_message_only.group(1).strip()
        else:  # neither contact nor message
            contact_name = None
            message = None

        # --- Ask for contact if missing ---
        attempts = 0
        while not contact_name and attempts < 2:
            speak("To whom should I send the WhatsApp message?", lang)
            contact_name = takecommand(lang).lower().strip()
            if contact_name == "none" or not contact_name:
                contact_name = None
                attempts += 1
        if not contact_name:
            speak("Sorry, I couldn't get the contact name.", lang)
            return

        # --- Ask for message if missing ---
        attempts = 0
        while not message and attempts < 2:
            speak(f"What message should I send to {contact_name}?", lang)
            message = takecommand(lang)
            if message == "none" or not message:
                message = None
                attempts += 1
        if not message:
            speak("Sorry, I couldn't get the message.", lang)
            return

        # === Function to search and send ===
        def try_send(contact_name, message):
            open_whatsapp_foreground()

            pyautogui.hotkey("ctrl", "f")
            time.sleep(1)
            pyautogui.write(contact_name)
            time.sleep(2)

            pyautogui.press("down")
            time.sleep(1)
            pyautogui.press("enter")
            time.sleep(2)

            pyautogui.typewrite(" ")
            time.sleep(1)
            pyautogui.press("backspace")

            pyautogui.write(message)
            time.sleep(1)
            pyautogui.press("enter")

            os.system("taskkill /f /im WhatsApp.exe")
            return True

        # First attempt
        speak("Opening WhatsApp", lang)
        try:
            try_send(contact_name, message)
            speak(f"Message sent to {contact_name}.", lang)
            return
        except Exception:
            os.system("taskkill /f /im WhatsApp.exe")

        # Retry once
        speak("I could not find the contact. Please say the name again.", lang)
        contact_name = takecommand(lang).lower().strip()
        if contact_name == "none" or not contact_name:
            speak("Sorry, contact name not found.", lang)
            return

        try:
            try_send(contact_name, message)
            speak(f"Message sent to {contact_name}.", lang)
        except Exception:
            os.system("taskkill /f /im WhatsApp.exe")
            speak("Sorry, I still couldn’t find that contact.", lang)

    except Exception as e:
        speak(f"Something went wrong: {e}", lang)



# ⚠️ Configure your Gmail here
SENDER_EMAIL = "crazybeast7022@gmail.com"
SENDER_PASSWORD = "brse vmnw ntzp hejc"  # Use App Password from Google

def extract_name_from_email(email: str) -> str:
    """Extract a clean name from the email ID (ignores numbers)."""
    username = email.split("@")[0]
    clean_name = re.sub(r"\d+", "", username)  # remove numbers
    if not clean_name:
        return "User"
    return clean_name.capitalize()

def send_email(lang="en"):
    """Send an email via Gmail. Supports short names + AI body generation with defaults."""
    try:
        sender_display_name = "Mallik Gowda M"
        today_date = datetime.now().strftime("%B %d, %Y")  # e.g. September 23, 2025

        # --- Receiver ---
        speak("Whom should I send the email to?", lang)
        receiver = takecommand(lang).lower().replace(" ", "")
        if receiver == "none" or not receiver:
            speak("I couldn't get the receiver name.", lang)
            return

        # Case 1: Predefined contacts
        if receiver in CONTACTS:
            receiver_email = CONTACTS[receiver]
            speak(f"Okay, sending email to {receiver}.", lang)

        # Case 2: Explicit email
        elif "@" in receiver:
            receiver_email = receiver
            speak(f"Okay, sending email to {receiver_email}.", lang)

        # Case 3: Short name → assume Gmail
        else:
            receiver_email = f"{receiver}@gmail.com"
            speak(f"Okay, sending email to {receiver_email}.", lang)

        # --- Subject ---
        speak("What is the subject?", lang)
        subject = takecommand(lang)
        if subject == "none" or not subject:
            speak("I couldn’t get the subject.", lang)
            return

        # --- Body ---
        speak("Will you say the message content, or should I generate it using AI?", lang)
        choice = takecommand(lang).lower()

        if any(word in choice for word in ["say", "tell", "bol", "heli"]):
            speak("Okay, please say the message content now.", lang)
            body = takecommand(lang)
            if body == "none" or not body:
                speak("I couldn’t catch the message. I will generate it using AI instead.", lang)
                body = ask_ollama(
                    f"Write a professional email about: {subject}. "
                    f"Make sure it is signed by {sender_display_name} and dated {today_date}.",
                    model="llama3:instruct"
                )
        else:
            speak("Okay, I will generate the message using AI.", lang)
            body = ask_ollama(
                f"Write a professional email about: {subject}. "
                f"Make sure it is signed by {sender_display_name} and dated {today_date}.",
                model="llama3:instruct"
            )

        # --- Construct & send ---
        msg = MIMEText(body, "plain","utf-8")
        msg["Subject"] = subject
        msg["From"] = formataddr((sender_display_name, SENDER_EMAIL))
        msg["To"] = receiver_email
        msg["Date"] = formatdate(localtime=True)

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())

        speak(f"Email has been sent to {receiver}.", lang)

    except Exception as e:
        print("\n================ EMAIL ERROR ================")
        print(traceback.format_exc())  # full stack trace
        print("============================================\n")
        speak(f"Something went wrong: {e}", lang)

SPOTIFY_CLIENT_ID = "28a58dadea464478b747932555238d3b"
SPOTIFY_CLIENT_SECRET = "579ac7436e784509bd1a09fa0d2da0e6"
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8000/callback"

SCOPE = "user-read-playback-state user-modify-playback-state"

CACHE_PATH = ".spotify_cache"

def get_spotify_client():
    """Always return a valid Spotify client with auto token refresh."""
    try:
        auth_manager = SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope=SCOPE,
            cache_path=CACHE_PATH,  # custom cache file
            open_browser=True       # auto open login page if needed
        )
        return spotipy.Spotify(auth_manager=auth_manager)
    except Exception as e:
        print("Spotify auth error:", e)
        if os.path.exists(CACHE_PATH):
            os.remove(CACHE_PATH)  # clear bad cache
        raise

def play_song_on_spotify(song, lang="en"):
    try:
        sp = get_spotify_client()  # always returns valid Spotipy client

        results = sp.search(q=song, type="track", limit=1)
        tracks = results.get("tracks", {}).get("items", [])

        if not tracks:
            speak("Sorry, I could not find that song on Spotify.", lang)
            return

        chosen_track = tracks[0]
        track_name = chosen_track["name"]
        artist_name = chosen_track["artists"][0]["name"]
        track_uri = chosen_track["uri"]

        devices = sp.devices()
        if not devices["devices"]:
            speak("No active Spotify devices found. Please open Spotify Desktop app.", lang)
            return

        device_id = devices["devices"][0]["id"]

        sp.start_playback(device_id=device_id, uris=[track_uri])

        speak(f"Playing {track_name} by {artist_name} on Spotify.", lang)

    except Exception as e:
        print("Spotify Error:", e)
        speak("Something went wrong while trying to play on Spotify.", lang)

def close_spotify(lang="en"):
    try:
        os.system("taskkill /f /im Spotify.exe")
        if lang == "en":
            speak("Spotify has been closed.", lang)
        elif lang == "hi":
            speak("स्पॉटिफ़ाई बंद कर दिया गया है।", lang)
        elif lang == "kn":
            speak("ಸ್ಪಾಟಿಫೈ ಮುಚ್ಚಲಾಗಿದೆ.", lang)
    except Exception as e:
        print("Close Spotify Error:", e)
        if lang == "en":
            speak("I couldn't close Spotify.", lang)
        elif lang == "hi":
            speak("मैं स्पॉटिफ़ाई को बंद नहीं कर सका।", lang)
        elif lang == "kn":
            speak("ನಾನು ಸ್ಪಾಟಿಫೈ ಮುಚ್ಚಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ.", lang)


