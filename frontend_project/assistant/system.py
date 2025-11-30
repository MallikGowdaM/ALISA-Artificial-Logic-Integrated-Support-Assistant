# system.py
import ctypes
import datetime
import os, subprocess, psutil
import socket
import threading
import cv2
import pyautogui
import requests
from speech import speak, takecommand
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import os
import subprocess
import psutil
import screen_brightness_control as sbc
from speech import speak
import time

def system_status(lang="en"):
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    battery = psutil.sensors_battery()

    if lang == "hi":
        message = f"सी पी यू {cpu} प्रतिशत, रैम {ram} प्रतिशत, डिस्क {disk} प्रतिशत।"
        if battery: message += f" बैटरी {battery.percent} प्रतिशत।"
        speak(message, lang="hi")
    elif lang == "kn":
        message = f"ಸಿಪಿಯು {cpu} ಶೇಕಡಾ, ರಾಮ್ {ram} ಶೇಕಡಾ, ಡಿಸ್ಕ್ {disk} ಶೇಕಡಾ."
        if battery: message += f" ಬ್ಯಾಟರಿ {battery.percent} ಶೇಕಡಾ."
        speak(message, lang="kn")
    else:
        message = f"CPU {cpu}% RAM {ram}% Disk {disk}%."
        if battery: message += f" Battery {battery.percent}%"
        speak(message, lang="en")

def shutdown_pc(lang="en"):
    os.system("shutdown /s /t 5")
    if lang == "hi":
        speak("सिस्टम शटडाउन हो रहा है।", lang="hi")
    elif lang == "kn":
        speak("ಸಿಸ್ಟಮ್ ಶಟ್ ಡೌನ್ ಆಗುತ್ತಿದೆ.", lang="kn")
    else:
        speak("Shutting down the system.", lang="en")

def restart_pc(lang="en"):
    os.system("shutdown /r /t 5")
    if lang == "hi":
        speak("सिस्टम रीस्टार्ट हो रहा है।", lang="hi")
    elif lang == "kn":
        speak("ಸಿಸ್ಟಮ್ ಮರುಪ್ರಾರಂಭಗೊಳ್ಳುತ್ತಿದೆ.", lang="kn")
    else:
        speak("Restarting the system.", lang="en")

def sleep(lang="en"):
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    if lang == "hi":
        speak("सिस्टम स्लीप मोड में जा रहा है।", lang="hi")
    elif lang == "kn":
        speak("ಸಿಸ್ಟಮ್ ನಿದ್ರಾ ಸ್ಥಿತಿಗೆ ಹೋಗುತ್ತಿದೆ.", lang="kn")
    else:
        speak("Putting system to sleep.", lang="en")

def lock(lang="en"):
    os.system("rundll32.exe user32.dll,LockWorkStation")
    if lang == "hi":
        speak("सिस्टम लॉक हो गया है।", lang="hi")
    elif lang == "kn":
        speak("ಸಿಸ್ಟಮ್ ಲಾಕ್ ಮಾಡಲಾಗಿದೆ.", lang="kn")
    else:
        speak("Locking the system.", lang="en")

# -----------------------------
# Camera Control
# -----------------------------

def camera_loop(cmp, stop_flag):
    """Continuously show webcam frames."""
    try:
        while not stop_flag["stop"]:
            ret, img = cmp.read()
            if not ret:
                continue
            cv2.imshow('Laptop Camera', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):  # emergency quit with Q key
                stop_flag["stop"] = True
                break
    finally:
        # ✅ Always close window from inside the loop thread
        cv2.destroyAllWindows()
        cv2.waitKey(1)

def open_camera(lang="en"):
    # ✅ Always open laptop's built-in camera
    cmp = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # for Windows laptops
    cmp.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cmp.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cmp.isOpened():
        speak("Laptop camera could not be opened.", lang)
        return

    # Instructions
    if lang == "hi":
        speak("कैमरा चालू है। 'फोटो खींचो' कहें या 'कैमरा बंद करो' कहें।", lang)
    elif lang == "kn":
        speak("ಕ್ಯಾಮೆರಾ ತೆರೆಯಲಾಗಿದೆ. 'ಫೋಟೋ ತೆಗೆಯಿರಿ' ಅಥವಾ 'ಕ್ಯಾಮೆರಾ ಮುಚ್ಚಿ' ಎಂದು ಹೇಳಿ.", lang)
    else:
        speak("Laptop camera is open. Say 'click photo' to capture, or 'close camera' to exit.", lang)

    stop_flag = {"stop": False}

    # ✅ Start camera thread
    t = threading.Thread(target=camera_loop, args=(cmp, stop_flag))
    t.start()

    while not stop_flag["stop"]:
        try:
            command = takecommand(lang).lower()  # this won’t freeze the camera thread
            if "click photo" in command or "take photo" in command:
                ret, img = cmp.read()
                if ret:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    BACKEND_DIR = os.path.join(os.getcwd(), "backend", "captures")
                    os.makedirs(BACKEND_DIR, exist_ok=True)
                    img_path = os.path.join(BACKEND_DIR, f"captured_{timestamp}.jpg")

                    # Enhance photo
                    alpha, beta = 1.3, 20
                    enhanced = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
                    cv2.imwrite(img_path, enhanced, [cv2.IMWRITE_JPEG_QUALITY, 95])

                    speak("Photo saved with better quality.", lang)

            elif "close camera" in command or "exit camera" in command:
                speak("Closing laptop camera now.", lang)
                stop_flag["stop"] = True
                break
        except Exception:
            continue

    t.join(timeout=2)
    if cmp.isOpened():
        cmp.release()
# -----------------------------
# Window Controls
# -----------------------------
def switch_window(lang="en"):
    """Switch between open windows (Alt+Tab)."""
    pyautogui.keyDown("alt")
    pyautogui.press("tab")
    pyautogui.keyUp("alt")
    if lang == "hi":
        speak("विंडो बदल दी गई है।", lang)
    elif lang == "kn":
        speak("ವಿಂಡೋ ಬದಲಾಯಿಸಲಾಗಿದೆ.", lang)
    else:
        speak("Switched window.", lang)


def minimize_window(lang="en"):
    """Force minimize the active window using Windows API."""
    user32 = ctypes.windll.user32
    hwnd = user32.GetForegroundWindow()
    user32.ShowWindow(hwnd, 6)  # 6 = SW_MINIMIZE

    if lang == "hi":
        speak("विंडो छोटा कर दिया गया है।", lang)
    elif lang == "kn":
        speak("ವಿಂಡೋ ಸಣ್ಣದಾಗಿದೆ.", lang)
    else:
        speak("Window minimized.", lang)


# -----------------------------
# Browser Tab Controls
# -----------------------------
def switch_tab(next=True, lang="en"):
    """Switch between browser tabs (Ctrl+Tab / Ctrl+Shift+Tab)."""
    if next:
        pyautogui.hotkey("ctrl", "tab")
    else:
        pyautogui.hotkey("ctrl", "shift", "tab")
    if lang == "hi":
        speak("टैब बदल दिया गया है।", lang)
    elif lang == "kn":
        speak("ಟ್ಯಾಬ್ ಬದಲಾಯಿಸಲಾಗಿದೆ.", lang)
    else:
        speak("Switched tab.", lang)

def get_ip_address(lang="en"):
    """Get and speak the system's IP address (local + public)."""
    try:
        # Local IP
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)

        # Public IP
        public_ip = requests.get("https://api.ipify.org").text
    except Exception as e:
        if lang == "hi":
            speak("आई पी पता प्राप्त करने में त्रुटि हुई।", lang)
        elif lang == "kn":
            speak("ಐಪಿ ವಿಳಾಸ ಪಡೆಯುವಲ್ಲಿ ದೋಷವಾಗಿದೆ.", lang)
        else:
            speak("Error getting IP address.", lang)
        return

    if lang == "hi":
        speak(f"आपका लोकल आई पी {local_ip} है और पब्लिक आई पी {public_ip} है।", lang)
    elif lang == "kn":
        speak(f"ನಿಮ್ಮ ಸ್ಥಳೀಯ ಐಪಿ {local_ip}, ಮತ್ತು ಸಾರ್ವಜನಿಕ ಐಪಿ {public_ip} ಆಗಿದೆ.", lang)
    else:
        speak(f"Your local IP is {local_ip}, and your public IP is {public_ip}.", lang)


#-------------------------------------------------------
# Volume Control
#-------------------------------------------------------
def control_volume(command, lang="en"):
    """
    Adjusts the system volume based on the spoken command.
    """
    try:
        # Get system volume interface
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))

        # Get current volume (0.0 to 1.0)
        current_volume = volume.GetMasterVolumeLevelScalar()

        command = command.lower()

        # --- Volume up ---
        if any(word in command for word in ["increase", "up", "raise", "louder"]):
            new_volume = min(current_volume + 0.1, 1.0)
            volume.SetMasterVolumeLevelScalar(new_volume, None)
            speak("Volume increased.", lang)

        # --- Volume down ---
        elif any(word in command for word in ["decrease", "down", "lower", "reduce", "quieter"]):
            new_volume = max(current_volume - 0.1, 0.0)
            volume.SetMasterVolumeLevelScalar(new_volume, None)
            speak("Volume decreased.", lang)

        # --- Unmute ---
        elif "unmute" in command or "sound on" in command:
            volume.SetMute(0, None)
            speak("Sound unmuted.", lang)

        # --- Mute ---
        elif "mute" in command:
            volume.SetMute(1, None)
            speak("System muted.", lang)

        # --- Set specific percentage ---
        elif "%" in command or "percent" in command:
            import re
            num = re.findall(r"\d+", command)
            if num:
                level = int(num[0]) / 100
                volume.SetMasterVolumeLevelScalar(min(max(level, 0.0), 1.0), None)
                speak(f"Volume set to {num[0]} percent.", lang)
            else:
                speak("Please say a valid volume percentage.", lang)

        else:
            speak("I didn't understand the volume command.", lang)

    except Exception as e:
        print(f"Volume control error: {e}")
        speak("Sorry, I couldn’t adjust the volume.", lang)

def system_control(command, lang="en"):
    command = command.lower().strip()

    # -------------------------------
    # Wi-Fi control
    # -------------------------------
    if "wifi" in command:
        if "on" in command:
            speak("Turning on Wi-Fi.", lang)
            os.system("netsh interface set interface \"Wi-Fi\" enabled")
        elif "off" in command:
            speak("Turning off Wi-Fi.", lang)
            os.system("netsh interface set interface \"Wi-Fi\" disabled")
        else:
            speak("Do you want to turn Wi-Fi on or off?", lang)

    # -------------------------------
    # Bluetooth control (Windows 10+)
    # -------------------------------
    elif "bluetooth" in command:
        try:
            if "on" in command:
                speak("Turning on Bluetooth.", lang)
                os.system("start ms-settings:bluetooth")
                time.sleep(1)
                pyautogui.hotkey("tab", "tab", "space")  # opens settings toggle
            elif "off" in command:
                speak("Turning off Bluetooth.", lang)
                os.system("start ms-settings:bluetooth")
                time.sleep(1)
                pyautogui.hotkey("tab", "tab", "space")
            else:
                speak("Do you want to turn Bluetooth on or off?", lang)
        except Exception as e:
            print(f"Bluetooth error: {e}")
            speak("Sorry, Bluetooth control is not available right now.", lang)

    # -------------------------------
    # Screen brightness control
    # -------------------------------
    elif "brightness" in command:
        try:
            current = sbc.get_brightness(display=0)[0]
            if "increase" in command or "up" in command:
                sbc.set_brightness(min(current + 10, 100))
                speak("Increased brightness.", lang)
            elif "decrease" in command or "down" in command or "reduce" in command:
                sbc.set_brightness(max(current - 10, 0))
                speak("Decreased brightness.", lang)
            elif "%" in command or "percent" in command:
                import re
                num = re.findall(r"\d+", command)
                if num:
                    sbc.set_brightness(int(num[0]))
                    speak(f"Brightness set to {num[0]} percent.", lang)
                else:
                    speak("Please specify the brightness level.", lang)
            else:
                speak(f"Current brightness is {current} percent.", lang)
        except Exception as e:
            print(f"Brightness error: {e}")
            speak("Unable to control brightness right now.", lang)

    # -------------------------------
    # Keyboard backlight (using WMI)
    # -------------------------------
    elif "keyboard light" in command or "keyboard backlight" in command:
        try:
            # Lenovo Legion keyboards toggle light with Fn + Spacebar
            speak("Toggling keyboard backlight.", lang)
            time.sleep(0.5)

            # Try sending the hardware toggle shortcut
            pyautogui.hotkey("fn", "space")

        except Exception as e:
            print(f"Keyboard light toggle error: {e}")
            speak("Sorry, I couldn't toggle the keyboard light. "
                  "You may need to press Function plus Spacebar manually.", lang)

    # -------------------------------
    # Battery saver
    # -------------------------------
    elif "battery saver" in command or "power saver" in command:
        try:
            if "on" in command or "enable" in command:
                speak("Turning on battery saver.", lang)
                os.system("powercfg /setactive a1841308-3541-4fab-bc81-f71556f20b4a")  # Power saver GUID
            elif "off" in command or "disable" in command:
                speak("Turning off battery saver.", lang)
                os.system("powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e")  # Balanced mode
            else:
                speak("Do you want to turn battery saver on or off?", lang)
        except Exception as e:
            print(f"Battery saver error: {e}")
            speak("Battery saver control not available.", lang)

    else:
        speak("Sorry, I didn’t understand the system control command.", lang)