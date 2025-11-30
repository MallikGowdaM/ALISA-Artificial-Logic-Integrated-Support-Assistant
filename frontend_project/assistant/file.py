# file.py
import os
import threading
import time
import subprocess
from pathlib import Path
import PyPDF2
import docx
import openpyxl
from speech import speak, takecommand
from ai import ask_ai   # Summarization with Gemma
# --- PATHS (adjust for OneDrive if needed) ---
BASE_PATH = r"D:\\"
DESKTOP_PATH = r"C:\Users\malli\Desktop"
DOWNLOADS_PATH = r"C:\Users\malli\Downloads"
DOCUMENTS_PATH = r"C:\Users\malli\Documents"

# ----------------------------
# HELPERS
# ----------------------------
def normalize_filename(spoken_name: str) -> str:
    """Convert spoken file names into actual filenames with extensions."""
    if not spoken_name:
        return ""
    name = spoken_name.lower().strip()
    name = name.replace(" dot ", ".")   # e.g. "trip dot document" -> "trip.document"
    name = name.replace(" ", "")        # remove spaces

    # Map common spoken words to extensions
    if name.endswith("document"):
        name = name.replace("document", "docx")
    elif name.endswith("text"):
        name = name.replace("text", "txt")
    elif name.endswith("excel"):
        name = name.replace("excel", "xlsx")
    # pdf stays pdf

    return name

def read_text_file(file_path):
    global listening_active
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def read_pdf_file(file_path):
    global listening_active
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        return "".join([page.extract_text() or "" for page in reader.pages])

def read_docx_file(file_path):
    global listening_active
    doc = docx.Document(file_path)
    return "\n".join(para.text for para in doc.paragraphs)

def read_excel_file(file_path):
    global listening_active
    try:
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active
        rows = []
        for row in sheet.iter_rows(values_only=True):
            row_text = ", ".join([str(cell) for cell in row if cell is not None])
            rows.append(row_text)
        return "\n".join(rows)
    except Exception:
        speak("Failed to read the Excel file.")
        return ""

def find_file(filename, search_paths):
    """Try all supported extensions if user did not specify one."""
    extensions = [".pdf", ".txt", ".docx", ".xlsx", ""]
    for path in search_paths:
        for root, dirs, files in os.walk(path):
            for ext in extensions:
                if filename.endswith(ext) and filename in files:
                    return os.path.join(root, filename)
                elif not filename.endswith(ext) and (filename + ext) in files:
                    return os.path.join(root, filename + ext)
    return None

# ----------------------------
# CREATE FOLDER
# ----------------------------
def create_folder(cmd=None):
    folder_name = None
    if cmd:
        words = cmd.lower().replace("create", "").replace("folder", "").strip()
        if words:
            folder_name = words

    attempts = 0
    while not folder_name and attempts < 2:
        speak("What should I name the folder?")
        response = takecommand()
        attempts += 1
        if response and response.lower() != "none":
            folder_name = response.strip()

    if not folder_name:
        speak("Could not get folder name. Cancelled.")
        return

    folder_path = os.path.join(BASE_PATH, folder_name)
    try:
        os.makedirs(folder_path, exist_ok=True)
        speak(f"Folder {folder_name} created on Desktop.")
    except Exception as e:
        speak(f"Error creating folder: {e}")

# ----------------------------
# CREATE FILE
# ----------------------------
def create_file(cmd=None):
    file_name = None
    if cmd:
        words = cmd.lower().replace("create", "").replace("file", "").strip()
        if words:
            file_name = normalize_filename(words)

    attempts = 0
    while not file_name and attempts < 2:
        speak("What should I name the file?")
        response = takecommand()
        attempts += 1
        if response and response.lower() != "none":
            file_name = normalize_filename(response)

    if not file_name:
        speak("Could not get file name. Cancelled.")
        return

    # ✅ Smart extension detection
    ext = None
    if "doc" in file_name or "document" in file_name or "word" in file_name:
        ext = ".docx"
    elif "excel" in file_name or "sheet" in file_name:
        ext = ".xlsx"
    elif "pdf" in file_name:
        ext = ".pdf"
    elif "note" in file_name or "text" in file_name:
        ext = ".txt"

    # If not detected → ask user
    if not ext:
        speak("Do you want it as Word, Excel, PDF, or Text?")
        response = takecommand().lower()
        if "word" in response or "document" in response or "doc" in response:
            ext = ".docx"
        elif "excel" in response or "sheet" in response:
            ext = ".xlsx"
        elif "pdf" in response:
            ext = ".pdf"
        else:
            ext = ".txt"  # default

    # Remove accidental duplicates like "reportdocx"
    for bad_ext in ["docx", "xlsx", "pdf", "txt"]:
        if file_name.endswith(bad_ext):
            file_name = file_name[: -len(bad_ext)]

    file_name = file_name.strip() + ext

    file_path = os.path.join(BASE_PATH, file_name)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("")
        speak(f"File {file_name} created on Desktop.")
    except Exception as e:
        speak(f"Error creating file: {e}")

# ----------------------------
# OPEN FILE
# ----------------------------
def open_file_interactive(cmd=None, lang="en"):
    """
    Open a file based on user command.
    If name given → use directly.
    If missing → ask up to 2 times, else cancel.
    """

    search_dirs = []
    file_name = None

    if cmd:
        spoken_cmd = cmd.lower()
        # Detect drive/folder
        if "desktop" in spoken_cmd: search_dirs = [DESKTOP_PATH]
        elif "download" in spoken_cmd or "downloads" in spoken_cmd: search_dirs = [DOWNLOADS_PATH]
        elif "document" in spoken_cmd or "documents" in spoken_cmd: search_dirs = [DOCUMENTS_PATH]
        elif "d drive" in spoken_cmd or spoken_cmd.strip() == "d": search_dirs = ["D:\\"]
        elif "c drive" in spoken_cmd or spoken_cmd.strip() == "c": search_dirs = ["C:\\"]
        # Extract possible file name
        words = spoken_cmd.replace("open", "").replace("file", "").replace("in", "").split()
        candidate = [w for w in words if w not in ["desktop", "downloads", "documents", "c", "d", "drive", "the", "a"]]
        if candidate:
            file_name = normalize_filename("".join(candidate))

    # Ask for location if missing (retry max 2 times)
    attempts = 0
    while not search_dirs and attempts < 2:
        speak("Where should I look? Desktop, Downloads, Documents, C drive, or D drive?")
        drive_response = takecommand().lower()
        attempts += 1
        if "desktop" in drive_response: search_dirs = [DESKTOP_PATH]
        elif "download" in drive_response or "downloads" in drive_response: search_dirs = [DOWNLOADS_PATH]
        elif "document" in drive_response or "documents" in drive_response: search_dirs = [DOCUMENTS_PATH]
        elif "d drive" in drive_response or drive_response.strip() == "d": search_dirs = ["D:\\"]
        elif "c drive" in drive_response or drive_response.strip() == "c": search_dirs = ["C:\\"]
    if not search_dirs:
        speak("Could not understand location. Cancelled.")
        return

    # Ask for file name if missing (retry max 2 times)
    attempts = 0
    while not file_name and attempts < 2:
        speak("What is the file name?")
        response = takecommand()
        attempts += 1
        if response and response.lower() != "none":
            file_name = normalize_filename(response)
    if not file_name:
        speak("Could not get file name. Cancelled.")
        return

    # Find file
    file_path = find_file(file_name, search_dirs)
    if not file_path:
        speak(f"Sorry, I couldn’t find {file_name}.")
        return

    # Ask action
    speak("Should I read it, summarize it, or just open it?")
    choice = takecommand().lower()

    if "summarize" in choice or "summary" in choice:
        text = ""
        if file_path.endswith(".pdf"): text = read_pdf_file(file_path)
        elif file_path.endswith(".txt"): text = read_text_file(file_path)
        elif file_path.endswith(".docx"): text = read_docx_file(file_path)
        elif file_path.endswith(".xlsx"): text = read_excel_file(file_path)
        trimmed = text[:3000] if len(text) > 3000 else text
        summary = ask_ai(f"Summarize the following document:\n{trimmed}")
        speak("Here's the summary:")
        speak(summary)

    elif "read" in choice:
        text = ""
        if file_path.endswith(".pdf"): text = read_pdf_file(file_path)
        elif file_path.endswith(".txt"): text = read_text_file(file_path)
        elif file_path.endswith(".docx"): text = read_docx_file(file_path)
        elif file_path.endswith(".xlsx"): text = read_excel_file(file_path)

        speak("Starting to read. Say 'stop reading' anytime.")
        reading_stopped = False

        def listen_for_stop():
            nonlocal reading_stopped
            while not reading_stopped:
                cmd = takecommand(ignore_flag=True).lower()  # bypass pause
                if "stop" in cmd:
                    reading_stopped = True
                    speak("Ok, stopped reading.")

        threading.Thread(target=listen_for_stop, daemon=True).start()

        for line in text.split("\n"):
            if reading_stopped:
                break
            if line.strip():
                speak(line.strip())
                time.sleep(0.3)

    else:
        subprocess.Popen(["start", file_path], shell=True)
        speak("Opening file.")
