import speech_recognition as sr

recognizer = sr.Recognizer()

with sr.Microphone() as source:
    print("Adjusting for background noise...")
    recognizer.adjust_for_ambient_noise(source, duration=1)

    print("Speak your command...")
    audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)

try:
    text = recognizer.recognize_google(audio)
    print("You said:", text)

except sr.UnknownValueError:
    print("Sorry, I could not understand the voice.")

except sr.RequestError as e:
    print("Speech recognition service error:", e)

except Exception as e:
    print("Error:", e)
    