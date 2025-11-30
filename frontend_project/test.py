import pyttsx3
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
for i, voice in enumerate(voices):
    print(f"Index {i}: {voice.name} | {voice.id}")
